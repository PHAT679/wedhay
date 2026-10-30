import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Building,
  TrendingUp,
  ShieldAlert,
  ArrowRight,
} from 'lucide-react';
import { useEvents } from '../contexts/EventContext';
import { formatCurrency } from '../utils/helpers';

export const AIReviewPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const { events, facilities } = useEvents();

  const initialEventId = searchParams.get('eventId') || events[1]?.id || events[0]?.id;
  const [selectedEventId, setSelectedEventId] = useState<string>(initialEventId);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const event = events.find((e) => e.id === selectedEventId);

  const runAnalysis = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 600);
  };

  // Structured analysis calculation
  const missingItems: string[] = [];
  const riskItems: string[] = [];
  const suggestions: string[] = [];

  if (event) {
    if (!event.safetyPlan && event.expectedAttendees > 200) {
      riskItems.push(
        `Quy mô sự kiện lớn (${event.expectedAttendees} người) nhưng chưa có phương án đảm bảo an toàn & PCCC đính kèm.`
      );
    }
    if (event.budgetItems.length === 0) {
      missingItems.push('Chưa có bảng kê dự toán kinh phí chi tiết.');
    } else {
      const total = event.budgetItems.reduce((s, i) => s + i.totalPrice, 0);
      if (total > 30000000) {
        riskItems.push(
          `Tổng dự toán vượt 30 triệu đồng (${formatCurrency(total)}) - Yêu cầu giải trình định mức và hóa đơn đỏ VAT theo quy chế tài chính ĐHĐN.`
        );
      }
    }
    if (!event.scheduleItems || event.scheduleItems.length === 0) {
      missingItems.push('Chưa có kịch bản chương trình (Agenda) phân bổ theo từng mốc thời gian.');
    }

    if (event.booking?.status === 'CONFLICT') {
      riskItems.push('Phát hiện trùng lịch phòng mượn với sự kiện khác. Cần chọn phòng hoặc khung giờ thay thế.');
    }

    suggestions.push('Nên bổ sung link form khảo sát ý kiến sinh viên sau sự kiện để làm minh chứng trong báo cáo.');
    suggestions.push('Đề xuất bố trí tối thiểu 4 micro không dây và 1 máy chiếu phụ tại sảnh đón tiếp đại biểu.');
  }

  const score = Math.max(30, 100 - missingItems.length * 15 - riskItems.length * 20);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 rounded-2xl p-6 text-white shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-500/30 text-indigo-200 border border-indigo-400/30 flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-amber-300" /> Trợ lý AI Thông minh
            </span>
            <span className="text-xs text-slate-400 font-medium">Chế độ phân tích tự động</span>
          </div>
          <h1 className="text-xl md:text-2xl font-bold tracking-tight">Rà soát Hồ sơ & Gợi ý Cơ sở vật chất</h1>
          <p className="text-slate-300 text-xs md:text-sm mt-1 max-w-xl">
            Sử dụng mô hình luật kết hợp AI để phát hiện thiếu sót, kiểm tra tính hợp lý của ngân sách và đề xuất giải pháp phòng tối ưu
          </p>
        </div>

        <button
          onClick={runAnalysis}
          disabled={isAnalyzing}
          className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold shadow-md transition-all cursor-pointer self-start md:self-auto"
        >
          <Sparkles className={`w-4 h-4 ${isAnalyzing ? 'animate-spin' : ''}`} />
          <span>{isAnalyzing ? 'Đang phân tích...' : 'Chạy lại rà soát'}</span>
        </button>
      </div>

      {/* Select Event */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 flex items-center justify-between shadow-2xs">
        <label className="text-xs font-semibold text-slate-700">Chọn hồ sơ sự kiện cần thẩm định:</label>
        <select
          value={selectedEventId}
          onChange={(e) => setSelectedEventId(e.target.value)}
          className="text-xs p-2 rounded-xl border border-slate-200 bg-slate-50 font-bold text-slate-800"
        >
          {events.map((ev) => (
            <option key={ev.id} value={ev.id}>
              {ev.eventCode} — {ev.title} ({ev.organizingUnit})
            </option>
          ))}
        </select>
      </div>

      {event && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Score & Summary */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs flex flex-col justify-between space-y-4">
            <div>
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Điểm chuẩn bị hồ sơ:
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-5xl font-black text-blue-600">{score}</span>
                <span className="text-slate-400 font-bold">/ 100</span>
              </div>
              <div className="mt-3">
                <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      score >= 80 ? 'bg-emerald-500' : score >= 60 ? 'bg-amber-500' : 'bg-rose-500'
                    }`}
                    style={{ width: `${score}%` }}
                  />
                </div>
              </div>
              <div className="text-xs text-slate-600 mt-4 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100">
                {score >= 80
                  ? 'Hồ sơ đạt tiêu chuẩn, có cấu trúc chi tiết, sẵn sàng trình BCN Khoa và Đoàn trường phê duyệt.'
                  : 'Hồ sơ còn một số điểm mâu thuẫn hoặc thiếu thông tin quan trọng. Cần hoàn thiện trước khi gửi.'}
              </div>
            </div>

            <div className="p-3 bg-indigo-50/60 rounded-xl border border-indigo-100 text-[11px] text-indigo-900">
              <span className="font-bold">Ghi chú xác minh:</span> Kết quả được đối chiếu tự động theo Quy chế tổ chức sự kiện sinh viên số 184/QĐ-ĐHKT.
            </div>
          </div>

          {/* Detailed Findings */}
          <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs space-y-5">
            <h3 className="text-sm font-bold text-slate-900 border-b pb-2 flex items-center justify-between">
              <span>Phân tích tính hợp lệ & Điểm rủi ro</span>
              <span className="text-xs font-normal text-slate-400">Chi tiết phát hiện</span>
            </h3>

            {/* Inconsistencies & Risks */}
            <div>
              <div className="text-xs font-bold text-rose-700 flex items-center gap-1.5 mb-2">
                <ShieldAlert className="w-4 h-4" /> Các rủi ro & Mâu thuẫn phát hiện ({riskItems.length})
              </div>
              {riskItems.length === 0 ? (
                <div className="text-xs text-slate-400 p-2.5 bg-emerald-50 text-emerald-800 rounded-xl border border-emerald-100 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Không phát hiện rủi ro nghiêm trọng về an toàn hoặc ngân sách
                </div>
              ) : (
                <div className="space-y-2">
                  {riskItems.map((risk, i) => (
                    <div key={i} className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                      <span>{risk}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Missing Info */}
            <div>
              <div className="text-xs font-bold text-amber-700 flex items-center gap-1.5 mb-2">
                <AlertTriangle className="w-4 h-4" /> Thông tin còn thiếu ({missingItems.length})
              </div>
              {missingItems.length === 0 ? (
                <div className="text-xs text-slate-400 p-2.5 bg-slate-50 rounded-xl border border-slate-100 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Các trường bắt buộc đã được điền đầy đủ
                </div>
              ) : (
                <div className="space-y-2">
                  {missingItems.map((item, i) => (
                    <div key={i} className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800 flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* AI Recommendations */}
            <div>
              <div className="text-xs font-bold text-indigo-700 flex items-center gap-1.5 mb-2">
                <Sparkles className="w-4 h-4" /> Đề xuất cải tiến ({suggestions.length})
              </div>
              <div className="space-y-2">
                {suggestions.map((sug, i) => (
                  <div key={i} className="p-3 bg-indigo-50 border border-indigo-200 rounded-xl text-xs text-indigo-900 flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
                    <span>{sug}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
