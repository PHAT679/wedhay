# file: controllers/auth_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services.auth_service import AuthService

auth = Blueprint("auth", __name__)
_svc = AuthService

@auth.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        role = str(session["user"].get("role", "")).strip().lower()
        if role in ["admin", "banhang", "kho"]:
            return redirect(url_for("dashboard.index"))
        else:
            session.clear()

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        
        result = _svc().login(username, password)
        if result["success"]:
            user_data = result["data"]
            role = (user_data.get("role") or "").strip().lower()
            if role not in ["admin", "banhang", "kho"]:
                flash("Tài khoản không có vai trò hợp lệ để đăng nhập hệ thống.", "danger")
                return redirect(url_for("auth.login"))

            session["user"] = user_data
            try:
                print("DEBUG SESSION USER:", session["user"])
            except Exception:
                pass
            return redirect(url_for("dashboard.index"))
        else:
            flash(result["message"], "danger")
            return redirect(url_for("auth.login"))

    return render_template("login.html")

@auth.route("/logout")
def logout():
    session.clear()
    flash("Bạn đã đăng xuất.", "info")
    return redirect(url_for("auth.login"))
