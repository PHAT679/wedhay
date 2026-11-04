def auth_user_processor(request):
    """Context processor cung cấp vai trò và thông tin tài khoản hiện tại cho mọi template."""
    context = {
        'current_tai_khoan': None,
        'current_role': None,
        'is_owner': False,
        'is_employee': False,
        'is_customer': False,
        'current_nhan_vien': None,
        'current_khach_hang': None,
    }

    if request.user.is_authenticated:
        try:
            tai_khoan = getattr(request.user, 'tai_khoan', None)
            if tai_khoan:
                context['current_tai_khoan'] = tai_khoan
                context['current_role'] = tai_khoan.vai_tro
                context['is_owner'] = (tai_khoan.vai_tro == 'Chủ Tiệm')
                context['is_employee'] = (tai_khoan.vai_tro == 'Nhân Viên')
                context['is_customer'] = (tai_khoan.vai_tro == 'Khách Hàng')
                
                if context['is_employee']:
                    context['current_nhan_vien'] = getattr(tai_khoan, 'nhan_vien', None)
                if context['is_customer']:
                    context['current_khach_hang'] = tai_khoan.khach_hang
        except Exception:
            pass

    return context
