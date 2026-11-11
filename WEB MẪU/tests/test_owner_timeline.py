import datetime
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import DatabaseError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import KhachHang, NhanVien, TaiKhoan
from apps.appointments.models import ChiTietLichHen, LichHen
from apps.assignments.models import PhanCong
from apps.appointments.services import get_available_slots
from apps.payments.models import GiaoDich
from apps.notifications.models import ThongBao
from apps.services.models import DichVu


class OwnerTimelineTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user('timeline_owner')
        TaiKhoan.objects.create(user=owner, vai_tro='Chủ Tiệm')
        staff = User.objects.create_user('timeline_staff')
        account = TaiKhoan.objects.create(user=staff, vai_tro='Nhân Viên')
        self.staff = NhanVien.objects.create(tai_khoan=account, ten_nhan_vien='Nhân viên kiểm thử')
        self.customer = KhachHang.objects.create(ho_ten='Khách kiểm thử', so_dien_thoai='0901234567')
        self.service = DichVu.objects.create(ten_dich_vu='Dịch vụ kiểm thử', gia_tien=80000, thoi_luong=60)
        self.day = timezone.localdate()
        self.client.force_login(owner)

    def make_appointment(self, day, hour, status):
        start = timezone.make_aware(datetime.datetime.combine(day, datetime.time(hour)))
        appointment = LichHen.objects.create(khach_hang=self.customer, ngay_gio_bat_dau=start, ten_lien_he='Khách kiểm thử', so_dien_thoai_lien_he='0901234567', trang_thai=status)
        ChiTietLichHen.objects.create(lich_hen=appointment, dich_vu=self.service, ten_dich_vu_dat=self.service.ten_dich_vu, don_gia_dat=80000, thoi_luong_dat=60)
        PhanCong.objects.create(lich_hen=appointment, nhan_vien=self.staff)
        return appointment

    def test_date_slots_multiple_appointments_and_pagination(self):
        first = self.make_appointment(self.day, 10, 'Chờ xác nhận')
        second = self.make_appointment(self.day, 10, 'Đã xác nhận')
        other_day = self.make_appointment(self.day + datetime.timedelta(days=1), 10, 'Hủy')
        url = reverse('owner:timeline')
        response = self.client.get(url, {'date': self.day.isoformat()})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([block['time_str'] for block in response.context['timeline_blocks']],
                         ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30'])
        self.assertContains(response, first.pk)
        self.assertContains(response, second.pk)
        shown = [a.pk for block in response.context['timeline_blocks'] for a in block['appointments']]
        self.assertEqual(shown.count(first.pk), 1)
        self.assertEqual(shown.count(second.pk), 1)
        self.assertNotContains(response, other_day.pk)
        self.assertContains(response, 'Dịch vụ kiểm thử')
        self.assertContains(response, 'Nhân viên kiểm thử')
        self.assertContains(response, 'Khung giờ còn trống')
        self.assertContains(response, reverse('owner:status_list'))
        self.assertContains(response, 'href="' + reverse('owner:status_list') + '"')
        self.assertContains(response, 'date=' + self.day.isoformat() + '&amp;page=2')
        page = self.client.get(url, {'date': self.day.isoformat(), 'page': 2})
        self.assertEqual([block['time_str'] for block in page.context['timeline_blocks']],
                         ['12:00', '12:30', '13:00', '13:30', '14:00', '14:30'])
        page = self.client.get(url, {'date': self.day.isoformat(), 'page': 4})
        self.assertEqual(len(page.context['timeline_blocks']), 2)
        self.assertContains(page, '18:30')
        next_day = self.client.get(url, {'date': (self.day + datetime.timedelta(days=1)).isoformat()})
        self.assertContains(next_day, other_day.pk)
        self.assertContains(next_day, 'Đã hủy')
        self.assertNotContains(next_day, first.pk)

    def test_timeline_empty_only_when_entire_day_has_no_appointments(self):
        url = reverse('owner:timeline')
        empty = self.client.get(url)
        self.assertEqual(empty.context['selected_date'], self.day)
        self.assertContains(empty, 'Ngày này chưa có lịch hẹn')
        self.assertContains(empty, 'Bạn có thể chọn một ngày khác để xem lịch hẹn.')
        self.assertNotContains(empty, 'class="tracking-row"')
        self.assertNotContains(empty, 'tracking-pagination')
        appointment = self.make_appointment(self.day, 16, 'Hủy')
        first_page = self.client.get(url, {'date': self.day.isoformat()})
        self.assertNotContains(first_page, 'Ngày này chưa có lịch hẹn')
        self.assertContains(first_page, 'class="tracking-row"')
        self.assertContains(first_page, 'tracking-pagination')
        last_page = self.client.get(url, {'date': self.day.isoformat(), 'page': 3})
        self.assertContains(last_page, appointment.pk)
        empty_other_day = self.client.get(url, {'date': (self.day + datetime.timedelta(days=1)).isoformat()})
        self.assertContains(empty_other_day, 'Ngày này chưa có lịch hẹn')

    def test_timeline_database_error_and_retry(self):
        day = self.day + datetime.timedelta(days=1)
        appointment = self.make_appointment(day, 10, 'Đã xác nhận')
        url = reverse('owner:timeline')
        with patch('apps.appointments.views.LichHen.objects.filter', side_effect=DatabaseError('test error')):
            with self.assertLogs('apps.appointments.views', level='ERROR'):
                response = self.client.get(url, {'date': day.isoformat()})
        self.assertEqual(response.status_code, 503)
        self.assertContains(response, 'Không thể tải dữ liệu lịch hẹn', status_code=503)
        self.assertContains(response, 'Thử lại', status_code=503)
        self.assertContains(response, day.isoformat(), status_code=503)
        self.assertNotContains(response, 'Ngày này chưa có lịch hẹn', status_code=503)
        self.assertNotContains(response, 'tracking-pagination', status_code=503)
        retry = self.client.get(url, {'date': day.isoformat()})
        self.assertContains(retry, appointment.pk)
        self.assertNotContains(retry, 'Không thể tải dữ liệu lịch hẹn')

    def test_owner_sidebar_routes_and_active_item(self):
        links = [
            ('owner:dashboard', 'Tổng quan'),
            ('owner:timeline', 'Theo dõi lịch hẹn'),
            ('owner:services_list', 'Quản lý dịch vụ'),
            ('owner:assignments_list', 'Quản lý phân công'),
            ('owner:customers_list', 'Quản lý khách hàng'),
        ]
        for route, label in links:
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertEqual(response.status_code, 200)
                sidebar = response.content.decode().split('<aside', 1)[1].split('</aside>', 1)[0]
                self.assertEqual(sidebar.count('class="nav-item '), 5)
                self.assertEqual(sidebar.count('nav-item active'), 1)
                for target, text in links:
                    self.assertIn('href="' + reverse(target) + '"', sidebar)
                    self.assertIn(text, sidebar)
                active_item = sidebar.split('nav-item active', 1)[1].split('</li>', 1)[0]
                self.assertIn(label, active_item)

    def test_timeline_detail_uses_selected_appointment_and_returns_to_date(self):
        appointment = self.make_appointment(self.day, 10, 'Đã xác nhận')
        url = reverse('owner:timeline_detail', args=[appointment.pk])
        response = self.client.get(url, {'date': self.day.isoformat(), 'page': 2})
        self.assertEqual(response.status_code, 200)
        for value in (appointment.pk, 'Khách kiểm thử', '0901234567', 'Dịch vụ kiểm thử', 'Nhân viên kiểm thử', 'Đã xác nhận', '60 phút'):
            self.assertContains(response, value)
        self.assertContains(response, 'date=' + self.day.isoformat() + '&amp;page=2')
        self.assertContains(response, reverse('owner:timeline'))
        self.assertEqual(self.client.get(reverse('owner:timeline_detail', args=['missing'])).status_code, 404)
        self.client.logout()
        self.assertNotEqual(self.client.get(url).status_code, 200)

    def test_details_hide_assigned_staff_while_awaiting_owner_confirmation(self):
        appointment = self.make_appointment(self.day, 10, 'Chờ xác nhận')
        timeline_url = reverse('owner:timeline_detail', args=[appointment.pk])
        standard_url = reverse('owner:appointment_detail', args=[appointment.pk])
        timeline = self.client.get(timeline_url)
        self.assertContains(timeline, 'Chưa phân công')
        self.assertNotContains(timeline, self.staff.ten_nhan_vien)
        standard = self.client.get(standard_url)
        self.assertContains(standard, 'Chưa phân công')
        self.assertNotContains(standard, self.staff.ten_nhan_vien)
        appointment.trang_thai = 'Đã xác nhận'
        appointment.save(update_fields=['trang_thai'])
        self.assertContains(self.client.get(timeline_url), self.staff.ten_nhan_vien)
        self.assertContains(self.client.get(standard_url), self.staff.ten_nhan_vien)
        appointment.phan_cong.update(dang_phu_trach=False)
        self.assertContains(self.client.get(timeline_url), 'Chưa phân công')

    def test_new_booking_notifications_open_status_update(self):
        owner = User.objects.get(username='timeline_owner')
        appointment = self.make_appointment(self.day, 10, 'Chờ xác nhận')
        old_url = reverse('owner:appointment_detail', args=[appointment.pk])
        status_url = reverse('owner:status_edit', args=[appointment.pk])
        for link in (old_url, status_url):
            with self.subTest(link=link):
                notice = ThongBao.objects.create(tai_khoan=owner.tai_khoan,
                    tieu_de='Lịch hẹn mới cần xác nhận', noi_dung='Thông báo kiểm thử',
                    loai_thong_bao='Lịch mới', lien_ket=link)
                response = self.client.get(reverse('notifications:mark_read', args=[notice.pk]))
                self.assertRedirects(response, status_url)
                notice.refresh_from_db()
                self.assertTrue(notice.da_doc)
                self.assertContains(self.client.get(status_url), appointment.pk)
        other = ThongBao.objects.create(tai_khoan=owner.tai_khoan,
            tieu_de='Khách hàng đã đổi lịch hẹn', noi_dung='Thông báo kiểm thử',
            loai_thong_bao='Đổi lịch', lien_ket=old_url)
        self.assertRedirects(self.client.get(reverse('notifications:mark_read', args=[other.pk])), old_url)

    def test_customer_booking_creates_status_update_notification_link(self):
        customer_user = User.objects.create_user('booking_notification_customer')
        TaiKhoan.objects.create(user=customer_user, vai_tro='Khách Hàng', khach_hang=self.customer)
        self.client.force_login(customer_user)
        date = self.day + datetime.timedelta(days=1)
        with patch('apps.appointments.views.get_available_slots', return_value=[{'time_str': '09:00', 'available': True}]):
            response = self.client.post(reverse('customer:booking'), {
                'service_ids': [self.service.pk], 'booking_date': date.isoformat(), 'booking_time': '09:00',
                'contact_name': self.customer.ho_ten, 'contact_phone': self.customer.so_dien_thoai,
            })
        self.assertEqual(response.status_code, 302)
        appointment = LichHen.objects.get(khach_hang=self.customer)
        notice = ThongBao.objects.get(tieu_de='Lịch hẹn mới cần xác nhận')
        self.assertEqual(notice.lien_ket, reverse('owner:status_edit', args=[appointment.pk]))

    def test_owner_notification_dropdown_without_view_all_page(self):
        owner = User.objects.get(username='timeline_owner')
        notification = ThongBao.objects.create(
            tai_khoan=owner.tai_khoan, tieu_de='Thông báo kiểm thử', noi_dung='Nội dung',
            loai_thong_bao='Lịch mới', lien_ket=reverse('owner:assignments_list'),
        )
        for url in (reverse('owner:dashboard'),):
            page = self.client.get(url)
            self.assertNotContains(page, 'Xem tất cả')
            self.assertContains(page, 'Thông báo kiểm thử')
            self.assertContains(page, reverse('notifications:mark_read', args=[notification.pk]))
            self.assertContains(page, reverse('notifications:mark_all_read'))
        response = self.client.get(reverse('notifications:list'))
        self.assertRedirects(response, reverse('owner:dashboard'))
        notification.refresh_from_db()
        self.assertFalse(notification.da_doc)
        selected = self.client.get(reverse('notifications:mark_read', args=[notification.pk]))
        self.assertRedirects(selected, reverse('owner:assignments_list'))
        notification.refresh_from_db()
        self.assertTrue(notification.da_doc)
        back = self.client.get(reverse('notifications:mark_all_read'), HTTP_REFERER='http://testserver' + reverse('owner:assignments_list'))
        self.assertEqual(back.url, 'http://testserver' + reverse('owner:assignments_list'))
        unsafe = self.client.get(reverse('notifications:mark_all_read'), HTTP_REFERER='https://example.com/')
        self.assertRedirects(unsafe, reverse('owner:dashboard'))
        self.client.force_login(self.staff.tai_khoan.user)
        employee_page = self.client.get(reverse('notifications:list'))
        self.assertEqual(employee_page.status_code, 200)
        self.assertContains(employee_page, 'Thông Báo Hệ Thống')
        self.assertNotContains(employee_page, 'class="nav-brand"')
        self.assertContains(self.client.get(reverse('employee:dashboard')), 'Xem tất cả')

    def test_employee_rejection_notification_read_and_keep_appointment(self):
        appointment = self.make_appointment(self.day, 10, 'Đã xác nhận')
        assignment = appointment.phan_cong.get(dang_phu_trach=True)
        owner = User.objects.get(username='timeline_owner')
        self.client.force_login(self.staff.tai_khoan.user)
        response = self.client.post(reverse('employee:reject_assignment', args=[assignment.pk]), {'ly_do_tu_choi': 'Có việc gia đình'})
        self.assertEqual(response.status_code, 302)
        assignment.refresh_from_db()
        self.assertEqual(assignment.trang_thai_tiep_nhan, 'Từ chối')
        notification = ThongBao.objects.get(tai_khoan=owner.tai_khoan, loai_thong_bao='Từ chối')
        self.assertFalse(notification.da_doc)
        for text in (appointment.pk, appointment.ten_lien_he, self.service.ten_dich_vu, self.staff.ten_nhan_vien, 'Có việc gia đình'):
            self.assertIn(text, notification.noi_dung)
        self.client.force_login(owner)
        status_url = reverse('notifications:owner_status')
        status = self.client.get(status_url).json()
        self.assertIn(notification.pk, status['rejection_ids'])
        self.assertEqual(status['count'], 1)
        self.client.get(reverse('notifications:list'))
        self.client.get(reverse('notifications:mark_all_read'))
        notification.refresh_from_db()
        self.assertFalse(notification.da_doc)
        entry = self.client.get(reverse('notifications:mark_read', args=[notification.pk]))
        notification.refresh_from_db()
        self.assertFalse(notification.da_doc)
        detail = self.client.get(entry.url)
        self.assertEqual(detail.status_code, 200)
        for text in (appointment.pk, appointment.ten_lien_he, self.service.ten_dich_vu, self.staff.ten_nhan_vien, 'Có việc gia đình', 'Từ chối lý do', 'Phân công lại'):
            self.assertContains(detail, text)
        notification.refresh_from_db()
        self.assertTrue(notification.da_doc)
        self.assertEqual(self.client.get(status_url).json()['count'], 0)
        keep = self.client.post(reverse('owner:rejection_keep', args=[assignment.pk]), {'notification': notification.pk})
        self.assertRedirects(keep, reverse('owner:assignments_list'))
        appointment.refresh_from_db()
        self.assertEqual(appointment.trang_thai, 'Đã xác nhận')
        self.assertFalse(appointment.phan_cong.filter(dang_phu_trach=True).exists())
        self.assertContains(self.client.get(reverse('owner:assignments_list')), appointment.pk)

    def test_rejection_notification_owner_cannot_access_others(self):
        appointment = self.make_appointment(self.day, 10, 'Đã xác nhận')
        assignment = appointment.phan_cong.get(dang_phu_trach=True)
        self.client.force_login(self.staff.tai_khoan.user)
        self.client.post(reverse('employee:reject_assignment', args=[assignment.pk]), {'ly_do_tu_choi': 'Bận'})
        notification = ThongBao.objects.get(loai_thong_bao='Từ chối')
        another_user = User.objects.create_user('other_owner')
        TaiKhoan.objects.create(user=another_user, vai_tro='Chủ Tiệm')
        self.client.force_login(another_user)
        detail_url = reverse('owner:rejection_detail', args=[assignment.pk])
        self.assertEqual(self.client.get(detail_url, {'notification': notification.pk}).status_code, 404)
        self.assertEqual(self.client.post(reverse('owner:rejection_keep', args=[assignment.pk]), {'notification': notification.pk}).status_code, 404)
        notification.refresh_from_db()
        self.assertFalse(notification.da_doc)

    def test_owner_header_account_logout_and_bell(self):
        owner = User.objects.get(username='timeline_owner')
        owner.first_name = 'Trần Bảo Nguyên'
        owner.save(update_fields=['first_name'])
        notification = ThongBao.objects.create(tai_khoan=owner.tai_khoan, tieu_de='Kiểm thử', noi_dung='Nội dung', loai_thong_bao='Từ chối')
        appointment = self.make_appointment(self.day, 10, 'Đã xác nhận')
        for url in (reverse('owner:dashboard'), reverse('owner:assign_staff', args=[appointment.pk])):
            with self.subTest(url=url):
                page = self.client.get(url)
                self.assertContains(page, 'Trần Bảo Nguyên')
                self.assertContains(page, 'class="overview-avatar">T')
                self.assertContains(page, 'Chủ tiệm')
                self.assertContains(page, 'class="overview-account-menu"')
                self.assertContains(page, reverse('accounts:logout'))
                self.assertContains(page, 'class="bell-counter">1')
                self.assertContains(page, 'owner-header-account.js')
                self.assertContains(page, 'owner-rejection-bell.js')
        notification.refresh_from_db()
        self.assertFalse(notification.da_doc)
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(self.client.get(reverse('owner:dashboard')).status_code, 302)
        self.client.force_login(self.staff.tai_khoan.user)
        self.assertNotContains(self.client.get(reverse('employee:dashboard')), 'owner-header-account.js')

    def test_owner_and_employee_sidebar_brand_is_not_a_link(self):
        for url in (reverse('owner:dashboard'), reverse('owner:assignments_list')):
            with self.subTest(url=url):
                page = self.client.get(url).content.decode()
                brand = page.split('<div class="sidebar-brand">', 1)[1].split('</div>', 1)[0]
                self.assertIn('class="sidebar-logo"', brand)
                self.assertNotIn('<a ', brand)
                self.assertNotIn('onclick', brand)
        self.client.force_login(self.staff.tai_khoan.user)
        page = self.client.get(reverse('employee:dashboard')).content.decode()
        brand = page.split('<div class="sidebar-brand">', 1)[1].split('</div>', 1)[0]
        self.assertIn('class="sidebar-logo"', brand)
        self.assertNotIn('<a ', brand)
        self.assertNotIn('onclick', brand)
        self.client.logout()
        public = self.client.get(reverse('home')).content.decode()
        self.assertIn('class="nav-brand"', public)

    def test_assignment_navigation_remains_available(self):
        appointment = self.make_appointment(self.day, 10, 'Đã xác nhận')
        assignment_url = reverse('owner:assign_staff', args=[appointment.pk])
        listing = self.client.get(reverse('owner:assignments_list'), {'mode': 'change'})
        self.assertContains(listing, assignment_url)
        form = self.client.get(assignment_url)
        self.assertContains(form, 'Chọn kỹ thuật viên')
        self.assertContains(form, appointment.pk)
        result = self.client.post(assignment_url, {'nhan_vien_id': self.staff.pk})
        self.assertRedirects(result, reverse('owner:appointment_detail', args=[appointment.pk]))
        self.assertEqual(appointment.phan_cong.filter(dang_phu_trach=True).count(), 1)
        detail = self.client.get(reverse('owner:appointment_detail', args=[appointment.pk]))
        self.assertTemplateUsed(detail, 'owner/timeline_detail.html')
        self.assertNotContains(detail, 'Phân Công Kỹ Thuật Viên (UC 5)')

    def test_change_assignment_screen_displays_current_and_available_staff(self):
        appointment = self.make_appointment(self.day, 10, 'Đã xác nhận')
        other_user = User.objects.create_user('replacement_staff')
        other_account = TaiKhoan.objects.create(user=other_user, vai_tro='Nhân Viên')
        replacement = NhanVien.objects.create(tai_khoan=other_account, ten_nhan_vien='Nhân viên thay thế')
        url = reverse('owner:assign_staff', args=[appointment.pk])
        listing = self.client.get(reverse('owner:assignments_list'), {'mode': 'change'})
        self.assertContains(listing, url + '?change=1')
        page = self.client.get(url, {'change': '1'})
        self.assertContains(page, 'Chọn nhân viên mới thay thế nhân viên hiện tại')
        self.assertContains(page, 'Nhân viên hiện tại: ' + self.staff.ten_nhan_vien)
        self.assertContains(page, replacement.ten_nhan_vien)
        self.assertContains(page, 'Tiếp tục')
        self.assertNotContains(page, 'name="from_assignment_selection"')
        response = self.client.post(url, {'nhan_vien_id': replacement.pk})
        self.assertRedirects(response, reverse('owner:appointment_detail', args=[appointment.pk]))
        self.assertEqual(appointment.phan_cong.get(dang_phu_trach=True).nhan_vien, replacement)

    def test_change_assignment_preview_and_final_confirmation(self):
        appointment = self.make_appointment(self.day, 10, 'Đã xác nhận')
        user = User.objects.create_user('preview_staff')
        account = TaiKhoan.objects.create(user=user, vai_tro='Nhân Viên')
        replacement = NhanVien.objects.create(tai_khoan=account, ten_nhan_vien='Nhân viên mới')
        url = reverse('owner:assign_staff', args=[appointment.pk])
        preview = self.client.post(url, {'nhan_vien_id': replacement.pk, 'preview_change': '1'})
        self.assertContains(preview, 'Xác nhận thay đổi phân công')
        self.assertContains(preview, self.staff.ten_nhan_vien)
        self.assertContains(preview, replacement.ten_nhan_vien)
        self.assertContains(preview, 'Không trùng lịch')
        self.assertContains(preview, url + '?change=1')
        self.assertEqual(appointment.phan_cong.get(dang_phu_trach=True).nhan_vien, self.staff)
        response = self.client.post(url, {'nhan_vien_id': replacement.pk, 'from_change_confirmation': '1'})
        success_url = reverse('owner:assignment_success', args=[appointment.pk])
        self.assertRedirects(response, success_url, fetch_redirect_response=False)
        self.assertEqual(appointment.phan_cong.get(dang_phu_trach=True).nhan_vien, replacement)
        page = self.client.get(success_url)
        self.assertContains(page, 'Thay đổi phân công thành công')
        self.assertContains(page, 'Thông tin nhân viên mới đã được cập nhật')
        self.assertContains(page, appointment.pk)
        self.assertContains(page, appointment.ten_lien_he)
        self.assertContains(page, reverse('owner:assignments_list'))
        self.assertNotContains(page, 'Phân công nhân viên thành công')

    def test_change_assignment_rechecks_conflicts_after_preview(self):
        appointment = self.make_appointment(self.day, 10, 'Đã xác nhận')
        user = User.objects.create_user('later_busy_staff')
        account = TaiKhoan.objects.create(user=user, vai_tro='Nhân Viên')
        replacement = NhanVien.objects.create(tai_khoan=account, ten_nhan_vien='Nhân viên mới')
        url = reverse('owner:assign_staff', args=[appointment.pk])
        preview = self.client.post(url, {'nhan_vien_id': replacement.pk, 'preview_change': '1'})
        self.assertContains(preview, 'Không trùng lịch')
        busy = self.make_appointment(self.day, 10, 'Đã xác nhận')
        busy.phan_cong.update(dang_phu_trach=False)
        PhanCong.objects.create(lich_hen=busy, nhan_vien=replacement)
        response = self.client.post(url, {'nhan_vien_id': replacement.pk}, follow=True)
        self.assertContains(response, 'bị trùng lịch')
        self.assertEqual(appointment.phan_cong.get(dang_phu_trach=True).nhan_vien, self.staff)

    def test_assignment_success_page_after_successful_selection_only(self):
        appointment = self.make_appointment(self.day, 10, 'Đã xác nhận')
        appointment.phan_cong.update(dang_phu_trach=False)
        success_url = reverse('owner:assignment_success', args=[appointment.pk])
        self.assertRedirects(self.client.get(success_url), reverse('owner:assignments_list'))
        response = self.client.post(reverse('owner:assign_staff', args=[appointment.pk]), {
            'nhan_vien_id': self.staff.pk, 'from_assignment_selection': '1',
        })
        self.assertRedirects(response, success_url, fetch_redirect_response=False)
        self.assertTrue(appointment.phan_cong.filter(dang_phu_trach=True, nhan_vien=self.staff).exists())
        page = self.client.get(success_url)
        self.assertContains(page, 'Phân công nhân viên thành công')
        self.assertContains(page, appointment.pk)
        self.assertContains(page, appointment.ten_lien_he)
        self.assertContains(page, self.service.ten_dich_vu)
        self.assertContains(page, reverse('owner:assignments_list'))
        self.assertRedirects(self.client.get(success_url), reverse('owner:assignments_list'))

    def test_assignment_form_displays_real_staff_availability(self):
        busy = self.make_appointment(self.day, 10, 'Đã xác nhận')
        target = self.make_appointment(self.day, 10, 'Chờ xác nhận')
        target.phan_cong.update(dang_phu_trach=False)
        free_user = User.objects.create_user('available_staff')
        free_account = TaiKhoan.objects.create(user=free_user, vai_tro='Nhân Viên')
        free_staff = NhanVien.objects.create(tai_khoan=free_account, ten_nhan_vien='Nhân viên còn trống')
        page = self.client.get(reverse('owner:assign_staff', args=[target.pk]))
        self.assertContains(page, target.pk)
        self.assertContains(page, target.ten_lien_he)
        self.assertContains(page, self.service.ten_dich_vu)
        options = {entry['employee'].pk: entry for entry in page.context['employee_options']}
        self.assertEqual(options[self.staff.pk]['conflict'].pk, busy.pk)
        self.assertIsNone(options[free_staff.pk]['conflict'])
        self.assertContains(page, 'Đã có lịch')
        self.assertContains(page, 'Trống lịch')
        self.assertContains(page, 'disabled')
        self.assertContains(page, 'Xác nhận phân công')

    def test_assignment_empty_state_only_when_no_pending_appointments(self):
        url = reverse('owner:assignments_list')
        empty = self.client.get(url)
        self.assertContains(empty, 'Không có dữ liệu lịch hẹn')
        self.assertContains(empty, 'Hiện không có lịch hẹn cần phân công')
        self.assertNotContains(empty, '<table class="assignment-table">', html=False)
        appointment = self.make_appointment(self.day, 9, 'Đã xác nhận')
        appointment.phan_cong.update(dang_phu_trach=False)
        populated = self.client.get(url)
        self.assertContains(populated, appointment.pk)
        self.assertContains(populated, '<table class="assignment-table">', html=False)
        self.assertNotContains(populated, 'Không có dữ liệu lịch hẹn')
        no_match = self.client.get(url, {'q': 'không tồn tại'})
        self.assertContains(no_match, 'Không tìm thấy lịch hẹn')
        self.assertNotContains(no_match, 'Không có dữ liệu lịch hẹn')
        with patch('apps.assignments.views.LichHen.objects.filter', side_effect=DatabaseError('database unavailable')):
            with self.assertRaises(DatabaseError):
                self.client.get(url)

    def test_assignment_pagination_in_both_modes_preserves_search(self):
        pending = []
        assigned = []
        for _ in range(6):
            appointment = self.make_appointment(self.day, 9, 'Đã xác nhận')
            appointment.phan_cong.update(dang_phu_trach=False)
            pending.append(appointment.pk)
            assigned.append(self.make_appointment(self.day, 10, 'Đã xác nhận').pk)
        url = reverse('owner:assignments_list')
        for mode, expected in [('pending', pending), ('change', assigned)]:
            with self.subTest(mode=mode):
                params = {'mode': mode, 'q': 'Khách kiểm thử'}
                first = self.client.get(url, params)
                second = self.client.get(url, {**params, 'page': 2})
                first_ids = [item.pk for item in first.context['appointments']]
                second_ids = [item.pk for item in second.context['appointments']]
                self.assertEqual((len(first_ids), len(second_ids)), (4, 2))
                self.assertFalse(set(first_ids) & set(second_ids))
                self.assertEqual(set(first_ids + second_ids), set(expected))
                self.assertContains(first, 'mode=' + mode)
                self.assertContains(first, 'page=2')
                self.assertContains(first, 'q=Kh%C3%A1ch')
                self.assertContains(second, 'aria-current="page">2')
                single = self.client.get(url, {'mode': mode, 'q': expected[0]})
                self.assertEqual(len(single.context['appointments']), 1)
                self.assertContains(single, 'aria-current="page">1')
                self.assertContains(single, 'aria-disabled="true"', count=4)

    def test_assignment_list_filters_search_and_change_navigation(self):
        pending = self.make_appointment(self.day, 9, 'Chờ xác nhận')
        pending.phan_cong.update(dang_phu_trach=False)
        assigned = self.make_appointment(self.day, 10, 'Đã xác nhận')
        canceled = self.make_appointment(self.day, 11, 'Hủy')
        canceled.phan_cong.update(dang_phu_trach=False)
        url = reverse('owner:assignments_list')
        listing = self.client.get(url)
        self.assertContains(listing, pending.pk)
        self.assertNotContains(listing, assigned.pk)
        self.assertNotContains(listing, canceled.pk)
        self.assertContains(listing, reverse('owner:assign_staff', args=[pending.pk]))
        self.assertContains(self.client.get(url, {'q': pending.pk}), pending.pk)
        self.assertContains(self.client.get(url, {'q': 'Khách kiểm thử'}), pending.pk)
        self.assertNotContains(self.client.get(url, {'q': 'không tồn tại'}), pending.pk)
        change = self.client.get(url, {'mode': 'change'})
        self.assertContains(change, assigned.pk)
        self.assertNotContains(change, pending.pk)
        self.assertContains(change, reverse('owner:assign_staff', args=[assigned.pk]))
        self.assertContains(self.client.get(reverse('owner:assign_staff', args=[assigned.pk])), 'Thay Đổi Phân Công')

    def test_status_list_defaults_all_dates_sorted_before_pagination(self):
        url = reverse('owner:status_list')
        specifications = [
            (2, 12, 'Hủy'), (1, 12, 'Hoàn thành'), (0, 12, 'Đã xác nhận'),
            (2, 10, 'Chờ xác nhận'), (0, 10, 'Chờ xác nhận'), (1, 10, 'Chờ xác nhận'),
            (0, 9, 'Đã xác nhận'), (0, 8, 'Hoàn thành'), (0, 7, 'Hủy'),
        ]
        items = [self.make_appointment(self.day + datetime.timedelta(days=day), hour, status)
                 for day, hour, status in specifications]
        first = self.client.get(url)
        second = self.client.get(url, {'page': 2})
        self.assertEqual(first.context['selected_date'], self.day)
        self.assertContains(first, 'name="date" placeholder="dd/mm/yyyy" value="' + self.day.isoformat() + '"')
        combined = list(first.context['page_obj']) + list(second.context['page_obj'])
        expected = sorted(items, key=lambda item: (item.thoi_diem_tao, item.pk))
        self.assertEqual([item.pk for item in combined], [item.pk for item in expected if timezone.localtime(item.ngay_gio_bat_dau).date() == self.day])
        self.assertContains(first, '?date=' + self.day.isoformat(), html=False)
        self.assertContains(first, '?date=' + (self.day - datetime.timedelta(days=1)).isoformat(), html=False)
        self.assertContains(first, '?date=' + (self.day + datetime.timedelta(days=1)).isoformat(), html=False)
        filtered = self.client.get(url, {'date': self.day.isoformat()})
        shown = list(filtered.context['page_obj']) + list(self.client.get(url, {'date': self.day.isoformat(), 'page': 2}).context['page_obj'])
        self.assertEqual([item.pk for item in shown], [item.pk for item in expected if timezone.localtime(item.ngay_gio_bat_dau).date() == self.day])
        cleared = self.client.get(url, {'date': ''})
        self.assertEqual(cleared.context['selected_date'], self.day)
        self.assertEqual(cleared.context['page_obj'].paginator.count, len(combined))

    def test_status_list_orders_by_booking_creation_instead_of_appointment_date(self):
        yesterday = self.make_appointment(self.day - datetime.timedelta(days=1), 9, 'Chờ xác nhận')
        tomorrow = self.make_appointment(self.day + datetime.timedelta(days=1), 9, 'Chờ xác nhận')
        today_later = self.make_appointment(self.day, 12, 'Chờ xác nhận')
        today_earlier = self.make_appointment(self.day, 9, 'Chờ xác nhận')
        after_tomorrow = self.make_appointment(self.day + datetime.timedelta(days=2), 9, 'Chờ xác nhận')
        confirmed = self.make_appointment(self.day, 8, 'Đã xác nhận')
        url = reverse('owner:status_list')
        first = self.client.get(url)
        actual = list(first.context['page_obj'])
        self.assertEqual([item.pk for item in actual], [today_later.pk, today_earlier.pk, confirmed.pk])
        filtered = self.client.get(url, {'date': (self.day - datetime.timedelta(days=1)).isoformat()})
        self.assertContains(filtered, yesterday.pk)

    def test_status_list_filters_paginates_and_links_to_detail(self):
        items = [self.make_appointment(self.day, 9 + i, 'Chờ xác nhận') for i in range(6)]
        other = self.make_appointment(self.day + datetime.timedelta(days=1), 10, 'Hủy')
        url = reverse('owner:status_list')
        response = self.client.get(url, {'date': self.day.isoformat()})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 4)
        self.assertContains(response, items[0].pk)
        self.assertNotContains(response, other.pk)
        self.assertContains(response, reverse('owner:status_edit', args=[items[0].pk]))
        page = self.client.get(url, {'date': self.day.isoformat(), 'page': 2})
        self.assertEqual(len(page.context['page_obj']), 2)
        self.assertContains(response, 'date=' + self.day.isoformat() + '&amp;page=2')
        self.assertContains(page, items[5].pk)
        status_detail = self.client.get(reverse('owner:status_edit', args=[items[5].pk]),
                                        {'date': self.day.isoformat(), 'page': 2})
        self.assertEqual(status_detail.status_code, 200)
        self.assertContains(status_detail, reverse('owner:status_list') + '?date=' + self.day.isoformat() + '&amp;page=2')
        detail = self.client.get(reverse('owner:appointment_detail', args=[items[5].pk]), {'from_status': '1', 'date': self.day.isoformat(), 'page': 2})
        self.assertContains(detail, 'date=' + self.day.isoformat() + '&amp;page=2')
        empty = self.client.get(url, {'date': (self.day + datetime.timedelta(days=2)).isoformat()})
        self.assertContains(empty, 'Không có lịch hẹn trong ngày này')

    def test_payment_amount_display_uses_vietnamese_grouping(self):
        from apps.appointments.templatetags.payment_format import payment_vnd
        for value, expected in [(3000, '3.000'), (100000, '100.000'),
                                (600000, '600.000'), (1000000, '1.000.000')]:
            self.assertEqual(payment_vnd(value), expected)

        appointment = self.make_appointment(self.day, 10, 'Đã xác nhận')
        appointment.chi_tiet.update(don_gia_dat=600000)
        url = reverse('owner:status_edit', args=[appointment.pk])
        for method in ('', 'QR', 'Tiền Mặt'):
            response = self.client.post(url, {'status': 'Hoàn thành', 'phuong_thuc': method})
            self.assertContains(response, '600.000 đ')
            if method == 'QR':
                self.assertContains(response, 'amount=600000')
                self.assertContains(response, 'Quét mã QR để thanh toán 600.000 đ')
            elif method == 'Tiền Mặt':
                self.assertContains(response, 'Xác nhận đã nhận đủ 600.000 đ')
        appointment.refresh_from_db()
        self.assertEqual(appointment.tong_tien, 600000)
        self.assertEqual(appointment.trang_thai, 'Đã xác nhận')

    def test_status_edit_validates_transitions_and_preserves_assignments(self):
        appointment = self.make_appointment(self.day, 10, 'Chờ xác nhận')
        url = reverse('owner:status_edit', args=[appointment.pk])
        response = self.client.get(url, {'date': self.day.isoformat(), 'page': 2})
        self.assertContains(response, 'Cập nhật trạng thái lịch hẹn')
        self.assertContains(response, 'date=' + self.day.isoformat() + '&amp;page=2')
        self.assertContains(response, 'Chưa phân công')
        invalid = self.client.post(url, {'status': 'Hoàn thành'})
        self.assertContains(invalid, 'Không thể chuyển sang trạng thái đã chọn.')
        self.assertNotContains(invalid, 'id="status-success-popup"')
        appointment.refresh_from_db()
        self.assertEqual(appointment.trang_thai, 'Chờ xác nhận')
        success = self.client.post(url, {'status': 'Đã xác nhận'})
        self.assertContains(success, 'Cập nhật trạng thái thành công')
        self.assertContains(success, f'Lịch {appointment.pk} đã được chuyển sang Đã xác nhận.')
        self.assertContains(success, reverse('owner:appointment_detail', args=[appointment.pk]))
        appointment.refresh_from_db()
        self.assertEqual(appointment.trang_thai, 'Đã xác nhận')
        self.assertEqual(appointment.phan_cong.count(), 1)
        self.assertContains(self.client.post(url, {'status': 'Hoàn thành'}), 'Thanh toán trước khi hoàn thành')
        appointment.refresh_from_db()
        self.assertEqual(appointment.trang_thai, 'Đã xác nhận')
        self.assertContains(self.client.post(url, {'status': 'Hoàn thành', 'phuong_thuc': 'Tiền Mặt', 'payment_confirm': '1'}), 'Cập nhật trạng thái thành công')
        appointment.refresh_from_db()
        self.assertEqual(appointment.trang_thai, 'Hoàn thành')
        self.assertContains(self.client.post(url, {'status': 'Hủy'}), 'Không thể chuyển sang trạng thái đã chọn.')
        appointment.refresh_from_db()
        self.assertEqual(appointment.trang_thai, 'Hoàn thành')
        self.client.logout()
        self.assertNotEqual(self.client.post(url, {'status': 'Hủy'}).status_code, 200)

    def test_completion_payment_steps_and_duplicate_protection(self):
        appointment = self.make_appointment(self.day, 10, 'Đã xác nhận')
        url = reverse('owner:status_edit', args=[appointment.pk])
        select = self.client.post(url, {'status': 'Hoàn thành'})
        self.assertContains(select, 'Thanh toán QR')
        self.assertContains(select, 'Tiền mặt')
        qr = self.client.post(url, {'status': 'Hoàn thành', 'phuong_thuc': 'QR'})
        self.assertContains(qr, 'img.vietqr.io')
        self.assertContains(qr, 'Xác nhận đã nhận tiền')
        cash = self.client.post(url, {'status': 'Hoàn thành', 'phuong_thuc': 'Tiền Mặt'})
        self.assertContains(cash, 'Xác nhận đã nhận đủ')
        appointment.refresh_from_db()
        self.assertEqual(appointment.trang_thai, 'Đã xác nhận')
        self.assertFalse(GiaoDich.objects.filter(lich_hen=appointment).exists())
        invalid = self.client.post(url, {'status': 'Hoàn thành', 'payment_confirm': '1'})
        self.assertContains(invalid, 'Vui lòng xác nhận phương thức thanh toán hợp lệ.')
        confirmed = self.client.post(url, {'status': 'Hoàn thành', 'phuong_thuc': 'QR', 'payment_confirm': '1'})
        self.assertContains(confirmed, 'Cập nhật trạng thái thành công')
        appointment.refresh_from_db()
        self.assertEqual(appointment.trang_thai, 'Hoàn thành')
        self.assertEqual(GiaoDich.objects.get(lich_hen=appointment).phuong_thuc, 'QR')
        self.client.post(url, {'status': 'Hoàn thành', 'phuong_thuc': 'QR', 'payment_confirm': '1'})
        self.assertEqual(GiaoDich.objects.filter(lich_hen=appointment).count(), 1)

    def test_payment_failure_does_not_complete_appointment(self):
        appointment = self.make_appointment(self.day, 10, 'Đã xác nhận')
        with patch('apps.payments.models.GiaoDich.save', side_effect=DatabaseError('test')):
            response = self.client.post(reverse('owner:status_edit', args=[appointment.pk]), {'status': 'Hoàn thành', 'phuong_thuc': 'Tiền Mặt', 'payment_confirm': '1'})
        self.assertContains(response, 'Không thể lưu trạng thái lịch hẹn.')
        self.assertNotContains(response, 'id="status-success-popup"')
        appointment.refresh_from_db()
        self.assertEqual(appointment.trang_thai, 'Đã xác nhận')
        self.assertFalse(GiaoDich.objects.filter(lich_hen=appointment).exists())

    def test_status_success_popups_and_capacity_after_cancel(self):
        day = self.day + datetime.timedelta(days=1)
        canceled = self.make_appointment(day, 10, 'Đã xác nhận')
        url = reverse('owner:status_edit', args=[canceled.pk])
        slots = lambda: {slot['time_str']: slot['available'] for slot in get_available_slots(day, 60)}
        self.assertFalse(slots()['10:00'])
        response = self.client.post(url, {'status': 'Hủy'})
        self.assertContains(response, 'Đã cập nhật trạng thái Hủy')
        self.assertContains(response, f'Lịch {canceled.pk} chuyển sang Hủy')
        self.assertContains(response, 'Nhân viên kiểm thử: khung 10:00–11:00 được giải phóng')
        self.assertTrue(slots()['10:00'])
        no_show = self.make_appointment(day, 13, 'Đã xác nhận')
        response = self.client.post(reverse('owner:status_edit', args=[no_show.pk]), {'status': 'Không đến'})
        self.assertContains(response, 'Đã cập nhật trạng thái Không đến')
        self.assertContains(response, f'Lịch {no_show.pk} đã được chuyển sang Không đến')
        invalid = self.client.post(reverse('owner:status_edit', args=[no_show.pk]), {'status': 'Hủy'})
        self.assertNotContains(invalid, 'id="status-success-popup"')

    def test_cancel_does_not_claim_staff_is_free_when_other_appointment_overlaps(self):
        day = self.day + datetime.timedelta(days=1)
        canceled = self.make_appointment(day, 10, 'Đã xác nhận')
        self.make_appointment(day, 10, 'Đã xác nhận')
        response = self.client.post(reverse('owner:status_edit', args=[canceled.pk]), {'status': 'Hủy'})
        self.assertContains(response, 'Lịch hẹn này không còn chiếm khung giờ phục vụ.')
        self.assertNotContains(response, 'được giải phóng')

    def test_database_failure_does_not_show_success_or_change_status(self):
        appointment = self.make_appointment(self.day, 10, 'Đã xác nhận')
        with patch('apps.appointments.models.LichHen.save', side_effect=DatabaseError('test')):
            response = self.client.post(reverse('owner:status_edit', args=[appointment.pk]), {'status': 'Hủy'})
        self.assertContains(response, 'Không thể lưu trạng thái lịch hẹn.')
        self.assertNotContains(response, 'id="status-success-popup"')
        appointment.refresh_from_db()
        self.assertEqual(appointment.trang_thai, 'Đã xác nhận')
