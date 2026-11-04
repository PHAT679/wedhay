# HỆ THỐNG QUẢN LÝ ĐẶT LỊCH TRỰC TUYẾN TIỆM NAIL EMMAY BEAUTY

**Đồ án Phân tích & Thiết kế Hệ thống Thông tin (PTTK-50K)**  
**Lớp:** 50k14.1 | **Nhóm:** 50k141.06.3007  
**Địa chỉ tiệm:** 356/87 Hoàng Diệu, Phường Hòa Cường, Đà Nẵng  
**Hotline:** 0905.123.456  

---

## 1. CÔNG NGHỆ & KIẾN TRÚC DỰ ÁN

- **Ngôn ngữ Backend:** Python 3 (Python 3.12+)
- **Backend Framework:** Django 6.1 (Django ORM, Authentication, Sessions, Forms, Views, Templates, Migrations)
- **Frontend:** HTML5, CSS3 thuần, Django Template Engine, Vanilla JavaScript
- **Thiết kế thương hiệu:** Phong cách **Luxury Feminine Beauty – Soft Pink (#C97F8E, #D98F9F, #FBECEF)**
- **Font chữ quy chuẩn:**
  - `Playfair Display`: Logo thương hiệu, tiêu đề trang, các heading quan trọng.
  - `Montserrat`: Nội dung, form, bảng dữ liệu, nút bấm, dashboard, timeline.
- **Cơ sở dữ liệu:** SQLite (giai đoạn phát triển/bảo vệ), thiết kế tương thích chuyển đổi 100% sang PostgreSQL / SQL Server.
- **Bảo mật:** CSRF protection, PBKDF2 Password Hashing, RBAC 3 vai trò tại Backend.

---

## 2. DANH SÁCH TÀI KHOẢN THỬ NGHIỆM (DEMO)

Tất cả tài khoản demo đều dùng mật khẩu mặc định: `123456`

| Vai trò (Role) | Tên đăng nhập (Username) | Mật khẩu | Họ và tên | Chức năng chính |
|---|---|---|---|---|
| **Chủ Tiệm (Owner)** | `chutiem` | `123456` | Emmay Beauty Owner | Timeline 30p, phân công KTV, quản lý dịch vụ, quản lý khách hàng, thu ngân |
| **Kỹ Thuật Viên 1** | `nhanvien1` | `123456` | Nguyễn Thị Mai | Xem lịch phân công, tiếp nhận / từ chối lịch (kèm lý do) |
| **Kỹ Thuật Viên 2** | `nhanvien2` | `123456` | Trần Thu Hà | Xem lịch phân công, tiếp nhận / từ chối lịch |
| **Kỹ Thuật Viên 3** | `nhanvien3` | `123456` | Lê Phương Thảo | Xem lịch phân công, tiếp nhận / từ chối lịch |
| **Khách Hàng 1** | `khachhang1` | `123456` | Nguyễn Hồng Nhung | Đặt lịch trực tuyến, đổi lịch, hủy lịch, xem lịch sử |
| **Khách Hàng 2** | `khachhang2` | `123456` | Đỗ Lan Anh | Đặt lịch, theo dõi trạng thái lịch hẹn |

*(Trên giao diện đăng nhập có sẵn 3 nút nhấn nhanh để tự động điền tài khoản Chủ Tiệm / Nhân Viên / Khách Hàng tiện cho việc chấm thi & thuyết trình).*

---

## 3. HƯỚNG DẪN CÀI ĐẶT & CHẠY DỰ ÁN TRÊN WINDOWS

### Bước 1: Mở Terminal (PowerShell hoặc CMD) tại thư mục dự án
```powershell
cd "d:\NAM3\PTTK-50K\BT-NHOM\WEB MẪU"
```

### Bước 2: Cài đặt thư viện phụ thuộc
```powershell
python -m pip install -r requirements.txt
```

### Bước 3: Áp dụng cơ sở dữ liệu
```powershell
python manage.py migrate
```

### Bước 4: Khởi tạo dữ liệu mẫu (Seed Data)
```powershell
python manage.py seed_emmay
```
*(Lệnh này tạo sẵn 8 dịch vụ nail, 1 chủ tiệm, 3 kỹ thuật viên, 3 khách hàng, các lịch hẹn mẫu ở nhiều trạng thái và thông báo mẫu).*

### Bước 5: Chạy máy chủ Development
```powershell
python manage.py runserver 8000
```
Truy cập trình duyệt: **`http://127.0.0.1:8000/`**

---

## 4. BẢNG ĐỐI CHIẾU USE CASE THEO TÀI LIỆU SRS

| STT | Use Case SRS | Tên chức năng | Vai trò | URL Route | Kiểm tra Business Rules |
|---|---|---|---|---|---|
| **1** | **UC 1** | Đăng nhập hệ thống | Tất cả | `/accounts/login/` | Mật khẩu băm PBKDF2, kiểm tra bắt buộc, điều hướng theo vai trò |
| **2** | **UC 2.1** | Tiếp nhận lịch được phân công | Kỹ thuật viên | `/employee/assignments/<id>/accept/` | Không nhận lịch đã hủy; tự động chuyển lịch sang "Đã xác nhận" |
| **3** | **UC 2.2** | Từ chối lịch được phân công | Kỹ thuật viên | `/employee/assignments/<id>/reject/` | **Bắt buộc nhập lý do**, hủy quyền phụ trách, thông báo khẩn cho Chủ Tiệm |
| **4** | **UC 2.3** | Xem thông tin lịch được phân công | Kỹ thuật viên | `/employee/` | Chỉ hiển thị các lịch được phân công cho chính KTV đăng nhập |
| **5** | **UC 3.1** | Theo dõi lịch hẹn bằng Timeline | Chủ tiệm | `/owner/timeline/` | Giờ mở cửa 09:00 - 19:00, bước 30 phút, lọc theo ngày trực quan |
| **6** | **UC 3.2** | Cập nhật trạng thái lịch hẹn | Chủ tiệm | `/owner/appointments/<id>/status/` | Chuyển đổi trạng thái, giải phóng slot khi Hủy, thông báo cho khách |
| **7** | **UC 4.1** | Danh sách dịch vụ nail | Chủ tiệm | `/owner/services/` | Tìm kiếm theo tên dịch vụ, hiển thị giá & thời lượng |
| **8** | **UC 4.2** | Thêm mới dịch vụ nail | Chủ tiệm | `/owner/services/create/` | Tên duy nhất, Giá > 0, Thời lượng thuộc [30,60,90,120,150,180] |
| **9** | **UC 4.3** | Chỉnh sửa dịch vụ nail | Chủ tiệm | `/owner/services/<id>/edit/` | Lịch hẹn đã đặt trước đó giữ nguyên đơn giá & thời lượng lúc đặt |
| **10** | **UC 4.4** | Xóa dịch vụ nail (Soft delete) | Chủ tiệm | `/owner/services/<id>/delete/` | **Chặn xóa** nếu dịch vụ đang có lịch "Chờ xác nhận" hoặc "Đã xác nhận" |
| **11** | **UC 5.1** | Danh sách lịch cần phân công | Chủ tiệm | `/owner/assignments/` | Tổng quan lịch hẹn hoạt động, tình trạng tiếp nhận của nhân viên |
| **12** | **UC 5.2** | Phân công kỹ thuật viên | Chủ tiệm | `/owner/assignments/assign/<id>/` | **Chống trùng lịch:** `start_A < end_B AND start_B < end_A`, KTV chỉ phục vụ 1 khách tại 1 thời điểm |
| **13** | **UC 6.1** | Danh sách & tìm kiếm khách hàng | Chủ tiệm | `/owner/customers/` | Tìm kiếm theo họ tên hoặc số điện thoại đúng 10 số |
| **14** | **UC 6.2** | Thêm thông tin khách hàng | Chủ tiệm | `/owner/customers/create/` | SĐT bắt buộc đúng 10 chữ số |
| **15** | **UC 6.3** | Sửa thông tin khách hàng | Chủ tiệm | `/owner/customers/<id>/edit/` | Cập nhật link Facebook, Zalo |
| **16** | **UC 6.4** | Xem chi tiết & lịch sử đặt | Chủ tiệm | `/owner/customers/<id>/` | Xem toàn bộ các lần đặt lịch trước đây và trạng thái |
| **17** | **UC 7.1** | Tạo lịch hẹn trực tuyến | Khách hàng | `/customer/booking/` | Chọn nhiều DV, tính tổng tiền & thời gian, slot trống theo sức chứa thợ, thông báo Chủ tiệm |
| **18** | **UC 7.2** | Đổi lịch hẹn | Khách hàng | `/customer/appointments/<id>/reschedule/` | Chọn ngày/giờ mới trống, giải phóng slot cũ, thông báo Chủ tiệm |
| **19** | **UC 7.3** | Hủy lịch hẹn | Khách hàng | `/customer/appointments/<id>/cancel/` | **Quy tắc 2 tiếng:** cảnh báo khi hủy dưới 2 giờ nhưng vẫn ghi nhận hủy per SRS |
| **20** | **UC 8** | Xem thông tin dịch vụ | Khách / Public | `/services/` | Hiển thị bảng giá, thời lượng, mô tả chuẩn thương hiệu |
| **21** | **UC 9** | Đăng ký tài khoản khách hàng | Khách / Public | `/accounts/register/` | Tên đăng nhập duy nhất, SĐT 10 số, liên kết hồ sơ khách hàng, mã hóa mật khẩu |
| **22** | **NFR** | Thông báo hệ thống | Tất cả | `/notifications/` | Chuông thông báo trực quan, badge số chưa đọc, lưu vết CSDL |
| **23** | **Mục 11**| Thanh toán Tiền mặt & QR | Chủ tiệm | `/payments/checkout/<id>/` | Tạo mã VietQR chuẩn theo số tiền và memo, hoàn tất lịch hẹn |

---

## 5. CHẠY BỘ KIỂM THỬ (UNIT TESTS)

Dự án đã tích hợp bộ kiểm thử tự động kiểm tra toàn bộ 9 nhóm ràng buộc nghiệp vụ:
```powershell
python manage.py test tests
```
Kết quả kiểm thử: **9/9 tests passed (OK)**.
