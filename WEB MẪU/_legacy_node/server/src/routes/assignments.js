import express from 'express';
import { db } from '../database.js';
import { authenticate, requireRole } from '../middleware/auth.js';

const router = express.Router();

function generateId(prefix) {
  const rand = Math.floor(1000 + Math.random() * 9000);
  return `${prefix}${Date.now().toString().slice(-4)}${rand.toString().slice(-2)}`;
}

// 1. Lấy danh sách nhân viên & kiểm tra tình trạng bận/rảnh theo khung giờ của lịch hẹn (UC 5.1 & UC 5.2 - Chủ tiệm)
router.get('/staff-availability', authenticate, requireRole('Chủ Tiệm'), (req, res) => {
  const { startTime, duration, excludeAppointmentId } = req.query;

  const staffList = db.prepare('SELECT MaNhanVien, MaTaiKhoan, TenNhanVien FROM NhanVien').all();

  if (!startTime || !duration) {
    return res.json(staffList.map(s => ({ ...s, isBusy: false, busyReason: null })));
  }

  const durationMin = parseInt(duration, 10);
  const targetStart = new Date(startTime).getTime();
  const targetEnd = targetStart + durationMin * 60 * 1000;

  const result = staffList.map(s => {
    // Tìm các lịch hẹn mà nhân viên này đang phụ trách trong ngày
    const assignments = db.prepare(`
      SELECT lh.MaLichHen, lh.NgayGioBatDau, lh.TenLienHe,
             SUM(ct.ThoiLuongDat) as TongThoiLuong
      FROM PhanCong pc
      JOIN LichHen lh ON pc.MaLichHen = lh.MaLichHen
      JOIN ChiTietLichHen ct ON lh.MaLichHen = ct.MaLichHen
      WHERE pc.MaNhanVien = ? AND pc.DangPhuTrach = 1 AND lh.TrangThai IN ('Chờ xác nhận', 'Đã xác nhận')
        ${excludeAppointmentId ? 'AND lh.MaLichHen != ?' : ''}
      GROUP BY lh.MaLichHen
    `).all(...(excludeAppointmentId ? [s.MaNhanVien, excludeAppointmentId] : [s.MaNhanVien]));

    let isBusy = false;
    let conflictDetails = null;

    for (const a of assignments) {
      const aStart = new Date(a.NgayGioBatDau).getTime();
      const aEnd = aStart + (a.TongThoiLuong || 30) * 60 * 1000;

      // Trùng nhau: (targetStart < aEnd) && (targetEnd > aStart)
      if (targetStart < aEnd && targetEnd > aStart) {
        isBusy = true;
        conflictDetails = `Trùng lịch với khách ${a.TenLienHe} (${new Date(a.NgayGioBatDau).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })})`;
        break;
      }
    }

    return {
      ...s,
      isBusy,
      busyReason: conflictDetails
    };
  });

  res.json(result);
});

// 2. Danh sách các lịch hẹn cần phân công (Chưa có ai nhận hoặc bị từ chối)
router.get('/pending', authenticate, requireRole('Chủ Tiệm'), (req, res) => {
  const pending = db.prepare(`
    SELECT lh.*, kh.HoTen as HoTenKhach, kh.SoDienThoai as SoDienThoaiKhach,
           pc.MaPhanCong, pc.TrangThaiTiepNhan, pc.LyDoTuChoi, pc.MaNhanVien, nv.TenNhanVien
    FROM LichHen lh
    JOIN KhachHang kh ON lh.MaKhachHang = kh.MaKhachHang
    LEFT JOIN PhanCong pc ON lh.MaLichHen = pc.MaLichHen AND pc.DangPhuTrach = 1
    LEFT JOIN NhanVien nv ON pc.MaNhanVien = nv.MaNhanVien
    WHERE lh.TrangThai IN ('Chờ xác nhận', 'Đã xác nhận')
    ORDER BY lh.NgayGioBatDau ASC
  `).all();

  for (const item of pending) {
    item.chiTietDichVu = db.prepare('SELECT * FROM ChiTietLichHen WHERE MaLichHen = ?').all(item.MaLichHen);
    item.tongTien = item.chiTietDichVu.reduce((sum, d) => sum + d.DonGiaDat, 0);
    item.tongThoiLuong = item.chiTietDichVu.reduce((sum, d) => sum + d.ThoiLuongDat, 0);
  }

  res.json(pending);
});

// 3. Phân công nhân viên cho lịch hẹn (UC 5.1 - Chủ tiệm)
router.post('/', authenticate, requireRole('Chủ Tiệm'), (req, res) => {
  const { maLichHen, maNhanVien } = req.body;

  if (!maLichHen || !maNhanVien) {
    return res.status(400).json({ message: 'Vui lòng chọn lịch hẹn và nhân viên cần phân công' });
  }

  const app = db.prepare('SELECT * FROM LichHen WHERE MaLichHen = ?').get(maLichHen);
  if (!app) {
    return res.status(404).json({ message: 'Không tìm thấy lịch hẹn' });
  }

  const staff = db.prepare('SELECT * FROM NhanVien WHERE MaNhanVien = ?').get(maNhanVien);
  if (!staff) {
    return res.status(404).json({ message: 'Không tìm thấy nhân viên' });
  }

  // Lấy thời lượng của lịch hẹn
  const services = db.prepare('SELECT ThoiLuongDat FROM ChiTietLichHen WHERE MaLichHen = ?').all(maLichHen);
  const totalDuration = services.reduce((sum, s) => sum + s.ThoiLuongDat, 0) || 30;

  const appStart = new Date(app.NgayGioBatDau).getTime();
  const appEnd = appStart + totalDuration * 60 * 1000;

  // BR-UC5-04: Kiểm tra chống trùng lịch nhân viên
  const busyAssignments = db.prepare(`
    SELECT lh.MaLichHen, lh.NgayGioBatDau, SUM(ct.ThoiLuongDat) as TongThoiLuong
    FROM PhanCong pc
    JOIN LichHen lh ON pc.MaLichHen = lh.MaLichHen
    JOIN ChiTietLichHen ct ON lh.MaLichHen = ct.MaLichHen
    WHERE pc.MaNhanVien = ? AND pc.DangPhuTrach = 1 AND lh.TrangThai IN ('Chờ xác nhận', 'Đã xác nhận')
      AND lh.MaLichHen != ?
    GROUP BY lh.MaLichHen
  `).all(maNhanVien, maLichHen);

  for (const b of busyAssignments) {
    const bStart = new Date(b.NgayGioBatDau).getTime();
    const bEnd = bStart + (b.TongThoiLuong || 30) * 60 * 1000;
    if (appStart < bEnd && appEnd > bStart) {
      return res.status(400).json({ message: 'Nhân viên đã có lịch trong khung giờ này' });
    }
  }

  try {
    const maPhanCong = generateId('PC');
    db.transaction(() => {
      // Hủy phụ trách cũ nếu có
      db.prepare('UPDATE PhanCong SET DangPhuTrach = 0 WHERE MaLichHen = ?').run(maLichHen);

      // Thêm phân công mới
      db.prepare(`
        INSERT INTO PhanCong (MaPhanCong, ThoiDiemPhanCong, TrangThaiTiepNhan, DangPhuTrach, MaLichHen, MaNhanVien)
        VALUES (?, datetime('now'), 'Chờ phản hồi', 1, ?, ?)
      `).run(maPhanCong, maLichHen, maNhanVien);

      // Tự động chuyển lịch sang 'Đã xác nhận' nếu đang là 'Chờ xác nhận'
      if (app.TrangThai === 'Chờ xác nhận') {
        db.prepare("UPDATE LichHen SET TrangThai = 'Đã xác nhận' WHERE MaLichHen = ?").run(maLichHen);
      }

      // Gửi thông báo đến nhân viên (BR-UC5-09)
      const formatted = new Date(app.NgayGioBatDau).toLocaleString('vi-VN');
      db.prepare(`
        INSERT INTO ThongBao (MaThongBao, MaTaiKhoanNhan, TieuDe, NoiDung, LoaiThongBao, LienKet, ThoiDiemTao)
        VALUES (?, ?, 'Lịch hẹn mới được phân công', ?, 'PHAN_CONG', '/employee/tasks', datetime('now'))
      `).run(generateId('TB'), staff.MaTaiKhoan, `Bạn được phân công phục vụ khách ${app.TenLienHe} vào lúc ${formatted}. Vui lòng kiểm tra và xác nhận.`);
    })();

    return res.status(201).json({ message: 'Phân công nhân viên thành công' });
  } catch (error) {
    console.error('Lỗi phân công:', error);
    return res.status(500).json({ message: 'Không thể phân công nhân viên. Vui lòng thử lại' });
  }
});

// 4. Thay đổi phân công nhân viên (UC 5.2 - Chủ tiệm)
router.put('/:id', authenticate, requireRole('Chủ Tiệm'), (req, res) => {
  const { id } = req.params; // maLichHen
  const { maNhanVienMoi } = req.body;

  if (!maNhanVienMoi) {
    return res.status(400).json({ message: 'Vui lòng chọn nhân viên mới' });
  }

  const app = db.prepare('SELECT * FROM LichHen WHERE MaLichHen = ?').get(id);
  if (!app) {
    return res.status(404).json({ message: 'Không tìm thấy lịch hẹn cần thay đổi' });
  }

  const staff = db.prepare('SELECT * FROM NhanVien WHERE MaNhanVien = ?').get(maNhanVienMoi);
  if (!staff) {
    return res.status(404).json({ message: 'Không tìm thấy nhân viên' });
  }

  // Kiểm tra trùng lịch nhân viên mới
  const services = db.prepare('SELECT ThoiLuongDat FROM ChiTietLichHen WHERE MaLichHen = ?').all(id);
  const totalDuration = services.reduce((sum, s) => sum + s.ThoiLuongDat, 0) || 30;
  const appStart = new Date(app.NgayGioBatDau).getTime();
  const appEnd = appStart + totalDuration * 60 * 1000;

  const busyAssignments = db.prepare(`
    SELECT lh.MaLichHen, lh.NgayGioBatDau, SUM(ct.ThoiLuongDat) as TongThoiLuong
    FROM PhanCong pc
    JOIN LichHen lh ON pc.MaLichHen = lh.MaLichHen
    JOIN ChiTietLichHen ct ON lh.MaLichHen = ct.MaLichHen
    WHERE pc.MaNhanVien = ? AND pc.DangPhuTrach = 1 AND lh.TrangThai IN ('Chờ xác nhận', 'Đã xác nhận')
      AND lh.MaLichHen != ?
    GROUP BY lh.MaLichHen
  `).all(maNhanVienMoi, id);

  for (const b of busyAssignments) {
    const bStart = new Date(b.NgayGioBatDau).getTime();
    const bEnd = bStart + (b.TongThoiLuong || 30) * 60 * 1000;
    if (appStart < bEnd && appEnd > bStart) {
      return res.status(400).json({ message: 'Nhân viên đã có lịch trong khung giờ này' });
    }
  }

  try {
    const maPhanCong = generateId('PC');
    db.transaction(() => {
      // Hủy phụ trách hiện tại
      db.prepare('UPDATE PhanCong SET DangPhuTrach = 0 WHERE MaLichHen = ?').run(id);

      // Thêm phân công nhân viên mới
      db.prepare(`
        INSERT INTO PhanCong (MaPhanCong, ThoiDiemPhanCong, TrangThaiTiepNhan, DangPhuTrach, MaLichHen, MaNhanVien)
        VALUES (?, datetime('now'), 'Chờ phản hồi', 1, ?, ?)
      `).run(maPhanCong, id, maNhanVienMoi);

      // Thông báo cho nhân viên mới
      const formatted = new Date(app.NgayGioBatDau).toLocaleString('vi-VN');
      db.prepare(`
        INSERT INTO ThongBao (MaThongBao, MaTaiKhoanNhan, TieuDe, NoiDung, LoaiThongBao, LienKet, ThoiDiemTao)
        VALUES (?, ?, 'Thay đổi phân công lịch hẹn', ?, 'PHAN_CONG', '/employee/tasks', datetime('now'))
      `).run(generateId('TB'), staff.MaTaiKhoan, `Chủ tiệm đã điều phối bạn phụ trách lịch hẹn khách ${app.TenLienHe} vào lúc ${formatted}.`);
    })();

    return res.json({ message: 'Thay đổi phân công thành công' });
  } catch (error) {
    console.error('Lỗi đổi phân công:', error);
    return res.status(500).json({ message: 'Không thể thay đổi phân công' });
  }
});

// 5. Nhân viên xem danh sách lịch được giao (UC 2.3)
router.get('/my-tasks', authenticate, requireRole('Nhân Viên'), (req, res) => {
  const staff = db.prepare('SELECT MaNhanVien FROM NhanVien WHERE MaTaiKhoan = ?').get(req.user.maTaiKhoan);
  if (!staff) {
    return res.status(404).json({ message: 'Không tìm thấy hồ sơ nhân viên' });
  }

  const tasks = db.prepare(`
    SELECT pc.MaPhanCong, pc.ThoiDiemPhanCong, pc.TrangThaiTiepNhan, pc.LyDoTuChoi, pc.ThoiDiemPhanHoi, pc.DangPhuTrach,
           lh.MaLichHen, lh.NgayGioBatDau, lh.TenLienHe, lh.SoDienThoaiLienHe, lh.TrangThai as TrangThaiLichHen,
           kh.HoTen as HoTenKhach, kh.SoDienThoai as SoDienThoaiKhach
    FROM PhanCong pc
    JOIN LichHen lh ON pc.MaLichHen = lh.MaLichHen
    JOIN KhachHang kh ON lh.MaKhachHang = kh.MaKhachHang
    WHERE pc.MaNhanVien = ? AND pc.DangPhuTrach = 1
    ORDER BY lh.NgayGioBatDau ASC
  `).all(staff.MaNhanVien);

  for (const t of tasks) {
    t.chiTietDichVu = db.prepare('SELECT * FROM ChiTietLichHen WHERE MaLichHen = ?').all(t.MaLichHen);
    t.tongThoiLuong = t.chiTietDichVu.reduce((sum, d) => sum + d.ThoiLuongDat, 0);
    t.tongTien = t.chiTietDichVu.reduce((sum, d) => sum + d.DonGiaDat, 0);
  }

  res.json(tasks);
});

// 6. Nhân viên xác nhận tiếp nhận lịch (UC 2.1)
router.post('/:id/accept', authenticate, requireRole('Nhân Viên'), (req, res) => {
  const { id } = req.params; // MaPhanCong

  const pc = db.prepare(`
    SELECT pc.*, nv.MaTaiKhoan, nv.TenNhanVien, lh.MaLichHen, lh.TrangThai as TrangThaiLich, lh.NgayGioBatDau, lh.TenLienHe
    FROM PhanCong pc
    JOIN NhanVien nv ON pc.MaNhanVien = nv.MaNhanVien
    JOIN LichHen lh ON pc.MaLichHen = lh.MaLichHen
    WHERE pc.MaPhanCong = ?
  `).get(id);

  if (!pc) {
    return res.status(404).json({ message: 'Không tìm thấy phân công' });
  }

  // 6a. Lịch hẹn không được phân công cho nhân viên đang đăng nhập
  if (pc.MaTaiKhoan !== req.user.maTaiKhoan) {
    return res.status(403).json({ message: 'Bạn không có quyền xác nhận lịch hẹn này' });
  }

  // 6b. Lịch hẹn đã bị hủy
  if (pc.TrangThaiLich === 'Hủy') {
    return res.status(400).json({ message: 'Lịch hẹn đã bị hủy, không thể xác nhận' });
  }

  // 6c. Đã xử lý trước đó
  if (pc.TrangThaiTiepNhan !== 'Chờ phản hồi') {
    return res.status(400).json({ message: 'Lịch hẹn đã được xử lý trước đó' });
  }

  try {
    db.transaction(() => {
      db.prepare(`
        UPDATE PhanCong
        SET TrangThaiTiepNhan = 'Đã tiếp nhận', ThoiDiemPhanHoi = datetime('now')
        WHERE MaPhanCong = ?
      `).run(id);

      // Thông báo cho Chủ tiệm
      const formatted = new Date(pc.NgayGioBatDau).toLocaleString('vi-VN');
      db.prepare(`
        INSERT INTO ThongBao (MaThongBao, MaTaiKhoanNhan, TieuDe, NoiDung, LoaiThongBao, LienKet, ThoiDiemTao)
        VALUES (?, 'TK_OWNER', 'Nhân viên đã tiếp nhận lịch', ?, 'TIEP_NHAN', '/owner/timeline', datetime('now'))
      `).run(generateId('TB'), `Nhân viên ${pc.TenNhanVien} đã xác nhận tiếp nhận lịch hẹn khách ${pc.TenLienHe} (${formatted}).`);
    })();

    return res.json({ message: 'Xác nhận lịch thành công' });
  } catch (error) {
    console.error('Lỗi tiếp nhận lịch:', error);
    return res.status(500).json({ message: 'Không thể xác nhận lịch hẹn. Vui lòng thử lại' });
  }
});

// 7. Nhân viên từ chối lịch được phân công (UC 2.2)
router.post('/:id/reject', authenticate, requireRole('Nhân Viên'), (req, res) => {
  const { id } = req.params; // MaPhanCong
  const { lyDoTuChoi } = req.body;

  // 8a. Nhân viên chưa nhập lý do từ chối (BR-UC2-04)
  if (!lyDoTuChoi || !lyDoTuChoi.trim()) {
    return res.status(400).json({ message: 'Yêu cầu nhập lý do' });
  }

  const pc = db.prepare(`
    SELECT pc.*, nv.MaTaiKhoan, nv.TenNhanVien, lh.MaLichHen, lh.NgayGioBatDau, lh.TenLienHe
    FROM PhanCong pc
    JOIN NhanVien nv ON pc.MaNhanVien = nv.MaNhanVien
    JOIN LichHen lh ON pc.MaLichHen = lh.MaLichHen
    WHERE pc.MaPhanCong = ?
  `).get(id);

  if (!pc) {
    return res.status(404).json({ message: 'Không tìm thấy phân công' });
  }

  if (pc.MaTaiKhoan !== req.user.maTaiKhoan) {
    return res.status(403).json({ message: 'Bạn không có quyền thao tác trên lịch hẹn này' });
  }

  try {
    db.transaction(() => {
      // BR-UC2-05: Ghi nhận từ chối và lý do, hủy phụ trách để chủ tiệm phân công lại
      db.prepare(`
        UPDATE PhanCong
        SET TrangThaiTiepNhan = 'Từ chối', LyDoTuChoi = ?, ThoiDiemPhanHoi = datetime('now'), DangPhuTrach = 0
        WHERE MaPhanCong = ?
      `).run(lyDoTuChoi.trim(), id);

      // Gửi thông báo khẩn cho Chủ tiệm
      const formatted = new Date(pc.NgayGioBatDau).toLocaleString('vi-VN');
      db.prepare(`
        INSERT INTO ThongBao (MaThongBao, MaTaiKhoanNhan, TieuDe, NoiDung, LoaiThongBao, LienKet, ThoiDiemTao)
        VALUES (?, 'TK_OWNER', 'CẢNH BÁO: Nhân viên từ chối lịch', ?, 'TU_CHOI', '/owner/assignments', datetime('now'))
      `).run(
        generateId('TB'),
        `Nhân viên ${pc.TenNhanVien} đã từ chối lịch hẹn ${pc.MaLichHen} lúc ${formatted} của khách ${pc.TenLienHe}.\nLý do: "${lyDoTuChoi.trim()}". Vui lòng phân công lại người khác!`
      );
    })();

    return res.json({ message: 'Yêu cầu từ chối lịch đã được ghi nhận và gửi đến chủ tiệm' });
  } catch (error) {
    console.error('Lỗi từ chối lịch:', error);
    return res.status(500).json({ message: 'Thao tác thất bại' });
  }
});

export default router;
