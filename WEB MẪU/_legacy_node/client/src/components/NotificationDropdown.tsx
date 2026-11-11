import React, { useState, useRef, useEffect } from 'react';
import { Bell, Check, Clock, ChevronRight } from 'lucide-react';
import { useNotifications } from '../context/NotificationContext';
import { useNavigate } from 'react-router-dom';

export const NotificationDropdown: React.FC = () => {
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotifications();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleNotificationClick = (item: any) => {
    markAsRead(item.MaThongBao);
    if (item.LienKet) {
      navigate(item.LienKet);
    }
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-xl text-stone-600 hover:text-darkRose hover:bg-softPink transition-colors"
        title="Thông báo"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 flex h-4 min-w-[1rem] px-1 items-center justify-center rounded-full bg-rosePink text-[10px] font-bold text-white shadow-sm animate-pulse">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl bg-white shadow-card border border-blushPink/80 py-2 z-50 animate-fadeIn">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-2 border-b border-blushPink/50">
            <div className="flex items-center gap-2">
              <h4 className="font-playfair font-semibold text-textCharcoal">Thông báo</h4>
              {unreadCount > 0 && (
                <span className="text-[11px] bg-softPink text-darkRose font-medium px-2 py-0.5 rounded-full">
                  {unreadCount} mới
                </span>
              )}
            </div>
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="text-xs text-rosePink hover:text-darkRose hover:underline flex items-center gap-1"
              >
                <Check className="w-3.5 h-3.5" /> Đọc tất cả
              </button>
            )}
          </div>

          {/* List */}
          <div className="max-h-80 overflow-y-auto divide-y divide-blushPink/30">
            {notifications.length === 0 ? (
              <div className="py-8 text-center text-stone-400 text-sm">
                Không có thông báo mới
              </div>
            ) : (
              notifications.slice(0, 10).map(item => (
                <div
                  key={item.MaThongBao}
                  onClick={() => handleNotificationClick(item)}
                  className={`p-3.5 hover:bg-softPink/40 cursor-pointer transition-colors ${
                    !item.DaDoc ? 'bg-softPink/20' : ''
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className={`text-sm ${!item.DaDoc ? 'font-semibold text-textCharcoal' : 'text-stone-600'}`}>
                      {item.TieuDe}
                    </p>
                    {!item.DaDoc && (
                      <span className="w-2 h-2 rounded-full bg-rosePink flex-shrink-0 mt-1" />
                    )}
                  </div>
                  <p className="text-xs text-stone-500 mt-1 line-clamp-2">
                    {item.NoiDung}
                  </p>
                  <div className="flex items-center justify-between mt-2 text-[10px] text-stone-400">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(item.ThoiDiemTao).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}{' '}
                      {new Date(item.ThoiDiemTao).toLocaleDateString('vi-VN')}
                    </span>
                    <span className="text-rosePink hover:underline flex items-center">
                      Chi tiết <ChevronRight className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-blushPink/50 pt-2 px-4 text-center">
            <button
              onClick={() => {
                navigate('/notifications');
                setIsOpen(false);
              }}
              className="text-xs text-darkRose font-medium hover:underline py-1"
            >
              Xem tất cả thông báo
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
