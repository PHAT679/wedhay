import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import KhachHang, TaiKhoan
from apps.appointments.models import ChiTietLichHen, LichHen
from apps.services.models import DichVu


class OwnerCustomerManagementTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user('customer_management_owner')
        TaiKhoan.objects.create(user=owner, vai_tro='Chủ Tiệm')
        self.client.force_login(owner)
        self.customers = [KhachHang.objects.create(ho_ten=f'Khách hàng {i}', so_dien_thoai=f'09000000{i:02d}') for i in range(9)]

    def add_service(self, customer, name, days, status):
        service = DichVu.objects.create(ten_dich_vu=name, gia_tien=100000, thoi_luong=30)
        appointment = LichHen.objects.create(khach_hang=customer, ten_lien_he=customer.ho_ten,
            so_dien_thoai_lien_he=customer.so_dien_thoai,
            ngay_gio_bat_dau=timezone.now() + datetime.timedelta(days=days), trang_thai=status)
        ChiTietLichHen.objects.create(lich_hen=appointment, dich_vu=service, ten_dich_vu_dat=name,
            don_gia_dat=service.gia_tien, thoi_luong_dat=30)

    def test_customer_list_search_pagination_and_actions(self):
        url = reverse('owner:customers_list')
        self.add_service(self.customers[0], 'Dịch vụ cũ', -4, 'Hoàn thành')
        self.add_service(self.customers[0], 'Dịch vụ mới', -2, 'Hoàn thành')
        self.add_service(self.customers[0], 'Dịch vụ đã hủy', -1, 'Hủy')
        first = self.client.get(url)
        self.assertContains(first, 'Quản lý thông tin khách hàng')
        self.assertContains(first, 'Dịch vụ mới')
        self.assertNotContains(first, 'Dịch vụ đã hủy')
        self.assertContains(first, reverse('owner:customer_create'))
        self.assertContains(first, reverse('owner:customer_detail', args=[self.customers[0].pk]))
        self.assertContains(first, reverse('owner:customer_update', args=[self.customers[0].pk]))
        self.assertEqual(len(first.context['customers']), 5)
        second = self.client.get(url, {'page': 2})
        self.assertEqual(len(second.context['customers']), 4)
        self.assertFalse({c.pk for c in first.context['customers']} & {c.pk for c in second.context['customers']})
        for term in (self.customers[0].ho_ten, self.customers[0].so_dien_thoai):
            result = self.client.get(url, {'q': term})
            self.assertContains(result, self.customers[0].ho_ten)
            self.assertEqual(result.context['page_obj'].paginator.count, 1)
            self.assertContains(result, 'class="customer-management-table customer-search-results"')
        empty = self.client.get(url, {'q': 'không tồn tại'})
        self.assertContains(empty, 'Không tìm thấy khách')
        self.assertContains(empty, 'customer-search-empty-icon')
        self.assertNotContains(empty, '<table class="customer-management-table">')
        self.assertContains(empty, 'value="không tồn tại"')
        self.assertContains(first, '<table class="customer-management-table">')
        self.assertNotContains(first, 'customer-search-empty-icon')

    def test_special_character_search_shows_invalid_criteria_message(self):
        url = reverse('owner:customers_list')
        for term in ('@@@', 'Khách@', '0900#', '<script>'):
            with self.subTest(term=term):
                response = self.client.get(url, {'q': term})
                self.assertContains(response, 'Tiêu chí tìm kiếm không hợp lệ')
                self.assertContains(response, 'Vui lòng nhập tên khách hàng hoặc số điện thoại.')
                self.assertNotContains(response, 'Không tìm thấy khách')
                self.assertNotContains(response, '<table class="customer-management-table">')
                self.assertEqual(response.context['page_obj'].paginator.count, 0)
        for term in ('Khách hàng 0', '0900000000'):
            response = self.client.get(url, {'q': term})
            self.assertContains(response, self.customers[0].ho_ten)
            self.assertNotContains(response, 'Tiêu chí tìm kiếm không hợp lệ')
        response = self.client.get(url, {'q': 'Không tồn tại'})
        self.assertContains(response, 'Không tìm thấy khách')
        self.assertNotContains(response, 'Tiêu chí tìm kiếm không hợp lệ')

    def test_create_customer_with_service_and_inline_errors(self):
        url = reverse('owner:customer_create')
        service = DichVu.objects.create(ten_dich_vu='Dịch vụ trực tiếp', gia_tien=100000, thoi_luong=30)
        hidden = DichVu.objects.create(ten_dich_vu='Dịch vụ đã xóa', gia_tien=100000, thoi_luong=30, da_xoa=True)
        page = self.client.get(url)
        self.assertContains(page, 'Thông tin khách hàng mới')
        self.assertContains(page, service.ten_dich_vu)
        self.assertContains(page, 'list="customer-service-options"')
        self.assertNotContains(page, hidden.ten_dich_vu)
        self.assertContains(page, 'Liên kết Facebook hoặc Zalo')
        self.assertContains(page, 'Dịch vụ khách hàng chọn')
        self.assertNotContains(page, 'Thông tin chưa hợp lệ')
        bad = self.client.post(url, {'ho_ten': '', 'so_dien_thoai': '123', 'dich_vu_truc_tiep': ''})
        self.assertContains(bad, 'Thông tin chưa hợp lệ', count=1)
        self.assertContains(bad, 'Vui lòng kiểm tra và nhập lại các thông tin bắt buộc.')
        self.assertContains(bad, 'Vui lòng nhập tên khách hàng.', count=1)
        self.assertContains(bad, 'Số điện thoại phải gồm đúng 10 chữ số.', count=1)
        self.assertContains(bad, 'Vui lòng chọn dịch vụ.', count=1)
        blank = self.client.post(url, {})
        self.assertContains(blank, 'Số điện thoại phải gồm đúng 10 chữ số.', count=1)
        self.assertContains(blank, 'Vui lòng nhập tên khách hàng.', count=1)
        self.assertContains(blank, 'Vui lòng chọn dịch vụ.', count=1)
        self.assertTrue(bad.context['form'].errors.get('ho_ten'))
        duplicate = self.client.post(url, {'ho_ten': 'Trùng', 'so_dien_thoai': self.customers[0].so_dien_thoai, 'dich_vu_truc_tiep': service.pk})
        self.assertContains(duplicate, 'Số điện thoại này đã tồn tại.')
        invalid_service = self.client.post(url, {'ho_ten': 'Khách nhập sai', 'so_dien_thoai': '0911222334', 'dich_vu_truc_tiep': 'Dịch vụ không tồn tại'})
        self.assertContains(invalid_service, 'Vui lòng chọn dịch vụ có trong danh sách.')
        self.assertFalse(KhachHang.objects.filter(so_dien_thoai='0911222334').exists())
        before = LichHen.objects.count()
        response = self.client.post(url, {'ho_ten': 'Khách đến trực tiếp', 'so_dien_thoai': '0911222333',
                                           'lien_ket': 'https://zalo.me/0911222333', 'dich_vu_truc_tiep': service.pk})
        self.assertRedirects(response, reverse('owner:customer_create'), fetch_redirect_response=False)
        success = self.client.get(reverse('owner:customer_create'))
        self.assertContains(success, 'Lưu thành công')
        self.assertContains(success, reverse('owner:customers_list'))
        self.assertNotContains(self.client.get(reverse('owner:customer_create')), 'Lưu thành công')
        customer = KhachHang.objects.get(so_dien_thoai='0911222333')
        self.assertEqual(customer.dich_vu_truc_tiep_id, service.pk)
        self.assertEqual(customer.link_zalo, 'https://zalo.me/0911222333')
        self.assertEqual(LichHen.objects.count(), before)
        typed = self.client.post(url, {'ho_ten': 'Khách nhập dịch vụ', 'so_dien_thoai': '0911222335', 'dich_vu_truc_tiep': service.ten_dich_vu})
        self.assertRedirects(typed, reverse('owner:customer_create'), fetch_redirect_response=False)
        self.assertEqual(KhachHang.objects.get(so_dien_thoai='0911222335').dich_vu_truc_tiep_id, service.pk)
        self.assertEqual(LichHen.objects.count(), before)
        canceled = self.client.get(reverse('owner:customer_create'))
        self.assertContains(canceled, reverse('owner:customers_list'))

    def test_existing_customer_profile_and_edit_remain_accessible(self):
        customer = self.customers[0]
        self.assertEqual(self.client.get(reverse('owner:customer_detail', args=[customer.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('owner:customer_update', args=[customer.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('owner:customer_create')).status_code, 200)

    def test_edit_customer_keeps_other_social_link_and_updates_service(self):
        customer = self.customers[0]
        customer.link_facebook = 'https://facebook.com/example'
        customer.link_zalo = 'https://zalo.me/example'
        customer.save()
        service = DichVu.objects.create(ten_dich_vu='Dịch vụ chọn', gia_tien=200000, thoi_luong=60)
        url = reverse('owner:customer_update', args=[customer.pk])
        self.assertContains(self.client.get(url), 'Chỉnh sửa hồ sơ khách hàng')
        response = self.client.post(url, {'ho_ten': customer.ho_ten, 'so_dien_thoai': customer.so_dien_thoai,
                                         'lien_ket': 'https://facebook.com/new', 'dich_vu_truc_tiep': service.pk})
        self.assertRedirects(response, url, fetch_redirect_response=False)
        success = self.client.get(url)
        self.assertContains(success, 'Lưu thành công')
        self.assertContains(success, 'Thông tin khách hàng đã được cập nhật.')
        self.assertContains(success, reverse('owner:customers_list'))
        self.assertNotContains(self.client.get(url), 'Lưu thành công')
        customer.refresh_from_db()
        self.assertEqual(customer.link_facebook, 'https://facebook.com/new')
        self.assertEqual(customer.link_zalo, 'https://zalo.me/example')
        self.assertEqual(customer.dich_vu_truc_tiep_id, service.pk)

    def test_eye_shows_selected_customer_appointment_history(self):
        customer = self.customers[0]
        self.add_service(customer, 'Dịch vụ lịch sử', 1, 'Hoàn thành')
        self.add_service(self.customers[1], 'Dịch vụ khách khác', 2, 'Hủy')
        url = reverse('owner:customer_detail', args=[customer.pk])
        response = self.client.get(url, {'display': 'history'})
        listing = self.client.get(reverse('owner:customers_list'))
        self.assertContains(listing, f'class="customer-management-history" href="{url}?display=history"')
        self.assertContains(response, customer.ho_ten)
        self.assertContains(response, 'Dịch vụ lịch sử')
        self.assertContains(response, 'data-dialog="history-detail-1"')
        self.assertContains(response, 'id="history-detail-1"')
        self.assertNotContains(response, 'Dịch vụ khách khác')
        self.assertContains(response, 'Hoàn thành')
        self.assertContains(response, 'Tổng số lần đặt lịch')
        self.assertContains(self.client.get(url), 'Hồ Sơ Khách Hàng')

    def test_eye_opens_read_only_customer_info(self):
        customer = self.customers[0]
        service = DichVu.objects.create(ten_dich_vu='Dịch vụ hồ sơ', gia_tien=100000, thoi_luong=30)
        customer.dich_vu_truc_tiep = service
        customer.link_zalo = 'zalo khách'
        customer.save()
        url = reverse('owner:customer_detail', args=[customer.pk])
        listing = self.client.get(reverse('owner:customers_list'))
        self.assertContains(listing, f'href="{url}?display=profile"')
        self.assertContains(listing, f'class="customer-management-history" href="{url}?display=history"')
        response = self.client.get(url, {'display': 'profile'})
        for value in (customer.ho_ten, customer.so_dien_thoai, service.ten_dich_vu, customer.link_zalo):
            self.assertContains(response, value)
        self.assertNotContains(response, '<form')

    def test_eye_history_paginates_five_appointments_newest_first(self):
        customer = self.customers[0]
        for index in range(6):
            self.add_service(customer, f'Dịch vụ phân trang {index}', index, 'Hoàn thành')
        url = reverse('owner:customer_detail', args=[customer.pk])
        response = self.client.get(url, {'display': 'history'})
        second = self.client.get(url, {'display': 'history', 'page': 2})
        appointments = list(response.context['appointments']) + list(second.context['appointments'])
        self.assertEqual(len(response.context['appointments']), 5)
        self.assertEqual(len(second.context['appointments']), 1)
        self.assertEqual(len({item.pk for item in appointments}), 6)
        self.assertEqual(appointments, sorted(appointments, key=lambda a: a.ngay_gio_bat_dau, reverse=True))
        self.assertContains(response, 'Phân trang lịch hẹn')
        self.assertContains(response, 'display=history&amp;page=2')
        self.assertContains(second, 'Dịch vụ phân trang 0')
        self.assertContains(second, 'id="history-detail-1"')
        self.assertContains(response, 'Tổng số lần đặt lịch<strong>6</strong>')
