import express from 'express';
import { db } from '../database.js';
import { authenticate, requireRole } from '../middleware/auth.js';

const router = express.Router();

function generateId(prefix) {
  const rand = Math.floor(1000 + Math.random() * 9000);
  return `${prefix}${Date.now().toString().slice(-4)}${rand.toString().slice(-2)}`;
}

// 1. Danh sách khách hàng và tìm kiếm (UC 6.4, 6.5 - Chủ tiệm)
router.get('/', authenticate, requireRole('Chủ Tiệm'), (req, res) => {
  const { search } = req.query;
  let query = 'SELECT * FROM KhachHang';
  const params = [];

  if (search && search.trim()) {
    const term = `%${search.trim()}%`;
    query += ' WHERE HoTen LIKE ? OR SoDienThoai LIKE ?';
    params.push(term, term);
  }

  query += ' ORDER BY HoTen ASC';

  const customers = db.prepare(query).all(...params);

  // Kèm tổng số lần đặt lịch
  for (const c of customers) {
    const count = db.prepare('SELECT COUNT(*) as c FROM LichHen WHERE MaKhachHang = ?').get(c.MaKhachHang).c;
    c.tongSoLanDat = count;
  }

  res.json(customers);
});

// 2. Thêm thông tin khách hàng mới (UC 6.1 - Chủ tiệm)
router.post('/', authenticate, requireRole('Chủ Tiệm'), (req, res) => {
  const { hoTen, soDienThoai, linkFacebook, linkZalo } = req.body;

  if (!hoTen || !soDienThoai) {
    return res.status(400).json({ message: 'Thông tin chưa hợp lệ (Họ tên và Số điện thoại là bắt buộc)' });
  }

  const cleanPhone = soDienThoai.trim();
  // BR-UC6-01: Số điện thoại phải gồm 10 số
  if (!/^[0-9]{10}$/.test(cleanPhone)) {
    return res.status(400).json({ message: 'Thông tin chưa hợp lệ (Số điện thoại phải gồm đúng 10 chữ số)' });
  }

  // Kiểm tra trùng SĐT
  const existing = db.prepare('SELECT * FROM KhachHang WHERE SoDienThoai = ?').get(cleanPhone);
  if (existing) {
    return res.status(400).json({ message: 'Số điện thoại này đã tồn tại trong danh sách khách hàng' });
  }

  try {
    const maKhachHang = generateId('KH');
    db.prepare(`
      INSERT INTO KhachHang (MaKhachHang, HoTen, SoDienThoai, LinkFacebook, LinkZalo)
      VALUES (?, ?, ?, ?, ?)
    `).run(maKhachHang, hoTen.trim(), cleanPhone, linkFacebook ? linkFacebook.trim() : null, linkZalo ? linkZalo.trim() : null);

    const newCustomer = db.prepare('SELECT * FROM KhachHang WHERE MaKhachHang = ?').get(maKhachHang);
    return res.status(201).json({ message: 'Thêm thông tin khách hàng thành công', customer: newCustomer });
  } catch (error) {
    console.error('Lỗi thêm khách hàng:', error);
    return res.status(500).json({ message: 'Đã xảy ra lỗi, vui lòng thử lại sau' });
  }
});

// 3. Sửa thông tin khách hàng (UC 6.3 - Chủ tiệm)
router.put('/:id', authenticate, requireRole('Chủ Tiệm'), (req, res) => {
  const { id } = req.params;
  const { hoTen, soDienThoai, linkFacebook, linkZalo } = req.body;

  const current = db.prepare('SELECT * FROM KhachHang WHERE MaKhachHang = ?').get(id);
  if (!current) {
    return res.status(404).json({ message: 'Không tìm thấy khách hàng' });
  }

  if (!hoTen || !soDienThoai) {
    return res.status(400).json({ message: 'Cập nhật thông tin khách hàng thất bại, vui lòng thử lại' });
  }

  const cleanPhone = soDienThoai.trim();
  if (!/^[0-9]{10}$/.test(cleanPhone)) {
    return res.status(400).json({ message: 'Số điện thoại không hợp lệ (phải gồm 10 chữ số)' });
  }

  // Kiểm tra SĐT không trùng với khách khác
  const duplicate = db.prepare('SELECT 1 FROM KhachHang WHERE SoDienThoai = ? AND MaKhachHang != ?').get(cleanPhone, id);
  if (duplicate) {
    return res.status(400).json({ message: 'Số điện thoại này đã được sử dụng bởi khách hàng khác' });
  }

  try {
    db.prepare(`
      UPDATE KhachHang
      SET HoTen = ?, SoDienThoai = ?, LinkFacebook = ?, LinkZalo = ?
      WHERE MaKhachHang = ?
    `).run(hoTen.trim(), cleanPhone, linkFacebook ? linkFacebook.trim() : null, linkZalo ? linkZalo.trim() : null, id);

    const updated = db.prepare('SELECT * FROM KhachHang WHERE MaKhachHang = ?').get(id);
    return res.json({ message: 'Lưu thành công', customer: updated });
  } catch (error) {
    console.error('Lỗi sửa khách hàng:', error);
    return res.status(500).json({ message: 'Cập nhật thông tin khách hàng thất bại, vui lòng thử lại' });
  }
});

// 4. Xem lịch sử đặt lịch của khách hàng (UC 6.2 - Chủ tiệm)
router.get('/:id/history', authenticate, requireRole('Chủ Tiệm'), (req, res) => {
  const { id } = req.params;

  const customer = db.prepare('SELECT * FROM KhachHang WHERE MaKhachHang = ?').get(id);
  if (!customer) {
    return res.status(404).json({ message: 'Không tìm thấy khách hàng' });
  }

  const history = db.prepare(`
    SELECT lh.*, pc.MaNhanVien, nv.TenNhanVien,
           gd.MaGiaoDich, gd.SoTien, gd.PhuongThuc, gd.TrangThai as TrangThaiThanhToan
    FROM LichHen lh
    LEFT JOIN PhanCong pc ON lh.MaLichHen = pc.MaLichHen AND pc.DangPhuTrach = 1
    LEFT JOIN NhanVien nv ON pc.MaNhanVien = nv.MaNhanVien
    LEFT JOIN GiaoDich gd ON lh.MaLichHen = gd.MaLichHen
    WHERE lh.MaKhachHang = ?
    ORDER BY lh.NgayGioBatDau DESC
  `).all(id);

  for (const item of history) {
    item.chiTietDichVu = db.prepare('SELECT * FROM ChiTietLichHen WHERE MaLichHen = ?').all(item.MaLichHen);
    item.tongTien = item.chiTietDichVu.reduce((sum, d) => sum + d.DonGiaDat, 0);
  }

  res.json({
    customer,
    tongSoLanDat: history.length,
    history
  });
});

export default router;
