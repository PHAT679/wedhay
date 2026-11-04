from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ThongBao


@login_required
def notifications_list_view(request):
    """Xem toàn bộ danh sách thông báo của tài khoản hiện tại."""
    tai_khoan = getattr(request.user, 'tai_khoan', None)
    if not tai_khoan:
        notifications = []
    else:
        notifications = ThongBao.objects.filter(tai_khoan=tai_khoan).order_by('-thoi_diem_tao')

    return render(request, 'notifications/list.html', {
        'notifications': notifications,
    })


@login_required
def notification_mark_read(request, pk):
    """Đánh dấu thông báo đã đọc và chuyển hướng đến trang tương ứng."""
    tai_khoan = getattr(request.user, 'tai_khoan', None)
    notif = get_object_or_404(ThongBao, pk=pk, tai_khoan=tai_khoan)
    notif.da_doc = True
    notif.save()

    if notif.lien_ket:
        return redirect(notif.lien_ket)
    return redirect('notifications:list')


@login_required
def mark_all_read(request):
    """Đánh dấu tất cả thông báo của tài khoản là đã đọc."""
    tai_khoan = getattr(request.user, 'tai_khoan', None)
    if tai_khoan:
        ThongBao.objects.filter(tai_khoan=tai_khoan, da_doc=False).update(da_doc=True)
        messages.success(request, 'Đã đánh dấu tất cả thông báo là đã đọc.')
    return redirect('notifications:list')
