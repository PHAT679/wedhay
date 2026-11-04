from django.shortcuts import render
from apps.services.models import DichVu


def home_view(request):
    """Trang chủ tiệm nail Emmay Beauty."""
    featured_services = DichVu.objects.filter(da_xoa=False).order_by('gia_tien')[:6]
    return render(request, 'home.html', {
        'services': featured_services,
        'salon_address': '356/87 Hoàng Diệu, Hòa Cường, Đà Nẵng',
        'salon_hotline': '0905.123.456',
        'salon_hours': '09:00 - 19:00 (Thứ 2 - Chủ Nhật)',
    })
