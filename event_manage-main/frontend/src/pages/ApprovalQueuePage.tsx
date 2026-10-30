import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CheckSquare,
  Clock,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Eye,
  Calendar,
  Building,
  User,
  ArrowRight,
} from 'lucide-react';
import { useEvents } from '../contexts/EventContext';
import { useAuth } from '../contexts/AuthContext';
import { roleNames, formatDate, statusLabels } from '../utils/helpers';

export const ApprovalQueuePage: React.FC = () => {
  const navigate = useNavigate();
  const { events, transitionEvent } = useEvents();
  const { currentUser } = useAuth();

  // Filter events pending current user's approval role
  const queueEvents = events.filter((e) => {
    if (currentUser.role === 'BCN_KHOA') return e.status === 'FACULTY_REVIEW';
    if (currentUser.role === 'DOAN_TRUONG') return e.status === 'UNIVERSITY_REVIEW' || e.status === 'BUDGET_REVIEW' || e.status === 'FACULTY_APPROVED';
    if (currentUser.role === 'CSVC') return e.status === 'FACILITY_REVIEW' || e.status === 'FACILITY_RETURN_PENDING' || e.status === 'PERMIT_ISSUED';
    if (currentUser.role === 'KHTC') return e.status === 'FINANCE_REVIEW' || e.status === 'FINANCE_APPROVAL_PENDING';
    if (currentUser.role === 'BTC') return e.status.includes('REVISION_REQUESTED') || e.status === 'FACILITY_CONFLICT';
    return true; // Admin sees all
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800">
              {roleNames[currentUser.role]}
            </span>
          </div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight mt-1">Hàng đợi xét duyệt & Thẩm định</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Danh sách các hồ sơ sự kiện đang chờ đơn vị bạn thẩm định, phê duyệt hoặc kiểm tra
          </p>
        </div>
      </div>

      {/* Queue Cards / Table */}
      {queueEvents.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-3">
          <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-slate-800">Tuyệt vời! Không có hồ sơ nào đang chờ duyệt</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Tất cả các hồ sơ gửi đến vai trò {roleNames[currentUser.role]} đã được xử lý xong.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {queueEvents.map((ev) => {
            const statusInfo = statusLabels[ev.status];
            return (
              <div
                key={ev.id}
                className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs hover:shadow-md transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                      {ev.eventCode}
                    </span>
                    <span
                      className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full border ${statusInfo?.bg} ${statusInfo?.color} ${statusInfo?.border}`}
                    >
                      {statusInfo?.label}
                    </span>
                    <span className="text-xs text-slate-400">• Đơn vị: {ev.organizingUnit}</span>
                  </div>

                  <h3
                    onClick={() => navigate(`/events/${ev.id}`)}
                    className="text-base font-bold text-slate-900 hover:text-blue-600 transition-colors cursor-pointer"
                  >
                    {ev.title}
                  </h3>

                  <p className="text-xs text-slate-600 line-clamp-2">{ev.objectives || ev.description}</p>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 pt-1">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      {formatDate(ev.startDate)}
                    </span>
                    <span className="flex items-center gap-1">
                      <Building className="w-3.5 h-3.5 text-slate-400" />
                      {ev.preferredVenue}
                    </span>
                    <span className="flex items-center gap-1">
                      <User className="w-3.5 h-3.5 text-slate-400" />
                      {ev.contactPerson}
                    </span>
                  </div>
                </div>

                {/* Quick Action buttons */}
                <div className="flex flex-wrap md:flex-col items-end gap-2 shrink-0 border-t md:border-t-0 md:border-l border-slate-100 pt-3 md:pt-0 md:pl-5">
                  <button
                    onClick={() => navigate(`/events/${ev.id}`)}
                    className="flex items-center gap-1.5 px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold cursor-pointer shadow-xs"
                  >
                    <Eye className="w-4 h-4" /> Xem hồ sơ & Duyệt
                  </button>

                  {currentUser.role === 'BCN_KHOA' && ev.status === 'FACULTY_REVIEW' && (
                    <button
                      onClick={() =>
                        transitionEvent(ev.id, 'BCN Khoa duyệt hồ sơ', 'FACULTY_APPROVED', 'Đồng ý nội dung')
                      }
                      className="flex items-center gap-1 px-3 py-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 rounded-lg text-xs font-semibold cursor-pointer"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" /> Duyệt nhanh
                    </button>
                  )}

                  {currentUser.role === 'DOAN_TRUONG' &&
                    (ev.status === 'FACULTY_APPROVED' || ev.status === 'UNIVERSITY_REVIEW') && (
                      <button
                        onClick={() =>
                          transitionEvent(
                            ev.id,
                            'Đoàn trường cấp phép tổ chức',
                            'PERMIT_ISSUED',
                            'Cấp phép tổ chức chính thức'
                          )
                        }
                        className="flex items-center gap-1 px-3 py-1.5 bg-teal-50 text-teal-700 hover:bg-teal-100 border border-teal-200 rounded-lg text-xs font-semibold cursor-pointer"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" /> Cấp phép nhanh
                      </button>
                    )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
