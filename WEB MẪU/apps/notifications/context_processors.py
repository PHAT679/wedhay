from .models import ThongBao


def notifications_processor(request):
    """Cung cấp số lượng thông báo chưa đọc và danh sách thông báo mới nhất cho giao diện."""
    context = {
        'unread_notifications_count': 0,
        'recent_notifications': [],
    }

    if request.user.is_authenticated:
        try:
            tai_khoan = getattr(request.user, 'tai_khoan', None)
            if tai_khoan:
                user_notifications = ThongBao.objects.filter(tai_khoan=tai_khoan)
                context['unread_notifications_count'] = user_notifications.filter(da_doc=False).count()
                context['recent_notifications'] = user_notifications.order_by('-thoi_diem_tao')[:8]
        except Exception:
            pass

    return context
