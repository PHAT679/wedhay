import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Calendar,
  Building,
  Plus,
  Trash2,
  AlertTriangle,
  ArrowRight,
  ArrowLeft,
  Check,
  Send,
  Save,
  DollarSign,
  Clock,
  FileText,
  Sparkles,
} from 'lucide-react';
import { useEvents } from '../contexts/EventContext';
import { useAuth } from '../contexts/AuthContext';
import { formatCurrency } from '../utils/helpers';
import { BudgetItem, ScheduleItem, ResourceBookingItem } from '../types';

export const EventCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const { createEvent, transitionEvent, saving, facilities, equipment, checkFacilityAvailability } = useEvents();
  const { currentUser } = useAuth();

  const [step, setStep] = useState<number>(1);

  // Form State
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    objectives: '',
    targetAudience: 'Sinh viên toàn trường',
    expectedAttendees: 150,
    organizingUnit: currentUser.department || 'CLB Sinh viên',
    contactPerson: currentUser.fullName,
    contactEmail: currentUser.email,
    contactPhone: currentUser.phone || '',
    startDate: '2024-11-20T08:00',
    endDate: '2024-11-20T17:00',
    preferredVenue: facilities[0]?.name || '',
    facilityId: facilities[0]?.id || '',
  });

  const [scheduleItems, setScheduleItems] = useState<ScheduleItem[]>([
    { id: '1', timeSlot: '08:00 - 08:30', activity: 'Đón tiếp đại biểu và sinh viên', responsible: 'Ban Lễ tân' },
    { id: '2', timeSlot: '08:30 - 11:30', activity: 'Nội dung chính của chương trình', responsible: 'Ban Tổ chức' },
  ]);

  const [budgetItems, setBudgetItems] = useState<BudgetItem[]>([
    { id: '1', category: 'In ấn', itemName: 'Backdrop sân khấu & Standee', quantity: 1, unitPrice: 2000000, totalPrice: 2000000 },
    { id: '2', category: 'Nước uống', itemName: 'Nước suối và trà bánh đại biểu', quantity: 1, unitPrice: 1200000, totalPrice: 1200000 },
  ]);

  const [selectedEquipment, setSelectedEquipment] = useState<{ equipmentId: string; quantity: number }[]>([
    { equipmentId: equipment[0]?.id || '', quantity: 2 },
  ]);

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Dynamic calculations
  const totalBudget = budgetItems.reduce((s, i) => s + i.totalPrice, 0);

  // Facility availability check
  const availabilityCheck = checkFacilityAvailability(
    formData.facilityId,
    new Date(formData.startDate).toISOString(),
    new Date(formData.endDate).toISOString()
  );

  const validateStep1 = () => {
    const err: Record<string, string> = {};
    if (!formData.title.trim()) err.title = 'Vui lòng nhập tên sự kiện';
    if (!formData.objectives.trim()) err.objectives = 'Vui lòng nhập mục tiêu sự kiện';
    if (!formData.organizingUnit.trim()) err.organizingUnit = 'Vui lòng nhập đơn vị tổ chức';
    if (formData.expectedAttendees <= 0) err.expectedAttendees = 'Số lượng người tham dự không hợp lệ';
    setErrors(err);
    return Object.keys(err).length === 0;
  };

  const handleNext = () => {
    if (step === 1 && !validateStep1()) return;
    setStep((prev) => Math.min(prev + 1, 5));
  };

  const handleBack = () => {
    setStep((prev) => Math.max(prev - 1, 1));
  };

  // Schedule row actions
  const addScheduleRow = () => {
    setScheduleItems([
      ...scheduleItems,
      { id: Date.now().toString(), timeSlot: '', activity: '', responsible: '' },
    ]);
  };
  const removeScheduleRow = (index: number) => {
    setScheduleItems(scheduleItems.filter((_, i) => i !== index));
  };
  const updateScheduleRow = (index: number, field: keyof ScheduleItem, val: string) => {
    const copy = [...scheduleItems];
    copy[index] = { ...copy[index], [field]: val };
    setScheduleItems(copy);
  };

  // Budget row actions
  const addBudgetRow = () => {
    setBudgetItems([
      ...budgetItems,
      { id: Date.now().toString(), category: 'Chi phí khác', itemName: '', quantity: 1, unitPrice: 0, totalPrice: 0 },
    ]);
  };
  const removeBudgetRow = (index: number) => {
    setBudgetItems(budgetItems.filter((_, i) => i !== index));
  };
  const updateBudgetRow = (index: number, field: keyof BudgetItem, val: any) => {
    const copy = [...budgetItems];
    const item = { ...copy[index], [field]: val };
    if (field === 'quantity' || field === 'unitPrice') {
      item.totalPrice = (Number(item.quantity) || 0) * (Number(item.unitPrice) || 0);
    }
    copy[index] = item;
    setBudgetItems(copy);
  };

  // Submit / Save
  const handleSave = async (isSubmit: boolean) => {
    if (saving) return;
    if (!validateStep1()) {
      setStep(1);
      return;
    }

    const bookingEquipment: ResourceBookingItem[] = selectedEquipment.map((se) => {
      const eq = equipment.find((e) => e.id === se.equipmentId);
      return {
        equipmentId: se.equipmentId,
        equipmentName: eq ? eq.name : 'Thiết bị',
        quantity: se.quantity,
      };
    });

    const facility = facilities.find((f) => f.id === formData.facilityId);

    const newEv = await createEvent({
      title: formData.title,
      description: formData.description,
      objectives: formData.objectives,
      targetAudience: formData.targetAudience,
      expectedAttendees: Number(formData.expectedAttendees),
      organizingUnit: formData.organizingUnit,
      contactPerson: formData.contactPerson,
      contactEmail: formData.contactEmail,
      contactPhone: formData.contactPhone,
      startDate: new Date(formData.startDate).toISOString(),
      endDate: new Date(formData.endDate).toISOString(),
      preferredVenue: facility?.name || formData.preferredVenue,
      scheduleItems,
      budgetItems,
      booking: {
        id: `bk-${Date.now()}`,
        facilityId: formData.facilityId,
        facilityName: facility?.name || formData.preferredVenue,
        startTime: new Date(formData.startDate).toISOString(),
        endTime: new Date(formData.endDate).toISOString(),
        status: availabilityCheck.isAvailable ? 'PENDING' : 'CONFLICT',
        conflictDetails: !availabilityCheck.isAvailable
          ? `Trùng lịch với hồ sơ ${availabilityCheck.conflictEvent?.eventCode}`
          : undefined,
        equipmentItems: bookingEquipment,
      },
    });

    if (!newEv) return;
    if (isSubmit) await transitionEvent(newEv.id, 'Nộp hồ sơ', 'FACULTY_REVIEW');
    navigate(`/events/${newEv.id}`);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Tạo hồ sơ sự kiện mới</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Quy trình chuẩn hóa 5 bước lập kế hoạch, dự toán ngân sách và mượn cơ sở vật chất
        </p>
      </div>

      {/* Steps Indicator */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-2xs">
        <div className="flex items-center justify-between text-xs font-semibold">
          {[
            { id: 1, label: 'Thông tin chung', icon: FileText },
            { id: 2, label: 'Kịch bản', icon: Clock },
            { id: 3, label: 'Dự trù kinh phí', icon: DollarSign },
            { id: 4, label: 'Cơ sở vật chất', icon: Building },
            { id: 5, label: 'Xác nhận & Nộp', icon: Check },
          ].map((s) => {
            const Icon = s.icon;
            const isCurrent = step === s.id;
            const isDone = step > s.id;
            return (
              <div
                key={s.id}
                onClick={() => setStep(s.id)}
                className={`flex items-center gap-2 cursor-pointer transition-colors ${
                  isCurrent ? 'text-blue-600 font-bold' : isDone ? 'text-emerald-600' : 'text-slate-400'
                }`}
              >
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs ${
                    isCurrent
                      ? 'bg-blue-600 text-white'
                      : isDone
                      ? 'bg-emerald-600 text-white'
                      : 'bg-slate-100 text-slate-500'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                </div>
                <span className="hidden sm:inline">{s.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Step Contents */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-2xs space-y-6">
        {/* Step 1: General Info */}
        {step === 1 && (
          <div className="space-y-4">
            <h2 className="text-sm font-bold text-slate-800 border-b pb-2">Bước 1: Thông tin cơ bản về sự kiện</h2>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Tên sự kiện <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                placeholder="Ví dụ: Ngày hội Sinh viên Khởi nghiệp DUE Startup Day 2024"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-hidden focus:border-blue-500"
              />
              {errors.title && <p className="text-[11px] text-rose-500 mt-1">{errors.title}</p>}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Đơn vị tổ chức <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.organizingUnit}
                  onChange={(e) => setFormData({ ...formData, organizingUnit: e.target.value })}
                  className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-hidden focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Quy mô người tham dự dự kiến <span className="text-rose-500">*</span>
                </label>
                <input
                  type="number"
                  min="10"
                  value={formData.expectedAttendees}
                  onChange={(e) => setFormData({ ...formData, expectedAttendees: Number(e.target.value) })}
                  className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-hidden focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Mục tiêu sự kiện <span className="text-rose-500">*</span>
              </label>
              <textarea
                rows={3}
                placeholder="Nêu rõ mục tiêu chính trị, học thuật, văn hóa phong trào hoặc giá trị mang lại cho sinh viên..."
                value={formData.objectives}
                onChange={(e) => setFormData({ ...formData, objectives: e.target.value })}
                className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-hidden focus:border-blue-500"
              />
              {errors.objectives && <p className="text-[11px] text-rose-500 mt-1">{errors.objectives}</p>}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Thời gian bắt đầu</label>
                <input
                  type="datetime-local"
                  value={formData.startDate}
                  onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
                  className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-hidden focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Thời gian kết thúc</label>
                <input
                  type="datetime-local"
                  value={formData.endDate}
                  onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
                  className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-hidden focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Schedule Agenda */}
        {step === 2 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b pb-2">
              <h2 className="text-sm font-bold text-slate-800">Bước 2: Kịch bản chương trình theo khung giờ</h2>
              <button
                type="button"
                onClick={addScheduleRow}
                className="flex items-center gap-1 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold rounded-lg cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5" /> Thêm tiết mục
              </button>
            </div>

            <div className="space-y-3">
              {scheduleItems.map((s, idx) => (
                <div key={s.id} className="flex items-center gap-3 bg-slate-50 p-3 rounded-xl border border-slate-200">
                  <div className="w-36 shrink-0">
                    <input
                      type="text"
                      placeholder="08:00 - 08:30"
                      value={s.timeSlot}
                      onChange={(e) => updateScheduleRow(idx, 'timeSlot', e.target.value)}
                      className="w-full text-xs p-2 rounded-lg border border-slate-200 bg-white"
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <input
                      type="text"
                      placeholder="Nội dung hoạt động chi tiết..."
                      value={s.activity}
                      onChange={(e) => updateScheduleRow(idx, 'activity', e.target.value)}
                      className="w-full text-xs p-2 rounded-lg border border-slate-200 bg-white"
                    />
                  </div>
                  <div className="w-40 shrink-0">
                    <input
                      type="text"
                      placeholder="Phụ trách (Ban...)"
                      value={s.responsible}
                      onChange={(e) => updateScheduleRow(idx, 'responsible', e.target.value)}
                      className="w-full text-xs p-2 rounded-lg border border-slate-200 bg-white"
                    />
                  </div>
                  <button
                    type="button"
                    onClick={() => removeScheduleRow(idx)}
                    className="text-slate-400 hover:text-rose-600 cursor-pointer p-1"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step 3: Budget Planning */}
        {step === 3 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b pb-2">
              <div>
                <h2 className="text-sm font-bold text-slate-800">Bước 3: Lập dự trù kinh phí</h2>
                <p className="text-xs text-slate-500">Tự động tính thành tiền và kiểm tra định mức</p>
              </div>
              <button
                type="button"
                onClick={addBudgetRow}
                className="flex items-center gap-1 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold rounded-lg cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5" /> Thêm khoản chi
              </button>
            </div>

            <div className="overflow-x-auto border border-slate-200 rounded-xl">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-[11px] font-bold text-slate-500 uppercase">
                  <tr>
                    <th className="py-2.5 px-3">Danh mục</th>
                    <th className="py-2.5 px-3">Khoản mục chi</th>
                    <th className="py-2.5 px-3 w-20 text-center">SL</th>
                    <th className="py-2.5 px-3 w-32 text-right">Đơn giá (VNĐ)</th>
                    <th className="py-2.5 px-3 w-32 text-right">Thành tiền</th>
                    <th className="py-2.5 px-3 w-10"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {budgetItems.map((b, idx) => (
                    <tr key={b.id}>
                      <td className="p-2">
                        <input
                          type="text"
                          value={b.category}
                          onChange={(e) => updateBudgetRow(idx, 'category', e.target.value)}
                          className="w-full p-1.5 border border-slate-200 rounded-md"
                        />
                      </td>
                      <td className="p-2">
                        <input
                          type="text"
                          value={b.itemName}
                          onChange={(e) => updateBudgetRow(idx, 'itemName', e.target.value)}
                          className="w-full p-1.5 border border-slate-200 rounded-md"
                        />
                      </td>
                      <td className="p-2">
                        <input
                          type="number"
                          min="1"
                          value={b.quantity}
                          onChange={(e) => updateBudgetRow(idx, 'quantity', Number(e.target.value))}
                          className="w-full p-1.5 border border-slate-200 rounded-md text-center"
                        />
                      </td>
                      <td className="p-2">
                        <input
                          type="number"
                          step="10000"
                          value={b.unitPrice}
                          onChange={(e) => updateBudgetRow(idx, 'unitPrice', Number(e.target.value))}
                          className="w-full p-1.5 border border-slate-200 rounded-md text-right font-mono"
                        />
                      </td>
                      <td className="p-2 text-right font-mono font-bold text-slate-800">
                        {formatCurrency(b.totalPrice)}
                      </td>
                      <td className="p-2 text-center">
                        <button
                          type="button"
                          onClick={() => removeBudgetRow(idx)}
                          className="text-slate-400 hover:text-rose-600 p-1"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="flex justify-end pt-2 text-sm">
              <div className="bg-slate-50 px-4 py-2 rounded-xl border border-slate-200 text-slate-800">
                Tổng dự toán: <span className="font-bold text-blue-600 text-base ml-1">{formatCurrency(totalBudget)}</span>
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Facility & Equipment Booking */}
        {step === 4 && (
          <div className="space-y-4">
            <h2 className="text-sm font-bold text-slate-800 border-b pb-2">Bước 4: Mượn Cơ sở vật chất & Thiết bị</h2>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Lựa chọn Hội trường / Phòng mượn:
              </label>
              <select
                value={formData.facilityId}
                onChange={(e) => {
                  const fac = facilities.find((f) => f.id === e.target.value);
                  setFormData({
                    ...formData,
                    facilityId: e.target.value,
                    preferredVenue: fac ? fac.name : '',
                  });
                }}
                className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white"
              >
                {facilities.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.name} (Sức chứa: {f.capacity} chỗ) — {f.location}
                  </option>
                ))}
              </select>
            </div>

            {/* Live Availability Banner */}
            {!availabilityCheck.isAvailable ? (
              <div className="p-4 bg-rose-50 border border-rose-300 rounded-xl text-xs text-rose-800 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold">Cảnh báo trùng lịch phòng:</div>
                  <div>
                    Phòng này đã được đăng ký bởi sự kiện:{' '}
                    <span className="font-bold">{availabilityCheck.conflictEvent?.eventCode}</span> (
                    {availabilityCheck.conflictEvent?.title}).
                  </div>
                  <div className="mt-1 text-[11px] text-rose-600">
                    Vui lòng chọn khung giờ khác hoặc chuyển sang phòng khác để tránh bị CSVC từ chối.
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 flex items-center gap-2">
                <Check className="w-4 h-4 text-emerald-600" />
                <span>Phòng hiện đang trống trong khung giờ bạn chọn. Sẵn sàng giữ chỗ.</span>
              </div>
            )}

            <div>
              <h3 className="text-xs font-bold text-slate-700 uppercase mb-2">Đăng ký thiết bị di động kèm theo:</h3>
              <div className="space-y-2">
                {equipment.slice(0, 5).map((eq) => {
                  const currentSelected = selectedEquipment.find((se) => se.equipmentId === eq.id);
                  const isChecked = !!currentSelected;
                  return (
                    <div
                      key={eq.id}
                      className="flex items-center justify-between p-2.5 rounded-xl border border-slate-200 bg-slate-50 text-xs"
                    >
                      <label className="flex items-center gap-2 cursor-pointer font-medium text-slate-800">
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedEquipment([...selectedEquipment, { equipmentId: eq.id, quantity: 1 }]);
                            } else {
                              setSelectedEquipment(selectedEquipment.filter((se) => se.equipmentId !== eq.id));
                            }
                          }}
                          className="rounded text-blue-600"
                        />
                        <span>{eq.name} (Khả dụng: {eq.availableQuantity}/{eq.totalQuantity})</span>
                      </label>

                      {isChecked && (
                        <div className="flex items-center gap-2">
                          <span className="text-[11px] text-slate-500">Số lượng:</span>
                          <input
                            type="number"
                            min="1"
                            max={eq.availableQuantity}
                            value={currentSelected.quantity}
                            onChange={(e) => {
                              const qty = Number(e.target.value);
                              setSelectedEquipment(
                                selectedEquipment.map((se) => (se.equipmentId === eq.id ? { ...se, quantity: qty } : se))
                              );
                            }}
                            className="w-16 p-1 text-center font-bold border border-slate-300 rounded-md bg-white text-xs"
                          />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Step 5: Summary & Submit */}
        {step === 5 && (
          <div className="space-y-4">
            <h2 className="text-sm font-bold text-slate-800 border-b pb-2">Bước 5: Kiểm tra lại và Nộp hồ sơ</h2>

            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <span className="text-slate-400">Tên sự kiện:</span>
                  <div className="font-bold text-slate-900">{formData.title}</div>
                </div>
                <div>
                  <span className="text-slate-400">Đơn vị tổ chức:</span>
                  <div className="font-semibold text-slate-800">{formData.organizingUnit}</div>
                </div>
                <div>
                  <span className="text-slate-400">Thời gian:</span>
                  <div className="font-semibold text-slate-800">{formData.startDate} → {formData.endDate}</div>
                </div>
                <div>
                  <span className="text-slate-400">Địa điểm đăng ký:</span>
                  <div className="font-semibold text-blue-700">{formData.preferredVenue}</div>
                </div>
                <div>
                  <span className="text-slate-400">Quy mô:</span>
                  <div className="font-semibold text-slate-800">{formData.expectedAttendees} sinh viên</div>
                </div>
                <div>
                  <span className="text-slate-400">Tổng dự toán:</span>
                  <div className="font-bold text-emerald-600">{formatCurrency(totalBudget)}</div>
                </div>
              </div>
            </div>

            <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl text-xs text-blue-800 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-blue-600" />
              <span>
                Sau khi gửi hồ sơ, hệ thống sẽ tự động chuyển đến Ban Chủ nhiệm Khoa để xét duyệt nội dung vòng 1.
              </span>
            </div>
          </div>
        )}

        {/* Form Bottom Controls */}
        <div className="flex items-center justify-between border-t border-slate-100 pt-4">
          <button
            type="button"
            onClick={step === 1 ? () => navigate('/events') : handleBack}
            className="flex items-center gap-1.5 px-4 py-2 border border-slate-200 text-slate-700 hover:bg-slate-50 rounded-xl text-xs font-semibold cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" /> {step === 1 ? 'Hủy bỏ' : 'Quay lại'}
          </button>

          <div className="flex items-center gap-2">
            {step < 5 ? (
              <button
                type="button"
                onClick={handleNext}
                className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold cursor-pointer shadow-xs"
              >
                Tiếp tục <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <>
                <button
                  type="button"
                  disabled={saving} onClick={() => handleSave(false)}
                  className="flex items-center gap-1.5 px-4 py-2 border border-slate-300 text-slate-700 hover:bg-slate-100 rounded-xl text-xs font-semibold cursor-pointer"
                >
                  <Save className="w-4 h-4" /> Lưu bản nháp
                </button>
                <button
                  type="button"
                  disabled={saving} onClick={() => handleSave(true)}
                  className="flex items-center gap-1.5 px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold cursor-pointer shadow-md"
                >
                  <Send className="w-4 h-4" /> Nộp hồ sơ chính thức
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
