# file: services/sales_service.py
from repositories.sales_repository import SalesRepository
from flask import session
from .base_service import BaseService
# import pyodbc

class SalesService(BaseService):
    POINTS_REQUIRED = 5
    POINT_DISCOUNT_VND = 50000

    def __init__(self):
        self.repo = SalesRepository()

    @staticmethod
    def _to_int(value, default=0):
        try:
            if value is None:
                return default
            if isinstance(value, str):
                value = value.strip().replace(",", "")
                if value == "":
                    return default
            return int(float(value))
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _to_float(value, default=0.0):
        try:
            if value is None:
                return default
            if isinstance(value, str):
                cleaned = value.strip().replace(",", "").replace("đ", "").replace("vnđ", "").replace("VND", "")
                cleaned = cleaned.strip()
                if cleaned == "":
                    return default
                value = cleaned
            return float(value)
        except (ValueError, TypeError):
            return default

    def get_sales_page_data(self, customer_keyword: str = "") -> dict:
        try:
            raw_products = self.repo.get_products_for_sale()
            products = []
            for row in raw_products:
                products.append({
                    "MASPCT": self.pick(row, ["MASPCT", "MA_SPCT"], "N/A"),
                    "TENSANPHAM": self.pick(row, ["TENSP", "TENSANPHAM", "TEN_SANPHAM"], "N/A"),
                    "MAU": self.pick(row, ["TEN_MAU", "MAU", "TENMAU"], ""),
                    "SIZE": self.pick(row, ["TEN_SIZE", "SIZE", "COKISIZE", "TENSIZE"], ""),
                    "GIA_BAN": self.pick(row, ["DONGIA_BAN", "GIABAN", "GIA_BAN"], 0),
                    "TONKHO": self.pick(row, ["SL_TONKHO", "SOLUONG", "TONKHO", "TON_KHO"], 0)
                })

            current_invoice_id = session.get("current_invoice_id")
            cart_items = []
            selected_customer = None
            customer_search_results = []
            invoice_summary = {
                "tam_tinh": 0,
                "chiet_khau_percent": 0,
                "tien_chiet_khau": 0,
                "giam_bang_diem": 0,
                "tong_can_thanh_toan": 0
            }

            if customer_keyword:
                customer_search_results = self.repo.search_customers_for_sale(customer_keyword)

            if current_invoice_id:
                price_by_maspct = {
                    str(p.get("MASPCT", "")).strip(): self._to_float(p.get("GIA_BAN"), 0.0)
                    for p in products
                }
                cart_items = self.get_invoice_cart(current_invoice_id, price_by_maspct)
                selected_customer = self.repo.get_invoice_customer(current_invoice_id)
                chiet_khau_percent = session.get("current_invoice_discount", 0)
                try:
                    chiet_khau_percent = float(chiet_khau_percent)
                except (ValueError, TypeError):
                    chiet_khau_percent = 0

                diem_sudung = 0
                if selected_customer:
                    diem_sudung = self._to_int(selected_customer.get("DIEM_SUDUNG"), 0)
                invoice_summary = self.calculate_invoice_summary(cart_items, chiet_khau_percent, diem_sudung)

            return {
                "success": True,
                "data": {
                    "products": products,
                    "current_invoice_id": current_invoice_id,
                    "next_invoice_id": self.repo.get_next_sales_invoice_id(),
                    "cart_items": cart_items,
                    "invoice_summary": invoice_summary,
                    "selected_customer": selected_customer,
                    "customer_search_results": customer_search_results,
                }
            }
        except Exception as e:
            print(f"[SalesService] get_sales_page_data error: {e}")
            return {
                "success": False,
                "data": {
                    "products": [],
                    "current_invoice_id": None,
                    "cart_items": [],
                    "invoice_summary": {
                        "tam_tinh": 0,
                        "chiet_khau_percent": 0,
                        "tien_chiet_khau": 0,
                        "giam_bang_diem": 0,
                        "tong_can_thanh_toan": 0
                    },
                    "selected_customer": None,
                    "customer_search_results": [],
                }
            }

    def get_invoice_cart(self, mahd: str, price_by_maspct: dict | None = None) -> list[dict]:
        raw_items = self.repo.get_invoice_detail(mahd)
        cart = []
        price_by_maspct = price_by_maspct or {}
        for item in raw_items:
            maspct = self.pick(item, ["MASPCT", "MA_SPCT"], "")
            ten_sp = self.pick(item, ["TENSANPHAM", "TEN_SANPHAM", "TENSP"], "Sản phẩm")
            mau = self.pick(item, ["MAU", "MAMAU", "TEN_MAU"], "")
            size = self.pick(item, ["SIZE", "MASIZE", "COKISIZE", "TEN_SIZE"], "")
            
            so_luong = self.pick(
                item,
                ["SOLUONG", "SO_LUONG", "SOLUONG_BAN", "SL", "SO_LUONG_BAN", "QUANTITY"],
                0
            )
            don_gia = self.pick(
                item,
                ["DONGIABAN", "DONGIA", "GIA_BAN", "DONGIA_BAN", "DON_GIA", "GIABAN", "PRICE", "UNIT_PRICE"],
                price_by_maspct.get(maspct, 0)
            )

            sl = self._to_int(so_luong, 0)
            dg = self._to_float(don_gia, 0.0)

            thanh_tien = self.pick(
                item,
                ["THANHTIEN", "THANH_TIEN", "TONGTIEN", "TONG_TIEN", "THANH_TIEN_BAN", "LINE_TOTAL", "AMOUNT"],
                sl * dg
            )
            tt = self._to_float(thanh_tien, sl * dg)

            cart.append({
                "ma_spct": maspct,
                "ten_san_pham": ten_sp,
                "mau": mau,
                "size": size,
                "so_luong": sl,
                "don_gia": dg,
                "thanh_tien": tt
            })
        return cart

    def calculate_invoice_summary(self, cart_items: list[dict], discount_percent: float, diem_sudung: int = 0) -> dict:
        tam_tinh = sum(item.get("thanh_tien", 0) for item in cart_items)
        tien_chiet_khau = tam_tinh * discount_percent / 100.0
        diem_da_dung = int(diem_sudung or 0)
        giam_bang_diem = self.POINT_DISCOUNT_VND if diem_da_dung >= self.POINTS_REQUIRED else 0
        tong_can_thanh_toan = tam_tinh - tien_chiet_khau - giam_bang_diem
        if tong_can_thanh_toan < 0:
            tong_can_thanh_toan = 0
        
        return {
            "tam_tinh": tam_tinh,
            "chiet_khau_percent": discount_percent,
            "tien_chiet_khau": tien_chiet_khau,
            "giam_bang_diem": giam_bang_diem,
            "tong_can_thanh_toan": tong_can_thanh_toan
        }

    def create_invoice(self, data: dict) -> dict:
        mahd = (data.get("mahd") or "").strip()
        makh = (data.get("makh") or "").strip()
        if not makh:
            makh = None
        manv = (data.get("manv") or "").strip()
        
        try:
            chietkhau = float(data.get("chietkhau") or 0)
        except ValueError:
            chietkhau = 0.0

        if not mahd:
            return {"success": False, "message": "Thiếu mã hóa đơn."}
        if not manv:
            return {
                "success": False,
                "message": "Không xác định được nhân viên đang đăng nhập. Vui lòng đăng nhập lại."
            }

        invoice_data = {
            "MAHDB": mahd,
            "MAKH": makh,
            "MANV": manv,
            "CHIETKHAU": chietkhau
        }

        try:
            success = self.repo.create_invoice(
                invoice_data["MAHDB"],
                invoice_data["MAKH"],
                invoice_data["MANV"],
                invoice_data["CHIETKHAU"]
            )
            if success:
                session["current_invoice_id"] = mahd
                session["current_invoice_discount"] = chietkhau
                return {"success": True, "message": "Tạo hóa đơn thành công."}
            return {"success": False, "message": "Không thể tạo hóa đơn."}
        except pyodbc.Error as e:
            err_text = str(e)
            if "Khách hàng không tồn tại" in err_text:
                return {
                    "success": False,
                    "message": "Mã khách hàng không tồn tại. Để trống nếu bán lẻ hoặc nhập mã KH hợp lệ."
                }
            if "trùng" in err_text.lower() or "duplicate" in err_text.lower():
                return {"success": False, "message": "Không thể tạo hóa đơn. Mã HĐ có thể bị trùng."}
            return {"success": False, "message": "Lỗi tạo hóa đơn từ database."}

    def add_item_to_invoice(self, mahd: str, maspct: str, soluong: int) -> dict:
        if not mahd:
            return {"success": False, "message": "Vui lòng tạo hóa đơn trước."}
        if not maspct or soluong <= 0:
            return {"success": False, "message": "Dữ liệu sản phẩm không hợp lệ."}

        # Check stock
        stock_status = self.repo.check_stock(maspct, soluong)
        if "Error" in stock_status:
            return {"success": False, "message": stock_status["Error"]}
        
        result_msg = stock_status.get("Result", "")
        if "không đủ" in result_msg.lower() or "hết hàng" in result_msg.lower():
            return {"success": False, "message": result_msg}

        # Add item
        try:
            success = self.repo.add_invoice_item(mahd, maspct, soluong)
            if success:
                return {"success": True, "message": "Thêm sản phẩm thành công."}
            return {"success": False, "message": "Lỗi thêm chi tiết hóa đơn."}
        except pyodbc.Error as e:
            err_text = str(e)
            if "PK_CTHDB" in err_text or "duplicate key" in err_text.lower():
                increased = self.repo.increase_existing_invoice_item(mahd, maspct, soluong)
                if increased:
                    return {"success": True, "message": "Đã tăng số lượng sản phẩm trong giỏ."}
            return {"success": False, "message": "Lỗi thêm chi tiết hóa đơn."}

    def checkout_invoice(self, mahd: str, tien_khach_dua: float, use_points: bool, discount_percent: float) -> dict:
        if not mahd:
            return {"success": False, "message": "Không có hóa đơn để thanh toán."}
        if tien_khach_dua < 0:
            return {"success": False, "message": "Số tiền không hợp lệ."}
        res = self.repo.checkout_invoice_with_points(mahd, tien_khach_dua, use_points, discount_percent)
        if res.get("success"):
            session.pop("current_invoice_id", None)
            session.pop("current_invoice_discount", None)
            session.pop("checkout_use_points", None)
            return {"success": True, "message": "Thanh toán thành công."}
        msg = str(res.get("message") or "Thanh toán thất bại.")
        if "Hóa đơn này đã áp dụng sử dụng điểm" in msg:
            return {"success": False, "message": "Hóa đơn này đã áp dụng sử dụng điểm, không thể dùng thêm!"}
        if "Khách hàng không đủ 5 điểm" in msg:
            return {"success": False, "message": "Khách hàng không đủ 5 điểm để sử dụng."}
        if "Hóa đơn đã thanh toán" in msg:
            return {"success": False, "message": "Hóa đơn đã thanh toán, không thể thanh toán lại."}
        return {"success": False, "message": msg}

    def assign_customer_to_current_invoice(self, mahd: str, makh: str) -> dict:
        if not mahd:
            return {"success": False, "message": "Vui lòng tạo hóa đơn trước."}
        makh = (makh or "").strip()
        if not makh:
            return {"success": False, "message": "Vui lòng chọn mã khách hàng."}
        try:
            points = self.repo.get_customer_points(makh)
            success = self.repo.update_invoice_customer(mahd, makh)
            if not success:
                return {"success": False, "message": "Không thể cập nhật khách hàng vào hóa đơn."}
            session["checkout_use_points"] = False
            return {"success": True, "message": f"Đã chọn khách hàng ({points} điểm)."}
        except pyodbc.Error as e:
            return {"success": False, "message": str(e)}

    def set_use_points_for_checkout(self, mahd: str, use_points: bool) -> dict:
        if not mahd:
            return {"success": False, "message": "Vui lòng tạo hóa đơn trước."}
        customer = self.repo.get_invoice_customer(mahd)
        if not customer or not (customer.get("MAKH") or "").strip():
            session["checkout_use_points"] = False
            return {"success": False, "message": "Vui lòng chọn khách hàng trước khi dùng điểm."}
        tong_diem = self._to_int(customer.get("TONG_DIEM"), 0)
        if use_points and tong_diem < 5:
            session["checkout_use_points"] = False
            return {"success": False, "message": "Khách hàng không đủ 5 điểm để sử dụng."}
        session["checkout_use_points"] = bool(use_points)
        return {"success": True, "message": "Đã cập nhật sử dụng điểm."}

    def get_customer_by_phone(self, phone: str) -> dict:
        normalized = (phone or "").strip()
        if len(normalized) != 10 or (not normalized.isdigit()):
            return {"success": False, "message": "Số điện thoại không hợp lệ."}
        customer = self.repo.get_customer_by_phone(normalized)
        if not customer:
            return {"success": False, "message": "Không tìm thấy khách hàng"}
        return {"success": True, "customer": customer}

    def set_customer_for_current_invoice(self, mahd: str, makh: str) -> dict:
        if not mahd:
            return {"success": False, "message": "Vui lòng tạo hóa đơn trước."}
        normalized_makh = (makh or "").strip()
        try:
            if normalized_makh:
                success = self.repo.update_invoice_customer(mahd, normalized_makh)
                if not success:
                    return {"success": False, "message": "Không thể cập nhật khách hàng vào hóa đơn."}
                points = self.repo.get_customer_points(normalized_makh)
                session["checkout_use_points"] = False
                return {
                    "success": True,
                    "message": "Đã gán khách hàng vào hóa đơn.",
                    "customer": {
                        "MAKH": normalized_makh,
                        "TONG_DIEM": points,
                    },
                }
            success = self.repo.update_invoice_customer(mahd, None)
            if not success:
                return {"success": False, "message": "Không thể chuyển về khách lẻ."}
            session["checkout_use_points"] = False
            return {"success": True, "message": "Đã chuyển hóa đơn về khách lẻ."}
        except pyodbc.Error as e:
            return {"success": False, "message": str(e)}
