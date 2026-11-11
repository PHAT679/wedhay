from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from tests import test_reschedule_feedback as fixtures
from apps.appointments.models import LichHen
from apps.accounts.models import KhachHang
from apps.notifications.models import ThongBao

class CancelPopupTests(TestCase):
    def setUp(self):
        fixtures.RescheduleFeedbackTests.setUp(self)
        self.url = reverse('customer:cancel', args=[self.item.pk])
    def post(self):
        return self.client.post(self.url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    def test_get_does_not_cancel(self):
        self.assertEqual(self.client.get(self.url).status_code,200)
        self.item.refresh_from_db(); self.assertEqual(self.item.trang_thai,'Chờ xác nhận')
    def test_success_and_repeat(self):
        count = LichHen.objects.count()
        response = self.post(); self.assertTrue(response.json()['success'])
        self.item.refresh_from_db()
        self.assertEqual(self.item.trang_thai,'Hủy')
        self.assertEqual(self.item.ngay_gio_bat_dau,self.old)
        self.assertEqual(self.item.tai_khoan_huy,self.cust_tk)
        self.assertEqual(LichHen.objects.count(),count)
        notices = ThongBao.objects.count()
        self.assertEqual(self.post().status_code,409)
        self.assertEqual(ThongBao.objects.count(),notices)
        page = self.client.get(reverse('customer:my_appointments'))
        self.assertContains(page,'Đã hủy')
        self.assertNotContains(page,self.url)
    def test_not_owned_missing_and_finished(self):
        other = KhachHang.objects.create(ma_khach_hang='KH099',ho_ten='Other',so_dien_thoai='0905111999')
        self.item.khach_hang=other; self.item.save()
        self.assertEqual(self.post().status_code,404)
        self.assertEqual(self.client.post(reverse('customer:cancel',args=['missing']),HTTP_X_REQUESTED_WITH='XMLHttpRequest').status_code,404)
        self.item.khach_hang=self.cust_kh; self.item.trang_thai='Hoàn thành';self.item.save()
        self.assertEqual(self.post().status_code,409)
    def test_csrf_and_rollback(self):
        secured=Client(enforce_csrf_checks=True);secured.force_login(self.cust_user)
        self.assertEqual(secured.post(self.url).status_code,403)
        with patch('apps.appointments.views.send_notification',side_effect=RuntimeError('test')):
            with self.assertRaises(RuntimeError): self.post()
        self.item.refresh_from_db();self.assertEqual(self.item.trang_thai,'Chờ xác nhận')
