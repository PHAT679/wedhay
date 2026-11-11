import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Logo } from '../components/Logo';
import { User, Lock, Eye, EyeOff, ArrowRight, Sparkles, CheckCircle2 } from 'lucide-react';
import loginRefImg from '../assets/login-reference.png';

export const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password) {
      setError('Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu');
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      const user = await login({ tenDangNhap: username.trim(), matKhau: password });

      // Điều hướng thông minh theo vai trò người dùng (UC 1)
      if (user.vaiTro === 'Chủ Tiệm') {
        navigate('/owner/timeline');
      } else if (user.vaiTro === 'Nhân Viên') {
        navigate('/employee/tasks');
      } else {
        const from = (location.state as any)?.from?.pathname || '/customer/my-appointments';
        navigate(from);
      }
    } catch (err: any) {
      setError(err.message || 'Tên tài khoản hoặc mật khẩu không chính xác');
    } finally {
      setIsLoading(false);
    }
  };

  // Nút đăng nhập thử nghiệm 1-click cho giáo viên & người chấm
  const fillDemo = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-[#FDF5F6] flex items-center justify-center p-3 sm:p-6 lg:p-8 font-montserrat">
      {/* Background silk atmosphere */}
      <div className="fixed inset-0 pointer-events-none opacity-40 bg-[radial-gradient(#F5DDE2_1px,transparent_1px)] [background-size:16px_16px]"></div>

      {/* Main Container Card matching the design image */}
      <div className="w-full max-w-5xl bg-white rounded-3xl shadow-[0_20px_60px_-15px_rgba(201,127,142,0.25)] border border-[#F5DDE2] overflow-hidden grid grid-cols-1 lg:grid-cols-2 relative z-10">
        
        {/* LEFT COLUMN: Silk, Nails, Perfume, and Luxury Branding */}
        <div className="hidden lg:block relative min-h-[620px] overflow-hidden bg-[#FBECEF]">
          {/* Reference image positioned with focus on the left artistic half */}
          <img
            src={loginRefImg}
            alt="Emmay Beauty Nail Art"
            className="absolute inset-0 w-full h-full object-cover object-left"
          />
          {/* Subtle gradient overlay to enhance text readability */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-white/10" />

          {/* Floating petals animation overlay */}
          <div className="absolute bottom-6 left-6 right-6 p-4 rounded-2xl bg-white/40 backdrop-blur-md border border-white/60 text-center">
            <p className="font-playfair italic text-darkRose font-medium text-sm">
              "Vẻ đẹp tinh tế từ đôi bàn tay ngọc ngà"
            </p>
            <p className="text-[11px] text-textCharcoal/70 tracking-wider uppercase mt-1">
              356/87 Hoàng Diệu • Đà Nẵng • Hotline: 0905 123 456
            </p>
          </div>
        </div>

        {/* RIGHT COLUMN: The Exact Login Form */}
        <div className="p-6 sm:p-10 lg:p-12 flex flex-col justify-between bg-white">
          <div>
            {/* Header with delicate logo */}
            <div className="text-center mb-8">
              <Logo size="md" showSubtitle={false} color="text-darkRose" />
              <p className="text-sm text-stone-500 mt-2 font-medium">
                Đăng nhập để quản lý lịch hẹn và dịch vụ
              </p>
            </div>

            {/* Error banner */}
            {error && (
              <div className="mb-6 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium animate-shake">
                {error}
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Username Input */}
              <div>
                <label className="block text-xs font-semibold text-textCharcoal mb-1.5">
                  Tên đăng nhập hoặc email
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-stone-400">
                    <User className="w-5 h-5" />
                  </div>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Nhập tên đăng nhập hoặc email"
                    className="w-full pl-11 pr-4 py-3 rounded-xl border border-blushPink bg-softPink/20 text-sm text-textCharcoal placeholder-stone-400 focus:outline-none focus:border-rosePink focus:bg-white focus:ring-2 focus:ring-rosePink/20 transition-all"
                  />
                </div>
              </div>

              {/* Password Input */}
              <div>
                <label className="block text-xs font-semibold text-textCharcoal mb-1.5">
                  Mật khẩu
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-stone-400">
                    <Lock className="w-5 h-5" />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Nhập mật khẩu"
                    className="w-full pl-11 pr-11 py-3 rounded-xl border border-blushPink bg-softPink/20 text-sm text-textCharcoal placeholder-stone-400 focus:outline-none focus:border-rosePink focus:bg-white focus:ring-2 focus:ring-rosePink/20 transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-stone-400 hover:text-darkRose transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Remember & Forgot Password */}
              <div className="flex items-center justify-between text-xs pt-1">
                <label className="flex items-center gap-2 cursor-pointer select-none text-stone-600">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded border-blushPink text-rosePink focus:ring-rosePink accent-rosePink"
                  />
                  <span>Ghi nhớ đăng nhập</span>
                </label>
                <button
                  type="button"
                  onClick={() => alert('Vui lòng liên hệ trực tiếp chủ tiệm Emmay Beauty (0905 123 456) để được cấp lại mật khẩu.')}
                  className="text-stone-500 hover:text-darkRose transition-colors"
                >
                  Quên mật khẩu?
                </button>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3.5 px-6 rounded-xl bg-gradient-to-r from-rosePink to-dustyRose hover:from-dustyRose hover:to-darkRose text-white font-medium text-sm shadow-md hover:shadow-lg transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed group"
              >
                {isLoading ? (
                  <span className="inline-block w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <span>Đăng nhập</span>
                    <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                  </>
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-blushPink/80" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-white px-3 text-stone-400">hoặc</span>
              </div>
            </div>

            {/* Link to Registration */}
            <div className="text-center text-xs text-stone-500">
              Chưa có tài khoản?{' '}
              <Link to="/register" className="font-semibold text-darkRose hover:underline">
                Đăng ký tài khoản khách hàng
              </Link>
            </div>
          </div>

          {/* Quick Demo Login Helpers for Evaluation */}
          <div className="mt-8 pt-4 border-t border-blushPink/40">
            <div className="flex items-center gap-1.5 text-[11px] font-semibold text-dustyRose uppercase tracking-wider mb-2">
              <Sparkles className="w-3.5 h-3.5" /> Tài khoản Demo kiểm thử:
            </div>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => fillDemo('chutiem', '123456')}
                className="p-2 rounded-xl bg-rose-50 border border-rose-200 hover:bg-rose-100 text-left transition-colors"
              >
                <div className="text-[11px] font-bold text-rose-800">Chủ Tiệm</div>
                <div className="text-[10px] text-stone-500">chutiem</div>
              </button>
              <button
                type="button"
                onClick={() => fillDemo('nhanvien1', '123456')}
                className="p-2 rounded-xl bg-blue-50 border border-blue-200 hover:bg-blue-100 text-left transition-colors"
              >
                <div className="text-[11px] font-bold text-blue-800">Nhân Viên</div>
                <div className="text-[10px] text-stone-500">nhanvien1</div>
              </button>
              <button
                type="button"
                onClick={() => fillDemo('khachhang1', '123456')}
                className="p-2 rounded-xl bg-purple-50 border border-purple-200 hover:bg-purple-100 text-left transition-colors"
              >
                <div className="text-[11px] font-bold text-purple-800">Khách Hàng</div>
                <div className="text-[10px] text-stone-500">khachhang1</div>
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
