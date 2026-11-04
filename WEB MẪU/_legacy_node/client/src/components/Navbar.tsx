import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Logo } from './Logo';
import { useAuth } from '../context/AuthContext';
import { NotificationDropdown } from './NotificationDropdown';
import { Calendar, Sparkles, User, LogOut, Menu, X, Clock, ShieldCheck } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="sticky top-0 z-40 bg-white/85 backdrop-blur-md border-b border-blushPink/80 shadow-sm transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <Logo size="sm" showSubtitle={false} />
            <div className="hidden sm:block">
              <span className="font-playfair font-semibold text-xl text-darkRose block leading-tight">
                Emmay Beauty
              </span>
              <span className="font-montserrat text-[10px] text-dustyRose tracking-widest uppercase block">
                356/87 Hoàng Diệu • Đà Nẵng
              </span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
            <Link
              to="/"
              className={`px-3 py-2 rounded-xl text-sm font-medium transition-all ${
                isActive('/') ? 'text-darkRose bg-softPink' : 'text-stone-600 hover:text-darkRose hover:bg-softPink/50'
              }`}
            >
              Trang chủ
            </Link>
            <Link
              to="/services"
              className={`px-3 py-2 rounded-xl text-sm font-medium transition-all ${
                isActive('/services') ? 'text-darkRose bg-softPink' : 'text-stone-600 hover:text-darkRose hover:bg-softPink/50'
              }`}
            >
              Bảng giá dịch vụ
            </Link>
            <Link
              to="/book"
              className={`px-4 py-2 rounded-xl text-sm font-medium flex items-center gap-1.5 transition-all ${
                isActive('/book')
                  ? 'bg-rosePink text-white shadow-soft'
                  : 'bg-softPink text-darkRose hover:bg-rosePink hover:text-white'
              }`}
            >
              <Calendar className="w-4 h-4" />
              Đặt lịch hẹn
            </Link>

            {user?.vaiTro === 'Khách Hàng' && (
              <Link
                to="/customer/my-appointments"
                className={`px-3 py-2 rounded-xl text-sm font-medium flex items-center gap-1.5 transition-all ${
                  isActive('/customer/my-appointments')
                    ? 'text-darkRose bg-softPink'
                    : 'text-stone-600 hover:text-darkRose hover:bg-softPink/50'
                }`}
              >
                <Clock className="w-4 h-4" />
                Lịch của tôi
              </Link>
            )}

            {user?.vaiTro === 'Chủ Tiệm' && (
              <Link
                to="/owner/timeline"
                className="px-3 py-2 rounded-xl text-sm font-semibold text-rose-700 bg-rose-50 border border-rose-200 hover:bg-rose-100 flex items-center gap-1.5"
              >
                <ShieldCheck className="w-4 h-4" />
                Quản trị tiệm
              </Link>
            )}

            {user?.vaiTro === 'Nhân Viên' && (
              <Link
                to="/employee/tasks"
                className="px-3 py-2 rounded-xl text-sm font-semibold text-blue-700 bg-blue-50 border border-blue-200 hover:bg-blue-100 flex items-center gap-1.5"
              >
                <Sparkles className="w-4 h-4" />
                Lịch phân công
              </Link>
            )}
          </nav>

          {/* Right Action Buttons */}
          <div className="hidden md:flex items-center space-x-3">
            {user ? (
              <div className="flex items-center space-x-3">
                <NotificationDropdown />

                <div className="flex items-center gap-2 pl-2 border-l border-blushPink">
                  <div className="w-9 h-9 rounded-full bg-softPink border border-rosePink/40 flex items-center justify-center text-darkRose font-bold text-sm">
                    {user.hoTen?.charAt(0) || 'U'}
                  </div>
                  <div className="text-left">
                    <p className="text-xs font-semibold text-textCharcoal line-clamp-1 max-w-[120px]">
                      {user.hoTen}
                    </p>
                    <span className="text-[10px] text-dustyRose font-medium block">
                      {user.vaiTro}
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => {
                    logout();
                    navigate('/login');
                  }}
                  className="p-2 text-stone-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-colors"
                  title="Đăng xuất"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link
                  to="/login"
                  className="px-4 py-2 rounded-xl text-sm font-medium text-darkRose hover:bg-softPink transition-all"
                >
                  Đăng nhập
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 rounded-xl text-sm font-medium bg-rosePink text-white hover:bg-dustyRose shadow-sm transition-all"
                >
                  Đăng ký
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex items-center md:hidden gap-2">
            {user && <NotificationDropdown />}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-xl text-stone-600 hover:text-darkRose hover:bg-softPink"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-blushPink/60 bg-white/95 px-4 pt-2 pb-6 space-y-2 animate-fadeIn">
          <Link
            to="/"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-xl text-base font-medium text-textCharcoal hover:bg-softPink"
          >
            Trang chủ
          </Link>
          <Link
            to="/services"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-xl text-base font-medium text-textCharcoal hover:bg-softPink"
          >
            Bảng giá dịch vụ
          </Link>
          <Link
            to="/book"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-xl text-base font-medium text-rosePink bg-softPink"
          >
            Đặt lịch hẹn ngay
          </Link>

          {user?.vaiTro === 'Khách Hàng' && (
            <Link
              to="/customer/my-appointments"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-xl text-base font-medium text-textCharcoal hover:bg-softPink"
            >
              Lịch hẹn của tôi
            </Link>
          )}

          {user?.vaiTro === 'Chủ Tiệm' && (
            <Link
              to="/owner/timeline"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-xl text-base font-medium text-rose-700 bg-rose-50"
            >
              Quản trị tiệm
            </Link>
          )}

          {user?.vaiTro === 'Nhân Viên' && (
            <Link
              to="/employee/tasks"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-xl text-base font-medium text-blue-700 bg-blue-50"
            >
              Lịch phân công của tôi
            </Link>
          )}

          <div className="pt-4 border-t border-blushPink/50">
            {user ? (
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold text-sm text-textCharcoal">{user.hoTen}</p>
                  <p className="text-xs text-dustyRose">{user.vaiTro}</p>
                </div>
                <button
                  onClick={() => {
                    logout();
                    setMobileMenuOpen(false);
                    navigate('/login');
                  }}
                  className="px-3 py-1.5 text-xs text-rose-600 bg-rose-50 rounded-lg hover:bg-rose-100"
                >
                  Đăng xuất
                </button>
              </div>
            ) : (
              <div className="flex gap-2">
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex-1 text-center py-2 text-sm font-medium text-darkRose bg-softPink rounded-xl"
                >
                  Đăng nhập
                </Link>
                <Link
                  to="/register"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex-1 text-center py-2 text-sm font-medium text-white bg-rosePink rounded-xl"
                >
                  Đăng ký
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
