# README_BACKEND.md — Seller Management System

## Cấu trúc dự án

```
web_moi/
├── app.py                  ← Chạy: python app.py
├── config.py               ← Cấu hình SQL Server
├── database.py             ← Kết nối pyodbc
├── requirements.txt
├── sql/
│   └── 00_MISSING_PROCEDURES.sql
├── controllers/            ← Flask Blueprints (nhận request)
├── services/               ← Business logic + validation
├── repositories/           ← Truy cập DB (EXEC SP / SELECT View)
├── templates/              ← Jinja2 HTML
└── static/css|js/          ← CSS + JavaScript
```

## 1. Cài đặt môi trường

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

## 2. Cấu hình SQL Server

Mở `config.py` và sửa:

```python
SERVER   = "localhost"              # hoặc .\SQLEXPRESS
DATABASE = "QL_BANHANG_SAUBANH"
DRIVER   = "ODBC Driver 17 for SQL Server"
TRUSTED  = "yes"                    # Windows Auth
```

Nếu dùng SQL Auth thay vì Windows Auth:
```python
TRUSTED  = "no"
USERNAME = "sa"
PASSWORD = "your_password"
```

## 3. Chạy SQL bổ sung

Mở SQL Server Management Studio, chạy:

```
sql/00_MISSING_PROCEDURES.sql
```

File này tạo các Stored Procedure và View còn thiếu:
- `V_NHACUNGCAP`
- `usp_THEM_SANPHAM`
- `usp_THEM_SANPHAM_CHITIET`
- `usp_THEM_BANGGIA`
- `usp_CAPNHAT_KHACHHANG`
- `usp_THEM_NHACUNGCAP`
- `usp_CAPNHAT_NHACUNGCAP`

## 4. Chạy ứng dụng

```bash
python app.py
```

Truy cập: **http://127.0.0.1:5000**

## 5. Phân quyền

| Role      | Quyền truy cập                                              |
|-----------|-------------------------------------------------------------|
| admin     | Tất cả chức năng                                            |
| seller    | Dashboard, Bán hàng, Sản phẩm, Khách hàng                  |
| warehouse | Dashboard, Tồn kho, Nhập hàng, Sản phẩm, Nhà cung cấp      |

## 6. Quy trình bán hàng POS

1. Vào **Bán hàng** → tìm kiếm/lọc sản phẩm bên trái
2. Bấm **Chọn** → mã SPCT tự điền vào form bên phải
3. Điền mã hóa đơn → **Tạo hóa đơn**
4. Kiểm tra tồn kho → **Thêm vào hóa đơn**
5. Nhập tiền khách đưa → **THANH TOÁN**

## 7. Kiến trúc 3-layer

```
Controller  →  Service  →  Repository  →  SQL Server
(Blueprint)    (Logic)      (EXEC SP /     (Stored Proc
                             SELECT View)    + Views)
```

**Nguyên tắc:**
- Repository: chỉ EXEC Stored Procedure hoặc SELECT View
- Service: validate input, xử lý lỗi, trả `{"success": bool, "message": str}`
- Controller: nhận request, gọi service, flash + redirect
