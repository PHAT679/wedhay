import React from 'react';
import { AppointmentStatus } from '../types';

interface BadgeProps {
  status: AppointmentStatus | 'Chờ phản hồi' | 'Đã tiếp nhận' | 'Từ chối' | string;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ status, className = '' }) => {
  let colorStyles = 'bg-stone-100 text-stone-700 border-stone-200';

  switch (status) {
    case 'Chờ xác nhận':
    case 'Chờ phản hồi':
      colorStyles = 'bg-amber-50 text-amber-700 border-amber-200';
      break;
    case 'Đã xác nhận':
    case 'Đã tiếp nhận':
      colorStyles = 'bg-blue-50 text-blue-700 border-blue-200';
      break;
    case 'Hoàn thành':
      colorStyles = 'bg-emerald-50 text-emerald-700 border-emerald-200';
      break;
    case 'Hủy':
    case 'Từ chối':
      colorStyles = 'bg-rose-50 text-rose-700 border-rose-200';
      break;
    case 'Không đến':
      colorStyles = 'bg-slate-100 text-slate-600 border-slate-300';
      break;
    default:
      colorStyles = 'bg-softPink text-darkRose border-rosePink/30';
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colorStyles} ${className}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5 opacity-75"></span>
      {status}
    </span>
  );
};
