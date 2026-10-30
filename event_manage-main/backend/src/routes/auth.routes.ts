import { Router, Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import { login, getUserById } from '../services/auth.service';
import { authenticate } from '../middleware/auth';
import { validate } from '../middleware/validate';
import { getPermissionsForRole, ROLE_PERMISSIONS } from '../config/permissions';

const router = Router();

const loginSchema = z.object({
  email: z.string().email('Email không đúng định dạng'),
  password: z.string().min(1, 'Vui lòng nhập mật khẩu'),
});

router.post('/login', validate(loginSchema), async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { email, password } = req.body;
    const result = await login(email, password);
    res.json({ success: true, data: result });
  } catch (err: any) {
    res.status(401).json({ success: false, error: err.message });
  }
});

router.get('/me', authenticate, async (req: Request, res: Response, next: NextFunction) => {
  try {
    const user = await getUserById(req.user!.userId);
    if (!user) {
      res.status(404).json({ success: false, error: 'Không tìm thấy người dùng' });
      return;
    }
    res.json({ success: true, data: user });
  } catch (err) {
    next(err);
  }
});

router.get('/permissions', authenticate, (req: Request, res: Response) => {
  res.json({
    success: true,
    data: {
      role: req.user!.role,
      permissions: getPermissionsForRole(req.user!.role),
      allRolePermissions: ROLE_PERMISSIONS,
    },
  });
});

router.post('/logout', (_req: Request, res: Response) => {
  res.json({ success: true, message: 'Đăng xuất thành công' });
});

export default router;
