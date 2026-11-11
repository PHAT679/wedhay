from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from apps.accounts.models import KhachHang, TaiKhoan
from apps.notifications.models import ThongBao

class CustomerAccountMenuTests(TestCase):
    def setUp(self):
        self.users=[]
        for i,name in enumerate(['Võ Văn Phát','Nguyễn Văn An','']):
            user=User.objects.create_user(username=f'navbar_user_{i}',first_name=name)
            profile=KhachHang.objects.create(ho_ten='Tên hồ sơ cũ' if name else '',so_dien_thoai=f'090500000{i}')
            TaiKhoan.objects.create(user=user,khach_hang=profile,vai_tro='Khách Hàng')
            self.users.append(user)
    def test_current_account_name_and_initial(self):
        for user in self.users:
            self.client.force_login(user)
            response=self.client.get(reverse('home'))
            name=user.get_full_name() or user.username
            self.assertContains(response,f'<strong>{name}</strong>')
            self.assertContains(response,f'aria-hidden="true">{name[0].upper()}</span>')
            self.assertNotContains(response,'<strong>Tên hồ sơ cũ</strong>')
            self.assertContains(response,'customer-account-menu.js')
    def test_logout_invalidates_session_and_protected_access(self):
        self.client.force_login(self.users[0])
        response=self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response,reverse('accounts:login'))
        self.assertNotIn('_auth_user_id',self.client.session)
        response=self.client.get(reverse('customer:my_appointments'))
        self.assertEqual(response.status_code,302)
        self.assertIn(reverse('accounts:login'),response.url)
    def test_guest_has_no_customer_menu_script(self):
        self.assertNotContains(self.client.get(reverse('home')),'customer-account-menu.js')

    def test_customer_notification_dropdown_and_unread_count(self):
        user = self.users[0]
        self.client.force_login(user)
        target = reverse('customer:my_appointments')
        notification = ThongBao.objects.create(tai_khoan=user.tai_khoan, tieu_de='Thông báo kiểm thử', noi_dung='Lịch hẹn', loai_thong_bao='Lịch mới', lien_ket=target)
        page = self.client.get(target)
        self.assertContains(page, 'class="bell-counter">1')
        self.assertContains(page, reverse('notifications:mark_read', args=[notification.pk]))
        self.assertNotContains(page, 'Xem tất cả thông báo')
        self.assertRedirects(self.client.get(reverse('notifications:list')), target)
        self.assertRedirects(self.client.get(reverse('notifications:mark_read', args=[notification.pk])), target)
        notification.refresh_from_db()
        self.assertTrue(notification.da_doc)
        self.assertNotContains(self.client.get(target), 'class="bell-counter"')

    def test_mark_all_read_without_success_banner(self):
        user = self.users[0]
        self.client.force_login(user)
        target = reverse('customer:my_appointments')
        notification = ThongBao.objects.create(tai_khoan=user.tai_khoan, tieu_de='Thông báo kiểm thử', noi_dung='Lịch hẹn', loai_thong_bao='Lịch mới', lien_ket=target)
        response = self.client.get(reverse('notifications:mark_all_read'), HTTP_REFERER='http://testserver' + target, follow=True)
        notification.refresh_from_db()
        self.assertTrue(notification.da_doc)
        self.assertNotContains(response, 'Đã đánh dấu tất cả thông báo là đã đọc.')
        self.assertNotContains(response, 'class="bell-counter"')
        self.assertNotContains(response, 'class="notif-item unread"')
