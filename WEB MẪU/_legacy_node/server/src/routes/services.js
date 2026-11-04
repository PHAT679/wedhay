import express from 'express';
import { db } from '../database.js';
import { authenticate, requireRole } from '../middleware/auth.js';

const router = express.Router();

function generateId(prefix) {
  const rand = Math.floor(1000 + Math.random() * 9000);
  return `${prefix}${Date.now().toString().slice(-4)}${rand.toString().slice(-2)}`;
}

// 1. Xem danh sách dịch vụ (UC 8 & UC 4.3)
router.get('/', (req, res) => {
  const { search } = req.query;
  let query = 'SELECT * FROM DichVu WHERE DaXoa = 0';
  const params = [];

  if (search && search.trim()) {
    query += ' AND TenDichVu LIKE ?';
    params.push(`%${search.trim()}%`);
  }

  query += ' ORDER BY GiaTien ASC';

  const services = db.prepare(query).all(...params);
  res.json(services);
});

// 2. Xem chi tiết 1 dịch vụ (UC 4.3)
router.get('/:id', (req, res) => {
  const service = db.prepare('SELECT * FROM DichVu WHERE MaDichVu = ? AND DaXoa = 0').get(req.params.id);
  if (!service) {
    return res.status(404).json({ message: 'Không tìm thấy dịch vụ' });
  }
  res.json(service);
});

// 3. Thêm dịch vụ mới (UC 4.1 - Chủ tiệm)
router.post('/', authenticate, requireRole('Chủ Tiệm'), (req, res) => {
  const { tenDichVu, giaTien, thoiLuong, ghiChu } = req.body;

  // BR-UC4-03: Bắt buộc
  if (!tenDichVu || giaTien === undefined || thoiLuong === undefined) {
    return res.status(400).json({ message: 'Dữ liệu không được để trống' });
  }

  const name = tenDichVu.trim();
  const price = parseInt(giaTien, 10);
  const duration = parseInt(thoiLuong, 10);

  // BR-UC4-04: Giá tiền là số nguyên dương
  if (isNaN(price) || price <= 0) {
    return res.status(400).json({ message: 'Giá tiền không hợp lệ (phải là số nguyên dương)' });
  }

  // BR-UC4-05: Thời gian thực hiện là bội số của 30 (30, 60, 90, 120, 150, 180)
  const validDurations = [30, 60, 90, 120, 150, 180];
  if (isNaN(duration) || !validDurations.includes(duration)) {
    return res.status(400).json({ message: 'Thời gian không hợp lệ (phải là 30, 60, 90, 120, 150 hoặc 180 phút)' });
  }

  // BR-UC4-02: Tên không trùng
  const existing = db.prepare('SELECT 1 FROM DichVu WHERE LOWER(TenDichVu) = LOWER(?) AND DaXoa = 0').get(name);
  if (existing) {
    return res.status(400).json({ message: 'Tên dịch vụ đã tồn tại' });
  }

  try {
    const maDichVu = generateId('DV');
    db.prepare(`
      INSERT INTO DichVu (MaDichVu, TenDichVu, GiaTien, ThoiLuong, GhiChu, DaXoa)
      VALUES (?, ?, ?, ?, ?, 0)
    `).run(maDichVu, name, price, duration, ghiChu ? ghiChu.trim() : null);

    const newService = db.prepare('SELECT * FROM DichVu WHERE MaDichVu = ?').get(maDichVu);
    return res.status(201).json({ message: 'Thêm dịch vụ thành công', service: newService });
  } catch (error) {
    console.error('Lỗi thêm dịch vụ:', error);
    return res.status(500).json({ message: 'Đã xảy ra lỗi, hãy thử lại sau' });
  }
});

// 4. Sửa thông tin dịch vụ (UC 4.2 - Chủ tiệm)
router.put('/:id', authenticate, requireRole('Chủ Tiệm'), (req, res) => {
  const { id } = req.params;
  const { tenDichVu, giaTien, thoiLuong, ghiChu } = req.body;

  const current = db.prepare('SELECT * FROM DichVu WHERE MaDichVu = ? AND DaXoa = 0').get(id);
  if (!current) {
    return res.status(404).json({ message: 'Không tìm thấy dịch vụ để chỉnh sửa' });
  }

  if (!tenDichVu || giaTien === undefined || thoiLuong === undefined) {
    return res.status(400).json({ message: 'Dữ liệu không được để trống' });
  }

  const name = tenDichVu.trim();
  const price = parseInt(giaTien, 10);
  const duration = parseInt(thoiLuong, 10);

  if (isNaN(price) || price <= 0) {
    return res.status(400).json({ message: 'Giá tiền không hợp lệ' });
  }

  const validDurations = [30, 60, 90, 120, 150, 180];
  if (isNaN(duration) || !validDurations.includes(duration)) {
    return res.status(400).json({ message: 'Thời gian không hợp lệ' });
  }

  // Tên không trùng với dịch vụ khác
  const duplicate = db.prepare('SELECT 1 FROM DichVu WHERE LOWER(TenDichVu) = LOWER(?) AND MaDichVu != ? AND DaXoa = 0').get(name, id);
  if (duplicate) {
    return res.status(400).json({ message: 'Tên dịch vụ đã tồn tại' });
  }

  try {
    db.prepare(`
      UPDATE DichVu
      SET TenDichVu = ?, GiaTien = ?, ThoiLuong = ?, GhiChu = ?
      WHERE MaDichVu = ?
    `).run(name, price, duration, ghiChu ? ghiChu.trim() : null, id);

    const updated = db.prepare('SELECT * FROM DichVu WHERE MaDichVu = ?').get(id);
    return res.json({ message: 'Cập nhật dịch vụ thành công', service: updated });
  } catch (error) {
    console.error('Lỗi cập nhật dịch vụ:', error);
    return res.status(500).json({ message: 'Đã có lỗi xảy ra!' });
  }
});

// 5. Xóa dịch vụ (UC 4.4 - Chủ tiệm)
router.delete('/:id', authenticate, requireRole('Chủ Tiệm'), (req, res) => {
  const { id } = req.params;

  const service = db.prepare('SELECT * FROM DichVu WHERE MaDichVu = ? AND DaXoa = 0').get(id);
  if (!service) {
    return res.status(404).json({ message: 'Không tìm thấy dịch vụ' });
  }

  // BR-UC4-08: Không được xóa dịch vụ nếu đang có lịch hẹn ở trạng thái "Chờ xác nhận" hoặc "Đã xác nhận"
  const activeBooking = db.prepare(`
    SELECT lh.MaLichHen, lh.TrangThai
    FROM ChiTietLichHen ct
    JOIN LichHen lh ON ct.MaLichHen = lh.MaLichHen
    WHERE ct.MaDichVu = ? AND lh.TrangThai IN ('Chờ xác nhận', 'Đã xác nhận')
    LIMIT 1
  `).get(id);

  if (activeBooking) {
    return res.status(400).json({ message: 'Không thể xóa vì dịch vụ đang được sử dụng trong các lịch hẹn chưa hoàn thành' });
  }

  try {
    // Soft delete
    db.prepare('UPDATE DichVu SET DaXoa = 1 WHERE MaDichVu = ?').run(id);
    return res.json({ message: 'Xóa dịch vụ thành công' });
  } catch (error) {
    console.error('Lỗi xóa dịch vụ:', error);
    return res.status(500).json({ message: 'Đã có lỗi xảy ra' });
  }
});

export default router;
