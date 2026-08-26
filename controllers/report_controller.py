# file: controllers/report_controller.py
from flask import Blueprint, render_template
from services.report_service import ReportService
from .decorators import login_required, role_required

reports = Blueprint("reports", __name__)


@reports.route("/reports")
@login_required
@role_required("admin")
def index():
    data = ReportService().get_report_dashboard()
    monthly_revenue = data.get("monthly_revenue", [])
    top_products = data.get("top_products", [])
    employee_sales = data.get("employee_sales", [])
    supplier_debts = data.get("supplier_debts", [])
    old_inventory = data.get("old_inventory", [])
    low_stock_products = data.get("low_stock_products", [])
    top_customers = data.get("top_customers", [])
    current_db = data.get("current_db")

    print("===== REPORT DEBUG =====")
    print("CURRENT DB:", current_db)
    print("MONTHLY REVENUE:", len(monthly_revenue))
    print("TOP PRODUCTS:", len(top_products))
    print("EMPLOYEE SALES:", len(employee_sales))
    print("SUPPLIER DEBTS:", len(supplier_debts))
    print("OLD INVENTORY:", len(old_inventory))
    print("LOW STOCK:", len(low_stock_products))
    print("TOP CUSTOMERS:", len(top_customers))

    return render_template(
        "reports.html",
        monthly_revenue=monthly_revenue,
        top_products=top_products,
        employee_sales=employee_sales,
        supplier_debts=supplier_debts,
        old_inventory=old_inventory,
        low_stock_products=low_stock_products,
        top_customers=top_customers,
    )
