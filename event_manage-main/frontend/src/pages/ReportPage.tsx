import React, { useState } from 'react';
import { FileCheck, Sparkles, Send, CheckCircle2, FileText } from 'lucide-react';
import { useEvents } from '../contexts/EventContext';
import { useAuth } from '../contexts/AuthContext';

export const ReportPage: React.FC = () => {
  const { events, saveReport, transitionEvent } = useEvents();
  const { currentUser } = useAuth();

  const [selectedEventId, setSelectedEventId] = useState<string>(events[0]?.id || '');
  const selectedEvent = events.find((e) => e.id === selectedEventId);

  const [actualAttendees, setActualAttendees] = useState(selectedEvent?.expectedAttendees || 150);
  const [summary, setSummary] = useState(selectedEvent?.report?.summary || '');
  const [achievements, setAchievements] = useState(selectedEvent?.report?.achievements || '');
  const [challenges, setChallenges] = useState(selectedEvent?.report?.challenges || '');
  const [lessonsLearned, setLessonsLearned] = useState(selectedEvent?.report?.lessonsLearned || '');
  const [recommendations, setRecommendations] = useState(selectedEvent?.report?.recommendations || '');

  // AI draft generator
  const handleGenerateAIDraft = () => {
    if (!selectedEvent) return;

    setSummary(
      `Chương trình "${selectedEvent.title}" do ${selectedEvent.organizingUnit} chủ trì tổ chức đã diễn ra thành công tốt đẹp tại ${selectedEvent.preferredVenue}. Sự kiện đã thu hút hơn ${actualAttendees} sinh viên và đại biểu tham dự.`
    );
    setAchievements(
      `1. Đạt 100% mục tiêu chuyên môn và phong trào đề ra trong kế hoạch.\n2. Ban tổ chức phối hợp hiệu quả với Bộ phận CSVC, đảm bảo an ninh trật tự và thiết bị vận hành an toàn.\n3. Nhận được đánh giá cao từ người tham dự thông qua biểu mẫu khảo sát trực tuyến.`
    );
    setChallenges(
      `1. Khâu đón tiếp lúc cao điểm đầu giờ còn hơi đông, cần bố trí thêm nhân sự check-in.\n2. Cần chuẩn bị thêm phương án micro dự phòng cho diễn giả.`
    );
    setLessonsLearned(
      `1. Cần họp rà soát kịch bản kỹ thuật âm thanh ánh sáng trước sự kiện 2 giờ.\n2. Đẩy mạnh truyền thông số đa kênh trên Fanpage trước ít nhất 7 ngày.`
    );
    setRecommendations(
      `1. Đề xuất Đoàn trường tiếp tục nhân rộng mô hình hoạt động này sang các kỳ tiếp theo.\n2. Đề nghị Nhà trường hỗ trợ nâng cấp thêm hệ thống âm thanh không dây tại hội trường.`
    );
  };

  const handleSubmitReport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedEvent) return;

    const success = await saveReport(selectedEvent.id, {
      actualAttendees,
      summary,
      achievements,
      challenges,
      lessonsLearned,
      recommendations,
      status: 'SUBMITTED',
    });

    if (!success) return;
    await transitionEvent(
      selectedEvent.id,
      'BTC nộp báo cáo tổng kết sự kiện cho Đoàn trường',
      'REPORT_PENDING',
      'Đã hoàn thiện báo cáo và số liệu thực tế'
    );
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Báo cáo Tổng kết Sự kiện</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Tổng hợp số liệu thực tế, đánh giá kết quả, rút kinh nghiệm và trình Đoàn trường phê duyệt đóng hồ sơ
        </p>
      </div>

      <form onSubmit={handleSubmitReport} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b pb-3">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Chọn sự kiện lập báo cáo:</label>
            <select
              value={selectedEventId}
              onChange={(e) => {
                setSelectedEventId(e.target.value);
                const ev = events.find((x) => x.id === e.target.value);
                if (ev) {
                  setActualAttendees(ev.expectedAttendees);
                  setSummary(ev.report?.summary || '');
                  setAchievements(ev.report?.achievements || '');
                }
              }}
              className="text-xs p-2.5 rounded-xl border border-slate-200 bg-slate-50 font-bold"
            >
              {events.map((ev) => (
                <option key={ev.id} value={ev.id}>
                  {ev.eventCode} — {ev.title}
                </option>
              ))}
            </select>
          </div>

          <button
            type="button"
            onClick={handleGenerateAIDraft}
            className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold shadow-md transition-all cursor-pointer self-start sm:self-end"
          >
            <Sparkles className="w-4 h-4 text-amber-300" />
            <span>AI Tạo bản nháp báo cáo</span>
          </button>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Số lượng người tham dự thực tế:</label>
          <input
            type="number"
            value={actualAttendees}
            onChange={(e) => setActualAttendees(Number(e.target.value))}
            className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-slate-50 font-bold"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">1. Tóm tắt diễn biến chương trình:</label>
          <textarea
            rows={3}
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-slate-50"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">2. Kết quả & Thành tựu đạt được:</label>
          <textarea
            rows={3}
            value={achievements}
            onChange={(e) => setAchievements(e.target.value)}
            className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-slate-50"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">3. Khó khăn & Tồn tại:</label>
            <textarea
              rows={3}
              value={challenges}
              onChange={(e) => setChallenges(e.target.value)}
              className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-slate-50"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">4. Bài học kinh nghiệm:</label>
            <textarea
              rows={3}
              value={lessonsLearned}
              onChange={(e) => setLessonsLearned(e.target.value)}
              className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-slate-50"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">5. Đề xuất & Kiến nghị với Nhà trường:</label>
          <textarea
            rows={2}
            value={recommendations}
            onChange={(e) => setRecommendations(e.target.value)}
            className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-slate-50"
          />
        </div>

        <div className="flex justify-end pt-3 border-t">
          <button
            type="submit"
            className="flex items-center gap-1.5 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold cursor-pointer shadow-xs"
          >
            <Send className="w-4 h-4" /> Nộp báo cáo cho Đoàn Trường
          </button>
        </div>
      </form>
    </div>
  );
};
