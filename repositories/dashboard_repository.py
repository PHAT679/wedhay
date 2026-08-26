# file: repositories/dashboard_repository.py
from .base_repository import BaseRepository


class DashboardRepository(BaseRepository):

    def get_revenue_by_month(self) -> list[dict]:
        return self.fetch_view("V_DOANH_THU_THEO_THANG")

    def get_top_products(self) -> list[dict]:
        try:
            return self.fetch_procedure("usp_TOP_SANPHAM")
        except Exception:
            return []

    def get_stock_items(self) -> list[dict]:
        return self.fetch_view("V_SANPHAM_TONKHO")

    def get_low_stock(self) -> list[dict]:
        return self.fetch_view("V_SANPHAM_SAP_HET")

    def get_old_stock(self) -> list[dict]:
        return self.fetch_view("V_HANG_TON_LAU")
