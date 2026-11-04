export type Role = 'Chủ Tiệm' | 'Nhân Viên' | 'Khách Hàng';

export interface User {
  maTaiKhoan: string;
  tenDangNhap: string;
  vaiTro: Role;
  maKhachHang?: string;
  maNhanVien?: string;
  hoTen: string;
  soDienThoai?: string;
  linkFacebook?: string;
  linkZalo?: string;
}

export interface Service {
  MaDichVu: string;
  TenDichVu: string;
  GiaTien: number;
  ThoiLuong: number; // 30, 60, 90, 120, 150, 180
  GhiChu?: string;
  DaXoa?: number;
}

export interface AppointmentDetail {
  MaLichHen: string;
  MaDichVu: string;
  TenDichVuDat: string;
  DonGiaDat: number;
  ThoiLuongDat: number;
  GhiChuThucHien?: string;
}

export type AppointmentStatus = 'Chờ xác nhận' | 'Đã xác nhận' | 'Hoàn thành' | 'Hủy' | 'Không đến';

export interface Appointment {
  MaLichHen: string;
  MaKhachHang: string;
  MaTaiKhoanHuy?: string;
  NgayGioBatDau: string;
  TenLienHe: string;
  SoDienThoaiLienHe: string;
  TrangThai: AppointmentStatus;
  ThoiDiemHuy?: string;
  HoTenKhachHang?: string;
  SoDienThoaiKhach?: string;
  LinkFacebook?: string;
  LinkZalo?: string;
  MaPhanCong?: string;
  TrangThaiTiepNhan?: 'Chờ phản hồi' | 'Đã tiếp nhận' | 'Từ chối';
  LyDoTuChoi?: string;
  MaNhanVien?: string;
  TenNhanVien?: string;
  MaGiaoDich?: string;
  SoTienDaThu?: number;
  SoTienThanhToan?: number;
  PhuongThucTT?: 'Tiền Mặt' | 'QR';
  PhuongThucThanhToan?: 'Tiền Mặt' | 'QR';
  TrangThaiTT?: string;
  chiTietDichVu?: AppointmentDetail[];
  tongTien?: number;
  tongThoiLuong?: number;
}

export interface Staff {
  MaNhanVien: string;
  MaTaiKhoan: string;
  TenNhanVien: string;
  isBusy?: boolean;
  busyReason?: string | null;
}

export interface Customer {
  MaKhachHang: string;
  HoTen: string;
  SoDienThoai: string;
  LinkFacebook?: string;
  LinkZalo?: string;
  tongSoLanDat?: number;
}

export interface NotificationItem {
  MaThongBao: string;
  MaTaiKhoanNhan: string;
  TieuDe: string;
  NoiDung: string;
  LoaiThongBao?: string;
  LienKet?: string;
  DaDoc: number;
  ThoiDiemTao: string;
}

export interface AvailableSlot {
  time: string;
  endTime: string;
  remainingStaff: number;
}
