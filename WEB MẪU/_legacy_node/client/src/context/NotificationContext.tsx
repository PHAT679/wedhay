import React, { createContext, useContext, useState, useEffect } from 'react';
import { NotificationItem } from '../types';
import { api } from '../services/api';
import { useAuth } from './AuthContext';

interface NotificationContextType {
  notifications: NotificationItem[];
  unreadCount: number;
  fetchNotifications: () => Promise<void>;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);

  const fetchNotifications = async () => {
    if (!user) {
      setNotifications([]);
      setUnreadCount(0);
      return;
    }

    try {
      const data = await api.getNotifications();
      setNotifications(data.notifications || []);
      setUnreadCount(data.unreadCount || 0);
    } catch (error) {
      // Quiet fail on network/polling
    }
  };

  useEffect(() => {
    if (user) {
      fetchNotifications();
      const interval = setInterval(fetchNotifications, 10000); // 10s polling
      return () => clearInterval(interval);
    }
  }, [user]);

  const markAsRead = async (id: string) => {
    try {
      await api.markNotificationAsRead(id);
      setNotifications(prev =>
        prev.map(n => (n.MaThongBao === id ? { ...n, DaDoc: 1 } : n))
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Lỗi đánh dấu đã đọc:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.markAllNotificationsAsRead();
      setNotifications(prev => prev.map(n => ({ ...n, DaDoc: 1 })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Lỗi đánh dấu tất cả đã đọc:', error);
    }
  };

  return (
    <NotificationContext.Provider
      value={{ notifications, unreadCount, fetchNotifications, markAsRead, markAllAsRead }}
    >
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};
