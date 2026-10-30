import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CalendarDays,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Building2,
  Receipt,
  FileCheck,
  PlusCircle,
  ArrowRight,
  TrendingUp,
  Sparkles,
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useAuth } from '../contexts/AuthContext';
import { useEvents } from '../contexts/EventContext';
import { roleNames, formatDateTime, statusLabels } from '../utils/helpers';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const { events } = useEvents();

  // Metrics
  const totalEvents = events.length;
  const pendingApproval = events.filter((e) =>
    ['FACULTY_REVIEW', 'UNIVERSITY_REVIEW', 'BUDGET_REVIEW', 'FACILITY_REVIEW', 'FINANCE_REVIEW'].includes(e.status)
  ).length;
  const needsRevision = events.filter((e) => e.status.includes('REVISION') || e.status === 'FACILITY_CONFLICT').length;
  const readyOrInProgress = events.filter((e) => ['READY_FOR_EVENT', 'EVENT_IN_PROGRESS', 'PERMIT_ISSUED'].includes(e.status)).length;
  const completed = events.filter((e) => e.status === 'COMPLETED').length;

  // Chart data: Distribution by status groups
  const statusGroupData = [
    { name: 'Đang duyệt', count: pendingApproval, color: '#f59e0b' },
    { name: 'Yêu cầu sửa', count: needsRevision, color: '#f97316' },
    { name: 'Đã cấp phép / Sẵn sàng', count: readyOrInProgress, color: '#0ea5e9' },
    { name: 'Hoàn tất', count: completed, color: '#10b981' },
    { name: 'Khác (Nháp/Nghiệm thu)', count: totalEvents - (pendingApproval + needsRevision + readyOrInProgress + completed), color: '#8b5cf6' },
  ];

  // Chart data: Monthly events
  const monthlyData = [
    { month: 'T7', count: 2 },
    { month: 'T8', count: 3 },
    { month: 'T9', count: 5 },
    { month: 'T10', count: 9 },
    { month: 'T11', count: 6 },
    { month: 'T12', count: 4 },
  ];

  // Recent workflow events
  const recentHistory = events
    .flatMap((e) =>
      e.history.map((h) => ({
        ...h,
        eventTitle: e.title,
        eventCode: e.eventCode,
        eventId: e.id,
      }))
    )
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 7);

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-indigo-950 rounded-2xl p-6 text-white shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-500/20 text-blue-300 border border-blue-400/30">
              {roleNames[currentUser.role]}
            </span>
            <span className="text-xs text-slate-400 font-medium">Trường Đại học Kinh tế – Đại học Đà Nẵng</span>
          </div>
          <h1 className="text-xl md:text-2xl font-bold tracking-tight">
            Xin chào, {currentUser.fullName}!
          </h1>
          <p className="text-slate-300 text-xs md:text-sm mt-1 max-w-xl">
            Hệ thống quản lý quy trình tiếp nhận, thẩm định đa cấp, mượn cơ sở vật chất và quyết toán sự kiện sinh viên.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/events/create')}
            className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold shadow-md transition-all cursor-pointer"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Tạo sự kiện mới</span>
          </button>
          <button
            onClick={() => navigate('/ai-review')}
            className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-200 border border-indigo-400/30 rounded-xl text-xs font-semibold transition-all cursor-pointer"
          >
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span>Rà soát AI</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-slate-500">Tổng số hồ sơ</div>
            <div className="text-2xl font-bold text-slate-900 mt-1">{totalEvents}</div>
            <div className="text-[11px] text-emerald-600 flex items-center gap-1 mt-1 font-semibold">
              <TrendingUp className="w-3 h-3" /> +3 sự kiện tháng này
            </div>
          </div>
          <div className="w-11 h-11 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <CalendarDays className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-slate-500">Đang chờ xét duyệt</div>
            <div className="text-2xl font-bold text-amber-600 mt-1">{pendingApproval}</div>
            <div className="text-[11px] text-slate-400 mt-1">Qua 3 cấp thẩm định</div>
          </div>
          <div className="w-11 h-11 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
            <Clock className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-slate-500">Yêu cầu chỉnh sửa / Trùng lịch</div>
            <div className="text-2xl font-bold text-orange-600 mt-1">{needsRevision}</div>
            <div className="text-[11px] text-orange-700 mt-1 font-medium">Cần xử lý kịp thời</div>
          </div>
          <div className="w-11 h-11 rounded-xl bg-orange-50 text-orange-600 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-slate-500">Đã hoàn tất toàn bộ</div>
            <div className="text-2xl font-bold text-emerald-600 mt-1">{completed}</div>
            <div className="text-[11px] text-emerald-700 mt-1 font-medium">Nghiệm thu & quyết toán</div>
          </div>
          <div className="w-11 h-11 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Status Distribution */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs">
          <h2 className="text-sm font-bold text-slate-800 mb-4 flex items-center justify-between">
            <span>Phân bố trạng thái hồ sơ</span>
            <span className="text-xs font-normal text-slate-400">Thời gian thực</span>
          </h2>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusGroupData}
                  dataKey="count"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={75}
                  innerRadius={45}
                  paddingAngle={3}
                >
                  {statusGroupData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-2 pt-3 border-t border-slate-100 text-[11px]">
            {statusGroupData.map((item) => (
              <div key={item.name} className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                <span className="text-slate-600 truncate">{item.name}:</span>
                <span className="font-bold text-slate-800">{item.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Monthly Events Bar Chart */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs lg:col-span-2">
          <h2 className="text-sm font-bold text-slate-800 mb-4 flex items-center justify-between">
            <span>Số lượng sự kiện theo tháng</span>
            <span className="text-xs font-normal text-slate-400">Năm học 2024 - 2025</span>
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="month" stroke="#94a3b8" fontSize={12} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} allowDecimals={false} />
                <Tooltip cursor={{ fill: '#f1f5f9' }} />
                <Bar dataKey="count" fill="#3b82f6" radius={[6, 6, 0, 0]} name="Số sự kiện" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Two Columns: Recent Workflow Activity & Priority Action Queue */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity Feed */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-slate-800">Nhật ký xử lý gần đây</h2>
            <button
              onClick={() => navigate('/events')}
              className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1 cursor-pointer"
            >
              Xem tất cả <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3.5">
            {recentHistory.map((h) => (
              <div
                key={h.id}
                onClick={() => navigate(`/events/${h.eventId}`)}
                className="flex items-start gap-3 p-2.5 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer border border-transparent hover:border-slate-100"
              >
                <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                  {h.actorName?.charAt(0) || 'U'}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800 truncate">{h.actorName}</span>
                    <span className="text-[10px] text-slate-400">{formatDateTime(h.timestamp)}</span>
                  </div>
                  <div className="text-xs text-blue-700 font-medium line-clamp-1">
                    {h.eventCode} — {h.eventTitle}
                  </div>
                  <div className="text-xs text-slate-600 mt-0.5">{h.action}</div>
                  {h.comments && (
                    <div className="text-[11px] text-slate-500 italic bg-slate-50 p-1.5 rounded-lg mt-1 border border-slate-100">
                      "{h.comments}"
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Nav / Key Actions */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-bold text-slate-800 mb-4">Phím tắt thao tác nhanh</h2>
            <div className="grid grid-cols-2 gap-3">
              <div
                onClick={() => navigate('/events/create')}
                className="p-4 rounded-xl border border-blue-200 bg-blue-50/60 hover:bg-blue-100/70 transition-all cursor-pointer"
              >
                <PlusCircle className="w-6 h-6 text-blue-600 mb-2" />
                <div className="font-bold text-xs text-blue-900">Nộp hồ sơ sự kiện</div>
                <div className="text-[11px] text-blue-700 mt-0.5">Biểu mẫu 5 bước chuẩn hóa</div>
              </div>

              <div
                onClick={() => navigate('/approvals')}
                className="p-4 rounded-xl border border-amber-200 bg-amber-50/60 hover:bg-amber-100/70 transition-all cursor-pointer"
              >
                <Clock className="w-6 h-6 text-amber-600 mb-2" />
                <div className="font-bold text-xs text-amber-900">Hàng đợi xét duyệt</div>
                <div className="text-[11px] text-amber-700 mt-0.5">{pendingApproval} hồ sơ chờ xử lý</div>
              </div>

              <div
                onClick={() => navigate('/calendar')}
                className="p-4 rounded-xl border border-purple-200 bg-purple-50/60 hover:bg-purple-100/70 transition-all cursor-pointer"
              >
                <Building2 className="w-6 h-6 text-purple-600 mb-2" />
                <div className="font-bold text-xs text-purple-900">Lịch hội trường</div>
                <div className="text-[11px] text-purple-700 mt-0.5">Kiểm tra trùng phòng & CSVC</div>
              </div>

              <div
                onClick={() => navigate('/settlements')}
                className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/60 hover:bg-emerald-100/70 transition-all cursor-pointer"
              >
                <Receipt className="w-6 h-6 text-emerald-600 mb-2" />
                <div className="font-bold text-xs text-emerald-900">Quyết toán tài chính</div>
                <div className="text-[11px] text-emerald-700 mt-0.5">Hóa đơn & chứng từ KHTC</div>
              </div>
            </div>
          </div>

          <div className="mt-4 p-3.5 rounded-xl bg-slate-900 text-white flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              <div>
                <div className="text-xs font-bold">Trợ lý AI Đánh giá Hồ sơ</div>
                <div className="text-[10px] text-slate-400">Tự động phát hiện thiếu sót & đề xuất phòng</div>
              </div>
            </div>
            <button
              onClick={() => navigate('/ai-review')}
              className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 rounded-lg text-xs font-semibold cursor-pointer"
            >
              Mở ngay
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
