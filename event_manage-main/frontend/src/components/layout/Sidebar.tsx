import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  CalendarDays,
  PlusCircle,
  CheckSquare,
  Building2,
  CalendarRange,
  ClipboardCheck,
  Receipt,
  FileBarChart2,
  Sparkles,
  BarChart3,
  Users,
  Settings,
  GraduationCap,
  Bell,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useEvents } from '../../contexts/EventContext';
import { roleNames } from '../../utils/helpers';
import { UserRole } from '../../types';

interface NavItemDef {
  to: string;
  label: string;
  icon: any;
  roles?: UserRole[];
  badge?: number;
  badgeText?: string;
}

export const Sidebar: React.FC = () => {
  const { currentUser, switchUser } = useAuth();
  const { events, notifications } = useEvents();

  // Calculate pending items for current user's role
  const pendingCount = events.filter((e) => {
    if (currentUser.role === 'BCN_KHOA') return e.status === 'FACULTY_REVIEW';
    if (currentUser.role === 'DOAN_TRUONG') return e.status === 'UNIVERSITY_REVIEW' || e.status === 'BUDGET_REVIEW';
    if (currentUser.role === 'CSVC') return e.status === 'FACILITY_REVIEW' || e.status === 'FACILITY_RETURN_PENDING';
    if (currentUser.role === 'KHTC') return e.status === 'FINANCE_REVIEW' || e.status === 'FINANCE_APPROVAL_PENDING';
    return false;
  }).length;

  const unreadNotifs = notifications.filter((n) => !n.isRead).length;

  // Định nghĩa danh mục menu kèm vai trò được phép truy cập
  const navItems: NavItemDef[] = [
    { 
      to: '/', 
      label: 'Tổng quan', 
      icon: LayoutDashboard 
    },
    { 
      to: '/events', 
      label: currentUser.role === 'BTC' ? 'Hồ sơ của tôi' : 'Hồ sơ sự kiện', 
      icon: CalendarDays 
    },
    { 
      to: '/events/create', 
      label: 'Tạo sự kiện mới', 
      icon: PlusCircle, 
      roles: ['BTC', 'ADMIN'] 
    },
    {
      to: '/approvals',
      label: 'Hàng đợi phê duyệt',
      icon: CheckSquare,
      roles: ['BCN_KHOA', 'DOAN_TRUONG', 'CSVC', 'KHTC', 'ADMIN'],
      badge: pendingCount > 0 ? pendingCount : undefined,
    },
    { 
      to: '/calendar', 
      label: 'Lịch tài nguyên & Phòng', 
      icon: CalendarRange 
    },
    { 
      to: '/facilities', 
      label: 'Cơ sở vật chất & Thiết bị', 
      icon: Building2, 
      roles: ['CSVC', 'ADMIN'] 
    },
    { 
      to: '/handover', 
      label: 'Bàn giao & Nghiệm thu', 
      icon: ClipboardCheck, 
      roles: ['CSVC', 'BTC', 'ADMIN'] 
    },
    { 
      to: '/settlements', 
      label: 'Quyết toán tài chính', 
      icon: Receipt, 
      roles: ['KHTC', 'BTC', 'ADMIN'] 
    },
    { 
      to: '/reports', 
      label: 'Báo cáo tổng kết', 
      icon: FileBarChart2, 
      roles: ['BTC', 'DOAN_TRUONG', 'ADMIN'] 
    },
    { 
      to: '/ai-review', 
      label: 'Trợ lý AI Rà soát', 
      icon: Sparkles, 
      badgeText: 'AI',
      roles: ['BTC', 'DOAN_TRUONG', 'BCN_KHOA', 'ADMIN'] 
    },
    { 
      to: '/analytics', 
      label: 'Báo cáo & Thống kê', 
      icon: BarChart3, 
      roles: ['BCN_KHOA', 'DOAN_TRUONG', 'CSVC', 'KHTC', 'ADMIN'] 
    },
    { 
      to: '/notifications', 
      label: 'Thông báo', 
      icon: Bell, 
      badge: unreadNotifs > 0 ? unreadNotifs : undefined 
    },
  ];

  const adminNavItems: NavItemDef[] = [
    { to: '/admin/users', label: 'Quản trị người dùng', icon: Users, roles: ['ADMIN'] },
    { to: '/admin/settings', label: 'Cấu hình hệ thống', icon: Settings, roles: ['ADMIN'] },
  ];

  // LỌC CHẶT CHẼ: Chỉ những mục menu mà vai trò hiện tại ĐƯỢC PHÉP mới hiển thị lên Sidebar
  const visibleNavItems = navItems.filter(
    (item) => !item.roles || item.roles.includes(currentUser.role)
  );

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0 h-screen sticky top-0 border-r border-slate-800 z-30 select-none">
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-800/80 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-blue-900/30">
          <GraduationCap className="w-6 h-6" />
        </div>
        <div>
          <div className="font-bold text-white tracking-tight flex items-center gap-1.5 text-base">
            EventFlow
            <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded-md bg-blue-500/20 text-blue-400 border border-blue-500/30">
              DUE
            </span>
          </div>
          <div className="text-[11px] text-slate-400 font-medium">Trường Đại học Kinh tế</div>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto px-3 py-3 space-y-1">
        <div className="px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-500 flex items-center justify-between">
          <span>Quyền hạn vai trò</span>
          <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-blue-400 font-bold">
            {currentUser.role}
          </span>
        </div>

        {visibleNavItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-sm font-semibold'
                    : 'text-slate-300 hover:bg-slate-800/70 hover:text-white'
                }`
              }
            >
              <div className="flex items-center gap-2.5">
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && (
                <span className="px-1.5 py-0.5 text-xs font-bold rounded-full bg-amber-500 text-white min-w-5 text-center">
                  {item.badge}
                </span>
              )}
              {item.badgeText && (
                <span className="px-1.5 py-0.5 text-[10px] font-bold rounded-md bg-indigo-500/30 text-indigo-300 border border-indigo-400/30">
                  {item.badgeText}
                </span>
              )}
            </NavLink>
          );
        })}

        {currentUser.role === 'ADMIN' && (
          <>
            <div className="px-3 pt-4 pb-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
              Hệ thống Quản trị
            </div>
            {adminNavItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-blue-600 text-white font-semibold'
                        : 'text-slate-300 hover:bg-slate-800/70 hover:text-white'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </>
        )}
      </div>

      {/* Role Switcher & Profile Widget */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/60">
        <div className="text-[11px] text-slate-400 mb-1 font-semibold uppercase tracking-wider">
          Chuyển đổi vai trò demo:
        </div>
        <select
          value={currentUser.role}
          onChange={(e) => switchUser(e.target.value as any)}
          aria-label="Chuyển đổi vai trò demo"
          className="w-full bg-slate-800 text-slate-200 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs font-medium focus:outline-hidden focus:ring-1 focus:ring-blue-500 mb-3 cursor-pointer"
        >
          <option value="BTC">1. BTC (Ban Tổ chức sinh viên)</option>
          <option value="BCN_KHOA">2. BCN Khoa (Xét duyệt cơ sở)</option>
          <option value="DOAN_TRUONG">3. Đoàn Trường (Thẩm định & Cấp phép)</option>
          <option value="CSVC">4. Cơ sở vật chất (Kiểm tra lịch & Bàn giao)</option>
          <option value="KHTC">5. Kế hoạch - Tài chính (Quyết toán)</option>
          <option value="ADMIN">6. Quản trị viên (Toàn quyền)</option>
        </select>

        <div className="flex items-center gap-2.5 pt-1">
          <div className="w-8 h-8 rounded-full bg-blue-600/30 text-blue-400 border border-blue-500/40 flex items-center justify-center font-bold text-xs shrink-0">
            {currentUser.fullName.charAt(0)}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-semibold text-white truncate">{currentUser.fullName}</div>
            <div className="text-[10px] text-blue-400 truncate font-semibold">{roleNames[currentUser.role]}</div>
          </div>
        </div>
      </div>
    </aside>
  );
};
