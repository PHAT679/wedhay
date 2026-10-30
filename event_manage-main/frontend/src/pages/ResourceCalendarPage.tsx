import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Calendar as CalendarIcon,
  Building,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
  Clock,
  CheckCircle2,
  Filter,
} from 'lucide-react';
import { useEvents } from '../contexts/EventContext';
import { formatDateTime, formatDate } from '../utils/helpers';

export const ResourceCalendarPage: React.FC = () => {
  const navigate = useNavigate();
  const { events, facilities } = useEvents();

  const [selectedFacility, setSelectedFacility] = useState<string>('ALL');
  const [currentMonth, setCurrentMonth] = useState<Date>(new Date(2024, 10, 1)); // November 2024 for rich sample data

  // Extract all confirmed or pending bookings
  const bookings = events
    .filter((e) => e.booking && e.status !== 'CANCELLED' && !e.status.includes('REJECTED'))
    .map((e) => ({
      ...e.booking!,
      eventId: e.id,
      eventCode: e.eventCode,
      eventTitle: e.title,
      organizingUnit: e.organizingUnit,
      eventStatus: e.status,
    }))
    .filter((b) => selectedFacility === 'ALL' || b.facilityId === selectedFacility);

  const prevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Lịch Cơ sở vật chất & Hội trường</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Theo dõi trực quan lịch đặt phòng, sảnh, sân thể thao và phát hiện xung đột thời gian thực
          </p>
        </div>

        {/* Facility Filter */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={selectedFacility}
            onChange={(e) => setSelectedFacility(e.target.value)}
            aria-label="Lọc theo hội trường hoặc phòng"
            className="bg-white border border-slate-200 text-xs rounded-xl px-3 py-2 font-medium focus:outline-hidden focus:border-blue-500 cursor-pointer shadow-2xs"
          >
            <option value="ALL">Tất cả hội trường & phòng</option>
            {facilities.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name} ({f.capacity} chỗ)
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Month Navigator Header */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 flex items-center justify-between shadow-2xs">
        <div className="flex items-center gap-2">
          <CalendarIcon className="w-5 h-5 text-blue-600" />
          <span className="text-base font-bold text-slate-800">
            Tháng {currentMonth.getMonth() + 1} / {currentMonth.getFullYear()}
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={prevMonth}
            aria-label="Tháng trước"
            className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 cursor-pointer text-slate-600"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            onClick={() => setCurrentMonth(new Date())}
            className="px-3 py-1.5 text-xs font-semibold rounded-lg border border-slate-200 hover:bg-slate-50 cursor-pointer text-slate-700"
          >
            Hôm nay
          </button>
          <button
            onClick={nextMonth}
            aria-label="Tháng sau"
            className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 cursor-pointer text-slate-600"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Bookings Timeline / Cards List */}
      <div className="space-y-4">
        <h2 className="text-sm font-bold text-slate-800">Danh sách các khung giờ đã đăng ký:</h2>

        {bookings.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center text-xs text-slate-400">
            Không có lịch đặt nào cho hội trường / thời gian này
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {bookings.map((b) => {
              const isConflict = b.status === 'CONFLICT';
              const isConfirmed = b.status === 'CONFIRMED';

              return (
                <div
                  key={b.id}
                  onClick={() => navigate(`/events/${b.eventId}`)}
                  className={`bg-white rounded-2xl p-5 border shadow-2xs transition-all hover:shadow-md cursor-pointer flex flex-col justify-between ${
                    isConflict
                      ? 'border-rose-300 ring-2 ring-rose-100 bg-rose-50/20'
                      : isConfirmed
                      ? 'border-emerald-200'
                      : 'border-amber-200'
                  }`}
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                        {b.eventCode}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase border ${
                          isConflict
                            ? 'bg-rose-100 text-rose-800 border-rose-300'
                            : isConfirmed
                            ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                            : 'bg-amber-100 text-amber-800 border-amber-300'
                        }`}
                      >
                        {isConflict ? 'Xung đột lịch' : isConfirmed ? 'Đã giữ chỗ' : 'Chờ xác nhận'}
                      </span>
                    </div>

                    <h3 className="text-sm font-bold text-slate-900 line-clamp-2">{b.eventTitle}</h3>
                    <div className="text-xs text-slate-500 font-medium">{b.organizingUnit}</div>

                    <div className="pt-2 border-t border-slate-100 space-y-1.5 text-xs text-slate-600">
                      <div className="flex items-center gap-1.5">
                        <Building className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                        <span className="font-semibold text-slate-800 truncate">{b.facilityName}</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                        <span>{formatDateTime(b.startTime)}</span>
                      </div>
                      <div className="text-[11px] text-slate-400 pl-5">đến {formatDateTime(b.endTime)}</div>
                    </div>

                    {isConflict && b.conflictDetails && (
                      <div className="p-2.5 bg-rose-50 border border-rose-200 rounded-xl text-[11px] text-rose-700 flex items-start gap-1.5 mt-2">
                        <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0 mt-0.5" />
                        <div>{b.conflictDetails}</div>
                      </div>
                    )}
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-blue-600 font-bold text-right flex items-center justify-end gap-1">
                    Xem chi tiết hồ sơ & đổi lịch →
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
