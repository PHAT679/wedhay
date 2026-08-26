# file: controllers/decorators.py
from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            flash("Vui lòng đăng nhập để tiếp tục.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = session.get("user")
            if not user:
                return redirect(url_for("auth.login"))

            role = str(user.get("role", "")).strip().lower()

            if role not in allowed_roles:
                if request.endpoint == "dashboard.index":
                    session.clear()
                    flash("Bạn không có quyền truy cập hệ thống.", "danger")
                    return redirect(url_for("auth.login"))
                else:
                    flash("Bạn không có quyền truy cập chức năng này.", "danger")
                    return redirect(url_for("dashboard.index"))

            return f(*args, **kwargs)
        return decorated
    return wrapper
