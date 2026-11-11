import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import KhachHang, NhanVien, TaiKhoan
from apps.appointments.models import LichHen
from apps.assignments.models import PhanCong


class BookingCreationOrderTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user('creation_owner')
        TaiKhoan.objects.create(user=owner, vai_tro='Chủ Tiệm')
        staff_user = User.objects.create_user('creation_employee')
        staff_account = TaiKhoan.objects.create(user=staff_user, vai_tro='Nhân Viên')
        self.staff = NhanVien.objects.create(tai_khoan=staff_account, ten_nhan_vien='Nhân viên')
        self.owner = owner
        self.staff_user = staff_user
        self.customer = KhachHang.objects.create(ho_ten='Khách hàng', so_dien_thoai='0901234567')
        self.appointments = []
        base_time = timezone.now() - datetime.timedelta(days=5)
        for i in range(12):
            appointment = LichHen.objects.create(
                ma_lich_hen=f'LH{i:03d}', khach_hang=self.customer, ten_lien_he=self.customer.ho_ten,
                so_dien_thoai_lien_he=self.customer.so_dien_thoai,
                ngay_gio_bat_dau=timezone.now() + datetime.timedelta(days=20-i),
                trang_thai='Đã xác nhận' if i % 2 == 0 else 'Chờ xác nhận',
            )
            created = base_time + datetime.timedelta(minutes=i // 2)
            LichHen.objects.filter(pk=appointment.pk).update(thoi_diem_tao=created)
            self.appointments.append(appointment)
            if i % 2 == 0:
                PhanCong.objects.create(lich_hen=appointment, nhan_vien=self.staff,
                    trang_thai_tiep_nhan='Đã tiếp nhận' if i % 4 == 0 else 'Chờ phản hồi')
        self.client.force_login(owner)

    def list_ids(self, url, params, assignment=False):
        ids = []
        for page in (1, 2, 3):
            response = self.client.get(url, {**params, 'page': page})
            page_obj = response.context['page_obj']
            if page > page_obj.paginator.num_pages:
                break
            ids.extend((row.lich_hen_id if assignment else row.pk) for row in page_obj)
        return ids

    def test_owner_status_and_assignment_modes_use_booking_creation_time(self):
        status_ids = self.list_ids(reverse('owner:status_list'), {})
        self.assertEqual(status_ids, [])
        for mode, index in [('pending', 1), ('change', 0)]:
            with self.subTest(mode=mode):
                ids = self.list_ids(reverse('owner:assignments_list'), {'mode': mode})
                self.assertEqual(ids, [a.pk for a in self.appointments if int(a.pk[-3:]) % 2 == index])

    def test_employee_list_uses_booking_time_not_status_or_assignment_time(self):
        self.client.force_login(self.staff_user)
        ids = self.list_ids(reverse('employee:dashboard'), {}, assignment=True)
        self.assertEqual(ids, [])
