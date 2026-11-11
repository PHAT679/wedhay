from django.shortcuts import render, redirect, get_object_or_404
from django.urls import Resolver404, resolve, reverse
from django.http import JsonResponse
from django.utils.timesince import timesince
from django.utils.http import url_has_allowed_host_and_scheme
from apps.accounts.decorators import owner_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ThongBao


@login_required
def notifications_list_view(request):
    """Xem toàn bộ danh sách thông báo của tài khoản hiện tại."""
    tai_khoan = getattr(request.user, 'tai_khoan', None)
    if tai_khoan and tai_khoan.vai_tro == 'Chủ Tiệm':
        return redirect('owner:dashboard')
    if tai_khoan and tai_khoan.vai_tro == 'Khách Hàng':
        return redirect('customer:my_appointments')
    if not tai_khoan:
        notifications = []
    else:
        notifications = ThongBao.objects.filter(tai_khoan=tai_khoan).order_by('-thoi_diem_tao')

    return render(request, 'notifications/list.html', {
        'notifications': notifications,
        'notifications_base': 'base_dashboard.html' if tai_khoan and tai_khoan.vai_tro == 'Nhân Viên' else 'base.html',
    })


@login_required
def notification_mark_read(request, pk):
    """Đánh dấu thông báo đã đọc và chuyển hướng đến trang tương ứng."""
    tai_khoan = getattr(request.user, 'tai_khoan', None)
    notif = get_object_or_404(ThongBao, pk=pk, tai_khoan=tai_khoan)
    if notif.loai_thong_bao == 'Từ chối' and (notif.lien_ket or '').startswith('/owner/assignments/rejection/'):
        return redirect(f'{notif.lien_ket}?notification={notif.pk}')
    notif.da_doc = True
    notif.save()

    if (tai_khoan.vai_tro == 'Chủ Tiệm' and notif.loai_thong_bao == 'Lịch mới'
            and notif.tieu_de == 'Lịch hẹn mới cần xác nhận' and notif.lien_ket):
        try:
            match = resolve(notif.lien_ket)
        except Resolver404:
            match = None
        if match and match.view_name == 'owner:appointment_detail':
            return redirect('owner:status_edit', pk=match.kwargs['pk'])

    if notif.lien_ket:
        return redirect(notif.lien_ket)
    if tai_khoan and tai_khoan.vai_tro == 'Khách Hàng':
        return redirect('customer:my_appointments')
    return redirect('notifications:list')


@login_required
def mark_all_read(request):
    """Đánh dấu tất cả thông báo của tài khoản là đã đọc."""
    tai_khoan = getattr(request.user, 'tai_khoan', None)
    if tai_khoan:
        unread = ThongBao.objects.filter(tai_khoan=tai_khoan, da_doc=False)
        if tai_khoan.vai_tro == 'Chủ Tiệm':
            unread = unread.exclude(loai_thong_bao='Từ chối')
            messages.success(request, 'Đã đánh dấu các thông báo khác là đã đọc; thông báo từ chối được đánh dấu khi mở chi tiết.')
        elif tai_khoan.vai_tro != 'Khách Hàng':
            messages.success(request, 'Đã đánh dấu tất cả thông báo là đã đọc.')
        unread.update(da_doc=True)
        if tai_khoan.vai_tro == 'Chủ Tiệm':
            referer = request.headers.get('Referer', '')
            if url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                return redirect(referer)
            return redirect('owner:dashboard')
    if tai_khoan and tai_khoan.vai_tro == 'Khách Hàng':
        referer = request.headers.get('Referer', '')
        if url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return redirect(referer)
        return redirect('customer:my_appointments')
    return redirect('notifications:list')


@owner_required
def owner_notification_status(request):
    notifications = ThongBao.objects.filter(tai_khoan=request.user.tai_khoan)
    unread = notifications.filter(da_doc=False)
    recent = notifications.order_by('-thoi_diem_tao', '-ma_thong_bao')[:8]
    response = JsonResponse({
        'count': unread.count(),
        'rejection_ids': list(unread.filter(loai_thong_bao='Từ chối').values_list('pk', flat=True)),
        'notifications': [{'title': n.tieu_de, 'body': n.noi_dung, 'time': timesince(n.thoi_diem_tao),
                           'unread': not n.da_doc, 'url': reverse('notifications:mark_read', args=[n.pk])}
                          for n in recent],
    })
    response['Cache-Control'] = 'no-store'
    return response
