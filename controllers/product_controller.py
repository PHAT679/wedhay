# file: controllers/product_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.product_service import ProductService
from .decorators import login_required, role_required

products = Blueprint("products", __name__)


@products.route("/products")
@login_required
@role_required("admin", "kho")
def index():
    keyword = request.args.get("q", "").strip()
    status = request.args.get("status", "all").strip()

    result = ProductService().get_products_page_data(keyword=keyword, status=status)
    products = result.get("data", {}).get("products", [])

    print("PRODUCT SEARCH KEYWORD:", keyword)
    print("PRODUCT SEARCH STATUS:", status)
    print("PRODUCT COUNT:", len(products))
    print("FIRST PRODUCT:", products[0] if products else "NO PRODUCT")

    next_maspct = ProductService().get_next_product_detail_id()

    return render_template(
        "products.html", 
        products=products,
        keyword=keyword,
        selected_status=status,
        product_count=len(products),
        next_maspct=next_maspct
    )


@products.route("/products/create", methods=["POST"])
@login_required
@role_required("admin", "kho")
def create():
    print("===== CREATE PRODUCT DEBUG =====")
    print("===== CREATE PRODUCT DEBUG =====")
    print("MASPCT:", request.form.get("MASPCT"))
    print("TENSP:", request.form.get("TENSP"))
    print("TEN_MAU:", request.form.get("TEN_MAU"))
    print("TEN_SIZE:", request.form.get("TEN_SIZE"))
    print("TENLOAISP:", request.form.get("TENLOAISP"))
    print("DONGIA_BAN:", request.form.get("DONGIA_BAN"))
    print("DONGIA_NHAP:", request.form.get("DONGIA_NHAP"))

    result = ProductService().create_product(request.form)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("products.index"))


@products.route("/products/create-detail", methods=["POST"])
@login_required
@role_required("admin", "kho")
def create_detail():
    result = ProductService().create_detail(
        request.form.get("maspct", ""),
        request.form.get("masp", ""),
        request.form.get("mamau", ""),
        request.form.get("masize", ""),
    )
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("products.index"))


@products.route("/products/create-price", methods=["POST"])
@login_required
@role_required("admin", "kho")
def create_price():
    result = ProductService().create_price(
        request.form.get("maspct", ""),
        request.form.get("giaban", 0),
        request.form.get("gianhap", 0),
        request.form.get("ngay_ap_dung", None),
    )
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("products.index"))
