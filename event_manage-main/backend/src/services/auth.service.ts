import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import prisma from '../config/database';
import { config } from '../config';
import { JwtPayload, UserRole } from '../types';
import { getPermissionsForRole } from '../config/permissions';

export async function login(email: string, password: string) {
  const user = await prisma.user.findUnique({ where: { email } });
  if (!user || !user.isActive) {
    throw new Error('Email hoặc mật khẩu không đúng');
  }

  // Chặn người dùng không có vai trò hoặc vai trò không hợp lệ
  if (!user.role || !Object.values(UserRole).includes(user.role as UserRole)) {
    throw new Error('Tài khoản chưa được phân quyền vai trò để truy cập hệ thống');
  }

  const isValid = await bcrypt.compare(password, user.passwordHash);
  if (!isValid) {
    throw new Error('Email hoặc mật khẩu không đúng');
  }

  const payload: JwtPayload = {
    userId: user.id,
    email: user.email,
    role: user.role as JwtPayload['role'],
    fullName: user.fullName,
  };

  const token = jwt.sign(payload, config.jwtSecret, { expiresIn: config.jwtExpiresIn as any });

  return {
    token,
    user: {
      id: user.id,
      email: user.email,
      fullName: user.fullName,
      role: user.role,
      department: user.department,
      phone: user.phone,
      permissions: getPermissionsForRole(user.role),
    },
  };
}

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 12);
}

export async function getUserById(userId: string) {
  const user = await prisma.user.findUnique({
    where: { id: userId },
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
  });
  if (!user) return null;
  return {
    ...user,
    permissions: getPermissionsForRole(user.role),
  };
}
