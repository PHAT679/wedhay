import { Router, Request, Response, NextFunction } from 'express';
import bcrypt from 'bcryptjs';
import prisma from '../config/database';
import { authenticate } from '../middleware/auth';
import { authorize } from '../middleware/authorize';
import { UserRole } from '../types';

const router = Router();

// List users (chỉ hiển thị những người dùng có vai trò hợp lệ và đang hoạt động)
router.get('/', authenticate, authorize(UserRole.ADMIN), async (_req: Request, res: Response, next: NextFunction) => {
  try {
    const users = await prisma.user.findMany({
      where: {
        role: {
          in: Object.values(UserRole),
        },
        isActive: true,
      },
      select: {
        id: true,
        email: true,
        fullName: true,
        role: true,
        department: true,
        phone: true,
        isActive: true,
        createdAt: true,
      },
      orderBy: { createdAt: 'desc' },
    });
    res.json({ success: true, data: users });
  } catch (err) {
    next(err);
  }
});

// Create user
router.post('/', authenticate, authorize(UserRole.ADMIN), async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { email, password, fullName, role, department, phone } = req.body;
    const existing = await prisma.user.findUnique({ where: { email } });
    if (existing) {
      res.status(400).json({ success: false, error: 'Email đã được sử dụng' });
      return;
    }

    const passwordHash = await bcrypt.hash(password || '123456', 10);
    const user = await prisma.user.create({
      data: {
        email,
        passwordHash,
        fullName,
        role,
        department,
        phone,
      },
      select: { id: true, email: true, fullName: true, role: true, department: true },
    });

    res.status(201).json({ success: true, data: user });
  } catch (err: any) {
    res.status(400).json({ success: false, error: err.message });
  }
});

// Update user
router.put('/:id', authenticate, authorize(UserRole.ADMIN), async (req: Request, res: Response, next: NextFunction) => {
  try {
    const id = Array.isArray(req.params.id) ? req.params.id[0] : req.params.id;
    const { fullName, role, department, phone, isActive, password } = req.body;
    const data: Record<string, any> = { fullName, role, department, phone, isActive };
    if (password) {
      data.passwordHash = await bcrypt.hash(password, 10);
    }

    const updated = await prisma.user.update({
      where: { id },
      data,
      select: { id: true, email: true, fullName: true, role: true, department: true, isActive: true },
    });

    res.json({ success: true, data: updated });
  } catch (err: any) {
    res.status(400).json({ success: false, error: err.message });
  }
});

export default router;
