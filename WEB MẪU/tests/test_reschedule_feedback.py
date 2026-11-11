import datetime
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from tests.test_emmay_business_rules import EmmayBeautyBusinessRulesTestCase as Fixtures
from apps.appointments.models import LichHen

class RescheduleFeedbackTests(TestCase):
    def setUp(self):
        Fixtures.setUp(self)
        self.client.force_login(self.cust_user)
        self.old = timezone.now() + datetime.timedelta(days=2)
        self.item = LichHen.objects.create(khach_hang=self.cust_kh, ngay_gio_bat_dau=self.old, ten_lien_he='Test', so_dien_thoai_lien_he='0905111222')
        self.url = reverse('customer:reschedule', args=[self.item.pk])
        self.data = {'booking_date': (timezone.localdate()+datetime.timedelta(days=3)).isoformat(), 'booking_time':'13:00'}
    def post(self, data=None):
        return self.client.post(self.url, data or self.data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    def test_my_appointments_show_newest_booking_first(self):
        newer = LichHen.objects.create(
            khach_hang=self.cust_kh, ngay_gio_bat_dau=self.old - datetime.timedelta(days=1),
            ten_lien_he='Lịch mới', so_dien_thoai_lien_he='0905111222',
        )
        response = self.client.get(reverse('customer:my_appointments'))
        self.assertEqual([appointment.pk for appointment in response.context['appointments']], [newer.pk, self.item.pk])
        self.assertLess(response.content.decode().index(newer.pk), response.content.decode().index(self.item.pk))
        self.item.ngay_gio_bat_dau = self.old + datetime.timedelta(days=10)
        self.item.save(update_fields=['ngay_gio_bat_dau'])
        refreshed = self.client.get(reverse('customer:my_appointments'))
        self.assertEqual([appointment.pk for appointment in refreshed.context['appointments']], [newer.pk, self.item.pk])

    def test_success_updates_existing_record(self):
        with patch('apps.appointments.views.get_available_slots', return_value=[{'time_str':'13:00','available':True}]):
            count = LichHen.objects.count()
            response = self.post()
        self.assertTrue(response.json()['success'])
        self.item.refresh_from_db()
        self.assertEqual(timezone.localtime(self.item.ngay_gio_bat_dau).strftime('%Y-%m-%d %H:%M'), self.data['booking_date']+' 13:00')
        self.assertEqual(LichHen.objects.count(), count)
    def test_invalid_missing_and_outside_range(self):
        for data in ({'booking_date':'bad'}, {'booking_date':self.data['booking_date']}, {'booking_date':(timezone.localdate()+datetime.timedelta(days=31)).isoformat(),'booking_time':'13:00'}):
            self.assertEqual(self.post(data).status_code,400)
        self.item.refresh_from_db(); self.assertEqual(self.item.ngay_gio_bat_dau,self.old)
    def test_full_slot_and_full_day(self):
        for values in ([], [{'time_str':'14:00','available':True}]):
            with patch('apps.appointments.views.get_available_slots', return_value=values):
                self.assertEqual(self.post().status_code,409)
        self.item.refresh_from_db(); self.assertEqual(self.item.ngay_gio_bat_dau,self.old)
    def test_permission_status_csrf(self):
        other = Client(); other.force_login(self.owner_user)
        self.assertNotEqual(other.post(self.url,self.data).status_code,200)
        secured = Client(enforce_csrf_checks=True); secured.force_login(self.cust_user)
        self.assertEqual(secured.post(self.url,self.data).status_code,403)
        self.item.trang_thai='Hủy'; self.item.save()
        self.assertEqual(self.post().status_code,400)
    def test_server_failure_rolls_back(self):
        with patch('apps.appointments.views.get_available_slots',return_value=[{'time_str':'13:00','available':True}]), patch('apps.appointments.views.send_notification',side_effect=RuntimeError('test')):
            with self.assertRaises(RuntimeError): self.post()
        self.item.refresh_from_db(); self.assertEqual(self.item.ngay_gio_bat_dau,self.old)
