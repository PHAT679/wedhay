from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import TaiKhoan
from apps.services.models import DichVu


class OwnerServicesListTests(TestCase):
    def setUp(self):
        user = User.objects.create_user('services_owner')
        TaiKhoan.objects.create(user=user, vai_tro='Chủ Tiệm')
        self.client.force_login(user)
        for i in range(9):
            DichVu.objects.create(ten_dich_vu=f'Dịch vụ {i}', gia_tien=120000, thoi_luong=30)

    def test_search_pagination_and_existing_actions(self):
        url = reverse('owner:services_list')
        first = self.client.get(url)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(len(first.context['services']), 5)
        self.assertContains(first, '120.000')
        self.assertContains(first, reverse('owner:service_create'))
        service = first.context['services'][0]
        self.assertContains(first, reverse('owner:service_update', args=[service.pk]))
        self.assertContains(first, reverse('owner:services_delete_list'))
        self.assertContains(self.client.get(reverse('owner:services_delete_list')), reverse('owner:service_delete', args=[service.pk]))
        second = self.client.get(url, {'page': 2})
        self.assertEqual(len(second.context['services']), 4)
        filtered = self.client.get(url, {'q': 'Dịch vụ 8'})
        self.assertEqual(len(filtered.context['services']), 1)
        self.assertContains(filtered, 'Dịch vụ 8')
        self.assertNotContains(filtered, 'Dịch vụ 0')
        edit = self.client.get(reverse('owner:service_update', args=[service.pk]))
        self.assertEqual(edit.status_code, 200)
        delete = self.client.get(reverse('owner:service_delete', args=[service.pk]))
        self.assertEqual(delete.status_code, 200)
        service.refresh_from_db()
        self.assertFalse(service.da_xoa)

    def test_delete_list_removes_only_selected_service(self):
        url = reverse('owner:services_delete_list')
        page = self.client.get(url)
        service, other = list(page.context['services'])[:2]
        self.assertContains(page, service.ten_dich_vu)
        self.assertContains(page, '120.000')
        self.assertContains(page, reverse('owner:services_list'))
        response = self.client.post(reverse('owner:service_delete', args=[service.pk]), {'from_delete_list': '1'})
        self.assertRedirects(response, url)
        service.refresh_from_db()
        other.refresh_from_db()
        self.assertTrue(service.da_xoa)
        self.assertFalse(other.da_xoa)
        self.assertNotContains(self.client.get(url), service.ten_dich_vu)

    def test_delete_list_pagination(self):
        url = reverse('owner:services_delete_list')
        first = self.client.get(url)
        second = self.client.get(url, {'page': 2})
        first_ids = {item.pk for item in first.context['services']}
        second_ids = {item.pk for item in second.context['services']}
        self.assertEqual((len(first_ids), len(second_ids)), (5, 4))
        self.assertFalse(first_ids & second_ids)
        self.assertEqual(first_ids | second_ids, set(DichVu.objects.values_list('pk', flat=True)))
        self.assertContains(first, '<dialog')
        self.assertContains(first, 'Bạn có chắc chắn muốn xóa dịch vụ này?')
        chosen = second.context['services'][0]
        result = self.client.post(reverse('owner:service_delete', args=[chosen.pk]), {'from_delete_list': '1', 'page': '2'}, follow=True)
        self.assertContains(result, 'Xóa dịch vụ thành công')
        self.assertContains(result, 'alert-service-deleted')
        self.assertEqual(result.context['page_obj'].number, 2)
        chosen.refresh_from_db()
        self.assertTrue(chosen.da_xoa)

    def test_create_form_validation_and_save(self):
        url = reverse('owner:service_create')
        response = self.client.get(url)
        self.assertContains(response, 'Thêm thông tin dịch vụ mới')
        self.assertContains(response, reverse('owner:services_list'))
        invalid = self.client.post(url, {'ten_dich_vu': 'Dịch vụ 0', 'gia_tien': 100000, 'thoi_luong': 30})
        self.assertContains(invalid, 'Tên dịch vụ đã tồn tại')
        self.assertEqual(DichVu.objects.count(), 9)
        saved = self.client.post(url, {'ten_dich_vu': 'Dịch vụ mới', 'gia_tien': 100000, 'thoi_luong': 30, 'ghi_chu': 'Ghi chú'})
        self.assertRedirects(saved, reverse('owner:services_list'), fetch_redirect_response=False)
        self.assertTrue(DichVu.objects.filter(ten_dich_vu='Dịch vụ mới', ghi_chu='Ghi chú').exists())
        result = self.client.get(reverse('owner:services_list'))
        self.assertContains(result, 'Thêm dịch vụ thành công')
        self.assertContains(result, 'alert-service-added')
        self.assertEqual(result.context['services'][0].ten_dich_vu, 'Dịch vụ mới')
        self.assertContains(result, 'class="owner-services-new"', count=1)
        refreshed = self.client.get(reverse('owner:services_list'))
        self.assertEqual(refreshed.context['services'][0].ten_dich_vu, 'Dịch vụ mới')
        self.assertNotContains(refreshed, 'class="owner-services-new"')

    def test_default_order_uses_insertion_not_service_code(self):
        latest = DichVu.objects.create(ma_dich_vu='AA001', ten_dich_vu='Dịch vụ sau cùng', gia_tien=100000, thoi_luong=30)
        response = self.client.get(reverse('owner:services_list'))
        self.assertEqual(response.context['services'][0].pk, latest.pk)

    def test_create_empty_required_fields(self):
        response = self.client.post(reverse('owner:service_create'), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dữ liệu không được để trống', count=3)
        self.assertNotContains(response, 'Thời lượng phải thuộc')
        self.assertEqual(response.content.decode().count('service-create-field has-error'), 3)
        self.assertEqual(DichVu.objects.count(), 9)
        partial = self.client.post(reverse('owner:service_create'), {'ten_dich_vu': 'Mới', 'gia_tien': 100000})
        self.assertContains(partial, 'Dữ liệu không được để trống', count=1)

    def test_duplicate_name_normalizes_case_and_whitespace(self):
        url = reverse('owner:service_create')
        duplicate = self.client.post(url, {'ten_dich_vu': '  DỊCH   VỤ 0  ', 'gia_tien': 100000, 'thoi_luong': 30})
        self.assertContains(duplicate, 'Tên dịch vụ đã tồn tại')
        self.assertEqual(DichVu.objects.count(), 9)

    def test_create_duplicate_and_invalid_price_together_preserves_duration(self):
        url = reverse('owner:service_create')
        page = self.client.get(url)
        self.assertContains(page, 'Chọn thời gian thực hiện')
        for duration in (30, 60, 90, 120, 150, 180):
            self.assertContains(page, f'value="{duration}"')
        for price in ('0', '-1000'):
            response = self.client.post(url, {'ten_dich_vu': 'Dịch vụ 0', 'gia_tien': price, 'thoi_luong': 60})
            self.assertContains(response, 'Tên dịch vụ đã tồn tại')
            self.assertContains(response, 'Giá tiền không hợp lệ')
            self.assertContains(response, 'value="60" selected')
            self.assertEqual(DichVu.objects.count(), 9)
        valid = self.client.post(url, {'ten_dich_vu': 'Dịch vụ mới khác', 'gia_tien': 1, 'thoi_luong': 90})
        self.assertRedirects(valid, reverse('owner:services_list'))
        self.assertTrue(DichVu.objects.filter(ten_dich_vu='Dịch vụ mới khác', gia_tien=1, thoi_luong=90).exists())

    def test_edit_invalid_prices_and_valid_save(self):
        service = DichVu.objects.first()
        url = reverse('owner:service_update', args=[service.pk])
        for price in ('0', '-1', '', 'abc'):
            with self.subTest(price=price):
                response = self.client.post(url, {'ten_dich_vu': service.ten_dich_vu, 'gia_tien': price, 'thoi_luong': 30})
                self.assertContains(response, 'Giá tiền không hợp lệ')
                service.refresh_from_db()
                self.assertEqual(service.gia_tien, 120000)
        valid = self.client.post(url, {'ten_dich_vu': service.ten_dich_vu, 'gia_tien': 50001, 'thoi_luong': 30})
        self.assertRedirects(valid, reverse('owner:services_list'))
        service.refresh_from_db()
        self.assertEqual(service.gia_tien, 50001)

    def test_edit_empty_name_and_price_errors_and_existing_values(self):
        service = DichVu.objects.first()
        url = reverse('owner:service_update', args=[service.pk])
        page = self.client.get(url)
        self.assertContains(page, 'Chỉnh sửa thông tin dịch vụ')
        self.assertContains(page, service.ten_dich_vu)
        self.assertContains(page, 'value="30" selected')
        response = self.client.post(url, {'ten_dich_vu': ' ', 'gia_tien': '0', 'thoi_luong': 60, 'ghi_chu': 'Nội dung giữ lại'})
        self.assertContains(response, 'Dữ liệu không được để trống')
        self.assertContains(response, 'Giá tiền không hợp lệ')
        self.assertContains(response, 'Nội dung giữ lại')
        self.assertContains(response, 'value="60" selected')
        service.refresh_from_db()
        self.assertEqual(service.gia_tien, 120000)
        self.assertEqual(DichVu.objects.count(), 9)
        saved = self.client.post(url, {'ten_dich_vu': 'Tên mới', 'gia_tien': 80000, 'thoi_luong': 60})
        self.assertRedirects(saved, reverse('owner:services_list'), fetch_redirect_response=False)
        result = self.client.get(reverse('owner:services_list'))
        self.assertContains(result, 'Cập nhật dịch vụ thành công')
        self.assertContains(result, 'alert-service-updated')
        self.assertContains(result, 'class="owner-services-new"', count=1)
        self.assertEqual(result.context['services'][0].pk, service.pk)
        self.assertNotContains(self.client.get(reverse('owner:services_list')), 'class="owner-services-new"')
        service.refresh_from_db()
        self.assertEqual(service.ten_dich_vu, 'Tên mới')
        self.assertEqual(DichVu.objects.count(), 9)
