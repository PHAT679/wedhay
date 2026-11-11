import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

client = Client()

print("--- 1. KIỂM TRA TRẠNG THÁI 1: GIAO DIỆN MẶC ĐỊNH ---")
r1 = client.get('/accounts/login/')
print("Status code:", r1.status_code)
assert 'auth-wrapper' in r1.content.decode('utf-8')
assert 'auth-alert-figma' not in r1.content.decode('utf-8')
assert 'Nhập tên tài khoản' in r1.content.decode('utf-8')
assert 'Nhập mật khẩu' in r1.content.decode('utf-8')
print("-> Trạng thái 1: OK (Không có alert, form đầy đủ)")

print("\n--- 2. KIỂM TRA TRẠNG THÁI 2: THIẾU THÔNG TIN ---")
r2 = client.post('/accounts/login/', {'username': '', 'password': ''})
print("Status code:", r2.status_code)
assert 'Vui lòng nhập đầy đủ tên tài khoản và mật khẩu' in r2.content.decode('utf-8')
print("-> Trạng thái 2: OK (Hiển thị thông báo thiếu thông tin đúng Figma)")

print("\n--- 3. KIỂM TRA TRẠNG THÁI 3: SAI THÔNG TIN ---")
r3 = client.post('/accounts/login/', {'username': 'chutiem', 'password': 'wrongpassword'})
print("Status code:", r3.status_code)
assert 'Tên tài khoản hoặc mật khẩu không chính xác' in r3.content.decode('utf-8')
print("-> Trạng thái 3: OK (Hiển thị thông báo sai thông tin đúng Figma)")

print("\n--- 4. KIỂM TRA ĐĂNG NHẬP THÀNH CÔNG & PHÂN QUYỀN 3 VAI TRÒ ---")
# Chủ tiệm
r_owner = client.post('/accounts/login/', {'username': 'chutiem', 'password': '123456'})
print("Owner login redirect:", r_owner.url)
assert r_owner.url == '/owner/'

# Nhân viên
client.logout()
r_staff = client.post('/accounts/login/', {'username': 'nhanvien1', 'password': '123456'})
print("Staff login redirect:", r_staff.url)
assert r_staff.url == '/employee/'

# Khách hàng
client.logout()
r_cust = client.post('/accounts/login/', {'username': 'khachhang1', 'password': '123456'})
print("Customer login redirect:", r_cust.url)
assert r_cust.url == '/customer/my-appointments/'

print("-> Phân quyền & chuyển hướng 3 vai trò: OK 100%")
