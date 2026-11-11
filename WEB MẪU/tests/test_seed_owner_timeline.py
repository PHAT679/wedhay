from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import NhanVien, TaiKhoan
from apps.appointments.models import LichHen
from apps.accounts.management.commands.seed_owner_timeline_test import MARKER
from apps.services.models import DichVu


class SeedOwnerTimelineTests(TestCase):
    def test_create_once_with_capacity_and_statuses(self):
        for i in range(2):
            user = User.objects.create_user(f'timeline_seed_{i}')
            account = TaiKhoan.objects.create(user=user, vai_tro='Nhân Viên')
            NhanVien.objects.create(tai_khoan=account, ten_nhan_vien=f'Nhân viên {i}')
        DichVu.objects.create(ten_dich_vu='Dịch vụ thử', gia_tien=80000, thoi_luong=30)
        output = StringIO()
        call_command('seed_owner_timeline_test', stdout=output)
        call_command('seed_owner_timeline_test', stdout=output)
        appointments = list(LichHen.objects.filter(chi_tiet__ghi_chu_thuc_hien=MARKER))
        self.assertEqual(len(appointments), 4)
        self.assertIn('Đã tồn tại: ', output.getvalue())
        self.assertEqual({a.pk for a in appointments}, {'LH101', 'LH102', 'LH103', 'LH104'})
        self.assertEqual(len({timezone.localtime(a.ngay_gio_bat_dau).date() for a in appointments}), 1)
        simultaneous = [a for a in appointments if timezone.localtime(a.ngay_gio_bat_dau).hour == 10]
        self.assertEqual(len(simultaneous), 2)
        self.assertEqual(len({a.phan_cong.get().nhan_vien_id for a in simultaneous}), 2)
        self.assertEqual(sorted(a.trang_thai for a in appointments), sorted(['Chờ xác nhận', 'Đã xác nhận', 'Chờ xác nhận', 'Hủy']))
