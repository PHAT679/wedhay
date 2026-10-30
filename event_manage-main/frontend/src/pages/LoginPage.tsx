import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GraduationCap, ArrowRight, Lock, Mail, ShieldCheck } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { roleNames } from '../utils/helpers';
import { UserRole } from '../types';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { loginWithEmail, allUsers } = useAuth();

  const [email, setEmail] = useState(new URLSearchParams(window.location.search).get('email') || 'btc1@eventflow.vn');
  const [password, setPassword] = useState('123456');
  const [error, setError] = useState('');

  const [pending, setPending] = useState(false);
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (pending) return;
    setPending(true); setError('');
    try { await loginWithEmail(email, password); navigate('/'); }
    catch (error) { setError(error instanceof Error ? error.message : 'Không kết nối được máy chủ. Hãy chạy CHAY_FULLSTACK.bat.'); }
    finally { setPending(false); }
  };
  const handleQuickLogin = (role: UserRole) => {
    const user = allUsers.find(u => u.role === role);
    if (user) setEmail(user.email);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Brand */}
        <div className="text-center space-y-2">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 text-white flex items-center justify-center mx-auto shadow-lg shadow-blue-500/30">
            <GraduationCap className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">EventFlow</h1>
          <p className="text-xs text-slate-300">
            Hệ thống Quản lý Quy trình Tổ chức Sự kiện Sinh viên
          </p>
          <div className="text-[11px] text-blue-400 font-semibold">
            Trường Đại học Kinh tế – Đại học Đà Nẵng
          </div>
        </div>

        {/* Login Box */}
        <div className="bg-white rounded-3xl p-6 shadow-2xl space-y-5">
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Email đăng nhập:</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    setError('');
                  }}
                  className="w-full text-xs pl-9 pr-3 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-hidden focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Mật khẩu:</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full text-xs pl-9 pr-3 py-2.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-hidden focus:border-blue-500"
                />
              </div>
            </div>

            {error && <div className="text-xs text-rose-500 font-medium">{error}</div>}

            <button
              type="submit" disabled={pending}
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-md transition-all cursor-pointer flex items-center justify-center gap-2"
            >
              <span>Đăng nhập hệ thống</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Quick Demo Access Bar */}
          <div className="pt-4 border-t border-slate-100 space-y-2">
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 text-center">
              Chọn email tài khoản mẫu, sau đó nhập mật khẩu:
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              {allUsers.slice(0, 6).map((u) => (
                <button
                  key={u.id}
                  type="button"
                  onClick={() => handleQuickLogin(u.role)}
                  className="p-2 rounded-xl border border-slate-200 hover:border-blue-300 hover:bg-blue-50/60 text-left transition-all cursor-pointer group"
                >
                  <div className="font-bold text-slate-800 text-[11px] group-hover:text-blue-700 truncate">
                    {u.fullName}
                  </div>
                  <div className="text-[10px] text-slate-500">{roleNames[u.role].split('(')[0]}</div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
