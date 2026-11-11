import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Logo } from './Logo';
import { useAuth } from '../context/AuthContext';
import {
  CalendarDays,
  Users2,
  Sparkles,
  UserCheck,
  Bell,
  LogOut,
  ArrowLeft,
  Scissors
} from 'lucide-react';

interface SidebarProps {
  role: 'Chủ Tiệm' | 'Nhân Viên';
}

export const Sidebar: React.FC<SidebarProps> = ({ role }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const ownerLinks = [
    { to: '/owner/timeline', label: 'Timeline Lịch hẹn', icon: CalendarDays },
    { to: '/owner/assignments', label: 'Quản lý phân công', icon: Users2 },
    { to: '/owner/services', label: 'Quản lý dịch vụ', icon: Scissors },
    { to: '/owner/customers', label: 'Quản lý khách hàng', icon: UserCheck },
    { to: '/notifications', label: 'Thông báo', icon: Bell },
  ];

  const employeeLinks = [
    { to: '/employee/tasks', label: 'Lịch được phân công', icon: Sparkles },
    { to: '/notifications', label: 'Thông báo cá nhân', icon: Bell },
  ];

  const links = role === 'Chủ Tiệm' ? ownerLinks : employeeLinks;

  return (
    <aside className="w-64 bg-white border-r border-blushPink/80 min-h-screen flex flex-col justify-between select-none">
      <div>
        {/* Top brand */}
        <div className="p-6 border-b border-blushPink/60">
          <Logo size="sm" showSubtitle={true} subtitleText={role === 'Chủ Tiệm' ? 'Hệ thống Quản trị' : 'Kỹ thuật viên'} />
        </div>

        {/* User Card */}
        <div className="p-4 mx-3 my-4 rounded-2xl bg-softPink/60 border border-blushPink flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-rosePink text-white font-bold flex items-center justify-center text-sm shadow-sm">
            {user?.hoTen?.charAt(0) || 'U'}
          </div>
          <div className="overflow-hidden">
            <h4 className="text-sm font-semibold text-textCharcoal truncate">{user?.hoTen}</h4>
            <span className="text-[11px] font-medium text-darkRose inline-block bg-white/70 px-2 py-0.5 rounded-full mt-0.5">
              {user?.vaiTro}
            </span>
          </div>
        </div>

        {/* Nav Links */}
        <nav className="px-3 space-y-1">
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-rosePink text-white shadow-soft font-semibold'
                      : 'text-stone-600 hover:text-darkRose hover:bg-softPink/60'
                  }`
                }
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                <span>{link.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Bottom actions */}
      <div className="p-4 border-t border-blushPink/60 space-y-2">
        <button
          onClick={() => navigate('/')}
          className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-medium text-stone-500 hover:text-darkRose hover:bg-softPink rounded-xl transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Về trang khách hàng
        </button>
        <button
          onClick={() => {
            logout();
            navigate('/login');
          }}
          className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-medium text-rose-600 hover:bg-rose-50 rounded-xl transition-colors"
        >
          <LogOut className="w-4 h-4" /> Đăng xuất
        </button>
      </div>
    </aside>
  );
};
