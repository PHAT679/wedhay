import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from apps.accounts.models import KhachHang, TaiKhoan, NhanVien
from apps.services.models import DichVu
from apps.appointments.models import LichHen, ChiTietLichHen
from apps.assignments.models import PhanCong
from apps.payments.models import GiaoDich
from apps.notifications.models import ThongBao, send_notification


class Command(BaseCommand):
    help = 'Khởi tạo dữ liệu mẫu cho hệ thống đặt lịch Emmay Beauty'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Bắt đầu khởi tạo dữ liệu mẫu Emmay Beauty...'))

        # 1. DỊCH VỤ (8 dịch vụ tiệm nail thực tế)
        services_data = [
            {
                'ma': 'DV001',
                'ten': 'Chăm sóc móng & Cắt da cơ bản',
                'gia': 80000,
                'thoi_luong': 30,
                'ghi_chu': 'Ngâm tay nước ấm, dưỡng móng, tỉa da chết gọn gàng.'
            },
            {
                'ma': 'DV002',
                'ten': 'Sơn Gel cao cấp Hàn Quốc',
                'gia': 150000,
                'thoi_luong': 60,
                'ghi_chu': 'Độ bền 3-4 tuần, nước bóng mịn không bong tróc.'
            },
            {
                'ma': 'DV003',
                'ten': 'Úp móng & Thiết kế Nail Art Pastel',
                'gia': 280000,
                'thoi_luong': 90,
                'ghi_chu': 'Mẫu vẽ hoa nhí, ombre thạch hồng phong cách Emmay Beauty.'
            },
            {
                'ma': 'DV004',
                'ten': 'Đắp Gel nhũ kim tuyến & Đính đá pha lê',
                'gia': 350000,
                'thoi_luong': 120,
                'ghi_chu': 'Kỹ thuật đắp gel tạo form chuẩn, đính đá sáng lấp lánh.'
            },
            {
                'ma': 'DV005',
                'ten': 'Nối móng đắp bột hoa nổi 3D Luxury',
                'gia': 450000,
                'thoi_luong': 150,
                'ghi_chu': 'Thiết kế hoa nổi thủ công tinh xảo, phong cách tiểu thư sang trọng.'
            },
            {
                'ma': 'DV006',
                'ten': 'Combo Toàn Diện: Spa Móng Chân + Tay + Vẽ Nghệ Thuật',
                'gia': 550000,
                'thoi_luong': 180,
                'ghi_chu': 'Chăm sóc da, tẩy tế bào chết, massage thư giãn kết hợp tạo bộ móng nghệ thuật.'
            },
            {
                'ma': 'DV007',
                'ten': 'Tháo móng cũ & Dưỡng phục hồi móng Collagen',
                'gia': 100000,
                'thoi_luong': 30,
                'ghi_chu': 'Tháo nhẹ nhàng không mỏng móng, ủ tinh chất phục hồi hư tổn.'
            },
            {
                'ma': 'DV008',
                'ten': 'Sơn mắt mèo kim cương & Tráng gương ngọc trai',
                'gia': 220000,
                'thoi_luong': 60,
                'ghi_chu': 'Hiệu ứng ánh sáng huyền ảo theo từng góc nghiêng thời thượng.'
            },
        ]

        dich_vu_objs = {}
        for s in services_data:
            dv, created = DichVu.objects.update_or_create(
                ma_dich_vu=s['ma'],
                defaults={
                    'ten_dich_vu': s['ten'],
                    'gia_tien': s['gia'],
                    'thoi_luong': s['thoi_luong'],
                    'ghi_chu': s['ghi_chu'],
                    'da_xoa': False
                }
            )
            dich_vu_objs[s['ma']] = dv
        self.stdout.write(self.style.SUCCESS('-> Đã tạo 8 dịch vụ tiêu chuẩn.'))

        # 2. TÀI KHOẢN CHỦ TIỆM (OWNER)
        user_owner, _ = User.objects.get_or_create(
            username='chutiem',
            defaults={'first_name': 'Chủ Tiệm', 'last_name': 'Emmay', 'email': 'emmaybeauty@gmail.com'}
        )
        user_owner.set_password('123456')
        user_owner.is_staff = True
        user_owner.is_superuser = True
        user_owner.save()

        tk_owner, _ = TaiKhoan.objects.update_or_create(
            user=user_owner,
            defaults={
                'ma_tai_khoan': 'TK001',
                'vai_tro': 'Chủ Tiệm',
                'khach_hang': None
            }
        )
        self.stdout.write(self.style.SUCCESS('-> Đã tạo tài khoản Chủ tiệm: chutiem / 123456'))

        # 3. TÀI KHOẢN NHÂN VIÊN (3 Kỹ thuật viên)
        employees_data = [
            ('nhanvien1', 'TK002', 'NV001', 'Nguyễn Thị Mai', 'mai.nguyen@emmay.vn'),
            ('nhanvien2', 'TK003', 'NV002', 'Trần Thu Hà', 'ha.tran@emmay.vn'),
            ('nhanvien3', 'TK004', 'NV003', 'Lê Phương Thảo', 'thao.le@emmay.vn'),
        ]

        nv_objs = {}
        for username, tk_code, nv_code, full_name, email in employees_data:
            u, _ = User.objects.get_or_create(
                username=username,
                defaults={'first_name': full_name, 'email': email}
            )
            u.set_password('123456')
            u.save()

            tk, _ = TaiKhoan.objects.update_or_create(
                user=u,
                defaults={'ma_tai_khoan': tk_code, 'vai_tro': 'Nhân Viên', 'khach_hang': None}
            )

            nv, _ = NhanVien.objects.update_or_create(
                tai_khoan=tk,
                defaults={'ma_nhan_vien': nv_code, 'ten_nhan_vien': full_name}
            )
            nv_objs[nv_code] = nv
        self.stdout.write(self.style.SUCCESS('-> Đã tạo 3 tài khoản Nhân viên: nhanvien1, nhanvien2, nhanvien3 / 123456'))

        # 4. TÀI KHOẢN KHÁCH HÀNG (3 khách mẫu)
        customers_data = [
            ('khachhang1', 'TK005', 'KH001', 'Nguyễn Hồng Nhung', '0905123456', 'https://fb.com/hongnhung', '0905123456'),
            ('khachhang2', 'TK006', 'KH002', 'Đỗ Lan Anh', '0914987654', 'https://fb.com/lananh.do', '0914987654'),
            ('khachhang3', 'TK007', 'KH003', 'Vũ Mỹ Linh', '0988654321', None, '0988654321'),
        ]

        kh_objs = {}
        for username, tk_code, kh_code, full_name, sdt, fb, zalo in customers_data:
            kh, _ = KhachHang.objects.update_or_create(
                ma_khach_hang=kh_code,
                defaults={
                    'ho_ten': full_name,
                    'so_dien_thoai': sdt,
                    'link_facebook': fb,
                    'link_zalo': zalo
                }
            )
            kh_objs[kh_code] = kh

            u, _ = User.objects.get_or_create(
                username=username,
                defaults={'first_name': full_name}
            )
            u.set_password('123456')
            u.save()

            tk, _ = TaiKhoan.objects.update_or_create(
                user=u,
                defaults={'ma_tai_khoan': tk_code, 'vai_tro': 'Khách Hàng', 'khach_hang': kh}
            )
        self.stdout.write(self.style.SUCCESS('-> Đã tạo 3 tài khoản Khách hàng: khachhang1, khachhang2, khachhang3 / 123456'))

        # 5. TẠO LỊCH HẸN MẪU ĐẠI DIỆN CHO CÁC TRẠNG THÁI
        today = datetime.date.today()
        lh1_time = timezone.make_aware(datetime.datetime.combine(today, datetime.time(9, 30)))
        lh2_time = timezone.make_aware(datetime.datetime.combine(today, datetime.time(14, 0)))
        lh3_time = timezone.make_aware(datetime.datetime.combine(today - datetime.timedelta(days=1), datetime.time(10, 0)))
        lh4_time = timezone.make_aware(datetime.datetime.combine(today + datetime.timedelta(days=1), datetime.time(15, 30)))

        # LH1: Đã xác nhận & Đã phân công KTV Mai tiếp nhận
        lh1, _ = LichHen.objects.update_or_create(
            ma_lich_hen='LH001',
            defaults={
                'khach_hang': kh_objs['KH001'],
                'ngay_gio_bat_dau': lh1_time,
                'ten_lien_he': 'Nguyễn Hồng Nhung',
                'so_dien_thoai_lien_he': '0905123456',
                'trang_thai': 'Đã xác nhận',
            }
        )
        ChiTietLichHen.objects.filter(lich_hen=lh1).delete()
        ChiTietLichHen.objects.create(
            lich_hen=lh1, dich_vu=dich_vu_objs['DV003'],
            ten_dich_vu_dat=dich_vu_objs['DV003'].ten_dich_vu,
            don_gia_dat=dich_vu_objs['DV003'].gia_tien,
            thoi_luong_dat=dich_vu_objs['DV003'].thoi_luong,
            ghi_chu_thuc_hien='Yêu cầu làm tone hồng pastel thạch'
        )
        PhanCong.objects.update_or_create(
            ma_phan_cong='PC001',
            defaults={
                'lich_hen': lh1,
                'nhan_vien': nv_objs['NV001'],
                'trang_thai_tiep_nhan': 'Đã tiếp nhận',
                'dang_phu_trach': True
            }
        )

        # LH2: Chờ xác nhận (Vừa được khách hàng đặt trực tuyến, chưa phân công)
        lh2, _ = LichHen.objects.update_or_create(
            ma_lich_hen='LH002',
            defaults={
                'khach_hang': kh_objs['KH002'],
                'ngay_gio_bat_dau': lh2_time,
                'ten_lien_he': 'Đỗ Lan Anh',
                'so_dien_thoai_lien_he': '0914987654',
                'trang_thai': 'Chờ xác nhận',
            }
        )
        ChiTietLichHen.objects.filter(lich_hen=lh2).delete()
        ChiTietLichHen.objects.create(
            lich_hen=lh2, dich_vu=dich_vu_objs['DV002'],
            ten_dich_vu_dat=dich_vu_objs['DV002'].ten_dich_vu,
            don_gia_dat=dich_vu_objs['DV002'].gia_tien,
            thoi_luong_dat=dich_vu_objs['DV002'].thoi_luong,
        )

        # LH3: Hoàn thành & Đã thanh toán QR
        lh3, _ = LichHen.objects.update_or_create(
            ma_lich_hen='LH003',
            defaults={
                'khach_hang': kh_objs['KH003'],
                'ngay_gio_bat_dau': lh3_time,
                'ten_lien_he': 'Vũ Mỹ Linh',
                'so_dien_thoai_lien_he': '0988654321',
                'trang_thai': 'Hoàn thành',
            }
        )
        ChiTietLichHen.objects.filter(lich_hen=lh3).delete()
        ChiTietLichHen.objects.create(
            lich_hen=lh3, dich_vu=dich_vu_objs['DV004'],
            ten_dich_vu_dat=dich_vu_objs['DV004'].ten_dich_vu,
            don_gia_dat=dich_vu_objs['DV004'].gia_tien,
            thoi_luong_dat=dich_vu_objs['DV004'].thoi_luong,
        )
        PhanCong.objects.update_or_create(
            ma_phan_cong='PC002',
            defaults={
                'lich_hen': lh3,
                'nhan_vien': nv_objs['NV002'],
                'trang_thai_tiep_nhan': 'Đã tiếp nhận',
                'dang_phu_trach': True
            }
        )
        GiaoDich.objects.update_or_create(
            ma_giao_dich='GD001',
            defaults={
                'lich_hen': lh3,
                'so_tien': 350000,
                'phuong_thuc': 'QR',
                'trang_thai': 'Thành công',
                'ma_tham_chieu': 'EMMAY_LH003_QR'
            }
        )

        # 6. THÔNG BÁO MẪU
        send_notification(
            tai_khoan=tk_owner,
            tieu_de='Lịch hẹn mới cần xác nhận',
            noi_dung='Khách hàng Đỗ Lan Anh vừa đặt lịch hẹn LH002 cho hôm nay lúc 14:00.',
            loai_thong_bao='Lịch mới',
            lien_ket='/owner/appointments/LH002/'
        )
        send_notification(
            tai_khoan=User.objects.get(username='nhanvien1').tai_khoan,
            tieu_de='Phân công lịch hẹn mới',
            noi_dung='Chủ tiệm đã phân công bạn phụ trách lịch hẹn LH001 (Khách: Nguyễn Hồng Nhung).',
            loai_thong_bao='Phân công',
            lien_ket='/employee/appointments/LH001/'
        )

        self.stdout.write(self.style.SUCCESS('-> Hoàn tất khởi tạo toàn bộ dữ liệu mẫu Emmay Beauty!'))
