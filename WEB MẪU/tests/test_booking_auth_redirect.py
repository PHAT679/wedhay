from html.parser import HTMLParser
from urllib.parse import urlencode

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import KhachHang, TaiKhoan


class BookingLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.current = [dict(attrs).get('href'), '']

    def handle_data(self, data):
        if self.current is not None:
            self.current[1] += data

    def handle_endtag(self, tag):
        if tag == 'a' and self.current is not None:
            self.links.append((self.current[0], self.current[1].strip()))
            self.current = None


class BookingAuthRedirectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('redirect_test', password='test-password')
        customer = KhachHang.objects.create(ho_ten='Khách kiểm thử', so_dien_thoai='0901234567')
        TaiKhoan.objects.create(user=cls.user, vai_tro='Khách Hàng', khach_hang=customer)

    def setUp(self):
        self.booking = reverse('customer:booking')
        self.login_url = reverse('accounts:login')

    def test_home_buttons_and_direct_access_require_login(self):
        parser = BookingLinks()
        parser.feed(self.client.get(reverse('home')).content.decode())
        for label in ('Đặt Lịch Ngay', 'Đặt Lịch Làm Móng Ngay'):
            self.assertIn((self.booking, label), parser.links)
        for method in (self.client.get, self.client.post):
            response = method(self.booking)
            self.assertRedirects(response, self.login_url + '?' + urlencode({'next': self.booking}))

    def test_next_survives_failed_login_and_success(self):
        target = self.booking + '?service=DV001'
        response = self.client.get(self.login_url, {'next': target})
        self.assertContains(response, f'name="next" value="{target}"')
        for password in ('', 'incorrect'):
            response = self.client.post(self.login_url, {
                'username': self.user.username, 'password': password, 'next': target,
            })
            self.assertEqual(response.context['next'], target)
        response = self.client.post(self.login_url, {
            'username': self.user.username, 'password': 'test-password', 'next': target,
        })
        self.assertRedirects(response, target)
        self.assertEqual(self.client.get(self.booking).status_code, 200)

    def test_authenticated_user_enters_booking(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.booking).status_code, 200)
        self.assertRedirects(self.client.get(self.login_url, {'next': self.booking}), self.booking)

    def test_ordinary_login_and_unsafe_next_keep_default_redirect(self):
        for target in ('', 'https://evil.example/', '//evil.example/', 'javascript:alert(1)', '/\\evil.example/'):
            with self.subTest(next=target):
                self.client.logout()
                response = self.client.post(self.login_url, {
                    'username': self.user.username, 'password': 'test-password', 'next': target,
                })
                self.assertRedirects(response, reverse('customer:my_appointments'))
