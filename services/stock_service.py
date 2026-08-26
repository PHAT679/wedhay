# file: services/stock_service.py
from repositories.stock_repository import StockRepository
from .base_service import BaseService

class StockService(BaseService):
    def __init__(self):
        self.repo = StockRepository()

    def _normalize_stock(self, raw_list) -> list[dict]:
        normalized = []
        for row in raw_list:
            normalized.append({
                "ma_spct": self.pick(row, ["MASPCT", "MA_SPCT"], "N/A"),
                "ten_san_pham": self.pick(row, ["TENSP", "TENSANPHAM", "TEN_SANPHAM"], "N/A"),
                "mau": self.pick(row, ["TEN_MAU", "MAU", "TENMAU"], ""),
                "size": self.pick(row, ["TEN_SIZE", "SIZE", "COKISIZE", "TENSIZE"], ""),
                "ton_kho": self.pick(row, ["SL_TONKHO", "SOLUONG", "TONKHO", "TON_KHO"], 0),
                "ngay_nhap": self.pick(row, ["NGAYNHAP", "NGAY_NHAP", "LAN_BAN_CUOI"], None),
                "da_ban": self.pick(row, ["DA_BAN"], 0)
            })
        return normalized

    def get_stock_page_data(self) -> dict:
        raw_stock = self.repo.get_stock_items()
        raw_low = self.repo.get_low_stock()
        raw_old = self.repo.get_old_stock()
        
        stock_items = self._normalize_stock(raw_stock)
        low_stock_items = self._normalize_stock(raw_low)
        old_stock_items = self._normalize_stock(raw_old)

        print("RAW STOCK COUNT:", len(raw_stock))
        print("RAW FIRST STOCK:", raw_stock[0] if raw_stock else "NO DATA")
        print("MAPPED STOCK COUNT:", len(stock_items))
        print("MAPPED FIRST STOCK:", stock_items[0] if stock_items else "NO DATA")

        return {
            "success": True,
            "data": {
                "stock_items":     stock_items,
                "low_stock_items": low_stock_items,
                "old_stock_items": old_stock_items,
                "stock_count":     len(stock_items),
                "low_stock_count": len(low_stock_items),
                "old_stock_count": len(old_stock_items),
            }
        }
