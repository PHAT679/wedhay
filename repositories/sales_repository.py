# file: repositories/sales_repository.py
from .base_repository import BaseRepository
# import pyodbc

class SalesRepository(BaseRepository):
    POINTS_REQUIRED = 5
    POINT_DISCOUNT_VND = 50000
    EARN_THRESHOLD_VND = 250000

    def get_products_for_sale(self) -> list[dict]:
        """Lấy danh sách sản phẩm để bán từ View V_SANPHAM_BAN"""
        return self.fetch_view("V_SANPHAM_BAN")

    def create_invoice(self, mahd: str, makh: str, manv: str, chietkhau: float) -> bool:
        """Tạo hóa đơn bán mới"""
        try:
            return self.execute_procedure("usp_TAO_HOADON_BAN", [mahd, makh, manv, chietkhau])
        except pyodbc.Error:
            raise

    def check_stock(self, maspct: str, soluong: int) -> dict:
        """Kiểm tra tồn kho"""
        try:
            result = self.execute_procedure_with_result("usp_KiemTraTonKho", [maspct, soluong])
            if result:
                return result[0]
            return {}
        except Exception as e:
            print(f"[Repo] check_stock error: {e}")
            return {"Error": "Lỗi hệ thống"}

    def add_invoice_item(self, mahd: str, maspct: str, soluong: int) -> bool:
        """Thêm chi tiết hóa đơn bán"""
        try:
            return self.execute_procedure("usp_THEM_CTHDB", [mahd, maspct, soluong])
        except pyodbc.Error:
            raise

    def increase_existing_invoice_item(self, mahd: str, maspct: str, soluong: int) -> bool:
        """Tăng số lượng sản phẩm đã có trong hóa đơn khi bị trùng khóa."""
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE dbo.CHITIET_HDBAN SET SOLUONG_BAN = ISNULL(SOLUONG_BAN, 0) + ? WHERE MAHDB = ? AND MASPCT = ?",
                [soluong, mahd, maspct]
            )
            if cur.rowcount == 0:
                conn.rollback()
                return False
            conn.commit()
            return True
        except pyodbc.Error:
            conn.rollback()
            try:
                cur.execute(
                    "UPDATE dbo.CHITIET_HDBAN SET SOLUONG = ISNULL(SOLUONG, 0) + ? WHERE MAHDB = ? AND MASPCT = ?",
                    [soluong, mahd, maspct]
                )
                if cur.rowcount == 0:
                    conn.rollback()
                    return False
                conn.commit()
                return True
            except pyodbc.Error as e:
                conn.rollback()
                print(f"[Repo] increase_existing_invoice_item error: {e}")
                return False
        finally:
            cur.close()

    def get_invoice_detail(self, mahd: str) -> list[dict]:
        """Lấy chi tiết hóa đơn bán (danh sách sản phẩm đã thêm)"""
        try:
            return self.fetch_procedure("usp_LAY_CHITIET_HOADON_BAN", [mahd])
        except Exception as e:
            print(f"[Repo] get_invoice_detail error: {e}")
            if "Could not find stored procedure 'usp_LAY_CHITIET_HOADON_BAN'" in str(e):
                print("[Repo] fallback to view V_HOADON_BAN_CHITIET by MAHDB")
                try:
                    return self.fetch_view_where("V_HOADON_BAN_CHITIET", "MAHDB = ?", [mahd])
                except Exception as view_err:
                    print(f"[Repo] fallback get_invoice_detail from view error: {view_err}")
            return []

    def checkout_invoice(self, mahd: str, tien_khach_dua: float) -> bool:
        """Thanh toán hóa đơn bán"""
        try:
            return self.execute_procedure("usp_THANH_TOAN_HOADON_BAN", [mahd, tien_khach_dua])
        except Exception:
            return False

    def get_next_sales_invoice_id(self):
        """Lấy mã hóa đơn bán tiếp theo từ usp_SINH_MA_HOADON_BAN"""
        try:
            result = self.fetch_procedure("usp_SINH_MA_HOADON_BAN")
            if result and len(result) > 0:
                return result[0].get("MAHDB")
        except Exception as e:
            print(f"[SalesRepo] get_next_sales_invoice_id error: {e}")
        return None

    def search_customers_for_sale(self, keyword: str) -> list[dict]:
        conn = self._conn()
        cur = conn.cursor()
        kw = (keyword or "").strip()
        if not kw:
            return []
        like_kw = f"%{kw}%"
        try:
            cur.execute(
                """
                SELECT
                    kh.MAKH,
                    kh.TENKH,
                    kh.SDT,
                    CAST(N'' AS NVARCHAR(255)) AS DIACHIKH,
                    ISNULL(v.TONG_DIEM, 0) AS TONG_DIEM
                FROM KHACHHANG kh
                LEFT JOIN V_DIEM_KHACHHANG v ON kh.MAKH = v.MAKH
                WHERE kh.SDT LIKE ?
                   OR kh.TENKH COLLATE Latin1_General_CI_AI LIKE ?
                ORDER BY kh.TENKH
                """,
                [like_kw, like_kw]
            )
            return self._rows_to_dicts(cur)
        finally:
            cur.close()

    def get_customer_points(self, makh: str) -> int:
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT ISNULL(TONG_DIEM, 0) AS TONG_DIEM FROM V_DIEM_KHACHHANG WHERE MAKH = ?",
                [makh]
            )
            rows = self._rows_to_dicts(cur)
            if not rows:
                return 0
            return int(rows[0].get("TONG_DIEM") or 0)
        finally:
            cur.close()

    def get_customer_by_phone(self, phone: str) -> dict | None:
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT TOP 1
                    kh.MAKH,
                    kh.TENKH,
                    kh.SDT,
                    ISNULL(v.TONG_DIEM, 0) AS TONG_DIEM
                FROM KHACHHANG kh
                LEFT JOIN V_DIEM_KHACHHANG v ON kh.MAKH = v.MAKH
                WHERE kh.SDT = ?
                """,
                [phone],
            )
            rows = self._rows_to_dicts(cur)
            return rows[0] if rows else None
        finally:
            cur.close()

    def get_invoice_customer(self, mahd: str) -> dict | None:
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT TOP 1
                    hd.MAHDB,
                    hd.MAKH,
                    kh.TENKH,
                    kh.SDT,
                    CAST(N'' AS NVARCHAR(255)) AS DIACHIKH,
                    ISNULL(v.TONG_DIEM, 0) AS TONG_DIEM,
                    ISNULL(hd.DIEM_SUDUNG, 0) AS DIEM_SUDUNG
                FROM HDBAN hd
                LEFT JOIN KHACHHANG kh ON hd.MAKH = kh.MAKH
                LEFT JOIN V_DIEM_KHACHHANG v ON hd.MAKH = v.MAKH
                WHERE hd.MAHDB = ?
                """,
                [mahd]
            )
            rows = self._rows_to_dicts(cur)
            return rows[0] if rows else None
        finally:
            cur.close()

    def update_invoice_customer(self, mahd: str, makh: str | None) -> bool:
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE HDBAN SET MAKH = ? WHERE MAHDB = ?", [makh, mahd])
            if cur.rowcount <= 0:
                conn.rollback()
                return False
            conn.commit()
            return True
        except pyodbc.Error:
            conn.rollback()
            raise
        finally:
            cur.close()

    def generate_loyalty_id(self) -> str:
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute("SELECT MAX(ID) AS MAX_ID FROM DIEMTICHLUY")
            rows = self._rows_to_dicts(cur)
            max_id = (rows[0].get("MAX_ID") if rows else "") or ""
            max_id = str(max_id).strip()
            if not max_id:
                return "DTL0000001"
            prefix = "".join(ch for ch in max_id if not ch.isdigit()) or "DTL"
            digits = "".join(ch for ch in max_id if ch.isdigit()) or "0"
            next_num = int(digits) + 1
            new_id = f"{prefix}{str(next_num).zfill(max(len(digits), 7))}"
            return new_id[:10]
        finally:
            cur.close()

    def use_customer_points(self, loyalty_id: str, makh: str, mahdb: str, conn=None) -> None:
        local_conn = conn or self._conn()
        cur = local_conn.cursor()
        try:
            cur.execute("SET NOCOUNT ON; EXEC dbo.usp_SUDUNG_DIEM ?, ?, ?", [loyalty_id, makh, mahdb])
        finally:
            cur.close()

    def add_customer_point(self, loyalty_id: str, makh: str, mahdb: str, conn=None) -> None:
        local_conn = conn or self._conn()
        cur = local_conn.cursor()
        try:
            cur.execute("SET NOCOUNT ON; EXEC dbo.usp_TICH_DIEM ?, ?, ?", [loyalty_id, makh, mahdb])
        finally:
            cur.close()

    def checkout_invoice_with_points(self, mahdb: str, money_received: float, use_points: bool, discount_percent: float) -> dict:
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM CHITIET_HDBAN WHERE MAHDB = ?", [mahdb])
            item_rows = self._rows_to_dicts(cur)
            if not item_rows or len(item_rows) <= 0:
                return {"success": False, "message": "Hóa đơn chưa có sản phẩm."}
            
            total_amount = 0.0
            for row in item_rows:
                sl = float(row.get("SOLUONG_BAN") or row.get("SOLUONG") or 0)
                dg = float(row.get("DONGIA_BAN") or row.get("DONGIA") or 0)
                total_amount += sl * dg

            cur.execute(
                """
                SELECT TOP 1
                    MAHDB,
                    MAKH,
                    ISNULL(CHIETKHAU, 0) AS CHIETKHAU,
                    ISNULL(DIEM_SUDUNG, 0) AS DIEM_SUDUNG,
                    ISNULL(TIENKHACHDUA, 0) AS TIENKHACHDUA
                FROM HDBAN
                WHERE MAHDB = ?
                """,
                [mahdb]
            )
            invoice_rows = self._rows_to_dicts(cur)
            if not invoice_rows:
                return {"success": False, "message": "Không tìm thấy hóa đơn để thanh toán."}
            invoice = invoice_rows[0]
            makh = (invoice.get("MAKH") or "").strip()
            current_diem_sudung = int(invoice.get("DIEM_SUDUNG") or 0)

            if float(invoice.get("TIENKHACHDUA") or 0) > 0:
                return {"success": False, "message": "Hóa đơn đã thanh toán, không thể thanh toán lại."}

            if use_points and not makh:
                return {"success": False, "message": "Vui lòng chọn khách hàng trước khi sử dụng điểm."}

            point_discount = 0.0
            if use_points:
                if current_diem_sudung >= self.POINTS_REQUIRED:
                    return {"success": False, "message": "Hóa đơn này đã áp dụng sử dụng điểm."}
                current_points = self.get_customer_points(makh)
                if current_points < self.POINTS_REQUIRED:
                    return {"success": False, "message": "Khách hàng không đủ 5 điểm để sử dụng."}
                loyalty_id = self.generate_loyalty_id()
                if not loyalty_id:
                    return {"success": False, "message": "Không thể sinh mã điểm."}
                self.use_customer_points(loyalty_id, makh, mahdb, conn=conn)
                point_discount = float(self.POINT_DISCOUNT_VND)

            # Tính lại
            discount_money = total_amount * discount_percent / 100.0
            amount_due = total_amount - discount_money - point_discount
            if amount_due < 0:
                amount_due = 0.0
            
            change_amount = money_received - amount_due

            print("===== CHECKOUT DEBUG =====")
            print("MAHDB:", mahdb)
            print("MAKH:", makh)
            print("USE POINTS:", use_points)
            print("DISCOUNT PERCENT:", discount_percent)
            print("TOTAL ITEMS:", total_amount)
            print("DISCOUNT MONEY:", discount_money)
            print("POINT DISCOUNT:", point_discount)
            print("AMOUNT DUE:", amount_due)
            print("MONEY RECEIVED:", money_received)
            print("CHANGE:", change_amount)

            if money_received < amount_due:
                conn.rollback()
                return {"success": False, "message": "Tiền khách đưa không đủ."}

            try:
                cur.execute("UPDATE HDBAN SET TIENKHACHDUA = ?, CHIETKHAU = ?, TONGTIENHANG = ? WHERE MAHDB = ?", [money_received, discount_percent, total_amount, mahdb])
            except pyodbc.Error:
                cur.execute("UPDATE HDBAN SET TIENKHACHDUA = ? WHERE MAHDB = ?", [money_received, mahdb])

            if makh:
                net_revenue = amount_due
                cur.execute(
                    "SELECT COUNT(1) AS CNT FROM DIEMTICHLUY WHERE MAHDB = ? AND DIEM_THAYDOI > 0",
                    [mahdb],
                )
                rewarded_rows = self._rows_to_dicts(cur)
                reward_exists = int(rewarded_rows[0].get("CNT") or 0) > 0 if rewarded_rows else False

                if (not reward_exists) and net_revenue >= self.EARN_THRESHOLD_VND:
                    loyalty_id = self.generate_loyalty_id()
                    if not loyalty_id:
                        conn.rollback()
                        return {"success": False, "message": "Không thể sinh mã điểm."}
                    self.add_customer_point(loyalty_id, makh, mahdb, conn=conn)

            conn.commit()
            return {"success": True, "message": "Thanh toán thành công."}
        except pyodbc.Error as e:
            conn.rollback()
            return {"success": False, "message": str(e)}
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": str(e)}
        finally:
            cur.close()
