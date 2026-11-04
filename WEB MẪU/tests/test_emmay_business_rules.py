import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from apps.accounts.models import KhachHang, TaiKhoan, NhanVien
from apps.services.models import DichVu
from apps.appointments.models import LichHen, ChiTietLichHen
from apps.appointments.services import get_available_slots
from apps.assignments.models import PhanCong
from apps.payments.models import GiaoDich
from apps.notifications.models import ThongBao


class EmmayBeautyBusinessRulesTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Tạo dịch vụ mẫu
        self.dv1 = DichVu.objects.create(
            ma_dich_vu='DV001',
            ten_dich_vu='Sơn Gel Hàn Quốc Test',
            gia_tien=150000,
            thoi_luong=60
        )
        self.dv2 = DichVu.objects.create(
            ma_dich_vu='DV002',
            ten_dich_vu='Đắp Gel Móng Test',
            gia_tien=250000,
            thoi_luong=90
        )

        # Chủ tiệm
        self.owner_user = User.objects.create_user(username='chutiem', password='password123')
        self.owner_tk = TaiKhoan.objects.create(user=self.owner_user, vai_tro='Chủ Tiệm', ma_tai_khoan='TK001')

        # Nhân viên
        self.emp_user = User.objects.create_user(username='nhanvien1', password='password123')
        self.emp_tk = TaiKhoan.objects.create(user=self.emp_user, vai_tro='Nhân Viên', ma_tai_khoan='TK002')
        self.emp = NhanVien.objects.create(tai_khoan=self.emp_tk, ma_nhan_vien='NV001', ten_nhan_vien='Nguyễn Kỹ Thuật')

        # Khách hàng
        self.cust_kh = KhachHang.objects.create(ma_khach_hang='KH001', ho_ten='Nguyễn Khách', so_dien_thoai='0905111222')
        self.cust_user = User.objects.create_user(username='khachhang1', password='password123')
        self.cust_tk = TaiKhoan.objects.create(user=self.cust_user, vai_tro='Khách Hàng', ma_tai_khoan='TK003', khach_hang=self.cust_kh)

    # -------------------------------------------------------------
    # 1. UC1 & UC9: Authentication & Registration Tests
    # -------------------------------------------------------------
    def test_login_success_and_role_redirect(self):
        """Kiểm tra đăng nhập đúng tài khoản và chuyển hướng theo vai trò."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'chutiem',
            'password': 'password123',
        })
        self.assertRedirects(response, reverse('owner:dashboard'))

    def test_login_invalid_credentials(self):
        """Kiểm tra đăng nhập sai mật khẩu."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'chutiem',
            'password': 'wrong_password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tên đăng nhập hoặc mật khẩu không chính xác')

    def test_customer_registration(self):
        """UC9: Đăng ký tài khoản khách hàng mới với SĐT 10 số."""
        response = self.client.post(reverse('accounts:register'), {
            'ho_ten': 'Trần Thị Thu',
            'so_dien_thoai': '0905999888',
            'username': 'thutran',
            'password': 'password123',
        })
        self.assertRedirects(response, reverse('customer:booking'))
        self.assertTrue(User.objects.filter(username='thutran').exists())
        self.assertTrue(KhachHang.objects.filter(so_dien_thoai='0905999888').exists())

    # -------------------------------------------------------------
    # 2. UC4: Services Management & Business Rules Tests
    # -------------------------------------------------------------
    def test_service_validation(self):
        """Giá tiền phải > 0 và thời lượng phải thuộc [30, 60, 90, 120, 150, 180]."""
        with self.assertRaises(Exception):
            DichVu.objects.create(
                ten_dich_vu='Dịch vụ sai giá',
                gia_tien=-50000,
                thoi_luong=60
            )

        with self.assertRaises(Exception):
            DichVu.objects.create(
                ten_dich_vu='Dịch vụ sai thời lượng',
                gia_tien=100000,
                thoi_luong=45  # Không phải bội số 30
            )

    def test_cannot_delete_service_with_active_appointments(self):
        """BR-UC4-08: Không được xóa dịch vụ đang có lịch hẹn Chờ xác nhận hoặc Đã xác nhận."""
        self.client.login(username='chutiem', password='password123')
        
        # Tạo lịch hẹn active chứa dv1
        start_time = timezone.now() + datetime.timedelta(days=1)
        lh = LichHen.objects.create(
            khach_hang=self.cust_kh,
            ngay_gio_bat_dau=start_time,
            ten_lien_he='Nguyễn Khách',
            so_dien_thoai_lien_he='0905111222',
            trang_thai='Chờ xác nhận'
        )
        ChiTietLichHen.objects.create(
            lich_hen=lh, dich_vu=self.dv1,
            ten_dich_vu_dat=self.dv1.ten_dich_vu,
            don_gia_dat=self.dv1.gia_tien,
            thoi_luong_dat=self.dv1.thoi_luong
        )

        response = self.client.post(reverse('owner:service_delete', kwargs={'pk': self.dv1.pk}))
        self.assertRedirects(response, reverse('owner:services_list'))
        
        self.dv1.refresh_from_db()
        self.assertFalse(self.dv1.da_xoa, 'Dịch vụ không được xóa mềm khi có lịch hẹn active!')

    # -------------------------------------------------------------
    # 3. UC5: Staff Assignment Conflict Detection
    # -------------------------------------------------------------
    def test_staff_conflict_detection(self):
        """Kiểm tra thuật toán chống trùng lịch nhân viên: start_A < end_B AND start_B < end_A."""
        self.client.login(username='chutiem', password='password123')

        tomorrow = timezone.localdate() + datetime.timedelta(days=1)
        # Lịch 1: 10:00 -> 11:30 (90 phút)
        time1 = timezone.make_aware(datetime.datetime.combine(tomorrow, datetime.time(10, 0)))
        lh1 = LichHen.objects.create(
            khach_hang=self.cust_kh, ngay_gio_bat_dau=time1,
            ten_lien_he='Khách 1', so_dien_thoai_lien_he='0905111222', trang_thai='Đã xác nhận'
        )
        ChiTietLichHen.objects.create(
            lich_hen=lh1, dich_vu=self.dv2,
            ten_dich_vu_dat=self.dv2.ten_dich_vu, don_gia_dat=self.dv2.gia_tien, thoi_luong_dat=90
        )
        # Phân công KTV emp phụ trách LH1
        PhanCong.objects.create(
            lich_hen=lh1, nhan_vien=self.emp, trang_thai_tiep_nhan='Đã tiếp nhận', dang_phu_trach=True
        )

        # Lịch 2: 10:30 -> 11:30 (trùng với Lịch 1)
        time2 = timezone.make_aware(datetime.datetime.combine(tomorrow, datetime.time(10, 30)))
        lh2 = LichHen.objects.create(
            khach_hang=self.cust_kh, ngay_gio_bat_dau=time2,
            ten_lien_he='Khách 2', so_dien_thoai_lien_he='0905111222', trang_thai='Chờ xác nhận'
        )
        ChiTietLichHen.objects.create(
            lich_hen=lh2, dich_vu=self.dv1,
            ten_dich_vu_dat=self.dv1.ten_dich_vu, don_gia_dat=self.dv1.gia_tien, thoi_luong_dat=60
        )

        # Thử phân công cùng KTV emp cho Lịch 2 -> Phải bị từ chối
        response = self.client.post(reverse('owner:assign_staff', kwargs={'appointment_pk': lh2.pk}), {
            'nhan_vien_id': self.emp.pk
        })
        self.assertRedirects(response, reverse('owner:appointment_detail', kwargs={'pk': lh2.pk}))
        self.assertFalse(
            PhanCong.objects.filter(lich_hen=lh2, nhan_vien=self.emp).exists(),
            'Không được phân công nhân viên khi bị trùng khung giờ!'
        )

    # -------------------------------------------------------------
    # 4. UC2: Employee Accept & Reject Tasks
    # -------------------------------------------------------------
    def test_employee_accept_assignment(self):
        """KTV tiếp nhận -> trạng thái đổi sang Đã tiếp nhận & lịch hẹn đổi sang Đã xác nhận."""
        self.client.login(username='nhanvien1', password='password123')
        
        tomorrow = timezone.localdate() + datetime.timedelta(days=1)
        time1 = timezone.make_aware(datetime.datetime.combine(tomorrow, datetime.time(14, 0)))
        lh = LichHen.objects.create(
            khach_hang=self.cust_kh, ngay_gio_bat_dau=time1,
            ten_lien_he='Khách Test', so_dien_thoai_lien_he='0905111222', trang_thai='Chờ xác nhận'
        )
        pc = PhanCong.objects.create(
            lich_hen=lh, nhan_vien=self.emp, trang_thai_tiep_nhan='Chờ phản hồi', dang_phu_trach=True
        )

        response = self.client.get(reverse('employee:accept_assignment', kwargs={'pk': pc.pk}))
        pc.refresh_from_db()
        lh.refresh_from_db()

        self.assertEqual(pc.trang_thai_tiep_nhan, 'Đã tiếp nhận')
        self.assertEqual(lh.trang_thai, 'Đã xác nhận')

    def test_employee_reject_requires_reason(self):
        """KTV từ chối bắt buộc phải có lý do và gửi thông báo cho chủ tiệm."""
        self.client.login(username='nhanvien1', password='password123')
        
        tomorrow = timezone.localdate() + datetime.timedelta(days=1)
        time1 = timezone.make_aware(datetime.datetime.combine(tomorrow, datetime.time(15, 0)))
        lh = LichHen.objects.create(
            khach_hang=self.cust_kh, ngay_gio_bat_dau=time1,
            ten_lien_he='Khách Test', so_dien_thoai_lien_he='0905111222', trang_thai='Chờ xác nhận'
        )
        pc = PhanCong.objects.create(
            lich_hen=lh, nhan_vien=self.emp, trang_thai_tiep_nhan='Chờ phản hồi', dang_phu_trach=True
        )

        # Gửi từ chối kèm lý do
        response = self.client.post(reverse('employee:reject_assignment', kwargs={'pk': pc.pk}), {
            'ly_do_tu_choi': 'Bận ca gia đình đột xuất'
        })
        pc.refresh_from_db()
        self.assertEqual(pc.trang_thai_tiep_nhan, 'Từ chối')
        self.assertFalse(pc.dang_phu_trach)
        self.assertTrue(ThongBao.objects.filter(tai_khoan=self.owner_tk, loai_thong_bao='Từ chối').exists())

    # -------------------------------------------------------------
    # 5. Section 11: Payment & Status Completion
    # -------------------------------------------------------------
    def test_payment_cash_or_qr_completes_appointment(self):
        """Thanh toán thành công cập nhật trạng thái lịch hẹn sang Hoàn thành."""
        self.client.login(username='chutiem', password='password123')

        start_time = timezone.now()
        lh = LichHen.objects.create(
            khach_hang=self.cust_kh, ngay_gio_bat_dau=start_time,
            ten_lien_he='Khách Test', so_dien_thoai_lien_he='0905111222', trang_thai='Đã xác nhận'
        )
        ChiTietLichHen.objects.create(
            lich_hen=lh, dich_vu=self.dv1,
            ten_dich_vu_dat=self.dv1.ten_dich_vu, don_gia_dat=150000, thoi_luong_dat=60
        )

        response = self.client.post(reverse('payments:checkout', kwargs={'appointment_pk': lh.pk}), {
            'phuong_thuc': 'QR'
        })
        lh.refresh_from_db()
        self.assertEqual(lh.trang_thai, 'Hoàn thành')
        self.assertTrue(GiaoDich.objects.filter(lich_hen=lh, phuong_thuc='QR', trang_thai='Thành công').exists())
