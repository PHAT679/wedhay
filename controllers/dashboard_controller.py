# file: controllers/dashboard_controller.py
from flask import Blueprint, render_template
from services.dashboard_service import DashboardService
from .decorators import login_required, role_required

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/")
@dashboard.route("/dashboard")
@login_required
@role_required("admin", "banhang", "kho")
def index():
    svc    = DashboardService()
    result = svc.get_dashboard_data()
    d      = result.get("data", {})
    kpis   = d.get("kpis", {})

    # Lấy revenue list, nếu None thì mặc định []
    revenue_list = d.get("revenue_by_month") or []
    revenue_labels = []
    revenue_data = []

    for row in revenue_list:
        if not isinstance(row, dict):
            continue
        
        # Xử lý linh hoạt cột THANG
        thang = (
            row.get("THANG") or row.get("Thang") or row.get("thang") or
            row.get("THANGNAM") or row.get("ThangNam") or row.get("NAM_THANG") or "Không rõ"
        )
        revenue_labels.append(str(thang))

        # Xử lý linh hoạt cột DOANHTHU
        doanh_thu_val = (
            row.get("DOANHTHU") or row.get("DOANH_THU") or row.get("DoanhThu") or
            row.get("doanh_thu") or row.get("TONG_DOANH_THU") or row.get("TongDoanhThu") or 0
        )
        try:
            revenue_data.append(float(doanh_thu_val))
        except (ValueError, TypeError):
            revenue_data.append(0.0)

    return render_template(
        "dashboard.html",
        doanh_thu_thang = kpis.get("doanh_thu_thang", 0),
        tong_sp         = kpis.get("tong_sp", 0),
        so_sap_het      = kpis.get("so_sap_het", 0),
        so_ton_lau      = kpis.get("so_ton_lau", 0),
        revenue_labels  = revenue_labels,
        revenue_data    = revenue_data,
        top_sp          = d.get("top_products") or [],
        sap_het         = d.get("low_stock_items") or [],
        ton_lau         = d.get("old_stock_items") or []
    )
