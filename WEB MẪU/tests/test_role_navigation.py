from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import KhachHang, NhanVien, TaiKhoan
from apps.appointments.models import LichHen


class RoleNavigationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('role_owner', password='pass123')
        TaiKhoan.objects.create(user=self.owner, vai_tro='Chủ Tiệm')
        self.employee = User.objects.create_user('role_employee', password='pass123')
        account = TaiKhoan.objects.create(user=self.employee, vai_tro='Nhân Viên')
        NhanVien.objects.create(tai_khoan=account, ten_nhan_vien='Nhân viên')
        self.customer_user = User.objects.create_user('role_customer', password='pass123')
        customer = KhachHang.objects.create(ho_ten='Khách hàng', so_dien_thoai='0901234567')
        TaiKhoan.objects.create(user=self.customer_user, vai_tro='Khách Hàng', khach_hang=customer)
        self.appointment = LichHen.objects.create(khach_hang=customer, ten_lien_he=customer.ho_ten,
            so_dien_thoai_lien_he=customer.so_dien_thoai, ngay_gio_bat_dau=timezone.now())

    def test_owner_and_employee_redirect_disallowed_urls(self):
        common = [reverse('home'), reverse('services:public_list'), reverse('customer:booking'),
                  reverse('customer:my_appointments'), reverse('accounts:login'), reverse('accounts:register'),
                  reverse('api_available_slots')]
        for user, home, forbidden in (
            (self.owner, 'owner:dashboard', [reverse('employee:dashboard')]),
            (self.employee, 'employee:dashboard', [reverse('owner:dashboard'),
                reverse('payments:checkout', args=[self.appointment.pk]), reverse('notifications:owner_status')]),
        ):
            self.client.force_login(user)
            with self.subTest(role=home):
                for url in common + forbidden:
                    self.assertRedirects(self.client.get(url), reverse(home), fetch_redirect_response=False)
                page = self.client.get(reverse(home))
                self.assertEqual(page.status_code, 200)
                self.assertNotContains(page, 'class="nav-brand"')
                self.assertIn('no-store', page['Cache-Control'])
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse('payments:checkout', args=[self.appointment.pk])).status_code, 200)

    def test_employee_notifications_stay_in_employee_interface(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse('notifications:list'))
        self.assertContains(response, 'Thông Báo Hệ Thống')
        self.assertNotContains(response, 'class="nav-brand"')
        self.assertContains(response, reverse('employee:dashboard'))
        self.assertIn('no-store', response['Cache-Control'])

    def test_login_ignores_wrong_role_next_and_logout_restores_public_access(self):
        for user, home in ((self.owner, 'owner:dashboard'), (self.employee, 'employee:dashboard')):
            response = self.client.post(reverse('accounts:login'), {
                'username': user.username, 'password': 'pass123', 'next': reverse('customer:booking'),
            })
            self.assertRedirects(response, reverse(home), fetch_redirect_response=False)
            self.assertRedirects(self.client.get(reverse('accounts:logout')), reverse('home' if user == self.employee else 'accounts:login'))
            self.assertNotIn('_auth_user_id', self.client.session)
            self.assertEqual(self.client.get(reverse('home')).status_code, 200)
            self.assertEqual(self.client.get(reverse('services:public_list')).status_code, 200)
            self.assertEqual(self.client.get(reverse(home)).status_code, 302)

    def test_customer_booking_and_anonymous_access(self):
        self.assertEqual(self.client.get(reverse('customer:booking')).status_code, 302)
        self.assertEqual(self.client.get(reverse('customer:booking_success', args=[self.appointment.pk])).status_code, 302)
        self.client.force_login(self.customer_user)
        self.assertEqual(self.client.get(reverse('customer:booking')).status_code, 200)
        self.assertEqual(self.client.get(reverse('customer:booking_success', args=[self.appointment.pk])).status_code, 200)
