import datetime
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from django.contrib.auth.models import User
from django.db import close_old_connections
from django.test import Client, TransactionTestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import KhachHang, NhanVien, TaiKhoan
from apps.appointments.models import ChiTietLichHen, LichHen
from apps.services.models import DichVu


class CapacityConcurrencyTests(TransactionTestCase):
    def setUp(self):
        staff = User.objects.create_user(username='staff_test')
        staff_account = TaiKhoan.objects.create(user=staff, vai_tro='Nhân Viên')
        NhanVien.objects.create(tai_khoan=staff_account, ten_nhan_vien='Staff')
        self.users = []
        for i in range(2):
            customer = KhachHang.objects.create(ho_ten=f'Customer {i}', so_dien_thoai=f'090000000{i}')
            user = User.objects.create_user(username=f'customer_test_{i}')
            TaiKhoan.objects.create(user=user, vai_tro='Khách Hàng', khach_hang=customer)
            self.users.append(user)
        self.service = DichVu.objects.create(ten_dich_vu='Service test', gia_tien=10000, thoi_luong=60)
        self.day = timezone.localdate() + datetime.timedelta(days=2)

    def race(self, requests):
        barrier = Barrier(2)
        def run(args):
            close_old_connections()
            try:
                user, url, data = args
                client = Client()
                client.force_login(user)
                barrier.wait(timeout=10)
                response = client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
                return response.status_code
            finally:
                close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as pool:
            return list(pool.map(run, requests))

    def test_simultaneous_booking_last_place(self):
        data = {'service_ids': [self.service.pk], 'booking_date': self.day.isoformat(), 'booking_time': '14:00', 'contact_name': 'Test', 'contact_phone': '0901234567'}
        statuses = self.race([(u, reverse('customer:booking'), data) for u in self.users])
        self.assertEqual(sorted(statuses), [302, 409])
        self.assertEqual(LichHen.objects.count(), 1)
        self.assertEqual(ChiTietLichHen.objects.count(), 1)

    def test_reschedule_availability_uses_live_appointments(self):
        client = Client()
        def slots(exclude=None):
            params = {'date': self.day.isoformat(), 'duration': 60}
            if exclude:
                params['exclude_id'] = exclude
            response = client.get(reverse('api_available_slots'), params)
            self.assertEqual(response.status_code, 200)
            return {s['time_str']: s['available'] for s in response.json()['slots']}
        def appointment(hour, status='Chờ xác nhận'):
            start = timezone.make_aware(datetime.datetime.combine(self.day, datetime.time(hour, 0)))
            item = LichHen.objects.create(khach_hang=self.users[0].tai_khoan.khach_hang, ngay_gio_bat_dau=start, ten_lien_he='Test', so_dien_thoai_lien_he='0901234567', trang_thai=status)
            ChiTietLichHen.objects.create(lich_hen=item, dich_vu=self.service, ten_dich_vu_dat='Service test', don_gia_dat=10000, thoi_luong_dat=60)
            return item
        initial = slots()
        self.assertEqual(len(initial), 17)
        self.assertTrue(all(initial.values()))
        own = appointment(9)
        self.assertFalse(slots()['09:00'])
        self.assertTrue(slots(own.pk)['09:00'])
        self.assertTrue(slots()['10:00'])
        appointment(10, 'Hủy')
        self.assertTrue(slots()['10:00'])
        for hour in range(10, 17):
            appointment(hour)
        self.assertEqual([time for time, available in slots().items() if available], ['17:00'])
        appointment(17)
        self.assertFalse(any(slots().values()))

    def test_simultaneous_reschedule_last_place(self):
        appointments = []
        for i, user in enumerate(self.users):
            start = timezone.make_aware(datetime.datetime.combine(self.day, datetime.time(9+i, 0)))
            item = LichHen.objects.create(khach_hang=user.tai_khoan.khach_hang, ngay_gio_bat_dau=start, ten_lien_he='Test', so_dien_thoai_lien_he='0901234567')
            ChiTietLichHen.objects.create(lich_hen=item, dich_vu=self.service, ten_dich_vu_dat='Service test', don_gia_dat=10000, thoi_luong_dat=60)
            appointments.append(item)
        data = {'booking_date': self.day.isoformat(), 'booking_time': '14:00'}
        statuses = self.race([(u, reverse('customer:reschedule', args=[item.pk]), data) for u, item in zip(self.users, appointments)])
        self.assertEqual(sorted(statuses), [200, 409])
        for item in appointments:
            item.refresh_from_db()
        self.assertEqual(sum(timezone.localtime(item.ngay_gio_bat_dau).hour == 14 for item in appointments), 1)

    def test_conflict_messages_and_unchanged_reschedule(self):
        original = timezone.make_aware(datetime.datetime.combine(self.day, datetime.time(9, 0)))
        item = LichHen.objects.create(khach_hang=self.users[0].tai_khoan.khach_hang, ngay_gio_bat_dau=original, ten_lien_he='Test', so_dien_thoai_lien_he='0901234567')
        ChiTietLichHen.objects.create(lich_hen=item, dich_vu=self.service, ten_dich_vu_dat='Service test', don_gia_dat=10000, thoi_luong_dat=60)
        def occupy(hour):
            start = timezone.make_aware(datetime.datetime.combine(self.day, datetime.time(hour, 0)))
            appointment = LichHen.objects.create(khach_hang=self.users[1].tai_khoan.khach_hang, ngay_gio_bat_dau=start, ten_lien_he='Test', so_dien_thoai_lien_he='0901234567')
            ChiTietLichHen.objects.create(lich_hen=appointment, dich_vu=self.service, ten_dich_vu_dat='Service test', don_gia_dat=10000, thoi_luong_dat=60)
        occupy(14)
        client = Client(); client.force_login(self.users[0])
        booking = {'service_ids': [self.service.pk], 'booking_date': self.day.isoformat(), 'booking_time': '14:00', 'contact_name': 'Test', 'contact_phone': '0901234567'}
        reschedule = {'booking_date': self.day.isoformat(), 'booking_time': '14:00'}
        for url, data in [(reverse('customer:booking'), booking), (reverse('customer:reschedule', args=[item.pk]), reschedule)]:
            response = client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, 409)
            self.assertIn('Khung giờ không còn chỗ', response.json()['message'])
        for hour in range(9, 19):
            if hour != 14:
                occupy(hour)
        for url, data in [(reverse('customer:booking'), booking), (reverse('customer:reschedule', args=[item.pk]), reschedule)]:
            response = client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, 409)
            self.assertIn('Ngày chọn không còn khung giờ trống', response.json()['message'])
        item.refresh_from_db()
        self.assertEqual(item.ngay_gio_bat_dau, original)
