import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Service } from '../types';
import { Search, Clock, Calendar, Sparkles } from 'lucide-react';

export const PublicServices: React.FC = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchServices();
  }, [searchTerm]);

  const fetchServices = async () => {
    setIsLoading(true);
    try {
      const data = await api.getServices(searchTerm);
      setServices(data);
    } catch (error) {
      console.error('Lỗi tải dịch vụ:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBookService = (serviceId: string) => {
    navigate('/book', { state: { preSelectedServiceId: serviceId } });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 font-montserrat">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto mb-10">
        <span className="text-xs font-bold text-rosePink uppercase tracking-widest block mb-1">
          Bảng Giá Dịch Vụ Chính Hãng
        </span>
        <h1 className="font-playfair text-3xl sm:text-4xl font-bold text-textCharcoal">
          Bảng Giá & Dịch Vụ Emmay Beauty
        </h1>
        <p className="text-stone-500 text-xs sm:text-sm mt-2">
          Giá tiền minh bạch, thời gian thực hiện rõ ràng theo chuẩn 30, 60, 90 phút
        </p>

        {/* Search Input */}
        <div className="mt-6 relative max-w-md mx-auto">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-stone-400">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Tìm kiếm tên dịch vụ..."
            className="w-full pl-10 pr-4 py-2.5 rounded-2xl border border-blushPink bg-white text-sm shadow-sm focus:outline-none focus:border-rosePink focus:ring-2 focus:ring-rosePink/20"
          />
        </div>
      </div>

      {/* Services Grid */}
      {isLoading ? (
        <div className="py-20 text-center">
          <div className="inline-block w-8 h-8 border-4 border-rosePink border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs text-stone-400 mt-3">Đang tải danh sách dịch vụ...</p>
        </div>
      ) : services.length === 0 ? (
        <div className="py-16 text-center bg-white rounded-3xl border border-blushPink max-w-md mx-auto">
          <p className="text-stone-500 text-sm font-medium">Không tìm thấy dịch vụ phù hợp</p>
          <button
            onClick={() => setSearchTerm('')}
            className="mt-3 text-xs text-darkRose font-semibold hover:underline"
          >
            Xem tất cả dịch vụ
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((s) => (
            <div
              key={s.MaDichVu}
              className="bg-white rounded-3xl p-6 border border-blushPink/80 shadow-card hover:shadow-soft transition-all duration-300 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-semibold text-darkRose bg-softPink px-3 py-1 rounded-full flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5" /> {s.ThoiLuong} phút
                  </span>
                  <span className="text-xs text-stone-400 font-mono">#{s.MaDichVu}</span>
                </div>

                <h3 className="font-playfair font-bold text-xl text-textCharcoal mb-2">
                  {s.TenDichVu}
                </h3>

                <p className="text-xs text-stone-500 leading-relaxed mb-4">
                  {s.GhiChu || 'Dịch vụ móng chất lượng cao tại tiệm nail Emmay Beauty.'}
                </p>
              </div>

              <div className="pt-4 border-t border-blushPink/50 flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-stone-400 uppercase tracking-wider block">Giá niêm yết</span>
                  <span className="font-bold text-lg text-darkRose">
                    {s.GiaTien.toLocaleString('vi-VN')} đ
                  </span>
                </div>

                <button
                  onClick={() => handleBookService(s.MaDichVu)}
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-rosePink to-dustyRose hover:from-dustyRose hover:to-darkRose text-white text-xs font-semibold shadow-sm transition-all flex items-center gap-1.5"
                >
                  <Calendar className="w-3.5 h-3.5" /> Đặt lịch này
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
