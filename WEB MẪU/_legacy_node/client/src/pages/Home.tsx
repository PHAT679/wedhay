import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { Service } from '../types';
import { Calendar, Sparkles, Clock, MapPin, Phone, ShieldCheck, Heart, ArrowRight } from 'lucide-react';
import loginRefImg from '../assets/login-reference.png';

export const Home: React.FC = () => {
  const [featuredServices, setFeaturedServices] = useState<Service[]>([]);

  useEffect(() => {
    api.getServices().then(services => {
      setFeaturedServices(services.slice(0, 4));
    }).catch(() => {});
  }, []);

  return (
    <div className="font-montserrat">
      {/* HERO SECTION */}
      <section className="relative overflow-hidden bg-gradient-to-b from-[#FBECEF] via-[#FFF9F8] to-white py-16 lg:py-24 border-b border-blushPink/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            
            {/* Left Content */}
            <div className="space-y-6 text-center lg:text-left">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white border border-rosePink/30 text-xs font-semibold text-darkRose shadow-sm">
                <Sparkles className="w-3.5 h-3.5 text-rosePink" />
                <span>Tiệm Nail Phong Cách Sang Trọng Tại Đà Nẵng</span>
              </div>

              <h1 className="font-playfair text-4xl sm:text-5xl lg:text-6xl font-bold text-textCharcoal tracking-tight leading-tight">
                Vẻ đẹp tinh tế từ <br />
                <span className="text-darkRose italic">từng nét móng xinh</span>
              </h1>

              <p className="text-stone-600 text-sm sm:text-base max-w-xl mx-auto lg:mx-0 leading-relaxed">
                Emmay Beauty mang đến trải nghiệm làm móng thư thái, chuẩn mực nghệ thuật với sơn gel nhập khẩu cao cấp, thiết kế móng nghệ thuật độc bản và quy trình đặt lịch trực tuyến nhanh chóng, đúng giờ.
              </p>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3 pt-2">
                <Link
                  to="/book"
                  className="w-full sm:w-auto px-8 py-3.5 rounded-2xl bg-gradient-to-r from-rosePink to-dustyRose hover:from-dustyRose hover:to-darkRose text-white font-semibold text-sm shadow-soft hover:shadow-lg transition-all flex items-center justify-center gap-2 group"
                >
                  <Calendar className="w-4 h-4" />
                  <span>Đặt lịch hẹn ngay</span>
                  <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                </Link>

                <Link
                  to="/services"
                  className="w-full sm:w-auto px-8 py-3.5 rounded-2xl bg-white border border-rosePink/40 text-darkRose hover:bg-softPink font-semibold text-sm transition-all text-center"
                >
                  Xem bảng giá dịch vụ
                </Link>
              </div>

              {/* Info Pills */}
              <div className="pt-6 grid grid-cols-2 sm:grid-cols-3 gap-3 border-t border-blushPink/60 text-left">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-softPink flex items-center justify-center text-darkRose">
                    <Clock className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-textCharcoal">9:00 - 19:00</p>
                    <p className="text-[10px] text-stone-500">Mở cửa hằng ngày</p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-softPink flex items-center justify-center text-darkRose">
                    <MapPin className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-textCharcoal">356/87 Hoàng Diệu</p>
                    <p className="text-[10px] text-stone-500">Hòa Cường, Đà Nẵng</p>
                  </div>
                </div>

                <div className="flex items-center gap-2 col-span-2 sm:col-span-1">
                  <div className="w-8 h-8 rounded-full bg-softPink flex items-center justify-center text-darkRose">
                    <Phone className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-textCharcoal">0905 123 456</p>
                    <p className="text-[10px] text-stone-500">Hotline hỗ trợ</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Visual Image */}
            <div className="relative">
              <div className="relative mx-auto max-w-md lg:max-w-none">
                <div className="rounded-3xl overflow-hidden shadow-2xl border-4 border-white aspect-[4/3] relative">
                  <img
                    src={loginRefImg}
                    alt="Emmay Beauty Artwork"
                    className="w-full h-full object-cover object-left hover:scale-105 transition-transform duration-700"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-darkRose/30 via-transparent to-transparent"></div>
                </div>

                {/* Badge decoration */}
                <div className="absolute -bottom-6 -left-6 bg-white/95 backdrop-blur-md p-4 rounded-2xl shadow-xl border border-blushPink flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-rosePink/20 text-darkRose flex items-center justify-center">
                    <Heart className="w-5 h-5 fill-rosePink text-rosePink" />
                  </div>
                  <div>
                    <p className="font-playfair font-bold text-sm text-textCharcoal">100% Hài Lòng</p>
                    <p className="text-[11px] text-stone-500">Chuẩn sơn gel & vệ sinh y tế</p>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* FEATURED SERVICES PREVIEW */}
      <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <span className="text-xs font-bold text-rosePink uppercase tracking-widest block mb-1">
            Menu Dịch Vụ Nổi Bật
          </span>
          <h2 className="font-playfair text-3xl font-bold text-textCharcoal">
            Dịch vụ được yêu thích nhất
          </h2>
          <p className="text-stone-500 text-xs sm:text-sm mt-2">
            Giá niêm yết minh bạch, thời lượng chuẩn hóa khớp với từng khung giờ hẹn của bạn
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {featuredServices.map(service => (
            <div
              key={service.MaDichVu}
              className="bg-white rounded-2xl p-6 border border-blushPink/80 shadow-card hover:shadow-soft transition-all duration-300 flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-[11px] font-semibold text-darkRose bg-softPink px-2.5 py-1 rounded-full flex items-center gap-1">
                    <Clock className="w-3 h-3" /> {service.ThoiLuong} phút
                  </span>
                  <Sparkles className="w-4 h-4 text-rosePink/60 group-hover:text-rosePink transition-colors" />
                </div>

                <h3 className="font-playfair font-bold text-lg text-textCharcoal group-hover:text-darkRose transition-colors">
                  {service.TenDichVu}
                </h3>
                <p className="text-xs text-stone-500 mt-2 line-clamp-2">
                  {service.GhiChu || 'Dịch vụ chăm sóc móng cao cấp tại Emmay Beauty'}
                </p>
              </div>

              <div className="mt-6 pt-4 border-t border-blushPink/50 flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-stone-400 block uppercase">Giá dịch vụ</span>
                  <span className="font-bold text-base text-darkRose">
                    {service.GiaTien.toLocaleString('vi-VN')} đ
                  </span>
                </div>
                <Link
                  to="/book"
                  className="px-3 py-1.5 rounded-xl bg-softPink text-darkRose hover:bg-rosePink hover:text-white text-xs font-medium transition-colors"
                >
                  Chọn làm
                </Link>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center mt-10">
          <Link
            to="/services"
            className="inline-flex items-center gap-2 text-sm font-semibold text-darkRose hover:underline"
          >
            <span>Xem toàn bộ danh mục dịch vụ</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* WHY CHOOSE EMMAY BEAUTY */}
      <section className="bg-softPink/40 py-16 border-y border-blushPink/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-2xl border border-blushPink shadow-sm text-center">
              <div className="w-12 h-12 rounded-full bg-softPink text-darkRose flex items-center justify-center mx-auto mb-4">
                <Clock className="w-6 h-6" />
              </div>
              <h4 className="font-playfair font-bold text-lg text-textCharcoal mb-2">Đúng Giờ Tuyệt Đối</h4>
              <p className="text-xs text-stone-500 leading-relaxed">
                Hệ thống đặt lịch thông minh kiểm soát slot trống 30 phút, cam kết không để khách hàng phải chờ đợi lâu khi đến hẹn.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-blushPink shadow-sm text-center">
              <div className="w-12 h-12 rounded-full bg-softPink text-darkRose flex items-center justify-center mx-auto mb-4">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h4 className="font-playfair font-bold text-lg text-textCharcoal mb-2">Sơn Gel & Vệ Sinh Chuẩn Y Tế</h4>
              <p className="text-xs text-stone-500 leading-relaxed">
                Dụng cụ làm móng được tiệt trùng UV 100%, sử dụng các dòng sơn an toàn cho móng, bền màu bóng đẹp từ 3-4 tuần.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-blushPink shadow-sm text-center">
              <div className="w-12 h-12 rounded-full bg-softPink text-darkRose flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-6 h-6" />
              </div>
              <h4 className="font-playfair font-bold text-lg text-textCharcoal mb-2">Thanh Toán QR Tiện Lợi</h4>
              <p className="text-xs text-stone-500 leading-relaxed">
                Thanh toán linh hoạt bằng tiền mặt hoặc quét mã VietQR tự động có sẵn số tiền và mã hóa đơn sau khi hoàn thành.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
