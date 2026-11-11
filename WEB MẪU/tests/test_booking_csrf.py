import re
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.appointments.models import LichHen

class BookingCsrfTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user('csrf-test', password='test-password')
        self.client.force_login(self.user)
        self.url = reverse('customer:booking')

    def token(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        tokens = re.findall(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.content.decode())
        self.assertEqual(len(tokens), 1)
        return tokens[0]

    def test_fresh_form_reaches_validation_without_creating_appointment(self):
        response = self.client.post(self.url, {'csrfmiddlewaretoken': self.token()})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vui lòng chọn ít nhất một dịch vụ nail.')
        self.assertEqual(LichHen.objects.count(), 0)

    def test_login_rotates_cookie_and_old_form_is_rejected(self):
        old_token = self.token()
        old_cookie = self.client.cookies['csrftoken'].value
        response = self.client.post(reverse('accounts:login'), {
            'csrfmiddlewaretoken': old_token, 'username': self.user.username,
            'password': 'test-password',
        })
        # An already-authenticated login does not rotate; simulate a new login session.
        self.client.logout()
        self.client.get(reverse('accounts:login'))
        login_token = self.client.cookies['csrftoken'].value
        self.client.post(reverse('accounts:login'), {
            'csrfmiddlewaretoken': login_token, 'username': self.user.username,
            'password': 'test-password',
        })
        self.assertNotEqual(old_cookie, self.client.cookies['csrftoken'].value)
        self.assertEqual(self.client.post(self.url, {'csrfmiddlewaretoken': old_token}).status_code, 403)
        self.assertEqual(self.client.post(self.url, {'csrfmiddlewaretoken': self.token()}).status_code, 200)
        self.assertEqual(LichHen.objects.count(), 0)

    def test_missing_token_remains_forbidden(self):
        self.token()
        self.assertEqual(self.client.post(self.url, {}).status_code, 403)
