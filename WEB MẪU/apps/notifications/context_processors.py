from .models import ThongBao


def notifications_processor(request):
    """Cung cấp số lượng thông báo chưa đọc và danh sách thông báo mới nhất cho giao diện."""
    context = {
        'unread_notifications_count': 0,
        'recent_notifications': [],
        'unread_rejection_ids': [],
    }

    if request.user.is_authenticated:
        try:
            tai_khoan = getattr(request.user, 'tai_khoan', None)
            if tai_khoan:
                user_notifications = ThongBao.objects.filter(tai_khoan=tai_khoan)
                context['unread_notifications_count'] = user_notifications.filter(da_doc=False).count()
                if tai_khoan.vai_tro == 'Chủ Tiệm':
                    context['unread_rejection_ids'] = list(user_notifications.filter(da_doc=False, loai_thong_bao='Từ chối').values_list('pk', flat=True))
                context['recent_notifications'] = user_notifications.order_by('-thoi_diem_tao')[:8]
        except Exception:
            pass

    return context
