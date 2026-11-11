import Database from 'better-sqlite3';
import bcrypt from 'bcryptjs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const dbPath = path.join(__dirname, '..', 'emmay_beauty.db');

export const db = new Database(dbPath);
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

export function initDatabase() {
  db.exec(`
    -- 1. Bang KhachHang
    CREATE TABLE IF NOT EXISTS KhachHang (
      MaKhachHang TEXT PRIMARY KEY,
      HoTen TEXT NOT NULL,
      SoDienThoai TEXT NOT NULL,
      LinkFacebook TEXT,
      LinkZalo TEXT
    );

    -- 2. Bang TaiKhoan
    CREATE TABLE IF NOT EXISTS TaiKhoan (
      MaTaiKhoan TEXT PRIMARY KEY,
      TenDangNhap TEXT UNIQUE NOT NULL,
      MatKhau TEXT NOT NULL,
      VaiTro TEXT NOT NULL CHECK(VaiTro IN ('Chủ Tiệm', 'Nhân Viên', 'Khách Hàng')),
      MaKhachHang TEXT,
      FOREIGN KEY (MaKhachHang) REFERENCES KhachHang(MaKhachHang)
    );

    -- 3. Bang NhanVien
    CREATE TABLE IF NOT EXISTS NhanVien (
      MaNhanVien TEXT PRIMARY KEY,
      MaTaiKhoan TEXT UNIQUE NOT NULL,
      TenNhanVien TEXT NOT NULL,
      FOREIGN KEY (MaTaiKhoan) REFERENCES TaiKhoan(MaTaiKhoan)
    );

    -- 4. Bang DichVu
    CREATE TABLE IF NOT EXISTS DichVu (
      MaDichVu TEXT PRIMARY KEY,
      TenDichVu TEXT UNIQUE NOT NULL,
      GiaTien INTEGER NOT NULL CHECK(GiaTien > 0),
      ThoiLuong INTEGER NOT NULL CHECK(ThoiLuong IN (30,60,90,120,150,180)),
      GhiChu TEXT,
      DaXoa INTEGER NOT NULL DEFAULT 0
    );

    -- 5. Bang LichHen
    CREATE TABLE IF NOT EXISTS LichHen (
      MaLichHen TEXT PRIMARY KEY,
      MaKhachHang TEXT NOT NULL,
      MaTaiKhoanHuy TEXT,
      NgayGioBatDau TEXT NOT NULL,
      TenLienHe TEXT NOT NULL,
      SoDienThoaiLienHe TEXT NOT NULL,
      TrangThai TEXT NOT NULL CHECK(TrangThai IN ('Chờ xác nhận', 'Đã xác nhận', 'Hoàn thành', 'Hủy', 'Không đến')),
      ThoiDiemHuy TEXT,
      FOREIGN KEY (MaKhachHang) REFERENCES KhachHang(MaKhachHang),
      FOREIGN KEY (MaTaiKhoanHuy) REFERENCES TaiKhoan(MaTaiKhoan)
    );

    -- 6. Bang ChiTietLichHen
    CREATE TABLE IF NOT EXISTS ChiTietLichHen (
      MaLichHen TEXT NOT NULL,
      MaDichVu TEXT NOT NULL,
      TenDichVuDat TEXT NOT NULL,
      DonGiaDat INTEGER NOT NULL,
      ThoiLuongDat INTEGER NOT NULL,
      GhiChuThucHien TEXT,
      PRIMARY KEY (MaLichHen, MaDichVu),
      FOREIGN KEY (MaLichHen) REFERENCES LichHen(MaLichHen) ON DELETE CASCADE,
      FOREIGN KEY (MaDichVu) REFERENCES DichVu(MaDichVu)
    );

    -- 7. Bang PhanCong
    CREATE TABLE IF NOT EXISTS PhanCong (
      MaPhanCong TEXT PRIMARY KEY,
      ThoiDiemPhanCong TEXT NOT NULL,
      TrangThaiTiepNhan TEXT NOT NULL DEFAULT 'Chờ phản hồi' CHECK(TrangThaiTiepNhan IN ('Chờ phản hồi', 'Đã tiếp nhận', 'Từ chối')),
      LyDoTuChoi TEXT,
      ThoiDiemPhanHoi TEXT,
      DangPhuTrach INTEGER NOT NULL DEFAULT 1,
      MaLichHen TEXT NOT NULL,
      MaNhanVien TEXT NOT NULL,
      FOREIGN KEY (MaLichHen) REFERENCES LichHen(MaLichHen) ON DELETE CASCADE,
      FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien)
    );

    -- 8. Bang GiaoDich
    CREATE TABLE IF NOT EXISTS GiaoDich (
      MaGiaoDich TEXT PRIMARY KEY,
      SoTien INTEGER NOT NULL CHECK(SoTien > 0),
      PhuongThuc TEXT NOT NULL CHECK(PhuongThuc IN ('Tiền Mặt', 'QR')),
      TrangThai TEXT NOT NULL CHECK(TrangThai IN ('Thành công', 'Thất bại')),
      ThoiDiemGiaoDich TEXT NOT NULL,
      MaLichHen TEXT UNIQUE NOT NULL,
      FOREIGN KEY (MaLichHen) REFERENCES LichHen(MaLichHen)
    );

    -- 9. Bang ThongBao
    CREATE TABLE IF NOT EXISTS ThongBao (
      MaThongBao TEXT PRIMARY KEY,
      MaTaiKhoanNhan TEXT NOT NULL,
      TieuDe TEXT NOT NULL,
      NoiDung TEXT NOT NULL,
      LoaiThongBao TEXT,
      LienKet TEXT,
      DaDoc INTEGER NOT NULL DEFAULT 0,
      ThoiDiemTao TEXT NOT NULL,
      FOREIGN KEY (MaTaiKhoanNhan) REFERENCES TaiKhoan(MaTaiKhoan)
    );
  `);

  seedData();
}

function seedData() {
  const count = db.prepare('SELECT COUNT(*) as c FROM TaiKhoan').get().c;
  if (count > 0) return;

  console.log('--- Đang khởi tạo dữ liệu mẫu cho hệ thống Emmay Beauty ---');

  const defaultPasswordHash = bcrypt.hashSync('123456', 10);

  // 1. Dữ liệu Tài khoản & Nhân sự
  // Chủ tiệm (Owner)
  db.prepare(`
    INSERT INTO TaiKhoan (MaTaiKhoan, TenDangNhap, MatKhau, VaiTro, MaKhachHang)
    VALUES (?, ?, ?, ?, NULL)
  `).run('TK_OWNER', 'chutiem', defaultPasswordHash, 'Chủ Tiệm');

  // 3 Nhân viên (Employees)
  const staff = [
    { id: 'NV001', tk: 'TK_NV01', username: 'nhanvien1', name: 'Nguyễn Thị Mai' },
    { id: 'NV002', tk: 'TK_NV02', username: 'nhanvien2', name: 'Trần Bảo Ngọc' },
    { id: 'NV003', tk: 'TK_NV03', username: 'nhanvien3', name: 'Lê Thùy Dương' }
  ];

  for (const s of staff) {
    db.prepare(`
      INSERT INTO TaiKhoan (MaTaiKhoan, TenDangNhap, MatKhau, VaiTro, MaKhachHang)
      VALUES (?, ?, ?, ?, NULL)
    `).run(s.tk, s.username, defaultPasswordHash, 'Nhân Viên');

    db.prepare(`
      INSERT INTO NhanVien (MaNhanVien, MaTaiKhoan, TenNhanVien)
      VALUES (?, ?, ?)
    `).run(s.id, s.tk, s.name);
  }

  // 3 Khách hàng mẫu
  const customers = [
    { id: 'KH001', tk: 'TK_KH01', username: 'khachhang1', name: 'Phạm Thu Trang', phone: '0905123456', fb: 'fb.com/thutrang.nail', zalo: '0905123456' },
    { id: 'KH002', tk: 'TK_KH02', username: 'khachhang2', name: 'Hoàng Minh Anh', phone: '0914888999', fb: 'fb.com/minhanh.h', zalo: '0914888999' },
    { id: 'KH003', tk: 'TK_KH03', username: 'khachhang3', name: 'Vũ Cẩm Ly', phone: '0935667788', fb: 'fb.com/camly.nail', zalo: '0935667788' }
  ];

  for (const c of customers) {
    db.prepare(`
      INSERT INTO KhachHang (MaKhachHang, HoTen, SoDienThoai, LinkFacebook, LinkZalo)
      VALUES (?, ?, ?, ?, ?)
    `).run(c.id, c.name, c.phone, c.fb, c.zalo);

    db.prepare(`
      INSERT INTO TaiKhoan (MaTaiKhoan, TenDangNhap, MatKhau, VaiTro, MaKhachHang)
      VALUES (?, ?, ?, ?, ?)
    `).run(c.tk, c.username, defaultPasswordHash, 'Khách Hàng', c.id);
  }

  // Khách vãng lai do chủ tiệm nhập trực tiếp (chưa tạo tài khoản login)
  db.prepare(`
    INSERT INTO KhachHang (MaKhachHang, HoTen, SoDienThoai, LinkFacebook, LinkZalo)
    VALUES (?, ?, ?, ?, ?)
  `).run('KH004', 'Đặng Thảo Vy', '0988776655', 'fb.com/thaovy.dang', '0988776655');

  // 2. Danh mục Dịch vụ (Theo đúng BR: giá > 0, thời lượng thuộc 30, 60, 90, 120, 150, 180)
  const services = [
    { id: 'DV001', name: 'Chăm sóc móng cơ bản & Cắt da', price: 60000, duration: 30, note: 'Vệ sinh, cắt da tay/chân và dũa form chuẩn' },
    { id: 'DV002', name: 'Sơn Gel trơn cao cấp', price: 120000, duration: 30, note: 'Sơn gel Hàn Quốc bóng đẹp, bền 3-4 tuần' },
    { id: 'DV003', name: 'Vẽ móng nghệ thuật (Nail Art)', price: 150000, duration: 60, note: 'Vẽ hoa, họa tiết ren, phong cách Hàn/Nhật' },
    { id: 'DV004', name: 'Úp móng gel tip / Nối móng', price: 200000, duration: 60, note: 'Form móng tự nhiên, độ bền cao' },
    { id: 'DV005', name: 'Đắp bột Ombre / Marble vân đá', price: 280000, duration: 90, note: 'Kỹ thuật loang màu, vân đá sang trọng' },
    { id: 'DV006', name: 'Combo Đính đá Charm Luxury', price: 180000, duration: 60, note: 'Charm nơ, đá Swarovski lấp lánh' },
    { id: 'DV007', name: 'Phá gel / Tháo móng cũ', price: 50000, duration: 30, note: 'Tháo an toàn, dưỡng móng bằng tinh dầu' },
    { id: 'DV008', name: 'Combo Spa tay chân thư giãn thảo mộc', price: 220000, duration: 60, note: 'Tẩy tế bào chết, ngâm chân thảo mộc & massage' }
  ];

  for (const s of services) {
    db.prepare(`
      INSERT INTO DichVu (MaDichVu, TenDichVu, GiaTien, ThoiLuong, GhiChu, DaXoa)
      VALUES (?, ?, ?, ?, ?, 0)
    `).run(s.id, s.name, s.price, s.duration, s.note);
  }

  // 3. Dữ liệu Lịch hẹn mẫu phân bổ các ngày (hôm nay, ngày mai) để kiểm thử Timeline
  const today = new Date().toISOString().slice(0, 10);
  
  // Lịch 1: 09:30 hôm nay (Đã xác nhận, có nhân viên NV001 phụ trách)
  const lh1 = 'LH001';
  db.prepare(`
    INSERT INTO LichHen (MaLichHen, MaKhachHang, NgayGioBatDau, TenLienHe, SoDienThoaiLienHe, TrangThai)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(lh1, 'KH001', `${today}T09:30:00`, 'Phạm Thu Trang', '0905123456', 'Đã xác nhận');

  db.prepare(`
    INSERT INTO ChiTietLichHen (MaLichHen, MaDichVu, TenDichVuDat, DonGiaDat, ThoiLuongDat, GhiChuThucHien)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(lh1, 'DV002', 'Sơn Gel trơn cao cấp', 120000, 30, 'Tone hồng pastel nhẹ nhàng');

  db.prepare(`
    INSERT INTO ChiTietLichHen (MaLichHen, MaDichVu, TenDichVuDat, DonGiaDat, ThoiLuongDat, GhiChuThucHien)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(lh1, 'DV006', 'Combo Đính đá Charm Luxury', 180000, 60, 'Đính đá 2 ngón cái');

  db.prepare(`
    INSERT INTO PhanCong (MaPhanCong, ThoiDiemPhanCong, TrangThaiTiepNhan, DangPhuTrach, MaLichHen, MaNhanVien)
    VALUES (?, datetime('now'), 'Đã tiếp nhận', 1, ?, ?)
  `).run('PC001', lh1, 'NV001');

  // Lịch 2: 11:00 hôm nay (Chờ xác nhận, chưa phân công)
  const lh2 = 'LH002';
  db.prepare(`
    INSERT INTO LichHen (MaLichHen, MaKhachHang, NgayGioBatDau, TenLienHe, SoDienThoaiLienHe, TrangThai)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(lh2, 'KH002', `${today}T11:00:00`, 'Hoàng Minh Anh', '0914888999', 'Chờ xác nhận');

  db.prepare(`
    INSERT INTO ChiTietLichHen (MaLichHen, MaDichVu, TenDichVuDat, DonGiaDat, ThoiLuongDat, GhiChuThucHien)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(lh2, 'DV003', 'Vẽ móng nghệ thuật (Nail Art)', 150000, 60, 'Vẽ hoa anh đào');

  // Lịch 3: 14:00 hôm nay (Đã phân công NV002, nhân viên đã từ chối với lý do)
  const lh3 = 'LH003';
  db.prepare(`
    INSERT INTO LichHen (MaLichHen, MaKhachHang, NgayGioBatDau, TenLienHe, SoDienThoaiLienHe, TrangThai)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(lh3, 'KH003', `${today}T14:00:00`, 'Vũ Cẩm Ly', '0935667788', 'Chờ xác nhận');

  db.prepare(`
    INSERT INTO ChiTietLichHen (MaLichHen, MaDichVu, TenDichVuDat, DonGiaDat, ThoiLuongDat, GhiChuThucHien)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(lh3, 'DV005', 'Đắp bột Ombre / Marble vân đá', 280000, 90, 'Ombre hồng nude');

  db.prepare(`
    INSERT INTO PhanCong (MaPhanCong, ThoiDiemPhanCong, TrangThaiTiepNhan, LyDoTuChoi, ThoiDiemPhanHoi, DangPhuTrach, MaLichHen, MaNhanVien)
    VALUES (?, datetime('now', '-2 hours'), 'Từ chối', 'Bận việc gia đình đột xuất', datetime('now', '-1 hours'), 0, ?, ?)
  `).run('PC002', lh3, 'NV002');

  // Lịch 4: 16:00 hôm nay (Hoàn thành & đã thanh toán QR)
  const lh4 = 'LH004';
  db.prepare(`
    INSERT INTO LichHen (MaLichHen, MaKhachHang, NgayGioBatDau, TenLienHe, SoDienThoaiLienHe, TrangThai)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(lh4, 'KH004', `${today}T16:00:00`, 'Đặng Thảo Vy', '0988776655', 'Hoàn thành');

  db.prepare(`
    INSERT INTO ChiTietLichHen (MaLichHen, MaDichVu, TenDichVuDat, DonGiaDat, ThoiLuongDat, GhiChuThucHien)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(lh4, 'DV004', 'Úp móng gel tip / Nối móng', 200000, 60, 'Dáng móng almond thanh mảnh');

  db.prepare(`
    INSERT INTO PhanCong (MaPhanCong, ThoiDiemPhanCong, TrangThaiTiepNhan, DangPhuTrach, MaLichHen, MaNhanVien)
    VALUES (?, datetime('now', '-4 hours'), 'Đã tiếp nhận', 1, ?, ?)
  `).run('PC003', lh4, 'NV003');

  db.prepare(`
    INSERT INTO GiaoDich (MaGiaoDich, SoTien, PhuongThuc, TrangThai, ThoiDiemGiaoDich, MaLichHen)
    VALUES (?, ?, ?, ?, datetime('now', '-3 hours'), ?)
  `).run('GD001', 200000, 'QR', 'Thành công', lh4);

  // Thông báo mẫu
  db.prepare(`
    INSERT INTO ThongBao (MaThongBao, MaTaiKhoanNhan, TieuDe, NoiDung, LoaiThongBao, LienKet, DaDoc, ThoiDiemTao)
    VALUES (?, ?, ?, ?, ?, ?, 0, datetime('now'))
  `).run('TB001', 'TK_OWNER', 'Nhân viên từ chối lịch', 'Trần Bảo Ngọc đã từ chối lịch hẹn LH003 lúc 14:00 (Lý do: Bận việc gia đình đột xuất)', 'TU_CHOI', '/owner/assignments');

  db.prepare(`
    INSERT INTO ThongBao (MaThongBao, MaTaiKhoanNhan, TieuDe, NoiDung, LoaiThongBao, LienKet, DaDoc, ThoiDiemTao)
    VALUES (?, ?, ?, ?, ?, ?, 0, datetime('now'))
  `).run('TB002', 'TK_NV01', 'Lịch hẹn mới được phân công', 'Bạn có lịch hẹn phục vụ khách Phạm Thu Trang lúc 09:30 hôm nay', 'PHAN_CONG', '/employee/tasks');

  console.log('--- Khởi tạo CSDL Emmay Beauty hoàn tất thành công! ---');
}
