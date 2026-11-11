from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core import signing
from django.db import DatabaseError, IntegrityError, connection
from django.db.models import Case, Exists, IntegerField, OuterRef, Q, Value, When
from django.db.models.expressions import RawSQL
from django.core.paginator import Paginator
from apps.accounts.decorators import owner_required
from .models import DichVu
from .forms import DichVuCreateForm, DichVuEditForm, normalize_service_name


def public_services_list(request):
    """UC8: Khách hàng xem danh mục dịch vụ."""
    services = DichVu.objects.filter(da_xoa=False).order_by('gia_tien', 'ma_dich_vu')
    paginator = Paginator(services, 6)
    page_obj = paginator.get_page(request.GET.get('page'))
    query = request.GET.copy()
    query.pop('page', None)
    return render(request, 'customer/services.html', {
        'services': page_obj,
        'page_obj': page_obj,
        'page_numbers': paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1),
        'pagination_query': query.urlencode(),
    })


@owner_required
def owner_services_list(request):
    """UC 4.1: Chủ tiệm xem danh sách và tìm kiếm dịch vụ."""
    query = request.GET.get('q', '').strip()
    services = DichVu.objects.filter(da_xoa=False)

    if query:
        services = services.filter(ten_dich_vu__icontains=query)

    try:
        new_service_id = request.get_signed_cookie('owner_new_service', max_age=120)
    except (KeyError, signing.BadSignature):
        new_service_id = None
    if query or request.GET.get('page', '1') != '1':
        new_service_id = None
    if connection.vendor == 'sqlite':
        services = services.annotate(_insertion_order=RawSQL('"DichVu"."rowid"', ()))
        ordering = ['-_insertion_order']
    else:
        ordering = ['-ma_dich_vu']
    if new_service_id:
        services = services.annotate(_just_created=Case(
            When(pk=new_service_id, then=Value(0)), default=Value(1), output_field=IntegerField(),
        ))
        ordering.insert(0, '_just_created')
    page_obj = Paginator(services.order_by(*ordering), 5).get_page(request.GET.get('page'))
    for service in page_obj:
        service.display_price = f'{service.gia_tien:,.0f}'.replace(',', '.')
    response = render(request, 'owner/services_management.html', {
        'services': page_obj,
        'page_obj': page_obj,
        'query': query,
        'new_service_id': new_service_id,
    })
    if 'owner_new_service' in request.COOKIES:
        response.delete_cookie('owner_new_service', samesite='Lax')
    return response


@owner_required
def owner_service_create(request):
    """UC 4.2: Thêm mới dịch vụ."""
    form = DichVuCreateForm(request.POST if request.method == 'POST' else None)
    for field_name in ('ten_dich_vu', 'gia_tien', 'thoi_luong'):
        form.fields[field_name].error_messages['required'] = 'Dữ liệu không được để trống'
    if request.method == 'POST' and form.is_valid():
        dv = form.save()
        messages.success(request, 'Thêm dịch vụ thành công', extra_tags='service-added')
        response = redirect('owner:services_list')
        response.set_signed_cookie('owner_new_service', dv.pk, max_age=120, httponly=True, samesite='Lax')
        return response

    return render(request, 'owner/service_create.html', {
        'form': form,
        'title': 'Thêm Dịch Vụ Mới',
        'existing_service_names': [normalize_service_name(name) for name in DichVu.objects.values_list('ten_dich_vu', flat=True)],
    })


@owner_required
def owner_service_detail(request, pk):
    service = get_object_or_404(DichVu, pk=pk, da_xoa=False)
    return render(request, 'owner/service_detail.html', {
        'service': service,
        'display_price': f'{service.gia_tien:,.0f}'.replace(',', '.'),
    })


@owner_required
def owner_service_update(request, pk):
    """UC 4.3: Chỉnh sửa dịch vụ."""
    service = get_object_or_404(DichVu, pk=pk, da_xoa=False)
    form = DichVuEditForm(request.POST if request.method == 'POST' else None, instance=service)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cập nhật dịch vụ thành công', extra_tags='service-updated')
        response = redirect('owner:services_list')
        response.set_signed_cookie('owner_new_service', service.pk, max_age=120, httponly=True, samesite='Lax')
        return response

    return render(request, 'owner/service_edit.html', {
        'form': form,
        'service': service,
        'title': f'Chỉnh Sửa Dịch Vụ: {service.ten_dich_vu}',
    })


@owner_required
def owner_services_delete_list(request):
    services = DichVu.objects.filter(da_xoa=False)
    if connection.vendor == 'sqlite':
        services = services.annotate(_insertion_order=RawSQL('"DichVu"."rowid"', ())).order_by('-_insertion_order')
    else:
        services = services.order_by('-ma_dich_vu')
    page_obj = Paginator(services, 5).get_page(request.GET.get('page'))
    for service in page_obj:
        service.display_price = f'{service.gia_tien:,.0f}'.replace(',', '.')
    return render(request, 'owner/services_delete_list.html', {
        'services': page_obj, 'page_obj': page_obj,
        'service_in_use': request.session.pop('service_delete_in_use', False),
    })


@owner_required
def owner_service_delete(request, pk):
    """
    UC 4.4: Xóa mềm dịch vụ.
    Giữ lại bản ghi dịch vụ và mọi tham chiếu để bảo toàn lịch sử.
    """
    service = get_object_or_404(DichVu, pk=pk, da_xoa=False)
    from_delete_list = request.method == 'POST' and request.POST.get('from_delete_list') == '1'
    return_to = 'owner:services_delete_list' if from_delete_list else 'owner:services_list'

    def delete_redirect():
        response = redirect(return_to)
        page = request.POST.get('page', '')
        if from_delete_list and page.isascii() and page.isdigit() and 0 < len(page) <= 6:
            response['Location'] += '?page=' + page
        return response

    def in_use_response():
        if from_delete_list:
            request.session['service_delete_in_use'] = True
        else:
            messages.error(request, 'Không thể xóa vì dịch vụ đang được sử dụng')
        return delete_redirect()

    if request.method == 'POST':
        from apps.appointments.models import ChiTietLichHen
        blocking_details = ChiTietLichHen.objects.filter(dich_vu_id=OuterRef('pk')).exclude(lich_hen__trang_thai='Hủy')
        try:
            updated = DichVu.objects.filter(pk=service.pk, da_xoa=False).filter(~Exists(blocking_details)).update(da_xoa=True)
        except IntegrityError:
            return in_use_response()
        except DatabaseError:
            if not from_delete_list:
                raise
            messages.error(request, 'Không thể xóa dịch vụ. Vui lòng thử lại.')
            return delete_redirect()
        if not updated:
            if service.chi_tiet_lich_hen.exclude(lich_hen__trang_thai='Hủy').exists():
                return in_use_response()
            messages.error(request, 'Không thể xóa dịch vụ. Vui lòng thử lại.')
            return delete_redirect()
        messages.success(request, 'Xóa dịch vụ thành công' if from_delete_list else f'Đã xóa dịch vụ "{service.ten_dich_vu}" thành công.', extra_tags='service-deleted' if from_delete_list else '')
        return delete_redirect()

    if service.chi_tiet_lich_hen.exclude(lich_hen__trang_thai='Hủy').exists():
        return in_use_response()

    return render(request, 'owner/service_confirm_delete.html', {'service': service})
