import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Logo } from '../components/Logo';
import { User, Lock, Phone, UserCheck, ArrowRight, CheckCircle2 } from 'lucide-react';

export const Register: React.FC = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [hoTen, setHoTen] = useState('');
  const [soDienThoai, setSoDienThoai] = useState('');
  const [tenDangNhap, setTenDangNhap] = useState('');
  const [matKhau, setMatKhau] = useState('');
  const [xacNhanMatKhau, setXacNhanMatKhau] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // 5a. Kiểm tra bỏ trống
    if (!hoTen.trim() || !soDienThoai.trim() || !tenDangNhap.trim() || !matKhau) {
      setError('Vui lòng nhập đầy đủ thông tin');
      return;
    }

    // 5b. Kiểm tra 10 chữ số
    const cleanPhone = soDienThoai.trim();
    if (!/^[0-9]{10}$/.test(cleanPhone)) {
      setError('Số điện thoại không hợp lệ (phải gồm đúng 10 chữ số)');
      return;
    }

    if (matKhau !== xacNhanMatKhau) {
      setError('Mật khẩu xác nhận không khớp');
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      await register({
        hoTen: hoTen.trim(),
        soDienThoai: cleanPhone,
        tenDangNhap: tenDangNhap.trim(),
        matKhau
      });

      setIsSuccess(true);
      setTimeout(() => {
        navigate('/book');
      }, 1500);
    } catch (err: any) {
      setError(err.message || 'Đăng ký tài khoản thất bại, vui lòng thử lại');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#FDF5F6] flex items-center justify-center p-4 sm:p-6 lg:p-8 font-montserrat">
      <div className="fixed inset-0 pointer-events-none opacity-40 bg-[radial-gradient(#F5DDE2_1px,transparent_1px)] [background-size:16px_16px]"></div>

      <div className="w-full max-w-lg bg-white rounded-3xl shadow-[0_20px_60px_-15px_rgba(201,127,142,0.2)] border border-[#F5DDE2] p-6 sm:p-10 relative z-10">
        <div className="text-center mb-6">
          <Logo size="md" showSubtitle={false} />
          <h2 className="font-playfair text-2xl font-semibold text-textCharcoal mt-2">
            Đăng ký tài khoản
          </h2>
          <p className="text-xs text-stone-500 mt-1 font-medium">
            Tạo tài khoản để đặt lịch làm móng trực tuyến nhanh chóng
          </p>
        </div>

        {error && (
          <div className="mb-5 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium animate-shake">
            {error}
          </div>
        )}

        {isSuccess ? (
          <div className="py-8 text-center space-y-3 animate-fadeIn">
            <CheckCircle2 className="w-16 h-16 text-emerald-500 mx-auto animate-bounce" />
            <h3 className="font-playfair text-xl font-semibold text-textCharcoal">
              Đăng ký tài khoản thành công!
            </h3>
            <p className="text-sm text-stone-500">
              Đang chuyển hướng bạn đến trang đặt lịch...
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-textCharcoal mb-1">
                Họ và tên của bạn <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-stone-400">
                  <UserCheck className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  value={hoTen}
                  onChange={(e) => setHoTen(e.target.value)}
                  placeholder="Ví dụ: Nguyễn Thùy Linh"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-blushPink bg-softPink/20 text-sm focus:outline-none focus:border-rosePink focus:bg-white focus:ring-2 focus:ring-rosePink/20"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-textCharcoal mb-1">
                Số điện thoại (10 chữ số) <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-stone-400">
                  <Phone className="w-4 h-4" />
                </div>
                <input
                  type="tel"
                  maxLength={10}
                  value={soDienThoai}
                  onChange={(e) => setSoDienThoai(e.target.value.replace(/\D/g, ''))}
                  placeholder="Ví dụ: 0905123456"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-blushPink bg-softPink/20 text-sm focus:outline-none focus:border-rosePink focus:bg-white focus:ring-2 focus:ring-rosePink/20"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-textCharcoal mb-1">
                Tên đăng nhập <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-stone-400">
                  <User className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  value={tenDangNhap}
                  onChange={(e) => setTenDangNhap(e.target.value)}
                  placeholder="Nhập tên đăng nhập"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-blushPink bg-softPink/20 text-sm focus:outline-none focus:border-rosePink focus:bg-white focus:ring-2 focus:ring-rosePink/20"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-textCharcoal mb-1">
                  Mật khẩu <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-stone-400">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type="password"
                    value={matKhau}
                    onChange={(e) => setMatKhau(e.target.value)}
                    placeholder="Mật khẩu"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-blushPink bg-softPink/20 text-sm focus:outline-none focus:border-rosePink focus:bg-white focus:ring-2 focus:ring-rosePink/20"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-textCharcoal mb-1">
                  Xác nhận <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-stone-400">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type="password"
                    value={xacNhanMatKhau}
                    onChange={(e) => setXacNhanMatKhau(e.target.value)}
                    placeholder="Nhập lại"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-blushPink bg-softPink/20 text-sm focus:outline-none focus:border-rosePink focus:bg-white focus:ring-2 focus:ring-rosePink/20"
                  />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-2 py-3 px-6 rounded-xl bg-gradient-to-r from-rosePink to-dustyRose hover:from-dustyRose hover:to-darkRose text-white font-medium text-sm shadow-md transition-all flex items-center justify-center gap-2 disabled:opacity-70"
            >
              {isLoading ? (
                <span className="inline-block w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <span>Tạo tài khoản</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        )}

        <div className="text-center text-xs text-stone-500 mt-6 pt-4 border-t border-blushPink/50">
          Đã có tài khoản?{' '}
          <Link to="/login" className="font-semibold text-darkRose hover:underline">
            Đăng nhập ngay
          </Link>
        </div>
      </div>
    </div>
  );
};
