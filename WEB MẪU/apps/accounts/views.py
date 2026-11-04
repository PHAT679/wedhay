from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from .forms import LoginForm, RegisterForm, KhachHangForm
from .models import KhachHang, TaiKhoan
from .decorators import owner_required


def login_view(request):
    """UC1: Đăng nhập theo SRS với phân quyền 3 vai trò và cơ chế phiên an toàn."""
    if request.user.is_authenticated:
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
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        remember_me = form.cleaned_data.get('remember_me')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)  # Browser close expires session
            else:
                request.session.set_expiry(1209600)  # 2 weeks

            messages.success(request, f'Chào mừng {user.first_name or user.username} đến với Emmay Beauty!')

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
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không chính xác.')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Đăng xuất người dùng."""
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất thành công.')
    return redirect('accounts:login')


def register_view(request):
    """UC9: Đăng ký tài khoản Khách hàng theo SRS."""
    if request.user.is_authenticated:
        return redirect('home')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ho_ten = form.cleaned_data['ho_ten']
        so_dien_thoai = form.cleaned_data['so_dien_thoai']
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

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

            # Tạo Django User
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

            # Tự động đăng nhập
            login(request, user)
            messages.success(request, 'Đăng ký tài khoản thành công! Chào mừng quý khách đến với Emmay Beauty.')
            return redirect('customer:booking')

    return render(request, 'accounts/register.html', {'form': form})


# =========================================================================
# UC6: QUẢN LÝ THÔNG TIN KHÁCH HÀNG (Dành cho Chủ Tiệm)
# =========================================================================

@owner_required
def owner_customers_list(request):
    """UC 6.1: Danh sách và tìm kiếm khách hàng theo tên hoặc số điện thoại."""
    query = request.GET.get('q', '').strip()
    customers = KhachHang.objects.all()

    if query:
        customers = customers.filter(
            Q(ho_ten__icontains=query) | Q(so_dien_thoai__icontains=query)
        )

    return render(request, 'owner/customers_list.html', {
        'customers': customers,
        'query': query,
    })


@owner_required
def owner_customer_create(request):
    """UC 6.2: Thêm mới thông tin khách hàng."""
    form = KhachHangForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        kh = form.save()
        messages.success(request, f'Đã thêm khách hàng "{kh.ho_ten}" thành công.')
        return redirect('owner:customers_list')

    return render(request, 'owner/customer_form.html', {
        'form': form,
        'title': 'Thêm Khách Hàng Mới',
    })


@owner_required
def owner_customer_update(request, pk):
    """UC 6.3: Cập nhật thông tin khách hàng."""
    customer = get_object_or_404(KhachHang, pk=pk)
    form = KhachHangForm(request.POST or None, instance=customer)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Đã cập nhật thông tin khách hàng "{customer.ho_ten}" thành công.')
        return redirect('owner:customers_list')

    return render(request, 'owner/customer_form.html', {
        'form': form,
        'customer': customer,
        'title': f'Chỉnh Sửa Khách Hàng: {customer.ho_ten}',
    })


@owner_required
def owner_customer_detail(request, pk):
    """UC 6.4: Xem chi tiết thông tin khách hàng và lịch sử đặt lịch."""
    customer = get_object_or_404(KhachHang, pk=pk)
    appointments = customer.lich_hen.order_by('-ngay_gio_bat_dau')

    return render(request, 'owner/customer_detail.html', {
        'customer': customer,
        'appointments': appointments,
    })
