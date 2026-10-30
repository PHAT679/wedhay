import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Bell,
  Search,
  RotateCcw,
  User as UserIcon,
  ChevronDown,
  Sparkles,
  CheckCheck,
  Calendar,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useEvents } from '../../contexts/EventContext';
import { roleNames, formatDateTime } from '../../utils/helpers';

export const Topbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { currentUser, switchUser, allUsers } = useAuth();
  const { notifications, markNotificationAsRead, markAllNotificationsAsRead, resetAllData, events } = useEvents();

  const [showNotifMenu, setShowNotifMenu] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const unreadNotifs = notifications.filter((n) => !n.isRead);

  // Filter events based on search query
  const searchResults = searchQuery.trim()
    ? events.filter(
        (e) =>
          e.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          e.eventCode.toLowerCase().includes(searchQuery.toLowerCase()) ||
          e.organizingUnit.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : [];

  return (
    <header className="h-16 bg-white border-b border-slate-200/80 px-6 flex items-center justify-between sticky top-0 z-20 shadow-2xs">
      {/* Search Bar */}
      <div className="relative w-80">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          placeholder="Tìm kiếm sự kiện, mã hồ sơ, đơn vị..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full bg-slate-50 border border-slate-200 text-xs rounded-xl pl-9 pr-4 py-2 focus:outline-hidden focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all"
        />

        {searchQuery.trim() && (
          <div className="absolute left-0 right-0 top-full mt-2 bg-white rounded-xl border border-slate-200 shadow-xl p-2 z-50 max-h-80 overflow-y-auto">
            {searchResults.length === 0 ? (
              <div className="p-3 text-xs text-slate-500 text-center">Không tìm thấy sự kiện nào</div>
            ) : (
              searchResults.map((ev) => (
                <div
                  key={ev.id}
                  onClick={() => {
                    navigate(`/events/${ev.id}`);
                    setSearchQuery('');
                  }}
                  className="p-2 hover:bg-slate-50 rounded-lg cursor-pointer transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-blue-600">{ev.eventCode}</span>
                    <span className="text-[10px] text-slate-400">{ev.organizingUnit}</span>
                  </div>
                  <div className="text-xs font-medium text-slate-800 line-clamp-1 mt-0.5">{ev.title}</div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-3">
        {/* Reset Demo Data Button */}
        <button
          onClick={() => {
            if (confirm('Khôi phục toàn bộ dữ liệu mẫu (8 sự kiện, CSVC, thông báo)?')) {
              resetAllData();
            }
          }}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-blue-700 bg-slate-100 hover:bg-blue-50 rounded-lg transition-colors border border-slate-200"
          title="Khôi phục dữ liệu ban đầu để demo"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Demo</span>
        </button>

        {/* Notifications Bell */}
        <div className="relative">
          <button
            onClick={() => setShowNotifMenu(!showNotifMenu)}
            aria-label="Thông báo hệ thống"
            className="w-9 h-9 rounded-xl bg-slate-100 hover:bg-slate-200/80 flex items-center justify-center text-slate-600 transition-colors relative cursor-pointer"
          >
            <Bell className="w-4 h-4" />
            {unreadNotifs.length > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-rose-500 text-white rounded-full text-[10px] font-bold flex items-center justify-center ring-2 ring-white">
                {unreadNotifs.length}
              </span>
            )}
          </button>

          {showNotifMenu && (
            <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-2xl border border-slate-200 shadow-2xl z-50 overflow-hidden">
              <div className="p-3.5 bg-slate-900 text-white flex items-center justify-between">
                <div className="text-xs font-bold uppercase tracking-wider">Thông báo hệ thống</div>
                {unreadNotifs.length > 0 && (
                  <button
                    onClick={markAllNotificationsAsRead}
                    className="text-[11px] text-blue-300 hover:text-white flex items-center gap-1 cursor-pointer"
                  >
                    <CheckCheck className="w-3.5 h-3.5" /> Đã đọc hết
                  </button>
                )}
              </div>
              <div className="max-h-80 overflow-y-auto divide-y divide-slate-100">
                {notifications.length === 0 ? (
                  <div className="p-6 text-center text-xs text-slate-400">Không có thông báo mới</div>
                ) : (
                  notifications.slice(0, 8).map((n) => (
                    <div
                      key={n.id}
                      onClick={() => {
                        markNotificationAsRead(n.id);
                        navigate(n.linkUrl);
                        setShowNotifMenu(false);
                      }}
                      className={`p-3 text-left hover:bg-slate-50 cursor-pointer transition-colors ${
                        !n.isRead ? 'bg-blue-50/50' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold text-slate-800">{n.title}</span>
                        {!n.isRead && <span className="w-2 h-2 rounded-full bg-blue-600 shrink-0" />}
                      </div>
                      <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">{n.content}</p>
                      <span className="text-[10px] text-slate-400 mt-1 block">{formatDateTime(n.createdAt)}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Profile Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-xl hover:bg-slate-100 transition-colors border border-slate-200/60 cursor-pointer"
          >
            <div className="w-7 h-7 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-xs">
              {currentUser.fullName.charAt(0)}
            </div>
            <div className="text-left">
              <div className="text-xs font-bold text-slate-800 leading-tight">{currentUser.fullName}</div>
              <div className="text-[10px] text-blue-600 font-semibold">{currentUser.role}</div>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 ml-1" />
          </button>

          {showUserMenu && (
            <div className="absolute right-0 top-full mt-2 w-64 bg-white rounded-2xl border border-slate-200 shadow-2xl p-2 z-50">
              <div className="p-3 border-b border-slate-100 mb-1">
                <div className="text-xs font-bold text-slate-900">{currentUser.fullName}</div>
                <div className="text-[11px] text-slate-500">{currentUser.email}</div>
                <div className="text-[11px] text-blue-700 font-semibold mt-1">{currentUser.department}</div>
              </div>

              <div className="px-2 py-1.5 text-[10px] font-bold uppercase text-slate-400 tracking-wider">
                Đổi tài khoản kiểm thử:
              </div>
              <div className="space-y-0.5">
                {allUsers
                  .filter((u) => Boolean(u.role))
                  .map((u) => (
                    <button
                      key={u.id}
                      onClick={() => {
                        switchUser(u.role);
                        setShowUserMenu(false);
                      }}
                      className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs flex items-center justify-between cursor-pointer ${
                        u.role === currentUser.role
                          ? 'bg-blue-50 text-blue-700 font-bold'
                          : 'text-slate-600 hover:bg-slate-50'
                      }`}
                    >
                      <span>{u.fullName}</span>
                      <span className="text-[10px] font-semibold text-slate-400">{u.role}</span>
                    </button>
                  ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
