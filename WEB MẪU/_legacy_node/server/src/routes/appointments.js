import express from 'express';
import { db } from '../database.js';
import { authenticate, requireRole } from '../middleware/auth.js';

const router = express.Router();

function generateId(prefix) {
  const rand = Math.floor(1000 + Math.random() * 9000);
  return `${prefix}${Date.now().toString().slice(-4)}${rand.toString().slice(-2)}`;
}

// Hàm phụ trợ: Chuyển 'HH:mm' thành số phút từ 0:00
function timeToMinutes(timeStr) {
  const [h, m] = timeStr.split(':').map(Number);
  return h * 60 + m;
}

// Hàm phụ trợ: Chuyển số phút thành 'HH:mm'
function minutesToTime(minutes) {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
}

// 1. Kiểm tra khung giờ trống (UC 7.1 & BR-UC3-03, BR-UC3-04, BR-UC7-01)
router.get('/available-slots', (req, res) => {
  const { date, duration } = req.query;

  if (!date || !duration) {
    return res.status(400).json({ message: 'Vui lòng cung cấp ngày và thời lượng dịch vụ' });
  }

  const durationMin = parseInt(duration, 10);
  if (isNaN(durationMin) || durationMin <= 0) {
    return res.status(400).json({ message: 'Thời lượng không hợp lệ' });
  }

  // Tổng số kỹ thuật viên của tiệm
  const totalStaff = db.prepare('SELECT COUNT(*) as c FROM NhanVien').get().c || 1;

  // Lấy các lịch hẹn trong ngày có trạng thái 'Chờ xác nhận' hoặc 'Đã xác nhận'
  const activeBookings = db.prepare(`
    SELECT lh.MaLichHen, lh.NgayGioBatDau,
           SUM(ct.ThoiLuongDat) as TongThoiLuong
    FROM LichHen lh
    JOIN ChiTietLichHen ct ON lh.MaLichHen = ct.MaLichHen
    WHERE DATE(lh.NgayGioBatDau) = ? AND lh.TrangThai IN ('Chờ xác nhận', 'Đã xác nhận')
    GROUP BY lh.MaLichHen
  `).all(date);

  // Mốc hoạt động: 9:00 (540 phút) đến 19:00 (1140 phút)
  // Giờ bắt đầu muộn nhất: 17:00 (1020 phút)
  const OPEN_TIME = 9 * 60; // 540
  const CLOSE_TIME = 19 * 60; // 1140
  const MAX_START_TIME = 17 * 60; // 1020
  const STEP = 30;

  const availableSlots = [];

  for (let startMin = OPEN_TIME; startMin <= MAX_START_TIME; startMin += STEP) {
    const endMin = startMin + durationMin;

    // Phải hoàn thành trước giờ đóng cửa 19:00
    if (endMin > CLOSE_TIME) {
      continue;
    }

    // Kiểm tra từng khoảng 30 phút trong [startMin, endMin)
    let isSlotAvailable = true;
    let minStaffRemaining = totalStaff;

    for (let checkMin = startMin; checkMin < endMin; checkMin += STEP) {
      let overlappingCount = 0;

      for (const b of activeBookings) {
        const bookingDate = new Date(b.NgayGioBatDau);
        const bStart = bookingDate.getHours() * 60 + bookingDate.getMinutes();
        const bEnd = bStart + (b.TongThoiLuong || 30);

        // Nếu trùng nhau trong khoảng checkMin -> checkMin + 30
        if (checkMin < bEnd && (checkMin + STEP) > bStart) {
          overlappingCount++;
        }
      }

      const remaining = totalStaff - overlappingCount;
      if (remaining <= 0) {
        isSlotAvailable = false;
        break;
      }
      if (remaining < minStaffRemaining) {
        minStaffRemaining = remaining;
      }
    }

    if (isSlotAvailable) {
      availableSlots.push({
        time: minutesToTime(startMin),
        endTime: minutesToTime(endMin),
        remainingStaff: minStaffRemaining
      });
    }
  }

  res.json({
    date,
    duration: durationMin,
    totalStaff,
    availableSlots
  });
});

// 2. Tạo lịch hẹn mới (UC 7.1)
router.post('/', authenticate, (req, res) => {
  const { tenLienHe, soDienThoaiLienHe, ngayGioBatDau, dichVuIds, ghiChu } = req.body;

  // BR-UC7-10: Bắt buộc họ tên, SĐT và ít nhất 1 dịch vụ
  if (!tenLienHe || !soDienThoaiLienHe || !ngayGioBatDau || !Array.isArray(dichVuIds) || dichVuIds.length === 0) {
    return res.status(400).json({ message: 'Vui lòng nhập đầy đủ họ tên, số điện thoại và chọn ít nhất một dịch vụ' });
  }

  const cleanPhone = soDienThoaiLienHe.trim();
  if (!/^[0-9]{10}$/.test(cleanPhone)) {
    return res.status(400).json({ message: 'Số điện thoại không hợp lệ (phải gồm 10 chữ số)' });
  }

  // Lấy chi tiết các dịch vụ đã chọn
  const placeholders = dichVuIds.map(() => '?').join(',');
  const selectedServices = db.prepare(`SELECT * FROM DichVu WHERE MaDichVu IN (${placeholders}) AND DaXoa = 0`).all(...dichVuIds);

  if (selectedServices.length === 0) {
    return res.status(400).json({ message: 'Dịch vụ đã chọn không hợp lệ hoặc đã bị ngưng' });
  }

  // Tự động tính tổng tiền và tổng thời gian (BR-UC7-11)
  const tongTien = selectedServices.reduce((sum, s) => sum + s.GiaTien, 0);
  const tongThoiLuong = selectedServices.reduce((sum, s) => sum + s.ThoiLuong, 0);

  const startDate = new Date(ngayGioBatDau);
  const startHour = startDate.getHours();
  const startMinute = startDate.getMinutes();
  const startMinTotal = startHour * 60 + startMinute;
  const endMinTotal = startMinTotal + tongThoiLuong;

  // Kiểm tra giờ hoạt động
  if (startMinTotal < 9 * 60 || startMinTotal > 17 * 60 || endMinTotal > 19 * 60) {
    return res.status(400).json({ message: 'Khung giờ đặt lịch không hợp lệ (tiệm phục vụ từ 9:00 - 19:00, đặt muộn nhất 17:00)' });
  }

  try {
    const bookingResult = db.transaction(() => {
      // 1. Tái kiểm tra slot trống tránh xung đột đồng thời (Race condition)
      const dateStr = ngayGioBatDau.slice(0, 10);
      const totalStaff = db.prepare('SELECT COUNT(*) as c FROM NhanVien').get().c || 1;

      const activeBookings = db.prepare(`
        SELECT lh.MaLichHen, lh.NgayGioBatDau, SUM(ct.ThoiLuongDat) as TongThoiLuong
        FROM LichHen lh
        JOIN ChiTietLichHen ct ON lh.MaLichHen = ct.MaLichHen
        WHERE DATE(lh.NgayGioBatDau) = ? AND lh.TrangThai IN ('Chờ xác nhận', 'Đã xác nhận')
        GROUP BY lh.MaLichHen
      `).all(dateStr);

      for (let checkMin = startMinTotal; checkMin < endMinTotal; checkMin += 30) {
        let count = 0;
        for (const b of activeBookings) {
          const bDate = new Date(b.NgayGioBatDau);
          const bStart = bDate.getHours() * 60 + bDate.getMinutes();
          const bEnd = bStart + (b.TongThoiLuong || 30);
          if (checkMin < bEnd && (checkMin + 30) > bStart) {
            count++;
          }
        }
        if (count >= totalStaff) {
          throw new Error('Khung giờ chọn đã hết chỗ tại thời điểm xác nhận. Vui lòng chọn khung giờ khác');
        }
      }

      // 2. Tìm hoặc tạo hồ sơ khách hàng
      let customerId = req.user.maKhachHang;
      if (!customerId) {
        let customer = db.prepare('SELECT MaKhachHang FROM KhachHang WHERE SoDienThoai = ?').get(cleanPhone);
        if (customer) {
          customerId = customer.MaKhachHang;
        } else {
          customerId = generateId('KH');
          db.prepare(`
            INSERT INTO KhachHang (MaKhachHang, HoTen, SoDienThoai)
            VALUES (?, ?, ?)
          `).run(customerId, tenLienHe.trim(), cleanPhone);
        }
      }

      // 3. Tạo bản ghi LichHen
      const maLichHen = generateId('LH');
      db.prepare(`
        INSERT INTO LichHen (MaLichHen, MaKhachHang, NgayGioBatDau, TenLienHe, SoDienThoaiLienHe, TrangThai)
        VALUES (?, ?, ?, ?, ?, 'Chờ xác nhận')
      `).run(maLichHen, customerId, ngayGioBatDau, tenLienHe.trim(), cleanPhone);

      // 4. Lưu từng dịch vụ vào ChiTietLichHen (bảo toàn giá & thời lượng lúc đặt theo BR-UC4-07)
      for (const s of selectedServices) {
        db.prepare(`
          INSERT INTO ChiTietLichHen (MaLichHen, MaDichVu, TenDichVuDat, DonGiaDat, ThoiLuongDat, GhiChuThucHien)
          VALUES (?, ?, ?, ?, ?, ?)
        `).run(maLichHen, s.MaDichVu, s.TenDichVu, s.GiaTien, s.ThoiLuong, ghiChu || null);
      }

      // 5. Gửi thông báo đến Chủ tiệm (NFR-02)
      const formattedTime = `${startDate.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })} ngày ${startDate.toLocaleDateString('vi-VN')}`;
      db.prepare(`
        INSERT INTO ThongBao (MaThongBao, MaTaiKhoanNhan, TieuDe, NoiDung, LoaiThongBao, LienKet, ThoiDiemTao)
        VALUES (?, 'TK_OWNER', 'Có lịch hẹn mới từ khách hàng', ?, 'LICH_MOI', '/owner/timeline', datetime('now'))
      `).run(generateId('TB'), `Khách hàng ${tenLienHe.trim()} vừa đặt lịch lúc ${formattedTime} (${selectedServices.map(s => s.TenDichVu).join(', ')}).`);

      return { maLichHen, tongTien, tongThoiLuong };
    });

    const result = bookingResult();

    // BR-UC7-04: Thông báo thành công bao gồm ngày, giờ hẹn, địa chỉ và số hotline của tiệm
    return res.status(201).json({
      message: 'Đặt lịch thành công',
      data: {
        maLichHen: result.maLichHen,
        ngayGioBatDau,
        tongTien: result.tongTien,
        tongThoiLuong: result.tongThoiLuong,
        diaChiTiem: '356/87 Hoàng Diệu, Hòa Cường, Đà Nẵng',
        hotline: '0905 123 456'
      }
    });
  } catch (error) {
    console.error('Lỗi đặt lịch:', error);
    return res.status(400).json({ message: error.message || 'Không thể tạo lịch hẹn. Vui lòng thử lại' });
  }
});

// 3. Khách hàng xem lịch hẹn của mình (UC 7)
router.get('/my', authenticate, (req, res) => {
  const customerId = req.user.maKhachHang;
  if (!customerId) {
    return res.json([]);
  }

  const appointments = db.prepare(`
    SELECT lh.*,
           pc.MaPhanCong, pc.TrangThaiTiepNhan, pc.MaNhanVien, nv.TenNhanVien,
           gd.MaGiaoDich, gd.SoTien as SoTienDaThu, gd.PhuongThuc as PhuongThucTT, gd.TrangThai as TrangThaiTT
    FROM LichHen lh
    LEFT JOIN PhanCong pc ON lh.MaLichHen = pc.MaLichHen AND pc.DangPhuTrach = 1
    LEFT JOIN NhanVien nv ON pc.MaNhanVien = nv.MaNhanVien
    LEFT JOIN GiaoDich gd ON lh.MaLichHen = gd.MaLichHen
    WHERE lh.MaKhachHang = ?
    ORDER BY lh.NgayGioBatDau DESC
  `).all(customerId);

  // Kèm danh sách dịch vụ chi tiết cho mỗi lịch
  for (const app of appointments) {
    app.chiTietDichVu = db.prepare(`
      SELECT * FROM ChiTietLichHen WHERE MaLichHen = ?
    `).all(app.MaLichHen);
    app.tongTien = app.chiTietDichVu.reduce((sum, item) => sum + item.DonGiaDat, 0);
    app.tongThoiLuong = app.chiTietDichVu.reduce((sum, item) => sum + item.ThoiLuongDat, 0);
  }

  res.json(appointments);
});

// 4. Chủ tiệm xem Timeline lịch hẹn (UC 3.1)
router.get('/timeline', authenticate, requireRole('Chủ Tiệm'), (req, res) => {
  const { date } = req.query;
  const targetDate = date || new Date().toISOString().slice(0, 10);

  const appointments = db.prepare(`
    SELECT lh.*, kh.HoTen as HoTenKhachHang, kh.SoDienThoai as SoDienThoaiKhach,
           kh.LinkFacebook, kh.LinkZalo,
           pc.MaPhanCong, pc.TrangThaiTiepNhan, pc.LyDoTuChoi, pc.MaNhanVien, nv.TenNhanVien,
           gd.MaGiaoDich, gd.SoTien as SoTienThanhToan, gd.PhuongThuc as PhuongThucThanhToan, gd.TrangThai as TrangThaiGiaoDich
    FROM LichHen lh
    JOIN KhachHang kh ON lh.MaKhachHang = kh.MaKhachHang
    LEFT JOIN PhanCong pc ON lh.MaLichHen = pc.MaLichHen AND pc.DangPhuTrach = 1
    LEFT JOIN NhanVien nv ON pc.MaNhanVien = nv.MaNhanVien
    LEFT JOIN GiaoDich gd ON lh.MaLichHen = gd.MaLichHen
    WHERE DATE(lh.NgayGioBatDau) = ?
    ORDER BY lh.NgayGioBatDau ASC
  `).all(targetDate);

  for (const app of appointments) {
    app.chiTietDichVu = db.prepare('SELECT * FROM ChiTietLichHen WHERE MaLichHen = ?').all(app.MaLichHen);
    app.tongTien = app.chiTietDichVu.reduce((sum, item) => sum + item.DonGiaDat, 0);
    app.tongThoiLuong = app.chiTietDichVu.reduce((sum, item) => sum + item.ThoiLuongDat, 0);
  }

  res.json({
    date: targetDate,
    total: appointments.length,
    appointments
  });
});

// 5. Xem chi tiết 1 lịch hẹn
router.get('/:id', authenticate, (req, res) => {
  const app = db.prepare(`
    SELECT lh.*, kh.HoTen as HoTenKhachHang, kh.SoDienThoai as SoDienThoaiKhach,
           pc.MaPhanCong, pc.TrangThaiTiepNhan, pc.LyDoTuChoi, nv.TenNhanVien, nv.MaNhanVien,
           gd.MaGiaoDich, gd.SoTien as SoTienThanhToan, gd.PhuongThuc as PhuongThucThanhToan
    FROM LichHen lh
    JOIN KhachHang kh ON lh.MaKhachHang = kh.MaKhachHang
    LEFT JOIN PhanCong pc ON lh.MaLichHen = pc.MaLichHen AND pc.DangPhuTrach = 1
    LEFT JOIN NhanVien nv ON pc.MaNhanVien = nv.MaNhanVien
    LEFT JOIN GiaoDich gd ON lh.MaLichHen = gd.MaLichHen
    WHERE lh.MaLichHen = ?
  `).get(req.params.id);

  if (!app) {
    return res.status(404).json({ message: 'Không tìm thấy lịch hẹn' });
  }

  app.chiTietDichVu = db.prepare('SELECT * FROM ChiTietLichHen WHERE MaLichHen = ?').all(app.MaLichHen);
  app.tongTien = app.chiTietDichVu.reduce((sum, item) => sum + item.DonGiaDat, 0);
  app.tongThoiLuong = app.chiTietDichVu.reduce((sum, item) => sum + item.ThoiLuongDat, 0);

  res.json(app);
});

// 6. Đổi lịch hẹn (UC 7.2 - Khách hàng)
router.put('/:id/reschedule', authenticate, (req, res) => {
  const { id } = req.params;
  const { ngayGioMoi } = req.body;

  if (!ngayGioMoi) {
    return res.status(400).json({ message: 'Vui lòng chọn thời gian mới' });
  }

  const app = db.prepare('SELECT * FROM LichHen WHERE MaLichHen = ?').get(id);
  if (!app) {
    return res.status(404).json({ message: 'Không tìm thấy lịch hẹn' });
  }

  // Khách chỉ được đổi lịch của chính mình
  if (req.user.vaiTro === 'Khách Hàng' && app.MaKhachHang !== req.user.maKhachHang) {
    return res.status(403).json({ message: 'Bạn không có quyền đổi lịch hẹn này' });
  }

  if (app.TrangThai === 'Hủy' || app.TrangThai === 'Hoàn thành') {
    return res.status(400).json({ message: 'Lịch hẹn đã hoàn thành hoặc đã bị hủy, không thể đổi' });
  }

  const services = db.prepare('SELECT ThoiLuongDat FROM ChiTietLichHen WHERE MaLichHen = ?').all(id);
  const totalDuration = services.reduce((sum, s) => sum + s.ThoiLuongDat, 0) || 30;

  try {
    db.transaction(() => {
      // Cập nhật ngày giờ mới (BR-UC7-06: cập nhật sang lịch mới ngay và giải phóng slot cũ)
      db.prepare(`
        UPDATE LichHen
        SET NgayGioBatDau = ?
        WHERE MaLichHen = ?
      `).run(ngayGioMoi, id);

      // Thông báo cho Chủ tiệm
      const formatted = new Date(ngayGioMoi).toLocaleString('vi-VN');
      db.prepare(`
        INSERT INTO ThongBao (MaThongBao, MaTaiKhoanNhan, TieuDe, NoiDung, LoaiThongBao, LienKet, ThoiDiemTao)
        VALUES (?, 'TK_OWNER', 'Khách hàng đổi lịch hẹn', ?, 'DOI_LICH', '/owner/timeline', datetime('now'))
      `).run(generateId('TB'), `Lịch hẹn ${id} của khách ${app.TenLienHe} đã chuyển sang ${formatted}. Vui lòng kiểm tra lại phân công nhân viên.`);
    })();

    return res.json({ message: 'Đổi lịch hẹn thành công', ngayGioMoi });
  } catch (error) {
    console.error('Lỗi đổi lịch:', error);
    return res.status(500).json({ message: 'Khung thời gian không còn chỗ hoặc thao tác thất bại' });
  }
});

// 7. Hủy lịch hẹn (UC 7.3 - Khách hàng, Chủ tiệm)
router.put('/:id/cancel', authenticate, (req, res) => {
  const { id } = req.params;
  const { lyDoHuy } = req.body;

  const app = db.prepare('SELECT * FROM LichHen WHERE MaLichHen = ?').get(id);
  if (!app) {
    return res.status(404).json({ message: 'Không tìm thấy lịch hẹn' });
  }

  if (app.TrangThai === 'Hủy') {
    return res.status(400).json({ message: 'Lịch hẹn này đã bị hủy trước đó' });
  }

  let isLateCancel = false;

  // Nếu Khách hàng hủy: kiểm tra quy tắc 2 tiếng (BR-UC7-7)
  if (req.user.vaiTro === 'Khách Hàng') {
    if (app.MaKhachHang !== req.user.maKhachHang) {
      return res.status(403).json({ message: 'Bạn không có quyền hủy lịch hẹn này' });
    }

    const appointmentTime = new Date(app.NgayGioBatDau).getTime();
    const now = Date.now();
    const diffHours = (appointmentTime - now) / (1000 * 60 * 60);

    if (diffHours < 2) {
      isLateCancel = true; // Hủy dưới 2 tiếng: ghi nhận hủy và cảnh báo cho tiệm
    }
  }

  try {
    db.transaction(() => {
      // Cập nhật trạng thái 'Hủy', giải phóng khung giờ (BR-UC3-05)
      db.prepare(`
        UPDATE LichHen
        SET TrangThai = 'Hủy', ThoiDiemHuy = datetime('now'), MaTaiKhoanHuy = ?
        WHERE MaLichHen = ?
      `).run(req.user.maTaiKhoan, id);

      // Nếu có phân công đang phụ trách thì giải phóng
      db.prepare(`
        UPDATE PhanCong
        SET DangPhuTrach = 0
        WHERE MaLichHen = ?
      `).run(id);

      // Gửi thông báo đến Chủ tiệm
      const lateNotice = isLateCancel ? ' (CẢNH BÁO: HỦY GẤP DƯỚI 2 TIẾNG)' : '';
      db.prepare(`
        INSERT INTO ThongBao (MaThongBao, MaTaiKhoanNhan, TieuDe, NoiDung, LoaiThongBao, LienKet, ThoiDiemTao)
        VALUES (?, 'TK_OWNER', ?, ?, 'HUY_LICH', '/owner/timeline', datetime('now'))
      `).run(
        generateId('TB'),
        `Lịch hẹn ${id} đã bị hủy${lateNotice}`,
        `Lịch hẹn lúc ${app.NgayGioBatDau} của khách ${app.TenLienHe} đã bị hủy bởi ${req.user.vaiTro}. Lý do: ${lyDoHuy || 'Khách hủy'}`
      );
    })();

    return res.json({
      message: 'Hủy lịch thành công',
      isLateCancel,
      note: isLateCancel ? 'Lịch đã được hủy thành công nhưng tiệm đã ghi nhận việc hủy dưới 2 tiếng.' : undefined
    });
  } catch (error) {
    console.error('Lỗi hủy lịch:', error);
    return res.status(500).json({ message: 'Không thể hủy lịch. Vui lòng thử lại sau' });
  }
});

// 8. Cập nhật trạng thái lịch hẹn (UC 3.2 - Chủ tiệm)
router.patch('/:id/status', authenticate, requireRole('Chủ Tiệm'), (req, res) => {
  const { id } = req.params;
  const { trangThai, lyDoHuy } = req.body;

  const validStatuses = ['Chờ xác nhận', 'Đã xác nhận', 'Hoàn thành', 'Hủy', 'Không đến'];
  if (!validStatuses.includes(trangThai)) {
    return res.status(400).json({ message: 'Trạng thái không hợp lệ' });
  }

  const app = db.prepare('SELECT * FROM LichHen WHERE MaLichHen = ?').get(id);
  if (!app) {
    return res.status(404).json({ message: 'Không tìm thấy lịch hẹn' });
  }

  try {
    db.transaction(() => {
      let thoiDiemHuy = null;
      let maTaiKhoanHuy = null;

      if (trangThai === 'Hủy') {
        thoiDiemHuy = new Date().toISOString();
        maTaiKhoanHuy = req.user.maTaiKhoan;
        // Giải phóng phân công
        db.prepare('UPDATE PhanCong SET DangPhuTrach = 0 WHERE MaLichHen = ?').run(id);
      }

      db.prepare(`
        UPDATE LichHen
        SET TrangThai = ?,
            ThoiDiemHuy = COALESCE(?, ThoiDiemHuy),
            MaTaiKhoanHuy = COALESCE(?, MaTaiKhoanHuy)
        WHERE MaLichHen = ?
      `).run(trangThai, thoiDiemHuy, maTaiKhoanHuy, id);

      // Bắn thông báo cho khách hàng nếu có tài khoản
      const customerAccount = db.prepare('SELECT MaTaiKhoan FROM TaiKhoan WHERE MaKhachHang = ?').get(app.MaKhachHang);
      if (customerAccount) {
        db.prepare(`
          INSERT INTO ThongBao (MaThongBao, MaTaiKhoanNhan, TieuDe, NoiDung, LoaiThongBao, LienKet, ThoiDiemTao)
          VALUES (?, ?, 'Cập nhật trạng thái lịch hẹn', ?, 'TRANG_THAI', '/customer/my-appointments', datetime('now'))
        `).run(generateId('TB'), customerAccount.MaTaiKhoan, `Lịch hẹn ngày ${app.NgayGioBatDau} của bạn đã chuyển sang trạng thái: "${trangThai}".`);
      }
    })();

    return res.json({ message: 'Cập nhật trạng thái thành công', trangThai });
  } catch (error) {
    console.error('Lỗi cập nhật trạng thái:', error);
    return res.status(500).json({ message: 'Cập nhật trạng thái thất bại, vui lòng thử lại' });
  }
});

export default router;
