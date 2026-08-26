# file: repositories/stock_repository.py
from .base_repository import BaseRepository


class StockRepository(BaseRepository):

    def get_stock_items(self) -> list[dict]:
        return self.fetch_view("V_SANPHAM_TONKHO")

    def get_low_stock(self) -> list[dict]:
        return self.fetch_view("V_SANPHAM_SAP_HET")

    def get_old_stock(self) -> list[dict]:
        return self.fetch_view("V_HANG_TON_LAU")
