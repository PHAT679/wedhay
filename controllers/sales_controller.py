# file: controllers/sales_controller.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from services.sales_service import SalesService
from .decorators import login_required, role_required

sales = Blueprint("sales", __name__)
_svc = SalesService

@sales.route("/sales", methods=["GET"])
@login_required
@role_required("admin", "banhang")
def index():
    try:
        user = session.get("user", {}) or {}
        current_employee_id = (user.get("manv") or "").strip()
        current_employee_name = (user.get("full_name") or "").strip()
        if not current_employee_id:
            session.clear()
            flash("Phiên đăng nhập không hợp lệ hoặc thiếu mã nhân viên. Vui lòng đăng nhập lại.", "warning")
            return redirect(url_for("auth.login"))
        customer_keyword = (request.args.get("customer_keyword") or "").strip()
        result = _svc().get_sales_page_data(customer_keyword=customer_keyword)
        data = result.get("data", {}) if result else {}
        next_invoice_id = data.get("next_invoice_id")
        selected_customer = data.get("selected_customer")
        use_points_checked = bool(session.get("checkout_use_points"))
        if selected_customer and int(selected_customer.get("DIEM_SUDUNG") or 0) >= 5:
            use_points_checked = True
        print("NEXT SALES INVOICE ID:", next_invoice_id)

        return render_template(
            "sales.html",
            products=data.get("products", []),
            current_invoice_id=data.get("current_invoice_id"),
            next_invoice_id=next_invoice_id,
            cart_items=data.get("cart_items", []),
            current_employee_id=current_employee_id,
            current_employee_name=current_employee_name,
            selected_customer=selected_customer,
            customer_search_results=data.get("customer_search_results", []),
            customer_keyword=customer_keyword,
            use_points_checked=use_points_checked,
            invoice_summary=data.get("invoice_summary", {
                "tam_tinh": 0,
                "chiet_khau_percent": 0,
                "tien_chiet_khau": 0,
                "giam_bang_diem": 0,
                "tong_can_thanh_toan": 0
            })
        )
    except Exception as e:
        print("SALES PAGE ERROR:", e)
        flash("Không thể tải trang bán hàng. Vui lòng kiểm tra service/database.", "danger")

        return render_template(
            "sales.html",
            products=[],
            current_invoice_id=None,
            next_invoice_id=None,
            cart_items=[],
            current_employee_id="",
            current_employee_name="",
            selected_customer=None,
            customer_search_results=[],
            customer_keyword="",
            use_points_checked=False,
            invoice_summary={
                "tam_tinh": 0,
                "chiet_khau_percent": 0,
                "tien_chiet_khau": 0,
                "giam_bang_diem": 0,
                "tong_can_thanh_toan": 0
            }
        )

@sales.route("/create-invoice", methods=["POST"])
@login_required
@role_required("admin", "banhang")
def create_invoice():
    mahd = (request.form.get("mahd") or "").strip()
    if not mahd:
        flash("Không thể sinh mã hóa đơn tự động. Vui lòng kiểm tra procedure usp_SINH_MA_HOADON_BAN.", "danger")
        return redirect(url_for("sales.index"))

    user = session.get("user", {}) or {}
    manv = (user.get("manv") or "").strip()
    if not manv:
        flash("Không xác định được nhân viên đang đăng nhập. Vui lòng đăng nhập lại.", "danger")
        return redirect(url_for("sales.index"))

    data = {
        "mahd":       mahd,
        "makh":       request.form.get("makh"),
        "manv":       manv,
        "chietkhau":  request.form.get("chietkhau", 0)
    }
    res = _svc().create_invoice(data)
    if res["success"]:
        session["checkout_use_points"] = False
        flash(res["message"], "success")
    else:
        flash(res["message"], "danger")
    return redirect(url_for("sales.index") + "#add-item-section")

@sales.route("/add-item", methods=["POST"])
@login_required
@role_required("admin", "banhang")
def add_item():
    mahd = session.get("current_invoice_id")
    maspct = request.form.get("maspct")
    
    try:
        soluong = int(request.form.get("soluong", 1))
    except ValueError:
        soluong = 0

    res = _svc().add_item_to_invoice(mahd, maspct, soluong)
    if res["success"]:
        flash(res["message"], "success")
    else:
        flash(res["message"], "danger")
    return redirect(url_for("sales.index") + "#cart-section")

@sales.route("/sales/select-customer", methods=["POST"])
@login_required
@role_required("admin", "banhang")
def select_customer():
    mahd = session.get("current_invoice_id")
    makh = request.form.get("selected_makh", "")
    res = _svc().assign_customer_to_current_invoice(mahd, makh)
    flash(res["message"], "success" if res["success"] else "danger")
    return redirect(url_for("sales.index") + "#checkoutForm")

@sales.route("/sales/toggle-use-points", methods=["POST"])
@login_required
@role_required("admin", "banhang")
def toggle_use_points():
    mahd = session.get("current_invoice_id")
    use_points = str(request.form.get("use_points", "")).lower() in {"1", "true", "on", "yes"}
    res = _svc().set_use_points_for_checkout(mahd, use_points)
    flash(res["message"], "success" if res["success"] else "danger")
    return redirect(url_for("sales.index") + "#checkoutForm")


@sales.route("/sales/customer-by-phone", methods=["GET"])
@login_required
@role_required("admin", "banhang")
def customer_by_phone():
    phone = (request.args.get("phone") or "").strip()
    res = _svc().get_customer_by_phone(phone)
    status_code = 200 if res.get("success") else 404
    return jsonify(res), status_code


@sales.route("/sales/set-customer", methods=["POST"])
@login_required
@role_required("admin", "banhang")
def set_customer():
    mahd = session.get("current_invoice_id")
    payload = request.get_json(silent=True) or {}
    makh = (payload.get("makh") or "").strip()
    res = _svc().set_customer_for_current_invoice(mahd, makh)
    status_code = 200 if res.get("success") else 400
    return jsonify(res), status_code

@sales.route("/checkout", methods=["POST"])
@login_required
@role_required("admin", "banhang")
def checkout():
    mahd = session.get("current_invoice_id")
    use_points = str(request.form.get("use_points", "")).lower() in {"1", "true", "on", "yes"}
    session["checkout_use_points"] = use_points
    
    try:
        tien_khach_dua = float(request.form.get("tienKhachDua", 0))
    except ValueError:
        tien_khach_dua = 0.0

    discount_percent = request.form.get("chietkhau") or request.form.get("CHIETKHAU") or session.get("current_invoice_discount", 0)
    try:
        discount_percent = float(discount_percent)
    except (ValueError, TypeError):
        discount_percent = 0.0

    print("===== CHECKOUT DEBUG =====")
    print("FORM DATA:", request.form)

    res = _svc().checkout_invoice(mahd, tien_khach_dua, use_points, discount_percent)
    if res["success"]:
        flash(res["message"], "success")
    else:
        flash(res["message"], "danger")
    return redirect(url_for("sales.index"))
