# file: services/report_service.py
from repositories.report_repository import ReportRepository
from .base_service import BaseService

class ReportService(BaseService):
    def __init__(self):
        self.repo = ReportRepository()

    def get_report_dashboard(self) -> dict:
        monthly_revenue = []
        for row in self.repo.get_monthly_revenue():
            monthly_revenue.append({
                "THANG": self.pick(row, ["THANG", "THANG_NAM", "NAM_THANG"], ""),
                "NAM": self.pick(row, ["NAM"], ""),
                "DOANH_THU": self.pick(row, ["DOANH_THU", "DOANHTHU", "TONG_DOANH_THU"], 0),
                "LOI_NHUAN": self.pick(row, ["LOI_NHUAN", "LOINHUAN"], 0),
            })

        top_products = []
        for row in self.repo.get_top_products():
            top_products.append({
                "MASP": self.pick(row, ["MASP", "MA_SP"], ""),
                "MASPCT": self.pick(row, ["MASPCT", "MA_SPCT"], ""),
                "TENSP": self.pick(row, ["TENSP", "TENSANPHAM", "TEN_SANPHAM"], "N/A"),
                "TONG_BAN": self.pick(row, ["TONG_BAN", "SOLUONG_BAN", "DA_BAN"], 0),
                "DOANH_THU": self.pick(row, ["DOANH_THU", "DOANHTHU", "TONG_DOANH_THU"], 0),
            })

        employee_sales = []
        for row in self.repo.get_employee_sales():
            employee_sales.append({
                "MANV": self.pick(row, ["MANV", "MA_NV"], ""),
                "TEN_NV": self.pick(row, ["TEN_NV", "TENNV"], "N/A"),
                "SO_HOA_DON": self.pick(row, ["SO_HOA_DON", "SOHOADON"], 0),
                "DOANH_SO": self.pick(row, ["DOANH_SO", "DOANHSO"], 0),
            })

        supplier_debts = []
        for row in self.repo.get_supplier_debts():
            supplier_debts.append({
                "MA_NCC": self.pick(row, ["MA_NCC", "MANCC"], ""),
                "TENNCC": self.pick(row, ["TENNCC", "TEN_NCC"], "N/A"),
                "TONG_NO": self.pick(row, ["TONG_NO", "TONGNO"], 0),
                "DA_TRA": self.pick(row, ["DA_TRA", "DATRA"], 0),
                "CONG_NO": self.pick(row, ["CONG_NO", "CONGNO"], 0),
                "TRANG_THAI": self.pick(row, ["TRANG_THAI"], ""),
            })

        old_inventory = []
        for row in self.repo.get_old_inventory():
            old_inventory.append({
                "MASP": self.pick(row, ["MASP"], ""),
                "MASPCT": self.pick(row, ["MASPCT", "MA_SPCT"], ""),
                "TENSP": self.pick(row, ["TENSP", "TENSANPHAM"], "N/A"),
                "SL_TONKHO": self.pick(row, ["SL_TONKHO", "TONKHO", "SOLUONG"], 0),
                "SO_NGAY_TON": self.pick(row, ["SO_NGAY_TON", "SONGAYTON"], None),
            })

        low_stock_products = []
        for row in self.repo.get_low_stock_products():
            low_stock_products.append({
                "MASPCT": self.pick(row, ["MASPCT", "MA_SPCT"], ""),
                "TENSP": self.pick(row, ["TENSP", "TENSANPHAM"], "N/A"),
                "TEN_MAU": self.pick(row, ["TEN_MAU", "MAU"], "—"),
                "TEN_SIZE": self.pick(row, ["TEN_SIZE", "SIZE"], "—"),
                "SL_TONKHO": self.pick(row, ["SL_TONKHO", "TONKHO", "SOLUONG"], 0),
            })

        top_customers = []
        for row in self.repo.get_top_customers():
            top_customers.append({
                "MAKH": self.pick(row, ["MAKH", "MA_KH"], ""),
                "TENKH": self.pick(row, ["TENKH", "TEN_KH"], "N/A"),
                "SO_HOA_DON": self.pick(row, ["SO_HOA_DON", "SOHOADON"], 0),
                "TONG_CHI_TIEU": self.pick(row, ["TONG_CHI_TIEU", "TONGCHITIEU", "DOANH_THU"], 0),
            })

        current_db = self.repo.get_current_database()

        return {
            "monthly_revenue": monthly_revenue,
            "top_products": top_products,
            "employee_sales": employee_sales,
            "supplier_debts": supplier_debts,
            "old_inventory": old_inventory,
            "low_stock_products": low_stock_products,
            "top_customers": top_customers,
            "current_db": current_db,
        }

    # Backward-compatible wrapper for existing controller calls
    def get_report_data(self) -> dict:
        dashboard = self.get_report_dashboard()
        return {"success": True, "data": dashboard}
