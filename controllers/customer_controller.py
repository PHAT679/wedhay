# file: controllers/customer_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from services.customer_service import CustomerService
from .decorators import login_required, role_required

customers = Blueprint("customers", __name__)


@customers.route("/customers")
@login_required
@role_required("admin", "banhang")
def index():
    d = CustomerService().get_customers().get("data", {})
    next_customer_id = d.get("next_customer_id")
    print("NEXT CUSTOMER ID:", next_customer_id)
    return render_template(
        "customers.html",
        customers        = d.get("customers", []),
        customer_points  = d.get("customer_points", []),
        next_customer_id = next_customer_id,
    )


@customers.route("/customers/add", methods=["POST"])
@login_required
@role_required("admin", "banhang")
def add_customer():
    result = CustomerService().add_customer(request.form)

    if result.get("success"):
        flash(result.get("message", "Thêm khách hàng thành công."), "success")
    else:
        flash(result.get("message", "Thêm khách hàng thất bại."), "danger")

    return redirect(url_for("customers.index"))


@customers.route("/customers/update", methods=["POST"])
@login_required
@role_required("admin", "banhang")
def update():
    result = CustomerService().update_customer(
        request.form.get("makh", ""),
        request.form.get("tenkh", ""),
        request.form.get("dienthoai", ""),
        request.form.get("diachi", ""),
    )
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("customers.index"))


@customers.route("/customers/points-history/<makh>")
@login_required
@role_required("admin", "banhang")
def points_history(makh):
    result = CustomerService().get_customer_point_history(makh)
    if not result.get("success"):
        return jsonify({"success": False, "message": result.get("message"), "data": []}), 400
    return jsonify({"success": True, "data": result.get("data", [])})
