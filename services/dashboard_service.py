# file: services/dashboard_service.py
from repositories.dashboard_repository import DashboardRepository
from datetime import datetime
from .base_service import BaseService


class DashboardService(BaseService):
    def __init__(self):
        self.repo = DashboardRepository()

    def get_dashboard_data(self) -> dict:
        raw_revenue_by_month = self.repo.get_revenue_by_month()
        raw_top_products     = self.repo.get_top_products()
        raw_stock_items      = self.repo.get_stock_items()
        raw_low_stock_items  = self.repo.get_low_stock()
        raw_old_stock_items  = self.repo.get_old_stock()

        revenue_by_month = []
        for row in raw_revenue_by_month:
            revenue_by_month.append({
                "THANG": self.pick(row, ["THANG", "THANG_NAM", "NAM_THANG"], "N/A"),
                "NAM": self.pick(row, ["NAM"], ""),
                "DOANHTHU": self.pick(row, ["DOANH_THU", "DOANHTHU", "TONG_DOANH_THU"], 0)
            })

        top_products = []
        for row in raw_top_products:
            top_products.append({
                "MASPCT": self.pick(row, ["MASP", "MA_SP", "MASPCT"], ""),
                "TENSANPHAM": self.pick(row, ["TENSP", "TENSANPHAM", "TEN_SANPHAM"], "N/A"),
                "SOLUONG_BAN": self.pick(row, ["TONG_BAN", "SOLUONG_BAN", "DA_BAN"], 0)
            })
            
        stock_items = []
        for row in raw_stock_items:
            stock_items.append({
                "MASPCT": self.pick(row, ["MASPCT", "MA_SPCT"], ""),
                "TENSANPHAM": self.pick(row, ["TENSP", "TENSANPHAM", "TEN_SANPHAM"], "N/A"),
                "TONKHO": self.pick(row, ["SL_TONKHO", "SOLUONG", "TONKHO"], 0)
            })

        low_stock_items = []
        for row in raw_low_stock_items:
            low_stock_items.append({
                "MASPCT": self.pick(row, ["MASPCT", "MA_SPCT"], ""),
                "TENSANPHAM": self.pick(row, ["TENSP", "TENSANPHAM", "TEN_SANPHAM"], "N/A"),
                "MAU": self.pick(row, ["TEN_MAU", "MAU", "TENMAU"], ""),
                "SIZE": self.pick(row, ["TEN_SIZE", "SIZE", "COKISIZE", "TENSIZE"], ""),
                "TONKHO": self.pick(row, ["SL_TONKHO", "SOLUONG", "TONKHO"], 0)
            })

        old_stock_items = []
        for row in raw_old_stock_items:
            old_stock_items.append({
                "MASPCT": self.pick(row, ["MASPCT", "MA_SPCT"], ""),
                "TENSANPHAM": self.pick(row, ["TENSP", "TENSANPHAM", "TEN_SANPHAM"], "N/A"),
                "TONKHO": self.pick(row, ["SL_TONKHO", "SOLUONG", "TONKHO"], 0),
                "NGAY_NHAP": self.pick(row, ["LAN_BAN_CUOI", "NGAY_BAN_CUOI", "NGAYNHAP", "NGAY_NHAP"], None)
            })

        # Doanh thu tháng hiện tại
        now = datetime.now()
        doanh_thu_thang = 0
        for row in revenue_by_month:
            thang = row.get("THANG")
            nam   = row.get("NAM")
            if str(thang) == str(now.month) and str(nam) == str(now.year):
                doanh_thu_thang = row.get("DOANHTHU", 0)
                break

        kpis = {
            "doanh_thu_thang": doanh_thu_thang,
            "tong_sp":         len(stock_items),
            "so_sap_het":      len(low_stock_items),
            "so_ton_lau":      len(old_stock_items),
        }

        return {
            "success": True,
            "data": {
                "revenue_by_month": revenue_by_month,
                "top_products":     top_products,
                "stock_items":      stock_items,
                "low_stock_items":  low_stock_items[:8],
                "old_stock_items":  old_stock_items[:8],
                "kpis":             kpis,
            }
        }
