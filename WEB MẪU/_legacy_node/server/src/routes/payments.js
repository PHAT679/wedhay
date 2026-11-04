import express from 'express';
import { db } from '../database.js';
import { authenticate, requireRole } from '../middleware/auth.js';

const router = express.Router();

function generateId(prefix) {
  const rand = Math.floor(1000 + Math.random() * 9000);
  return `${prefix}${Date.now().toString().slice(-4)}${rand.toString().slice(-2)}`;
}

// 1. Tạo thông tin mã VietQR động theo lịch hẹn (UC 3.2 - Alternative 3a1)
router.post('/generate-qr', authenticate, (req, res) => {
  const { maLichHen } = req.body;

  if (!maLichHen) {
    return res.status(400).json({ message: 'Vui lòng cung cấp mã lịch hẹn' });
  }

  const app = db.prepare('SELECT * FROM LichHen WHERE MaLichHen = ?').get(maLichHen);
  if (!app) {
    return res.status(404).json({ message: 'Không tìm thấy lịch hẹn' });
  }

  const services = db.prepare('SELECT DonGiaDat FROM ChiTietLichHen WHERE MaLichHen = ?').all(maLichHen);
  const totalAmount = services.reduce((sum, s) => sum + s.DonGiaDat, 0);

  // Cấu hình tài khoản tiệm Emmay Beauty
  const bankConfig = {
    bankId: 'MB', // Ngân hàng Quân Đội
    accountNo: '0905123456',
    accountName: 'TIEM NAIL EMMAY BEAUTY',
    template: 'compact2'
  };

  const memo = `EMMAY ${maLichHen}`;
  // Chuẩn VietQR URL tương thích app ngân hàng thật
  const qrUrl = `https://img.vietqr.io/image/${bankConfig.bankId}-${bankConfig.accountNo}-${bankConfig.template}.png?amount=${totalAmount}&addInfo=${encodeURIComponent(memo)}&accountName=${encodeURIComponent(bankConfig.accountName)}`;

  res.json({
    maLichHen,
    soTien: totalAmount,
    noiDung: memo,
    nganHang: 'MB Bank (Ngân hàng Quân Đội)',
    soTaiKhoan: bankConfig.accountNo,
    chuTaiKhoan: bankConfig.accountName,
    qrUrl
  });
});

// 2. Xác nhận hoàn tất thanh toán (Tiền mặt hoặc Quét QR) (UC 3.2)
router.post('/confirm', authenticate, requireRole('Chủ Tiệm'), (req, res) => {
  const { maLichHen, phuongThuc } = req.body;

  if (!maLichHen || !phuongThuc) {
    return res.status(400).json({ message: 'Thiếu thông tin thanh toán' });
  }

  if (!['Tiền Mặt', 'QR'].includes(phuongThuc)) {
    return res.status(400).json({ message: 'Phương thức thanh toán không hợp lệ' });
  }

  const app = db.prepare('SELECT * FROM LichHen WHERE MaLichHen = ?').get(maLichHen);
  if (!app) {
    return res.status(404).json({ message: 'Không tìm thấy lịch hẹn' });
  }

  const services = db.prepare('SELECT DonGiaDat FROM ChiTietLichHen WHERE MaLichHen = ?').all(maLichHen);
  const totalAmount = services.reduce((sum, s) => sum + s.DonGiaDat, 0);

  try {
    const maGiaoDich = generateId('GD');
    db.transaction(() => {
      // 1. Kiểm tra xem đã có giao dịch chưa
      const existing = db.prepare('SELECT MaGiaoDich FROM GiaoDich WHERE MaLichHen = ?').get(maLichHen);
      if (existing) {
        db.prepare(`
          UPDATE GiaoDich
          SET SoTien = ?, PhuongThuc = ?, TrangThai = 'Thành công', ThoiDiemGiaoDich = datetime('now')
          WHERE MaLichHen = ?
        `).run(totalAmount, phuongThuc, maLichHen);
      } else {
        db.prepare(`
          INSERT INTO GiaoDich (MaGiaoDich, SoTien, PhuongThuc, TrangThai, ThoiDiemGiaoDich, MaLichHen)
          VALUES (?, ?, ?, 'Thành công', datetime('now'), ?)
        `).run(maGiaoDich, totalAmount, phuongThuc, maLichHen);
      }

      // 2. Cập nhật trạng thái lịch hẹn thành 'Hoàn thành'
      db.prepare(`
        UPDATE LichHen
        SET TrangThai = 'Hoàn thành'
        WHERE MaLichHen = ?
      `).run(maLichHen);

      // 3. Thông báo cho khách hàng
      const customerAccount = db.prepare('SELECT MaTaiKhoan FROM TaiKhoan WHERE MaKhachHang = ?').get(app.MaKhachHang);
      if (customerAccount) {
        db.prepare(`
          INSERT INTO ThongBao (MaThongBao, MaTaiKhoanNhan, TieuDe, NoiDung, LoaiThongBao, LienKet, ThoiDiemTao)
          VALUES (?, ?, 'Thanh toán thành công', ?, 'THANH_TOAN', '/customer/my-appointments', datetime('now'))
        `).run(
          generateId('TB'),
          customerAccount.MaTaiKhoan,
          `Bạn đã thanh toán thành công ${totalAmount.toLocaleString('vi-VN')} VNĐ cho lịch hẹn ${maLichHen} qua ${phuongThuc}. Cảm ơn bạn đã ghé Emmay Beauty!`
        );
      }
    })();

    return res.json({
      message: 'Thanh toán thành công',
      soTien: totalAmount,
      phuongThuc,
      trangThai: 'Hoàn thành'
    });
  } catch (error) {
    console.error('Lỗi thanh toán:', error);
    return res.status(500).json({ message: 'Không thể xác nhận thanh toán. Vui lòng thử lại' });
  }
});

export default router;
