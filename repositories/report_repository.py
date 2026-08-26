# file: repositories/report_repository.py
from .base_repository import BaseRepository


class ReportRepository(BaseRepository):

    def get_monthly_revenue(self) -> list[dict]:
        try:
            return self.fetch_view("V_DOANH_THU_THEO_THANG")
        except Exception as e:
            print(f"[ReportRepo] get_monthly_revenue error: {e}")
            return []

    def get_top_products(self) -> list[dict]:
        try:
            return self.fetch_view("V_TOP_SANPHAM_BAN_CHAY")
        except Exception as e:
            print(f"[ReportRepo] get_top_products error: {e}")
            return []

    def get_employee_sales(self) -> list[dict]:
        try:
            return self.fetch_view("V_NHANVIEN_DOANH_SO")
        except Exception as e:
            print(f"[ReportRepo] get_employee_sales error: {e}")
            return []

    def get_supplier_debts(self) -> list[dict]:
        try:
            return self.fetch_view("V_CONG_NO_NHA_CUNG_CAP")
        except Exception as e:
            print(f"[ReportRepo] get_supplier_debts error: {e}")
            return []

    def get_old_inventory(self) -> list[dict]:
        try:
            return self.fetch_view("V_HANG_TON_LAU")
        except Exception as e:
            print(f"[ReportRepo] get_old_inventory error: {e}")
            return []

    def get_low_stock_products(self) -> list[dict]:
        try:
            return self.fetch_view("V_SANPHAM_SAP_HET")
        except Exception as e:
            print(f"[ReportRepo] get_low_stock_products error: {e}")
            return []

    def get_top_customers(self) -> list[dict]:
        try:
            return self.fetch_view("V_KHACHHANG_MUANHIEUNHAT")
        except Exception as e:
            print(f"[ReportRepo] get_top_customers error: {e}")
            return []

    def get_current_database(self) -> str | None:
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute("SELECT DB_NAME() AS CurrentDatabase")
            row = cur.fetchone()
            return row[0] if row else None
        except Exception as e:
            print(f"[ReportRepo] get_current_database error: {e}")
            return None
        finally:
            cur.close()

    # Backward-compatible aliases
    def get_revenue_by_month(self) -> list[dict]:
        return self.get_monthly_revenue()

    def get_old_stock(self) -> list[dict]:
        return self.get_old_inventory()

    def get_best_customers(self) -> list[dict]:
        return self.get_top_customers()

    def get_low_stock(self) -> list[dict]:
        return self.get_low_stock_products()
