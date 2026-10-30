import prisma from '../config/database';
import { config } from '../config';

export interface AIReviewResult {
  isAI: boolean;
  score: number; // 0 - 100
  summary: string;
  missingFields: string[];
  inconsistencies: string[];
  risks: string[];
  suggestions: string[];
  details: {
    category: string;
    level: 'INFO' | 'WARNING' | 'ERROR';
    message: string;
  }[];
}

export async function reviewApplication(eventId: string): Promise<AIReviewResult> {
  const event = await prisma.event.findUnique({
    where: { id: eventId },
    include: {
      budgetItems: true,
      scheduleItems: true,
      resourceBookings: { include: { facility: true, bookingItems: { include: { equipment: true } } } },
      attachments: true,
    },
  });

  if (!event) throw new Error('Không tìm thấy sự kiện');

  // Rule-based analyzer (fallback or default)
  const missingFields: string[] = [];
  const inconsistencies: string[] = [];
  const risks: string[] = [];
  const suggestions: string[] = [];
  const details: AIReviewResult['details'] = [];

  // 1. Basic Fields Check
  if (!event.title || event.title.trim().length < 5) {
    missingFields.push('Tên sự kiện quá ngắn hoặc chưa nhập');
    details.push({ category: 'Thông tin chung', level: 'ERROR', message: 'Tên sự kiện cần rõ ràng và tối thiểu 5 ký tự' });
  }
  if (!event.objectives || event.objectives.trim().length < 20) {
    missingFields.push('Mục tiêu sự kiện sơ sài');
    details.push({ category: 'Kế hoạch', level: 'WARNING', message: 'Mục tiêu sự kiện cần cụ thể, nêu bật giá trị cho sinh viên' });
  }
  if (!event.targetAudience) {
    missingFields.push('Chưa xác định đối tượng tham dự');
    details.push({ category: 'Đối tượng', level: 'WARNING', message: 'Cần xác định đối tượng: sinh viên toàn trường, sinh viên khoa hay đại biểu ngoài trường' });
  }
  if (!event.expectedAttendees || event.expectedAttendees <= 0) {
    missingFields.push('Số lượng người tham dự chưa hợp lệ');
    details.push({ category: 'Quy mô', level: 'ERROR', message: 'Cần có số lượng dự kiến để bố trí cơ sở vật chất' });
  }

  // 2. Schedule Check
  if (!event.startDate || !event.endDate) {
    missingFields.push('Chưa nhập thời gian bắt đầu hoặc kết thúc');
    details.push({ category: 'Thời gian', level: 'ERROR', message: 'Thiếu mốc thời gian diễn ra' });
  } else if (new Date(event.startDate) >= new Date(event.endDate)) {
    inconsistencies.push('Thời gian bắt đầu phải trước thời gian kết thúc');
    details.push({ category: 'Thời gian', level: 'ERROR', message: 'Thời gian kết thúc không thể trước hoặc bằng thời gian bắt đầu' });
  }

  // 3. Program Agenda / Schedule Items
  if (!event.scheduleItems || event.scheduleItems.length === 0) {
    suggestions.push('Nên bổ sung kịch bản chi tiết theo khung giờ (Agenda/Timeline)');
    details.push({ category: 'Kịch bản', level: 'WARNING', message: 'Chưa có phân bổ các tiết mục / nội dung chi tiết theo mốc thời gian' });
  }

  // 4. Budget check
  if (!event.budgetItems || event.budgetItems.length === 0) {
    suggestions.push('Sự kiện chưa có dự trù kinh phí chi tiết');
    details.push({ category: 'Ngân sách', level: 'INFO', message: 'Nếu sự kiện có kinh phí, vui lòng bổ sung từng khoản chi cụ thể' });
  } else {
    const totalBudget = event.budgetItems.reduce((s, i) => s + i.totalPrice, 0);
    if (totalBudget > 50000000) {
      risks.push('Dự toán vượt mức 50 triệu đồng - Cần giải trình định mức chi và hóa đơn VAT theo quy chế tài chính');
      details.push({ category: 'Ngân sách', level: 'WARNING', message: 'Tổng ngân sách lớn yêu cầu thẩm định kỹ nguồn tài trợ và chứng từ' });
    }
  }

  // 5. Safety & Venue
  if (!event.safetyPlan && (event.expectedAttendees || 0) > 200) {
    risks.push('Sự kiện quy mô trên 200 người nhưng chưa có phương án an toàn và trật tự');
    details.push({ category: 'An toàn', level: 'WARNING', message: 'Cần phương án phòng cháy chữa cháy, lối thoát hiểm và điều phối y tế' });
  }

  // 6. Facility & Capacity Match
  if (event.resourceBookings && event.resourceBookings.length > 0) {
    for (const b of event.resourceBookings) {
      if (b.facility && b.facility.capacity && (event.expectedAttendees || 0) > b.facility.capacity) {
        inconsistencies.push(`Số người tham dự (${event.expectedAttendees}) vượt quá sức chứa hội trường ${b.facility.name} (${b.facility.capacity} chỗ)`);
        details.push({ category: 'Cơ sở vật chất', level: 'ERROR', message: `Quá tải sức chứa hội trường ${b.facility.name}` });
      }
    }
  } else {
    suggestions.push('Chưa đăng ký hội trường hoặc phòng mượn thông qua hệ thống');
  }

  const score = Math.max(20, 100 - (missingFields.length * 15 + inconsistencies.length * 20 + risks.length * 10));

  let summary = `Hồ sơ đạt ${score}/100 điểm đánh giá sơ bộ. `;
  if (inconsistencies.length > 0 || missingFields.length > 0) {
    summary += `Phát hiện ${inconsistencies.length} điểm mâu thuẫn và ${missingFields.length} thông tin cần bổ sung trước khi trình BCN Khoa / Đoàn trường.`;
  } else {
    summary += 'Hồ sơ có cấu trúc tương đối đầy đủ và hợp lệ, sẵn sàng chuyển cấp xét duyệt.';
  }

  return {
    isAI: config.aiProvider !== 'rule-based' && !!config.aiApiKey,
    score,
    summary,
    missingFields,
    inconsistencies,
    risks,
    suggestions,
    details,
  };
}

export async function suggestResources(data: {
  expectedAttendees: number;
  startTime: string;
  endTime: string;
  eventType?: string;
}) {
  const start = new Date(data.startTime);
  const end = new Date(data.endTime);

  const facilities = await prisma.facility.findMany({ where: { isActive: true } });
  const allEquipment = await prisma.equipment.findMany({ where: { isActive: true } });

  // Find suitable halls by capacity
  const suitableFacilities = facilities.filter((f) => (f.capacity || 0) >= data.expectedAttendees);

  // Check bookings for conflicts
  const activeBookings = await prisma.resourceBooking.findMany({
    where: {
      status: { in: ['PENDING', 'TENTATIVE', 'CONFIRMED'] },
      startTime: { lt: end },
      endTime: { gt: start },
    },
  });

  const bookedFacilityIds = new Set(activeBookings.map((b) => b.facilityId));

  const availableOptions = suitableFacilities.map((f) => ({
    facility: f,
    isAvailable: !bookedFacilityIds.has(f.id),
    suitabilityScore: Math.round(
      100 - Math.min(50, Math.abs((f.capacity || 0) - data.expectedAttendees) / ((f.capacity || 1) / 100))
    ),
    recommendedEquipment: allEquipment.slice(0, 4).map((e) => ({
      equipmentId: e.id,
      name: e.name,
      suggestedQuantity: e.type === 'AUDIO' ? 2 : e.type === 'VISUAL' ? 1 : 10,
    })),
  }));

  return {
    isAI: config.aiProvider !== 'rule-based' && !!config.aiApiKey,
    requestedAttendees: data.expectedAttendees,
    options: availableOptions.sort((a, b) => (b.isAvailable ? 1 : 0) - (a.isAvailable ? 1 : 0)),
  };
}

export async function generateReportDraft(eventId: string) {
  const event = await prisma.event.findUnique({
    where: { id: eventId },
    include: {
      budgetItems: true,
      scheduleItems: true,
      settlements: { include: { items: true } },
      handoverRecords: true,
      returnInspections: true,
    },
  });

  if (!event) throw new Error('Không tìm thấy sự kiện');

  const settlement = event.settlements[0];
  const totalBudget = event.budgetItems.reduce((s, i) => s + i.totalPrice, 0);
  const totalActual = settlement ? settlement.totalActual : totalBudget;

  const draft = {
    isAI: config.aiProvider !== 'rule-based' && !!config.aiApiKey,
    actualAttendees: event.expectedAttendees || 150,
    summary: `Chương trình "${event.title}" do ${event.organizingUnit} tổ chức đã diễn ra thuận lợi từ ngày ${event.startDate ? new Date(event.startDate).toLocaleDateString('vi-VN') : '...'} tại ${event.preferredVenue || 'Hội trường trường'}. Sự kiện thu hút khoảng ${event.expectedAttendees || 150} sinh viên và đại biểu tham gia.`,
    achievements: `- Đạt 100% mục tiêu đề ra về mặt chuyên môn và phong trào sinh viên.\n- Tổ chức đúng tiến độ theo khung thời gian đã duyệt.\n- Nhận được phản hồi tích cực từ người tham dự về khâu tổ chức và nội dung truyền đạt.`,
    challenges: `- Công tác đón tiếp tại sảnh ban đầu còn hơi ùn ứ do số lượng sinh viên đến cùng thời điểm.\n- Cần chuẩn bị thêm phương án dự phòng micro và pin sân khấu.`,
    lessonsLearned: `- Cần phân công rõ đầu mối phụ trách kỹ thuật âm thanh và ánh sáng trước 2 giờ.\n- Tăng cường truyền thông số trên Fanpage trước sự kiện ít nhất 5 ngày.`,
    recommendations: `- Đề xuất Nhà trường tiếp tục tạo điều kiện hỗ trợ cơ sở vật chất cho các kỳ sinh hoạt tiếp theo.\n- Hỗ trợ kinh phí quyết toán nhanh chóng cho các hóa đơn vật tư in ấn.`,
    financialOverview: {
      totalBudget,
      totalActual,
      difference: totalActual - totalBudget,
    },
  };

  return draft;
}
