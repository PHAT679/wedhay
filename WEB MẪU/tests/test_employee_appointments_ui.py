import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import KhachHang, NhanVien, TaiKhoan
from apps.appointments.models import ChiTietLichHen, LichHen
from apps.assignments.models import PhanCong
from apps.services.models import DichVu


class EmployeeAppointmentsUITests(TestCase):
    def setUp(self):
        self.staff = []
        for i in range(2):
            user = User.objects.create_user(username=f'employee_ui_{i}')
            account = TaiKhoan.objects.create(user=user, vai_tro='Nhân Viên')
            employee = NhanVien.objects.create(tai_khoan=account, ten_nhan_vien=f'Nhân viên {i}')
            self.staff.append((user, employee))
        self.customer = KhachHang.objects.create(ho_ten='Khách kiểm thử', so_dien_thoai='0901234567')
        self.service = DichVu.objects.create(ten_dich_vu='Dịch vụ kiểm thử', gia_tien=80000, thoi_luong=60)
        self.today = timezone.localdate()
        self.client.force_login(self.staff[0][0])

    def make_assignment(self, employee, day, hour=10):
        start = timezone.make_aware(datetime.datetime.combine(day, datetime.time(hour)))
        appointment = LichHen.objects.create(khach_hang=self.customer, ngay_gio_bat_dau=start, ten_lien_he='Khách kiểm thử', so_dien_thoai_lien_he='0901234567')
        ChiTietLichHen.objects.create(lich_hen=appointment, dich_vu=self.service, ten_dich_vu_dat=self.service.ten_dich_vu, don_gia_dat=80000, thoi_luong_dat=60)
        return PhanCong.objects.create(lich_hen=appointment, nhan_vien=employee, trang_thai_tiep_nhan='Chờ phản hồi')

    def test_empty_filter_and_pagination(self):
        dashboard = reverse('employee:dashboard')
        empty = self.client.get(dashboard)
        self.assertContains(empty, 'Chưa có lịch hẹn được phân công')
        self.assertContains(empty, 'Chưa có lịch hẹn được phân công trong ngày này')
        self.assertContains(empty, 'employee-empty-icon')
        self.assertNotContains(empty, '<table')
        self.assertContains(empty, 'employee-date-control')
        self.assertNotContains(empty, 'employee-pagination')
        for i in range(6):
            self.make_assignment(self.staff[0][1], self.today, 9 + i)
        other = self.make_assignment(self.staff[1][1], self.today, 16)
        tomorrow = self.make_assignment(self.staff[0][1], self.today + datetime.timedelta(days=1))
        first = self.client.get(dashboard)
        self.assertEqual(len(first.context['assignments']), 5)
        self.assertContains(first, '<table')
        self.assertNotContains(first, 'employee-empty-icon')
        self.assertNotContains(first, other.lich_hen.pk)
        second = self.client.get(dashboard, {'date': self.today.isoformat(), 'page': 2})
        self.assertEqual(len(second.context['assignments']), 1)
        self.assertContains(second, 'date=' + self.today.isoformat())
        filtered = self.client.get(dashboard, {'date': (self.today + datetime.timedelta(days=1)).isoformat()})
        self.assertContains(filtered, tomorrow.lich_hen.pk)
        empty_day = self.client.get(dashboard, {'date': (self.today + datetime.timedelta(days=2)).isoformat()})
        self.assertContains(empty_day, 'employee-empty-icon')
        self.assertContains(empty_day, 'employee-date-control')
        self.assertNotContains(empty_day, '<table')

    def test_single_page_still_shows_pagination(self):
        self.make_assignment(self.staff[0][1], self.today)
        response = self.client.get(reverse('employee:dashboard'))
        self.assertContains(response, 'class="employee-pagination"')
        self.assertContains(response, 'aria-current="page">1')
        self.assertContains(response, 'aria-disabled="true"', count=4)

    def test_status_priority_and_rejected_detail(self):
        confirmed = self.make_assignment(self.staff[0][1], self.today, 9)
        confirmed.trang_thai_tiep_nhan = 'Đã tiếp nhận'
        confirmed.save(update_fields=['trang_thai_tiep_nhan'])
        rejected = self.make_assignment(self.staff[0][1], self.today, 10)
        rejected.trang_thai_tiep_nhan = 'Từ chối'
        rejected.dang_phu_trach = False
        rejected.save(update_fields=['trang_thai_tiep_nhan', 'dang_phu_trach'])
        pending = self.make_assignment(self.staff[0][1], self.today, 11)
        canceled = self.make_assignment(self.staff[0][1], self.today, 12)
        canceled.lich_hen.trang_thai = 'Hủy'
        canceled.lich_hen.save(update_fields=['trang_thai'])
        page = self.client.get(reverse('employee:dashboard'))
        self.assertEqual([row.pk for row in page.context['assignments']],
                         [pending.pk, confirmed.pk, rejected.pk, canceled.pk])
        self.assertContains(page, 'Đã từ chối')
        detail = self.client.get(reverse('employee:appointment_detail', args=[rejected.lich_hen.pk]))
        self.assertContains(detail, 'Đã từ chối')
        self.assertNotContains(detail, 'Xác nhận lịch</a>')

    def test_detail_permissions_and_existing_actions(self):
        own = self.make_assignment(self.staff[0][1], self.today)
        other = self.make_assignment(self.staff[1][1], self.today, 12)
        detail = self.client.get(reverse('employee:appointment_detail', args=[own.lich_hen.pk]), {'date': self.today.isoformat(), 'page': 2})
        self.assertContains(detail, 'Khách kiểm thử')
        self.assertContains(detail, 'Dịch vụ kiểm thử')
        self.assertContains(detail, 'page=2')
        default_detail = self.client.get(reverse('employee:appointment_detail', args=[own.lich_hen.pk]), {'page': 2})
        self.assertContains(default_detail, reverse('employee:dashboard') + '?page=2')
        denied = self.client.get(reverse('employee:appointment_detail', args=[other.lich_hen.pk]))
        self.assertRedirects(denied, reverse('employee:dashboard'))
        self.assertEqual(self.client.get(reverse('employee:accept_assignment', args=[other.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('employee:reject_assignment', args=[other.pk]), {'ly_do_tu_choi': 'Bận'}).status_code, 404)
        response = self.client.get(reverse('employee:accept_assignment', args=[own.pk]))
        self.assertEqual(response.status_code, 302)
        own.refresh_from_db()
        self.assertEqual(own.trang_thai_tiep_nhan, 'Đã tiếp nhận')
        pending = self.make_assignment(self.staff[0][1], self.today, 14)
        response = self.client.post(reverse('employee:reject_assignment', args=[pending.pk]), {'ly_do_tu_choi': 'Bận việc'})
        self.assertEqual(response.status_code, 302)
        pending.refresh_from_db()
        self.assertEqual(pending.trang_thai_tiep_nhan, 'Từ chối')
        self.assertFalse(pending.dang_phu_trach)

    def test_default_shows_upcoming_dates_but_respects_selected_date(self):
        tomorrow = self.today + datetime.timedelta(days=1)
        assignment = self.make_assignment(self.staff[0][1], tomorrow)
        dashboard = reverse('employee:dashboard')
        response = self.client.get(dashboard)
        self.assertEqual(response.context['selected_date'], self.today)
        self.assertNotContains(response, assignment.lich_hen.pk)
        self.assertContains(self.client.get(dashboard, {'date': tomorrow.isoformat()}), assignment.lich_hen.pk)
        empty = self.client.get(dashboard, {'date': self.today.isoformat()})
        self.assertEqual(empty.context['selected_date'], self.today)
        self.assertContains(empty, 'Chưa có lịch hẹn được phân công')

    def test_upcoming_appointments_ordered_by_creation_and_keep_date_filter(self):
        tomorrow = self.today + datetime.timedelta(days=1)
        later = self.today + datetime.timedelta(days=2)
        confirmed = self.make_assignment(self.staff[0][1], self.today, 9)
        confirmed.trang_thai_tiep_nhan = 'Đã tiếp nhận'
        confirmed.save(update_fields=['trang_thai_tiep_nhan'])
        pending = self.make_assignment(self.staff[0][1], tomorrow, 10)
        for hour in range(9, 14):
            self.make_assignment(self.staff[0][1], later, hour)
        past = self.make_assignment(self.staff[0][1], self.today - datetime.timedelta(days=2), 10)
        canceled = self.make_assignment(self.staff[0][1], tomorrow, 11)
        canceled.lich_hen.trang_thai = 'Hủy'
        canceled.lich_hen.save(update_fields=['trang_thai'])
        url = reverse('employee:dashboard')
        first = self.client.get(url)
        self.assertEqual(first.context['selected_date'], self.today)
        self.assertEqual(first.context['page_obj'].paginator.count, 1)
        self.assertEqual(first.context['assignments'][0].pk, confirmed.pk)
        self.assertNotContains(first, past.lich_hen.pk)
        self.assertNotContains(first, canceled.lich_hen.pk)
        later_page = self.client.get(url, {'date': later.isoformat()})
        self.assertEqual(later_page.context['page_obj'].paginator.count, 5)
        selected = self.client.get(url, {'date': tomorrow.isoformat()})
        self.assertContains(selected, pending.lich_hen.pk)
        self.assertContains(selected, canceled.lich_hen.pk)
        self.assertNotContains(selected, confirmed.lich_hen.pk)
        self.assertEqual(selected.context['assignments'][0].pk, pending.pk)
        previous = self.client.get(url, {'date': (self.today - datetime.timedelta(days=2)).isoformat()})
        self.assertContains(previous, past.lich_hen.pk)

    def test_appointment_creation_order_ignores_assignment_and_status(self):
        confirmed = self.make_assignment(self.staff[0][1], self.today, 9)
        confirmed.trang_thai_tiep_nhan = 'Đã tiếp nhận'
        confirmed.save(update_fields=['trang_thai_tiep_nhan'])
        older = self.make_assignment(self.staff[0][1], self.today, 10)
        newer = self.make_assignment(self.staff[0][1], self.today + datetime.timedelta(days=1), 11)
        newest = self.make_assignment(self.staff[0][1], self.today, 12)
        url = reverse('employee:dashboard')
        result = self.client.get(url)
        self.assertEqual([row.pk for row in result.context['assignments']], [older.pk, newest.pk, confirmed.pk])
        filtered = self.client.get(url, {'date': self.today.isoformat()})
        self.assertEqual([row.pk for row in filtered.context['assignments']], [older.pk, newest.pk, confirmed.pk])

    def test_employee_can_cancel_only_own_confirmed_appointment(self):
        own = self.make_assignment(self.staff[0][1], self.today)
        own.trang_thai_tiep_nhan = 'Đã tiếp nhận'
        own.save()
        own.lich_hen.trang_thai = 'Đã xác nhận'
        own.lich_hen.save()
        url = reverse('employee:cancel_appointment', args=[own.lich_hen.pk])
        detail = self.client.get(reverse('employee:appointment_detail', args=[own.lich_hen.pk]))
        self.assertContains(detail, 'Hủy lịch hẹn')
        self.assertEqual(self.client.get(url).status_code, 405)
        other_client = self.client_class()
        other_client.force_login(self.staff[1][0])
        self.assertEqual(other_client.post(url).status_code, 404)
        secured = self.client_class(enforce_csrf_checks=True)
        secured.force_login(self.staff[0][0])
        self.assertEqual(secured.post(url).status_code, 403)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        canceled_page = self.client.get(response.url)
        self.assertContains(canceled_page, 'Đã hủy lịch hẹn của khách hàng.')
        self.assertContains(canceled_page, 'employee-status canceled')
        own.lich_hen.refresh_from_db()
        self.assertEqual(own.lich_hen.trang_thai, 'Hủy')
        self.assertEqual(own.lich_hen.tai_khoan_huy, self.staff[0][1].tai_khoan)
        self.assertIsNotNone(own.lich_hen.thoi_diem_huy)
        self.assertNotContains(self.client.get(reverse('employee:appointment_detail', args=[own.lich_hen.pk])), 'Hủy lịch hẹn</button>')
        self.client.post(url)
        own.lich_hen.refresh_from_db()
        self.assertEqual(own.lich_hen.trang_thai, 'Hủy')

    def test_employee_cannot_cancel_unaccepted_or_completed_appointment(self):
        assignment = self.make_assignment(self.staff[0][1], self.today)
        url = reverse('employee:cancel_appointment', args=[assignment.lich_hen.pk])
        self.assertEqual(self.client.post(url).status_code, 404)
        assignment.trang_thai_tiep_nhan = 'Đã tiếp nhận'
        assignment.save()
        assignment.lich_hen.trang_thai = 'Hoàn thành'
        assignment.lich_hen.save()
        self.assertEqual(self.client.post(url).status_code, 302)
        assignment.lich_hen.refresh_from_db()
        self.assertEqual(assignment.lich_hen.trang_thai, 'Hoàn thành')

    def test_list_displays_receipt_status_for_completed_appointments(self):
        pending = self.make_assignment(self.staff[0][1], self.today, 9)
        accepted = self.make_assignment(self.staff[0][1], self.today, 10)
        canceled = self.make_assignment(self.staff[0][1], self.today, 11)
        completed_pending = self.make_assignment(self.staff[0][1], self.today, 12)
        for assignment in (accepted, completed_pending):
            assignment.lich_hen.trang_thai = 'Hoàn thành'
            assignment.lich_hen.save()
        accepted.trang_thai_tiep_nhan = 'Đã tiếp nhận'
        accepted.save()
        canceled.lich_hen.trang_thai = 'Hủy'
        canceled.lich_hen.save()
        response = self.client.get(reverse('employee:dashboard'), {'date': self.today.isoformat()})
        self.assertContains(response, 'class="employee-status pending">Chờ xác nhận', count=2)
        self.assertContains(response, 'class="employee-status confirmed">Đã xác nhận', count=1)
        self.assertContains(response, 'class="employee-status canceled">Đã hủy', count=1)
        self.assertNotContains(response, '>Hoàn thành<')
