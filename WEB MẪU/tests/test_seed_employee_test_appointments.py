import datetime
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import NhanVien, TaiKhoan
from apps.appointments.models import LichHen
from apps.assignments.models import PhanCong
from apps.services.models import DichVu
from apps.accounts.management.commands.seed_employee_test_appointments import SPECS


class SeedEmployeeAppointmentsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('seed_staff')
        account = TaiKhoan.objects.create(user=self.user, vai_tro='Nhân Viên')
        self.staff = NhanVien.objects.create(tai_khoan=account, ten_nhan_vien='Nhân viên kiểm thử')
        durations = [90, 60, 30, 60, 30]
        for spec, duration in zip(SPECS, durations):
            if not DichVu.objects.filter(ten_dich_vu=spec[3]).exists():
                DichVu.objects.create(ten_dich_vu=spec[3], thoi_luong=duration, gia_tien=100000)
        self.day = timezone.localdate() + datetime.timedelta(days=1)

    def test_seed_idempotent_and_list_detail(self):
        out = StringIO()
        for _ in range(2):
            call_command('seed_employee_test_appointments', employee='seed_staff', date=self.day.isoformat(), stdout=out)
        self.assertIn('Tạo mới: 5', out.getvalue())
        self.assertIn('tạo mới: 0', out.getvalue())
        self.assertEqual(LichHen.objects.count(), 5)
        self.assertEqual(PhanCong.objects.filter(nhan_vien=self.staff, dang_phu_trach=True).count(), 5)
        self.client.force_login(self.user)
        response = self.client.get(reverse('employee:dashboard'), {'date': self.day.isoformat()})
        self.assertEqual(len(response.context['assignments']), 5)
        for spec in SPECS:
            self.assertContains(response, spec[0])
            detail = self.client.get(reverse('employee:appointment_detail', args=[spec[0]]))
            self.assertEqual(detail.status_code, 200)
            self.assertContains(detail, spec[1])
            if spec[4] == 'Hủy':
                self.assertNotContains(detail, 'Xác nhận lịch')
                self.assertNotContains(detail, "onclick=\"openModal('reject-modal')\"")
            elif spec[5] == 'Chờ phản hồi':
                self.assertContains(detail, 'Xác nhận lịch')
                self.assertContains(detail, "onclick=\"openModal('reject-modal')\"")
        self.assertContains(response, 'class="employee-status pending">Chờ xác nhận', count=3)
        self.assertContains(response, 'class="employee-status confirmed">Đã xác nhận', count=1)
        self.assertContains(response, 'class="employee-status canceled">Đã hủy', count=1)

    def test_missing_staff_does_not_create_data(self):
        with self.assertRaises(CommandError):
            call_command('seed_employee_test_appointments', employee='missing')
        self.assertEqual(LichHen.objects.count(), 0)

    def test_new_batch_preserves_existing_test_data(self):
        out = StringIO()
        call_command('seed_employee_test_appointments', employee='seed_staff', date=self.day.isoformat(), stdout=out)
        next_day = self.day + datetime.timedelta(days=1)
        for _ in range(2):
            call_command('seed_employee_test_appointments', employee='seed_staff', start=6, date=next_day.isoformat(), stdout=out)
        self.assertEqual(LichHen.objects.count(), 10)
        self.assertTrue(LichHen.objects.filter(pk='0000000001').exists())
        self.assertTrue(LichHen.objects.filter(pk='0000000006').exists())
        self.assertTrue(LichHen.objects.filter(pk='0000000010').exists())
        self.assertIn('tạo mới: 0', out.getvalue())
