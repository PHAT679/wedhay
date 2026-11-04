from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from apps.accounts.decorators import owner_required
from .models import DichVu
from .forms import DichVuForm


def public_services_list(request):
    """UC8: Khách hàng xem danh mục dịch vụ."""
    services = DichVu.objects.filter(da_xoa=False).order_by('gia_tien')
    return render(request, 'customer/services.html', {'services': services})


@owner_required
def owner_services_list(request):
    """UC 4.1: Chủ tiệm xem danh sách và tìm kiếm dịch vụ."""
    query = request.GET.get('q', '').strip()
    services = DichVu.objects.filter(da_xoa=False)

    if query:
        services = services.filter(ten_dich_vu__icontains=query)

    return render(request, 'owner/services_list.html', {
        'services': services,
        'query': query,
    })


@owner_required
def owner_service_create(request):
    """UC 4.2: Thêm mới dịch vụ."""
    form = DichVuForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        dv = form.save()
        messages.success(request, f'Đã thêm dịch vụ "{dv.ten_dich_vu}" thành công.')
        return redirect('owner:services_list')

    return render(request, 'owner/service_form.html', {
        'form': form,
        'title': 'Thêm Dịch Vụ Mới',
    })


@owner_required
def owner_service_update(request, pk):
    """UC 4.3: Chỉnh sửa dịch vụ."""
    service = get_object_or_404(DichVu, pk=pk, da_xoa=False)
    form = DichVuForm(request.POST or None, instance=service)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Đã cập nhật dịch vụ "{service.ten_dich_vu}" thành công.')
        return redirect('owner:services_list')

    return render(request, 'owner/service_form.html', {
        'form': form,
        'service': service,
        'title': f'Chỉnh Sửa Dịch Vụ: {service.ten_dich_vu}',
    })


@owner_required
def owner_service_delete(request, pk):
    """
    UC 4.4: Xóa mềm dịch vụ.
    Business Rule BR-UC4-08: Không được xóa dịch vụ đang có lịch hẹn Chờ xác nhận hoặc Đã xác nhận.
    """
    service = get_object_or_404(DichVu, pk=pk, da_xoa=False)
    
    # Kiểm tra ràng buộc nghiệp vụ
    active_appointments_exist = service.chi_tiet_lich_hen.filter(
        lich_hen__trang_thai__in=['Chờ xác nhận', 'Đã xác nhận']
    ).exists()

    if active_appointments_exist:
        messages.error(
            request,
            f'Không thể xóa dịch vụ "{service.ten_dich_vu}" vì đang có lịch hẹn Chờ xác nhận hoặc Đã xác nhận chưa hoàn tất!'
        )
        return redirect('owner:services_list')

    if request.method == 'POST':
        service.da_xoa = True
        service.save()
        messages.success(request, f'Đã xóa dịch vụ "{service.ten_dich_vu}" thành công.')
        return redirect('owner:services_list')

    return render(request, 'owner/service_confirm_delete.html', {'service': service})
