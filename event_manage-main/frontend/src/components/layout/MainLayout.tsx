import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { Toast } from '../common/Toast';

import { useAuth } from '../../contexts/AuthContext';
import { useEvents } from '../../contexts/EventContext';

export const MainLayout: React.FC = () => {
  const auth = useAuth();
  const { loading, syncError, saving, refresh, importLegacy } = useEvents();
  if (auth.loading) return <div className="p-8">Đang kiểm tra đăng nhập...</div>;
  if (!auth.authenticated) return <Navigate to="/login" replace />;
  const downloadLegacy = () => {
    const raw = localStorage.getItem('eventflow_events_v1') || '[]';
    const url = URL.createObjectURL(new Blob([raw], { type: 'application/json' }));
    const link = document.createElement('a'); link.href = url; link.download = 'eventflow-ho-so-cu.json'; link.click(); URL.revokeObjectURL(url);
  };
  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Topbar />
        <main className="flex-1 p-6 overflow-y-auto">
          {syncError && <div role="alert" className="mb-4 p-3 bg-red-50 text-red-700 rounded-xl">Không đồng bộ được: {syncError} <button onClick={() => void refresh()}>Thử lại</button></div>}
          {localStorage.getItem('eventflow_events_v1') && <details className="mb-4 p-3 bg-amber-50 rounded-xl text-sm"><summary>Hồ sơ cũ trong trình duyệt này vẫn được giữ an toàn</summary><p>Nhập hồ sơ thuộc tài khoản đang đăng nhập thành bản nháp trên máy chủ để kiểm tra và nộp lại. Lịch sử gốc được lưu bản sao; nhập lại không tạo trùng.</p><button onClick={downloadLegacy} className="mr-4 underline">Tải bản sao hồ sơ cũ</button><button disabled={saving} onClick={() => void importLegacy()} className="underline">Nhập hồ sơ cũ lên máy chủ</button></details>}
          {saving && <div role="status" className="mb-3 text-blue-700">Đang lưu lên máy chủ...</div>}
          {loading ? <div>Đang tải dữ liệu dùng chung từ máy chủ...</div> : <Outlet />}
        </main>
      </div>
      <Toast />
    </div>
  );
};
