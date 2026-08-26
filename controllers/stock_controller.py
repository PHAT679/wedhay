# file: controllers/stock_controller.py
from flask import Blueprint, render_template
from services.stock_service import StockService
from .decorators import login_required, role_required

stock = Blueprint("stock", __name__)

@stock.route("/stock")
@login_required
@role_required("admin", "kho")
def index():
    d = StockService().get_stock_page_data().get("data", {})
    return render_template(
        "stock.html",
        stock_items     = d.get("stock_items", []),
        low_stock_items = d.get("low_stock_items", []),
        old_stock_items = d.get("old_stock_items", []),
        stock_count     = d.get("stock_count", 0),
        low_stock_count = d.get("low_stock_count", 0),
        old_stock_count = d.get("old_stock_count", 0)
    )
