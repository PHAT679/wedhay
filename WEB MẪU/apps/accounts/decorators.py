from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


def role_required(*allowed_roles):
    """
    Decorator kiểm tra vai trò người dùng tại Backend.
    Nếu chưa đăng nhập: redirect về login kèm thông báo.
    Nếu sai vai trò: trả về 403 Forbidden hoặc redirect kèm thông báo lỗi.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Vui lòng đăng nhập để tiếp tục.')
                return redirect('accounts:login')
            
            tai_khoan = getattr(request.user, 'tai_khoan', None)
            if not tai_khoan or tai_khoan.vai_tro not in allowed_roles:
                messages.error(request, 'Bạn không có quyền truy cập vào chức năng này.')
                return HttpResponseForbidden('403 Forbidden - Bạn không có quyền truy cập.')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def owner_required(view_func):
    return role_required('Chủ Tiệm')(view_func)


def employee_required(view_func):
    return role_required('Nhân Viên')(view_func)


def customer_required(view_func):
    return role_required('Khách Hàng')(view_func)
