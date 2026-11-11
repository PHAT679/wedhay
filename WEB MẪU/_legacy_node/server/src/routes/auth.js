import express from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { db } from '../database.js';
import { JWT_SECRET, authenticate } from '../middleware/auth.js';

const router = express.Router();

// Helper generate unique ID
function generateId(prefix) {
  const rand = Math.floor(1000 + Math.random() * 9000);
  return `${prefix}${Date.now().toString().slice(-4)}${rand.toString().slice(-2)}`;
}

// 1. Đăng nhập (UC 1)
router.post('/login', (req, res) => {
  const { tenDangNhap, matKhau } = req.body;

  if (!tenDangNhap || !matKhau) {
    return res.status(400).json({ message: 'Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu' });
  }

  const user = db.prepare(`
    SELECT t.*, k.HoTen as HoTenKhach, k.SoDienThoai, n.TenNhanVien, n.MaNhanVien
    FROM TaiKhoan t
    LEFT JOIN KhachHang k ON t.MaKhachHang = k.MaKhachHang
    LEFT JOIN NhanVien n ON t.MaTaiKhoan = n.MaTaiKhoan
    WHERE t.TenDangNhap = ?
  `).get(tenDangNhap.trim());

  if (!user) {
    return res.status(401).json({ message: 'Tên tài khoản hoặc mật khẩu không chính xác' });
  }

  const isMatch = bcrypt.compareSync(matKhau, user.MatKhau);
  if (!isMatch) {
    return res.status(401).json({ message: 'Tên tài khoản hoặc mật khẩu không chính xác' });
  }

  const displayName = user.VaiTro === 'Chủ Tiệm'
    ? 'Chủ Tiệm Emmay'
    : user.VaiTro === 'Nhân Viên'
      ? user.TenNhanVien
      : user.HoTenKhach || user.TenDangNhap;

  const payload = {
    maTaiKhoan: user.MaTaiKhoan,
    tenDangNhap: user.TenDangNhap,
    vaiTro: user.VaiTro,
    maKhachHang: user.MaKhachHang,
    maNhanVien: user.MaNhanVien,
    hoTen: displayName,
    soDienThoai: user.SoDienThoai
  };

  const token = jwt.sign(payload, JWT_SECRET, { expiresIn: '7d' });

  return res.json({
    message: 'Đăng nhập thành công',
    token,
    user: payload
  });
});

// 2. Đăng ký tài khoản Khách hàng (UC 9)
router.post('/register', (req, res) => {
  const { hoTen, soDienThoai, tenDangNhap, matKhau } = req.body;

  // BR-UC9-01: Bắt buộc nhập đầy đủ
  if (!hoTen || !soDienThoai || !tenDangNhap || !matKhau) {
    return res.status(400).json({ message: 'Vui lòng nhập đầy đủ thông tin' });
  }

  // BR-UC9-02: Số điện thoại phải gồm đúng 10 chữ số
  const cleanPhone = soDienThoai.trim();
  const phoneRegex = /^[0-9]{10}$/;
  if (!phoneRegex.test(cleanPhone)) {
    return res.status(400).json({ message: 'Số điện thoại không hợp lệ (phải gồm đúng 10 chữ số)' });
  }

  // BR-UC9-03: Tên đăng nhập không được trùng
  const existingUser = db.prepare('SELECT 1 FROM TaiKhoan WHERE TenDangNhap = ?').get(tenDangNhap.trim());
  if (existingUser) {
    return res.status(400).json({ message: 'Tên đăng nhập đã tồn tại' });
  }

  try {
    const transaction = db.transaction(() => {
      // Kiểm tra xem khách hàng có SĐT này đã được chủ tiệm thêm trước đó chưa
      let customer = db.prepare('SELECT * FROM KhachHang WHERE SoDienThoai = ?').get(cleanPhone);
      let maKhachHang;

      if (customer) {
        maKhachHang = customer.MaKhachHang;
        // Kiểm tra xem khách hàng này đã liên kết với tài khoản nào chưa
        const linkedAccount = db.prepare('SELECT 1 FROM TaiKhoan WHERE MaKhachHang = ?').get(maKhachHang);
        if (linkedAccount) {
          throw new Error('Số điện thoại này đã được liên kết với một tài khoản khác');
        }
      } else {
        maKhachHang = generateId('KH');
        db.prepare(`
          INSERT INTO KhachHang (MaKhachHang, HoTen, SoDienThoai)
          VALUES (?, ?, ?)
        `).run(maKhachHang, hoTen.trim(), cleanPhone);
      }

      const maTaiKhoan = generateId('TK');
      const hashPassword = bcrypt.hashSync(matKhau, 10);

      db.prepare(`
        INSERT INTO TaiKhoan (MaTaiKhoan, TenDangNhap, MatKhau, VaiTro, MaKhachHang)
        VALUES (?, ?, ?, 'Khách Hàng', ?)
      `).run(maTaiKhoan, tenDangNhap.trim(), hashPassword, maKhachHang);

      // Thêm thông báo chào mừng
      db.prepare(`
        INSERT INTO ThongBao (MaThongBao, MaTaiKhoanNhan, TieuDe, NoiDung, LoaiThongBao, LienKet, ThoiDiemTao)
        VALUES (?, ?, 'Chào mừng đến với Emmay Beauty!', 'Tài khoản của bạn đã được khởi tạo thành công. Hãy đặt lịch làm móng ngay hôm nay nhé!', 'HE_THONG', '/customer/book', datetime('now'))
      `).run(generateId('TB'), maTaiKhoan);

      return { maTaiKhoan, maKhachHang };
    });

    const result = transaction();

    const payload = {
      maTaiKhoan: result.maTaiKhoan,
      tenDangNhap: tenDangNhap.trim(),
      vaiTro: 'Khách Hàng',
      maKhachHang: result.maKhachHang,
      hoTen: hoTen.trim(),
      soDienThoai: cleanPhone
    };

    const token = jwt.sign(payload, JWT_SECRET, { expiresIn: '7d' });

    return res.status(201).json({
      message: 'Đăng ký tài khoản thành công',
      token,
      user: payload
    });
  } catch (error) {
    console.error('Lỗi đăng ký:', error);
    return res.status(500).json({ message: error.message || 'Đăng ký tài khoản thất bại, vui lòng thử lại' });
  }
});

// 3. Lấy thông tin tài khoản hiện tại
router.get('/me', authenticate, (req, res) => {
  const user = db.prepare(`
    SELECT t.MaTaiKhoan, t.TenDangNhap, t.VaiTro, t.MaKhachHang,
           k.HoTen as HoTenKhach, k.SoDienThoai, k.LinkFacebook, k.LinkZalo,
           n.TenNhanVien, n.MaNhanVien
    FROM TaiKhoan t
    LEFT JOIN KhachHang k ON t.MaKhachHang = k.MaKhachHang
    LEFT JOIN NhanVien n ON t.MaTaiKhoan = n.MaTaiKhoan
    WHERE t.MaTaiKhoan = ?
  `).get(req.user.maTaiKhoan);

  if (!user) {
    return res.status(404).json({ message: 'Không tìm thấy người dùng' });
  }

  return res.json({
    maTaiKhoan: user.MaTaiKhoan,
    tenDangNhap: user.TenDangNhap,
    vaiTro: user.VaiTro,
    maKhachHang: user.MaKhachHang,
    maNhanVien: user.MaNhanVien,
    hoTen: user.VaiTro === 'Chủ Tiệm' ? 'Chủ Tiệm Emmay' : user.VaiTro === 'Nhân Viên' ? user.TenNhanVien : user.HoTenKhach,
    soDienThoai: user.SoDienThoai,
    linkFacebook: user.LinkFacebook,
    linkZalo: user.LinkZalo
  });
});

export default router;
