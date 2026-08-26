# file: controllers/supplier_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from services.supplier_service import SupplierService
from .decorators import login_required, role_required

suppliers = Blueprint("suppliers", __name__)


@suppliers.route("/suppliers")
@login_required
@role_required("admin", "kho")
def index():
    service = SupplierService()
    suppliers_list = []
    supplier_debts = []
    next_supplier_id = None
    current_db = None
    try:
        suppliers_list = service.get_all_suppliers()
        supplier_debts = service.get_supplier_debts()
        next_supplier_id = service.repo.get_next_supplier_id()
        current_db = service.get_current_database()
    except Exception as e:
        flash(f"Không thể tải dữ liệu nhà cung cấp từ SQL Server: {e}", "danger")

    print("===== SUPPLIERS PAGE DEBUG =====")
    print("CURRENT DB:", current_db)
    print("SUPPLIER COUNT:", len(suppliers_list))
    print("FIRST SUPPLIER:", suppliers_list[0] if suppliers_list else "NO SUPPLIER")
    print("===== SUPPLIER DEBT DEBUG =====")
    print("SUPPLIER DEBT COUNT:", len(supplier_debts))
    print("FIRST DEBT:", supplier_debts[0] if supplier_debts else "NO DEBT")
    print("NEXT SUPPLIER ID:", next_supplier_id)

    return render_template(
        "suppliers.html",
        suppliers=suppliers_list,
        supplier_debts=supplier_debts,
        supplier_count=len(suppliers_list),
        supplier_debt_count=len(supplier_debts),
        next_supplier_id=next_supplier_id,
    )


@suppliers.route("/suppliers/<ma_ncc>/unpaid-invoices")
@login_required
@role_required("admin", "kho")
def unpaid_invoices(ma_ncc):
    try:
        invoices = SupplierService().get_unpaid_purchase_invoices(ma_ncc)
        print("===== UNPAID INVOICES DEBUG =====")
        print("MA_NCC:", ma_ncc)
        print("COUNT:", len(invoices))
        print("FIRST INVOICE:", invoices[0] if invoices else "NO INVOICE")
        return jsonify({"success": True, "data": invoices})
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "data": []}), 400


@suppliers.route("/suppliers/pay-debt", methods=["POST"])
@login_required
@role_required("admin", "kho")
def pay_debt():
    mahdn = (request.form.get("MAHDN") or "").strip()
    sotientra = request.form.get("SOTIENTRA")
    print("===== PAY SUPPLIER DEBT DEBUG =====")
    print("MAHDN:", mahdn)
    print("SOTIENTRA:", sotientra)

    result = SupplierService().pay_supplier_debt(mahdn, sotientra)
    if result.get("success"):
        flash("Thanh toán công nợ thành công.", "success")
    else:
        flash(result.get("message", "Thanh toán công nợ thất bại."), "danger")
    return redirect(url_for("suppliers.index"))


@suppliers.route("/suppliers/add", methods=["POST"])
@login_required
@role_required("admin", "kho")
def add_supplier():
    ma_ncc = (request.form.get("mancc") or request.form.get("MA_NCC") or "").strip()
    tenncc = (request.form.get("tenncc") or request.form.get("TENNCC") or "").strip()
    sdt_ncc = (request.form.get("sdt_ncc") or request.form.get("dienthoai") or request.form.get("SDT_NCC") or request.form.get("sdt") or "").strip()
    diachi_ncc = (request.form.get("diachi_ncc") or request.form.get("diachi") or request.form.get("DIACHI_NCC") or request.form.get("DIACHI") or "").strip()
    stk_ncc = (request.form.get("stk_ncc") or request.form.get("STK_NCC") or "").strip()

    print("===== ADD SUPPLIER FORM DEBUG =====")
    print("FORM DATA:", dict(request.form))
    print("MA_NCC:", ma_ncc)
    print("TENNCC:", tenncc)
    print("SDT_NCC:", sdt_ncc)
    print("DIACHI_NCC:", diachi_ncc)
    print("STK_NCC:", stk_ncc)

    data = {
        "mancc": ma_ncc,
        "tenncc": tenncc,
        "sdt_ncc": sdt_ncc,
        "diachi_ncc": diachi_ncc,
        "stk_ncc": stk_ncc,
    }

    result = SupplierService().add_supplier(data)

    if result.get("success"):
        flash(result.get("message", "Thêm nhà cung cấp thành công."), "success")
    else:
        flash(result.get("message", "Thêm nhà cung cấp thất bại."), "danger")

    return redirect(url_for("suppliers.index"))


@suppliers.route("/suppliers/update", methods=["POST"])
@login_required
@role_required("admin", "kho")
def update():
    result = SupplierService().update_supplier(
        request.form.get("mancc", ""),
        request.form.get("tenncc", ""),
        request.form.get("dienthoai", ""),
        request.form.get("diachi", ""),
    )
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("suppliers.index"))
