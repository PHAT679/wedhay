# file: repositories/purchase_repository.py
from .base_repository import BaseRepository


class PurchaseRepository(BaseRepository):

    def get_purchase_details(self) -> list[dict]:
        return self.fetch_view("V_HOADON_NHAP_CHITIET")

    def get_debts(self) -> list[dict]:
        return self.fetch_view("V_CONG_NO_NHA_CUNG_CAP")

    def get_suppliers(self) -> list[dict]:
        try:
            return self.fetch_procedure("usp_LAY_DANH_SACH_NHACUNGCAP")
        except Exception as e:
            print(f"[PurchaseRepo] get_suppliers error: {e}")
            return []

    def get_purchase_invoice_info(self, mahdn: str) -> dict:
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute("SELECT MAHDN, MA_NCC, MANV, CHIETKHAU FROM HDNHAP WHERE MAHDN = ?", [mahdn])
            row = cur.fetchone()
            if row:
                return {
                    "mahdn": row[0],
                    "ma_ncc": row[1],
                    "manv": row[2],
                    "chietkhau": float(row[3] or 0)
                }
        except Exception as e:
            print(f"[PurchaseRepo] get_purchase_invoice_info error: {e}")
        finally:
            cur.close()
        return {}

    def create_purchase(self, mahdn: str, mancc: str, manv: str):
        self.execute_procedure("dbo.usp_TAO_HOADON_NHAP", [mahdn, mancc, manv])

    def add_item(self, mahdn: str, maspct: str, soluong: int):
        self.execute_procedure("dbo.usp_THEM_CTHDN", [mahdn, maspct, soluong])

    def pay_debt(self, matt: str, mahdn: str, so_tien: float):
        self.execute_procedure("usp_THANH_TOAN_HDN", [matt, mahdn, so_tien])

    def get_next_purchase_invoice_id(self):
        try:
            result = self.fetch_procedure("usp_SINH_MA_HOADON_NHAP")
            if result and len(result) > 0:
                return result[0].get("MAHDN")
        except Exception as e:
            print(f"[PurchaseRepo] get_next_purchase_invoice_id error: {e}")
        return None

    def get_next_payment_id(self):
        try:
            result = self.fetch_procedure("usp_SINH_MA_THANHTOAN")
            if result and len(result) > 0:
                return result[0].get("MATT")
        except Exception as e:
            print(f"[PurchaseRepo] get_next_payment_id error: {e}")
        return None

    def get_purchase_items(self, mahdn: str) -> list[dict]:
        conn = self._conn()
        cur = conn.cursor()
        sql = """
            SELECT
                ct.MAHDN,
                ct.MASPCT,
                sp.TENSP,
                mau.TEN_MAU,
                size.TEN_SIZE,
                ct.SOLUONG_NHAP,
                bg.DONGIA_NHAP,
                (ct.SOLUONG_NHAP * ISNULL(bg.DONGIA_NHAP, 0)) AS THANH_TIEN
            FROM CHITIET_HDNHAP ct
            JOIN HDNHAP h
                ON ct.MAHDN = h.MAHDN
            JOIN SANPHAM_CHITIET spct
                ON ct.MASPCT = spct.MASPCT
            JOIN SANPHAM sp
                ON spct.MASP = sp.MASP
            LEFT JOIN DANHMUC_MAU mau
                ON spct.MA_MAU = mau.MA_MAU
            LEFT JOIN DANHMUC_SIZE size
                ON spct.MA_SIZE = size.MA_SIZE
            OUTER APPLY (
                SELECT TOP 1 bg2.DONGIA_NHAP
                FROM BANGGIA bg2
                WHERE bg2.MASPCT = ct.MASPCT
                  AND bg2.NGAY_BAT_DAU <= h.NGAYGIO_NK
                  AND (
                        bg2.NGAY_KET_THUC IS NULL
                        OR bg2.NGAY_KET_THUC >= h.NGAYGIO_NK
                  )
                ORDER BY bg2.NGAY_BAT_DAU DESC
            ) bg
            WHERE ct.MAHDN = ?
            ORDER BY ct.MASPCT;
        """
        try:
            cur.execute(sql, [mahdn])
            return self._rows_to_dicts(cur)
        except Exception as e:
            print(f"[PurchaseRepo] get_purchase_items error: {e}")
            return []
        finally:
            cur.close()

    def get_purchase_summary(self, mahdn: str) -> dict:
        conn = self._conn()
        cur = conn.cursor()
        sql = """
            SELECT
                H.MAHDN,
                ISNULL(SUM(CT.SOLUONG_NHAP), 0) AS TONG_SOLUONG,
                ISNULL(H.TONGTIEN, 0) AS TONG_TIEN_HANG,
                ISNULL(H.CHIETKHAU, 0) AS CHIETKHAU_PERCENT,
                ISNULL(H.TONGTIEN, 0) * ISNULL(H.CHIETKHAU, 0) / 100 AS TIEN_CHIET_KHAU,
                CASE
                    WHEN ISNULL(H.TONGTIEN, 0) - (ISNULL(H.TONGTIEN, 0) * ISNULL(H.CHIETKHAU, 0) / 100) < 0
                    THEN 0
                    ELSE ISNULL(H.TONGTIEN, 0) - (ISNULL(H.TONGTIEN, 0) * ISNULL(H.CHIETKHAU, 0) / 100)
                END AS CAN_THANH_TOAN
            FROM HDNHAP H
            LEFT JOIN CHITIET_HDNHAP CT
                ON H.MAHDN = CT.MAHDN
            WHERE H.MAHDN = ?
            GROUP BY H.MAHDN, H.TONGTIEN, H.CHIETKHAU
        """
        try:
            cur.execute(sql, [mahdn])
            row = cur.fetchone()
            if row:
                return {
                    "tong_soluong": float(row[1] or 0),
                    "tong_tien_hang": float(row[2] or 0),
                    "chietkhau_percent": float(row[3] or 0),
                    "tien_chiet_khau": float(row[4] or 0),
                    "can_thanh_toan": float(row[5] or 0),
                }
        except Exception as e:
            print(f"[PurchaseRepo] get_purchase_summary error: {e}")
        finally:
            cur.close()
        return {
            "tong_soluong": 0,
            "tong_tien_hang": 0,
            "chietkhau_percent": 0,
            "tien_chiet_khau": 0,
            "can_thanh_toan": 0,
        }

    def update_purchase_discount(self, mahdn: str, chietkhau: float):
        conn = self._conn()
        cur = conn.cursor()
        sql = """
            UPDATE HDNHAP
            SET CHIETKHAU = ?
            WHERE MAHDN = ?
        """
        try:
            cur.execute(sql, [chietkhau, mahdn])
            conn.commit()
        finally:
            cur.close()

    def get_products_for_purchase(self, keyword: str | None = None, status: str | None = None) -> list[dict]:
        conn = self._conn()
        cur = conn.cursor()
        sql = """
            SELECT
                MASPCT,
                TENSP,
                TEN_MAU,
                TEN_SIZE,
                SL_TONKHO,
                DONGIA_NHAP,
                CASE
                    WHEN SL_TONKHO <= 0 THEN N'Hết hàng'
                    WHEN SL_TONKHO <= 10 THEN N'Sắp hết'
                    ELSE N'Còn hàng'
                END AS TRANG_THAI
            FROM dbo.V_SANPHAM_NHAP
            WHERE
                (
                    ? IS NULL OR ? = N''
                    OR MASPCT COLLATE Latin1_General_CI_AI LIKE N'%' + ? + N'%'
                    OR TENSP COLLATE Latin1_General_CI_AI LIKE N'%' + ? + N'%'
                    OR TEN_MAU COLLATE Latin1_General_CI_AI LIKE N'%' + ? + N'%'
                    OR TEN_SIZE COLLATE Latin1_General_CI_AI LIKE N'%' + ? + N'%'
                )
                AND
                (
                    ? IS NULL OR ? = N'' OR ? = N'all'
                    OR (? = N'available' AND SL_TONKHO > 10)
                    OR (? = N'low' AND SL_TONKHO > 0 AND SL_TONKHO <= 10)
                    OR (? = N'out' AND SL_TONKHO <= 0)
                )
            ORDER BY TENSP, MASPCT;
        """
        keyword_value = (keyword or "").strip()
        status_value = (status or "").strip().lower()
        keyword_param = keyword_value if keyword_value else None
        status_param = status_value if status_value else None
        params = [
            keyword_param, keyword_value, keyword_value, keyword_value, keyword_value, keyword_value,
            status_param, status_value, status_value, status_value, status_value, status_value
        ]
        try:
            cur.execute(sql, params)
            return self._rows_to_dicts(cur)
        except Exception as e:
            print(f"[PurchaseRepo] get_products_for_purchase error: {e}")
            return []
        finally:
            cur.close()

    def purchase_exists(self, mahdn: str) -> bool:
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) AS CNT FROM HDNHAP WHERE MAHDN = ?", [mahdn])
            row = cur.fetchone()
            return row[0] > 0 if row else False
        except Exception as e:
            print(f"[PurchaseRepo] purchase_exists error: {e}")
            return False
        finally:
            cur.close()

    def count_purchase_details(self, mahdn: str) -> int:
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) AS CNT FROM CHITIET_HDNHAP WHERE MAHDN = ?", [mahdn])
            row = cur.fetchone()
            return row[0] if row else 0
        except Exception as e:
            print(f"[PurchaseRepo] count_purchase_details error: {e}")
            return 0
        finally:
            cur.close()
