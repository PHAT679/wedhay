import express from 'express';
import { db } from '../database.js';
import { authenticate } from '../middleware/auth.js';

const router = express.Router();

// 1. Lấy danh sách thông báo của tài khoản hiện tại
router.get('/', authenticate, (req, res) => {
  const notifications = db.prepare(`
    SELECT * FROM ThongBao
    WHERE MaTaiKhoanNhan = ?
    ORDER BY ThoiDiemTao DESC
    LIMIT 30
  `).all(req.user.maTaiKhoan);

  const unreadCount = db.prepare(`
    SELECT COUNT(*) as c FROM ThongBao
    WHERE MaTaiKhoanNhan = ? AND DaDoc = 0
  `).get(req.user.maTaiKhoan).c;

  res.json({
    unreadCount,
    notifications
  });
});

// 2. Đánh dấu một thông báo đã đọc
router.patch('/:id/read', authenticate, (req, res) => {
  db.prepare(`
    UPDATE ThongBao
    SET DaDoc = 1
    WHERE MaThongBao = ? AND MaTaiKhoanNhan = ?
  `).run(req.params.id, req.user.maTaiKhoan);

  res.json({ message: 'Đã đánh dấu đã đọc' });
});

// 3. Đánh dấu tất cả thông báo đã đọc
router.patch('/read-all', authenticate, (req, res) => {
  db.prepare(`
    UPDATE ThongBao
    SET DaDoc = 1
    WHERE MaTaiKhoanNhan = ?
  `).run(req.user.maTaiKhoan);

  res.json({ message: 'Đã đánh dấu tất cả đã đọc' });
});

export default router;
