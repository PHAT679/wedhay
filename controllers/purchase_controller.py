# file: controllers/purchase_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from services.purchase_service import PurchaseService
from .decorators import login_required, role_required

purchase = Blueprint("purchase", __name__)


@purchase.route("/purchase")
@login_required
@role_required("admin", "kho")
def index():
    current_purchase_invoice_id = session.get("current_purchase_invoice_id")
    
    d = PurchaseService().get_purchase_page_data(current_purchase_invoice_id)
    
    next_purchase_invoice_id = d.get("next_purchase_invoice_id")
    purchase_items = d.get("purchase_items", [])
    purchase_summary = d.get("purchase_summary", {})
    products = d.get("products", [])
    suppliers = d.get("suppliers", [])

    print("===== PURCHASE SUMMARY DEBUG =====")
    print("CURRENT PURCHASE ID:", current_purchase_invoice_id)
    print("PURCHASE SUMMARY:", purchase_summary)
    print("TONG_TIEN_HANG:", purchase_summary.get("tong_tien_hang"))
    print("CHIET_KHAU:", purchase_summary.get("chietkhau_percent"))
    print("TIEN_CHIET_KHAU:", purchase_summary.get("tien_chiet_khau"))
    print("CAN_THANH_TOAN:", purchase_summary.get("can_thanh_toan"))
    print("===== PURCHASE PRODUCTS DEBUG =====")
    print("USING VIEW: dbo.V_SANPHAM_NHAP")
    print("PRODUCT COUNT:", len(products))
    print("FIRST PRODUCT:", products[0] if products else "NO PRODUCT")
    for product in products:
        print("MASPCT:", product.get("MASPCT") or product.get("maspct"))
        print("SL_TONKHO:", product.get("TONKHO") if "TONKHO" in product else product.get("sl_tonkho"))
        print("PURCHASE ALLOW SELECT:", True)

    return render_template(
        "purchase.html",
        current_purchase_invoice_id=current_purchase_invoice_id,
        current_purchase=d.get("current_purchase", {}),
        next_purchase_invoice_id=next_purchase_invoice_id,
        purchase_items=purchase_items,
        purchase_summary=purchase_summary,
        products=products,
        suppliers=suppliers,
    )


@purchase.route("/purchase/create", methods=["POST"])
@login_required
@role_required("admin", "kho")
def create_purchase():
    print("===== CREATE PURCHASE DEBUG =====")
    print("FORM DATA:", request.form)
    print("MAHDN FROM FORM:", request.form.get("MAHDN") or request.form.get("mahdn"))
    print("MA_NCC FROM FORM:", request.form.get("MA_NCC") or request.form.get("mancc"))
    print("SESSION USER:", session.get("user"))
    print("MANV FROM SESSION:", session.get("user", {}).get("manv") or session.get("user", {}).get("ma_nv"))

    mahdn = request.form.get("MAHDN") or request.form.get("mahdn")
    ma_ncc = request.form.get("MA_NCC") or request.form.get("mancc")
    user = session.get("user", {})
    manv = user.get("manv") or user.get("ma_nv")

    if not mahdn:
        flash("Không xác định được mã phiếu nhập.", "danger")
        return redirect(url_for("purchase.index"))
    if not ma_ncc:
        flash("Vui lòng chọn nhà cung cấp.", "danger")
        return redirect(url_for("purchase.index"))
    if not manv:
        flash("Không xác định được nhân viên đang đăng nhập. Vui lòng đăng nhập lại.", "danger")
        return redirect(url_for("purchase.index"))

    form_data = request.form.to_dict()
    form_data["MAHDN"] = mahdn
    form_data["MA_NCC"] = ma_ncc
    result = PurchaseService().create_purchase_invoice(form_data, user)
    if result["success"]:
        session["current_purchase_invoice_id"] = result.get("mahdn") or mahdn
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("purchase.index"))


@purchase.route("/purchase/add-item", methods=["POST"])
@login_required
@role_required("admin", "kho")
def add_item():
    current_purchase_invoice_id = session.get("current_purchase_invoice_id")
    
    print("===== ADD PURCHASE ITEM DEBUG =====")
    print("FORM DATA:", request.form)
    print("MAHDN FROM FORM:", request.form.get("MAHDN") or current_purchase_invoice_id)
    print("MASPCT FROM FORM:", request.form.get("MASPCT"))
    print("SOLUONG FROM FORM:", request.form.get("SOLUONG"))
    print("SOLUONG_NHAP FROM FORM:", request.form.get("SOLUONG_NHAP"))

    mahdn = request.form.get("MAHDN") or current_purchase_invoice_id
    maspct = request.form.get("MASPCT")
    soluong_raw = request.form.get("SOLUONG") or request.form.get("SOLUONG_NHAP") or "1"

    if not mahdn:
        flash("Vui lòng tạo phiếu nhập trước.", "danger")
        return redirect(url_for("purchase.index"))

    if not maspct:
        flash("Vui lòng chọn sản phẩm.", "danger")
        return redirect(url_for("purchase.index"))

    try:
        soluong = int(soluong_raw)
    except ValueError:
        flash("Số lượng nhập không hợp lệ.", "danger")
        return redirect(url_for("purchase.index"))

    if soluong <= 0:
        flash("Số lượng nhập phải lớn hơn 0.", "danger")
        return redirect(url_for("purchase.index"))

    result = PurchaseService().add_purchase_item(mahdn, maspct, soluong)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("purchase.index"))


@purchase.route("/purchase/complete", methods=["POST"])
@login_required
@role_required("admin", "kho")
def complete_purchase():
    print("===== COMPLETE PURCHASE DEBUG =====")
    print("MAHDN FROM FORM:", request.form.get("MAHDN"))
    print("CURRENT PURCHASE ID:", session.get("current_purchase_invoice_id"))

    mahdn = request.form.get("MAHDN") or session.get("current_purchase_invoice_id")

    if not mahdn:
        flash("Chưa có phiếu nhập để hoàn thành.", "danger")
        return redirect(url_for("purchase.index"))

    result = PurchaseService().complete_purchase(mahdn)

    if result["success"]:
        session.pop("current_purchase_invoice_id", None)
        flash("Hoàn thành phiếu nhập thành công.", "success")
    else:
        flash(result["message"], "danger")

    return redirect(url_for("purchase.index"))


@purchase.route("/purchase/update-discount", methods=["POST"])
@login_required
@role_required("admin", "kho")
def update_discount():
    data = request.get_json(silent=True) or {}
    mahdn = data.get("mahdn") or session.get("current_purchase_invoice_id")
    chietkhau = data.get("chietkhau", 0)

    print("===== UPDATE DISCOUNT DEBUG =====")
    print("MAHDN:", mahdn)
    print("CHIETKHAU:", chietkhau)

    result = PurchaseService().update_purchase_discount(mahdn, chietkhau)
    if not result.get("success"):
        return jsonify(result), 400

    purchase_summary = result.get("purchase_summary", {})
    print("PURCHASE SUMMARY:", purchase_summary)
    return jsonify(result), 200
