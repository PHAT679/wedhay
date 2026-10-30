import React from 'react';
import { Users, Shield, Plus, Mail, Phone, Building } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { roleNames } from '../utils/helpers';

export const UserManagementPage: React.FC = () => {
  const { allUsers, currentUser } = useAuth();

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Quản trị Người dùng & Phân quyền</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Danh sách tài khoản kiểm thử và phân cấp quyền thẩm định theo quy chế Đại học Kinh tế
          </p>
        </div>

        <button
          onClick={() => alert('Thêm người dùng mới vào hệ thống LDAP/SSO')}
          className="flex items-center gap-1.5 px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold cursor-pointer shadow-xs"
        >
          <Plus className="w-4 h-4" /> Thêm tài khoản
        </button>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 text-[11px] font-bold text-slate-500 uppercase border-b border-slate-200">
                <th className="py-3 px-4">Họ và tên</th>
                <th className="py-3 px-4">Email</th>
                <th className="py-3 px-4">Vai trò nghiệp vụ</th>
                <th className="py-3 px-4">Đơn vị / Khoa</th>
                <th className="py-3 px-4">Số điện thoại</th>
                <th className="py-3 px-4 text-center">Trạng thái</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {allUsers.filter((u) => Boolean(u.role)).length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-400">
                    Không có người dùng nào được phân quyền trong hệ thống
                  </td>
                </tr>
              ) : (
                allUsers
                  .filter((u) => Boolean(u.role))
                  .map((u) => (
                    <tr key={u.id} className="hover:bg-slate-50/70">
                      <td className="py-3.5 px-4 font-bold text-slate-900 flex items-center gap-2">
                        <div className="w-7 h-7 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold shrink-0">
                          {u.fullName.charAt(0)}
                        </div>
                        <span>{u.fullName}</span>
                      </td>
                      <td className="py-3.5 px-4 text-slate-600 font-mono">{u.email}</td>
                      <td className="py-3.5 px-4">
                        <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                          {roleNames[u.role] || u.role}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-slate-700">{u.department}</td>
                      <td className="py-3.5 px-4 text-slate-500">{u.phone}</td>
                      <td className="py-3.5 px-4 text-center">
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                          Đang hoạt động
                        </span>
                      </td>
                    </tr>
                  ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
