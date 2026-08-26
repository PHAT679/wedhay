# file: repositories/supplier_repository.py
from .base_repository import BaseRepository
import pyodbc


class SupplierRepository(BaseRepository):

    def get_all_suppliers(self) -> list[dict]:
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute("SET NOCOUNT ON; EXEC dbo.usp_LAY_DANH_SACH_NHACUNGCAP")
            rows = self._rows_to_dicts(cur)
            suppliers = []
            for row in rows:
                suppliers.append({
                    "ma_ncc": row.get("MA_NCC"),
                    "tenncc": row.get("TENNCC"),
                    "diachi_ncc": row.get("DIACHI_NCC"),
                    "sdt_ncc": row.get("SDT_NCC"),
                    "stk_ncc": row.get("STK_NCC"),
                })
            return suppliers
        finally:
            cur.close()

    def get_supplier_debts(self) -> list[dict]:
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute("SET NOCOUNT ON; EXEC dbo.usp_LAY_CONG_NO_NHA_CUNG_CAP")
            rows = self._rows_to_dicts(cur)
            debts = []
            for row in rows:
                debts.append({
                    "ma_ncc": row.get("MA_NCC"),
                    "tenncc": row.get("TENNCC"),
                    "tong_no": row.get("TONG_NO"),
                    "da_tra": row.get("DA_TRA"),
                    "cong_no": row.get("CONG_NO"),
                    "trang_thai": row.get("TRANG_THAI"),
                })
            return debts
        finally:
            cur.close()

    def get_unpaid_purchase_invoices(self, ma_ncc: str) -> list[dict]:
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute("SET NOCOUNT ON; EXEC dbo.usp_LAY_HDN_CONG_NO_THEO_NCC ?", [ma_ncc])
            rows = self._rows_to_dicts(cur)
            invoices = []
            for row in rows:
                invoices.append({
                    "mahdn": row.get("MAHDN"),
                    "ma_ncc": row.get("MA_NCC"),
                    "ngaygio_nk": row.get("NGAYGIO_NK"),
                    "tongtien": row.get("TONGTIEN"),
                    "chietkhau": row.get("CHIETKHAU"),
                    "tien_chiet_khau": row.get("TIEN_CHIET_KHAU"),
                    "phai_tra": row.get("PHAI_TRA"),
                    "da_tra": row.get("DA_TRA"),
                    "cong_no": row.get("CONG_NO"),
                    "trang_thai": row.get("TRANG_THAI"),
                })
            return invoices
        finally:
            cur.close()

    def generate_payment_id(self):
        result = self.fetch_procedure("dbo.usp_SINH_MA_THANHTOAN")
        if result and len(result) > 0:
            return result[0].get("MATT")
        return None

    def pay_supplier_debt(self, matt: str, mahdn: str, sotientra: float):
        self.execute_procedure("dbo.usp_THANH_TOAN_HDN", [matt, mahdn, sotientra])

    def get_current_database(self) -> str | None:
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute("SELECT DB_NAME() AS CurrentDatabase")
            row = cur.fetchone()
            return row[0] if row else None
        finally:
            cur.close()

    def get_suppliers(self) -> list[dict]:
        return self.get_all_suppliers()

    def get_debts(self) -> list[dict]:
        return self.get_supplier_debts()

    def add_supplier(self, mancc: str, tenncc: str, sdt_ncc: str | None, diachi_ncc: str | None, stk_ncc: str | None):
        print("EXEC dbo.usp_THEM_NHACUNGCAP ?, ?, ?, ?, ?")
        print(mancc, tenncc, sdt_ncc, diachi_ncc, stk_ncc)
        try:
            self.execute_procedure("usp_THEM_NHACUNGCAP", [mancc, tenncc, sdt_ncc, diachi_ncc, stk_ncc])
        except pyodbc.Error as e:
            print("ADD SUPPLIER SQL ERROR:", e)
            raise

    def update_supplier(self, mancc: str, tenncc: str, dienthoai: str, diachi: str):
        self.execute_procedure("usp_CAPNHAT_NHACUNGCAP", [mancc, tenncc, dienthoai, diachi])

    def get_next_supplier_id(self):
        """Lấy mã nhà cung cấp tiếp theo từ usp_SINH_MA_NHACUNGCAP"""
        try:
            result = self.fetch_procedure("usp_SINH_MA_NHACUNGCAP")
            if result and len(result) > 0:
                return result[0].get("MA_NCC")
        except Exception as e:
            print(f"[SupplierRepo] get_next_supplier_id error: {e}")
        return None
