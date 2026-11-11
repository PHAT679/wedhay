from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import OuterRef, Q, Subquery
from django.core.paginator import Paginator
from .forms import LoginForm, RegisterForm, KhachHangCreateForm, KhachHangForm, KhachHangUpdateForm
from .models import KhachHang, TaiKhoan
from .decorators import owner_required


import logging
import unicodedata

logger = logging.getLogger(__name__)


def login_view(request):
    """UC1: Đăng nhập theo SRS với phân quyền 3 vai trò, chuẩn 4 trạng thái theo Figma."""
    next_url = request.POST.get('next', request.GET.get('next', '')).strip()
    if not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        next_url = ''
    if request.user.is_authenticated:
        tai_khoan = getattr(request.user, 'tai_khoan', None)
        if tai_khoan and tai_khoan.vai_tro in ('Chủ Tiệm', 'Nhân Viên'):
            return redirect('owner:dashboard' if tai_khoan.vai_tro == 'Chủ Tiệm' else 'employee:dashboard')
        if next_url:
            return redirect(next_url)
        tai_khoan = getattr(request.user, 'tai_khoan', None)
        if tai_khoan:
            if tai_khoan.vai_tro == 'Chủ Tiệm':
                return redirect('owner:dashboard')
            elif tai_khoan.vai_tro == 'Nhân Viên':
                return redirect('employee:dashboard')
            else:
                return redirect('customer:my_appointments')
        return redirect('home')

    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        raw_username = request.POST.get('username', '').strip()
        raw_password = request.POST.get('password', '')

        # Trạng thái 2: Thiếu thông tin
        if not raw_username or not raw_password:
            messages.error(request, 'Vui lòng nhập đầy đủ tên tài khoản và mật khẩu')
            return render(request, 'accounts/login.html', {'form': form, 'next': next_url})

        try:
            # Trạng thái xác thực
            user = authenticate(request, username=raw_username, password=raw_password)
            if user is not None:
                login(request, user)
                # Mặc định duy trì phiên đăng nhập theo cấu hình
                request.session.set_expiry(1209600)
                tai_khoan = getattr(user, 'tai_khoan', None)
                if tai_khoan and tai_khoan.vai_tro in ('Chủ Tiệm', 'Nhân Viên'):
                    return redirect('owner:dashboard' if tai_khoan.vai_tro == 'Chủ Tiệm' else 'employee:dashboard')
                if next_url:
                    return redirect(next_url)

                tai_khoan = getattr(user, 'tai_khoan', None)
                if tai_khoan:
                    if tai_khoan.vai_tro == 'Chủ Tiệm':
                        return redirect('owner:dashboard')
                    elif tai_khoan.vai_tro == 'Nhân Viên':
                        return redirect('employee:dashboard')
                    else:
                        return redirect('customer:my_appointments')
                return redirect('home')
            else:
                # Trạng thái 3: Sai thông tin
                messages.error(request, 'Tên tài khoản hoặc mật khẩu không chính xác')
        except Exception as e:
            # Trạng thái 4: Lỗi hệ thống
            logger.exception("Lỗi không mong muốn trong quá trình xử lý đăng nhập: %s", e)
            messages.error(request, 'Đã xảy ra lỗi, hãy thử lại sau')

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    """Đăng xuất người dùng."""
    is_employee = request.user.is_authenticated and getattr(getattr(request.user, 'tai_khoan', None), 'vai_tro', None) == 'Nhân Viên'
    logout(request)
    return redirect('home' if is_employee else 'accounts:login')


def register_view(request):
    """UC9: Đăng ký tài khoản Khách hàng theo SRS & Figma chuẩn 6 trạng thái."""
    if request.user.is_authenticated:
        return redirect('home')

    general_error = None
    success_message = None

    if request.GET.get('registered') == '1':
        success_message = 'Đăng kí tài khoản thành công'

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == '1'

    form = RegisterForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        if form.is_valid():
            ho_ten = form.cleaned_data['ho_ten']
            so_dien_thoai = form.cleaned_data['so_dien_thoai']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                with transaction.atomic():
                    # Kiểm tra nếu khách hàng đã từng được chủ tiệm tạo thông tin theo SĐT
                    khach_hang = KhachHang.objects.filter(so_dien_thoai=so_dien_thoai).first()
                    if not khach_hang:
                        khach_hang = KhachHang.objects.create(
                            ho_ten=ho_ten,
                            so_dien_thoai=so_dien_thoai
                        )
                    else:
                        # Cập nhật họ tên nếu chưa có
                        if not khach_hang.ho_ten:
                            khach_hang.ho_ten = ho_ten
                            khach_hang.save()

                    # Tạo Django User với mật khẩu được hash an toàn
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        first_name=ho_ten
                    )

                    # Tạo TaiKhoan liên kết Khách Hàng
                    TaiKhoan.objects.create(
                        user=user,
                        vai_tro='Khách Hàng',
                        khach_hang=khach_hang
                    )

                    # Nếu là AJAX request từ frontend Figma:
                    if is_ajax:
                        return JsonResponse({
                            'success': True,
                            'message': 'Đăng kí tài khoản thành công',
                            'redirect_url': reverse('accounts:login')
                        })

                    # Với submit POST thông thường: chuyển đến trang đăng nhập
                    messages.success(request, 'Đăng ký tài khoản thành công! Chào mừng quý khách đến với Emmay Beauty.')
                    return redirect('accounts:login')
            except Exception as e:
                logger.exception("Lỗi trong quá trình đăng ký tài khoản: %s", e)
                general_error = 'Đăng ký tài khoản thất bại, vui lòng thử lại'
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'general_error': general_error
                    }, status=400)
        else:
            if is_ajax:
                errors = {}
                for field, err_list in form.errors.items():
                    errors[field] = err_list[0]
                return JsonResponse({
                    'success': False,
                    'errors': errors
                }, status=400)

    return render(request, 'accounts/register.html', {
        'form': form,
        'general_error': general_error,
        'success_message': success_message,
    })


# =========================================================================
# UC6: QUẢN LÝ THÔNG TIN KHÁCH HÀNG (Dành cho Chủ Tiệm)
# =========================================================================

@owner_required
def owner_customers_list(request):
    """UC 6.1: Danh sách và tìm kiếm khách hàng theo tên hoặc số điện thoại."""
    query = request.GET.get('q', '').strip()
    customers = KhachHang.objects.all()
    invalid_query = bool(query) and any(
        not (char.isalnum() or char.isspace() or unicodedata.category(char).startswith('M'))
        for char in query
    )

    if invalid_query:
        customers = customers.none()
    elif query:
        customers = customers.filter(
            Q(ho_ten__icontains=query) | Q(so_dien_thoai__icontains=query)
        )

    from apps.appointments.models import ChiTietLichHen
    latest_service = ChiTietLichHen.objects.filter(
        lich_hen__khach_hang_id=OuterRef('pk'), lich_hen__trang_thai='Hoàn thành',
    ).order_by('-lich_hen__ngay_gio_bat_dau', '-lich_hen_id', '-pk').values('ten_dich_vu_dat')[:1]
    customers = customers.annotate(latest_service=Subquery(latest_service)).order_by('ma_khach_hang')
    page_obj = Paginator(customers, 5).get_page(request.GET.get('page'))
    return render(request, 'owner/customers_management.html', {
        'customers': page_obj,
        'page_obj': page_obj,
        'page_range': page_obj.paginator.get_elided_page_range(page_obj.number),
        'query': query,
        'invalid_query': invalid_query,
    })


@owner_required
def owner_customer_create(request):
    """UC 6.2: Thêm mới thông tin khách hàng."""
    form = KhachHangCreateForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        request.session['customer_create_success'] = True
        return redirect('owner:customer_create')

    return render(request, 'owner/customer_create.html', {
        'form': form,
        'title': 'Thêm Khách Hàng Mới',
        'customer_create_success': request.session.pop('customer_create_success', False),
    })


@owner_required
def owner_customer_update(request, pk):
    """UC 6.3: Cập nhật thông tin khách hàng."""
    customer = get_object_or_404(KhachHang, pk=pk)
    form = KhachHangUpdateForm(request.POST or None, instance=customer)
    if request.method == 'POST' and form.is_valid():
        form.save()
        request.session['customer_update_success'] = str(customer.pk)
        return redirect('owner:customer_update', pk=customer.pk)

    customer_update_success = request.method == 'GET' and request.session.get('customer_update_success') == str(customer.pk)
    if customer_update_success:
        request.session.pop('customer_update_success', None)
    return render(request, 'owner/customer_form.html', {
        'form': form,
        'customer': customer,
        'title': f'Chỉnh Sửa Khách Hàng: {customer.ho_ten}',
        'customer_update_success': customer_update_success,
    })


@owner_required
def owner_customer_detail(request, pk):
    """UC 6.4: Xem chi tiết thông tin khách hàng và lịch sử đặt lịch."""
    customer = get_object_or_404(KhachHang, pk=pk)
    appointments = customer.lich_hen.order_by('-ngay_gio_bat_dau')

    if request.GET.get('display') == 'profile':
        return render(request, 'owner/customer_view_info.html', {'customer': customer})

    if request.GET.get('display') == 'history':
        page_obj = Paginator(appointments.order_by('-ngay_gio_bat_dau', '-pk').prefetch_related('chi_tiet'), 5).get_page(request.GET.get('page'))
        return render(request, 'owner/customer_eye_history.html', {
            'customer': customer,
            'appointments': page_obj,
            'page_range': page_obj.paginator.get_elided_page_range(page_obj.number),
        })

    return render(request, 'owner/customer_detail.html', {
        'customer': customer,
        'appointments': appointments,
    })
