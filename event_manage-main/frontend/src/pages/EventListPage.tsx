import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Filter,
  PlusCircle,
  Eye,
  Edit,
  Sparkles,
  Calendar,
  Building,
  Users,
  ChevronRight,
  ArrowUpDown,
} from 'lucide-react';
import { useEvents } from '../contexts/EventContext';
import { useAuth } from '../contexts/AuthContext';
import { statusLabels, formatDate, formatCurrency } from '../utils/helpers';
import { EventStatus } from '../types';

export const EventListPage: React.FC = () => {
  const navigate = useNavigate();
  const { events } = useEvents();
  const { currentUser } = useAuth();

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [unitFilter, setUnitFilter] = useState<string>('ALL');

  // Filter list
  const filteredEvents = events.filter((ev) => {
    const matchSearch =
      ev.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ev.eventCode.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ev.organizingUnit.toLowerCase().includes(searchTerm.toLowerCase());

    const matchStatus =
      statusFilter === 'ALL'
        ? true
        : statusFilter === 'PENDING'
        ? ['FACULTY_REVIEW', 'UNIVERSITY_REVIEW', 'BUDGET_REVIEW', 'FACILITY_REVIEW', 'FINANCE_REVIEW'].includes(ev.status)
        : statusFilter === 'REVISION'
        ? ev.status.includes('REVISION') || ev.status === 'FACILITY_CONFLICT'
        : statusFilter === 'APPROVED'
        ? ['PERMIT_ISSUED', 'FACILITY_RESERVED', 'READY_FOR_EVENT', 'EVENT_IN_PROGRESS'].includes(ev.status)
        : statusFilter === 'COMPLETED'
        ? ev.status === 'COMPLETED'
        : ev.status === statusFilter;

    const matchUnit = unitFilter === 'ALL' || ev.organizingUnit === unitFilter;

    return matchSearch && matchStatus && matchUnit;
  });

  const uniqueUnits = Array.from(new Set(events.map((e) => e.organizingUnit)));

  return (
    <div className="space-y-5">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Hồ sơ Sự kiện</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Danh sách toàn bộ hồ sơ tiếp nhận, phê duyệt và cấp phép tổ chức sự kiện
          </p>
        </div>

        <button
          onClick={() => navigate('/events/create')}
          className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-all cursor-pointer self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Tạo hồ sơ mới</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-2xs flex flex-wrap gap-3 items-center justify-between">
        <div className="flex flex-wrap items-center gap-3 flex-1 min-w-[280px]">
          {/* Search Input */}
          <div className="relative flex-1 min-w-[220px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Tìm kiếm theo mã, tên sự kiện, đơn vị..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-9 pr-3 py-2 text-xs focus:outline-hidden focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            aria-label="Lọc theo trạng thái hồ sơ"
            className="bg-slate-50 border border-slate-200 text-slate-700 text-xs rounded-xl px-3 py-2 focus:outline-hidden focus:border-blue-500 cursor-pointer"
          >
            <option value="ALL">Tất cả trạng thái</option>
            <option value="PENDING">Đang chờ xét duyệt (Các cấp)</option>
            <option value="REVISION">Yêu cầu chỉnh sửa / Trùng lịch</option>
            <option value="APPROVED">Đã cấp phép / Sẵn sàng tổ chức</option>
            <option value="COMPLETED">Đã hoàn tất toàn bộ</option>
            <option value="DRAFT">Bản nháp</option>
            <option value="FACULTY_REVIEW">Chờ BCN Khoa duyệt</option>
            <option value="UNIVERSITY_REVIEW">Chờ Đoàn trường duyệt</option>
            <option value="FACILITY_CONFLICT">Xung đột lịch CSVC</option>
            <option value="FINANCE_REVIEW">Chờ duyệt tài chính KHTC</option>
          </select>

          {/* Unit Filter */}
          <select
            value={unitFilter}
            onChange={(e) => setUnitFilter(e.target.value)}
            aria-label="Lọc theo đơn vị tổ chức"
            className="bg-slate-50 border border-slate-200 text-slate-700 text-xs rounded-xl px-3 py-2 focus:outline-hidden focus:border-blue-500 cursor-pointer max-w-[200px] truncate"
          >
            <option value="ALL">Tất cả đơn vị tổ chức</option>
            {uniqueUnits.map((u) => (
              <option key={u} value={u}>
                {u}
              </option>
            ))}
          </select>
        </div>

        <div className="text-xs text-slate-500 font-medium">
          Tìm thấy <span className="font-bold text-slate-800">{filteredEvents.length}</span> hồ sơ
        </div>
      </div>

      {/* Events Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                <th className="py-3 px-4">Mã hồ sơ</th>
                <th className="py-3 px-4">Tên sự kiện & Đơn vị</th>
                <th className="py-3 px-4">Thời gian</th>
                <th className="py-3 px-4">Địa điểm dự kiến</th>
                <th className="py-3 px-4">Quy mô</th>
                <th className="py-3 px-4">Trạng thái phê duyệt</th>
                <th className="py-3 px-4 text-right">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
              {filteredEvents.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    Không tìm thấy hồ sơ sự kiện phù hợp
                  </td>
                </tr>
              ) : (
                filteredEvents.map((ev) => {
                  const statusInfo = statusLabels[ev.status] || {
                    label: ev.status,
                    color: 'text-slate-700',
                    bg: 'bg-slate-100',
                    border: 'border-slate-200',
                  };

                  return (
                    <tr
                      key={ev.id}
                      className="hover:bg-slate-50/70 transition-colors group cursor-pointer"
                      onClick={() => navigate(`/events/${ev.id}`)}
                    >
                      <td className="py-3.5 px-4 font-mono font-bold text-blue-600 whitespace-nowrap">
                        {ev.eventCode}
                      </td>

                      <td className="py-3.5 px-4 min-w-[240px] max-w-xs">
                        <div className="font-semibold text-slate-900 line-clamp-1 group-hover:text-blue-600 transition-colors">
                          {ev.title}
                        </div>
                        <div className="text-[11px] text-slate-500 mt-0.5 flex items-center gap-1">
                          <Users className="w-3 h-3 text-slate-400" />
                          <span>{ev.organizingUnit}</span>
                        </div>
                      </td>

                      <td className="py-3.5 px-4 whitespace-nowrap text-slate-600">
                        <div className="flex items-center gap-1.5 font-medium">
                          <Calendar className="w-3.5 h-3.5 text-slate-400" />
                          <span>{formatDate(ev.startDate)}</span>
                        </div>
                      </td>

                      <td className="py-3.5 px-4 text-slate-600 max-w-[180px] truncate">
                        <div className="flex items-center gap-1.5">
                          <Building className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                          <span className="truncate">{ev.preferredVenue}</span>
                        </div>
                      </td>

                      <td className="py-3.5 px-4 whitespace-nowrap font-medium text-slate-800">
                        {ev.expectedAttendees} người
                      </td>

                      <td className="py-3.5 px-4 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-semibold border ${statusInfo.bg} ${statusInfo.color} ${statusInfo.border}`}
                        >
                          {statusInfo.label}
                        </span>
                      </td>

                      <td className="py-3.5 px-4 text-right whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            onClick={() => navigate(`/events/${ev.id}`)}
                            className="p-1.5 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors cursor-pointer"
                            title="Xem chi tiết hồ sơ"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => navigate(`/events/${ev.id}/edit`)}
                            className="p-1.5 text-slate-500 hover:text-amber-600 hover:bg-amber-50 rounded-lg transition-colors cursor-pointer"
                            title="Chỉnh sửa hồ sơ"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => navigate(`/ai-review?eventId=${ev.id}`)}
                            className="p-1.5 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors cursor-pointer"
                            title="Rà soát hồ sơ bằng AI"
                          >
                            <Sparkles className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
