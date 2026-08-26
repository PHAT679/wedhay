# file: app.py
"""
Seller Management System — POS cho cửa hàng thời trang trẻ em
Chạy: python app.py  →  http://127.0.0.1:5000
"""

from flask import Flask, redirect, url_for, render_template, session
from config import Config
import database

# ── Blueprints ────────────────────────────────────────────────────────
from controllers.auth_controller     import auth
from controllers.dashboard_controller import dashboard
from controllers.sales_controller    import sales
from controllers.product_controller  import products
from controllers.stock_controller    import stock
from controllers.purchase_controller import purchase
from controllers.customer_controller import customers
from controllers.supplier_controller import suppliers
from controllers.report_controller   import reports


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY

    # Đăng ký database teardown
    database.init_app(app)

    # Đăng ký blueprints
    for bp in [auth, dashboard, sales, products, stock, purchase, customers, suppliers, reports]:
        app.register_blueprint(bp)

    # ── Context processor: inject session user vào mọi template ────────
    @app.context_processor
    def inject_user():
        return {"current_user": session.get("user", {})}

    # ── Error handlers ─────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return render_template(
            "error.html",
            error_code=404,
            error_title="Không tìm thấy trang",
            error_message="Trang bạn tìm không tồn tại.",
        ), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template(
            "error.html",
            error_code=500,
            error_title="Lỗi máy chủ",
            error_message="Hệ thống gặp sự cố. Vui lòng thử lại.",
        ), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000, host="0.0.0.0")
