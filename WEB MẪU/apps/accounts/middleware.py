from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.cache import patch_cache_control, patch_vary_headers
from django.utils.deprecation import MiddlewareMixin


class RoleNavigationMiddleware(MiddlewareMixin):
    """Keep owner and employee sessions inside their permitted areas."""

    def process_view(self, request, view_func, view_args, view_kwargs):
        match = request.resolver_match
        if not match:
            return None
        user = request.user
        account = getattr(user, 'tai_khoan', None) if user.is_authenticated else None
        role = getattr(account, 'vai_tro', None)
        namespace = match.namespace
        name = match.view_name

        if namespace == 'customer' and user.is_authenticated and role not in ('Chủ Tiệm', 'Nhân Viên', 'Khách Hàng'):
            return HttpResponseForbidden('Bạn cần tài khoản khách hàng để sử dụng chức năng này.')

        if role not in ('Chủ Tiệm', 'Nhân Viên'):
            return None

        destination = 'owner:dashboard' if role == 'Chủ Tiệm' else 'employee:dashboard'
        public_views = {'home', 'services:public_list', 'accounts:login', 'accounts:register', 'api_available_slots'}
        denied = name in public_views or namespace == 'customer' or namespace == 'admin'
        denied = denied or (role == 'Chủ Tiệm' and namespace == 'employee')
        denied = denied or (role == 'Nhân Viên' and (namespace in ('owner', 'payments') or name == 'notifications:owner_status'))
        return redirect(destination) if denied else None

    def process_response(self, request, response):
        match = getattr(request, 'resolver_match', None)
        account = getattr(request.user, 'tai_khoan', None) if request.user.is_authenticated else None
        staff_notifications = match and match.namespace == 'notifications' and getattr(account, 'vai_tro', None) in ('Chủ Tiệm', 'Nhân Viên')
        if match and (match.namespace in ('owner', 'employee', 'payments') or staff_notifications):
            patch_cache_control(response, private=True, no_cache=True, no_store=True, must_revalidate=True)
            patch_vary_headers(response, ('Cookie',))
        return response
