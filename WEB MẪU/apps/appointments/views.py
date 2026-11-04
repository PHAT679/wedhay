import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from apps.accounts.models import KhachHang, TaiKhoan, phone_validator
from apps.accounts.decorators import owner_required, customer_required
from apps.services.models import DichVu
from apps.notifications.models import send_notification
from .models import LichHen, ChiTietLichHen
from .services import get_available_slots, OPEN_HOUR, CLOSE_HOUR


# =========================================================================
# UC7: QUẢN LÝ LỊCH HẸN (Dành cho Khách Hàng)
# =========================================================================

def customer_booking_view(request):
    """
    UC 7.1: Tạo lịch hẹn trực tuyến.
    Khách chọn nhiều dịch vụ -> hệ thống tính tổng tiền, tổng thời lượng ->
    chọn ngày -> hiển thị khung giờ còn khả năng tiếp nhận -> khách xác nhận.
    """
    services = DichVu.objects.filter(da_xoa=False).order_by('gia_tien')
    today = timezone.localdate()
    max_date = today + datetime.timedelta(days=30)

    # Lấy thông tin mặc định nếu đã đăng nhập
    default_name = ''
    default_phone = ''
    if request.user.is_authenticated:
        tai_khoan = getattr(request.user, 'tai_khoan', None)
        if tai_khoan and tai_khoan.khach_hang:
            default_name = tai_khoan.khach_hang.ho_ten
            default_phone = tai_khoan.khach_hang.so_dien_thoai

    if request.method == 'POST':
        selected_service_ids = request.POST.getlist('service_ids')
        booking_date_str = request.POST.get('booking_date', '').strip()
        booking_time_str = request.POST.get('booking_time', '').strip()
        contact_name = request.POST.get('contact_name', '').strip()
        contact_phone = request.POST.get('contact_phone', '').strip()
        notes = request.POST.get('notes', '').strip()

        # 1. Kiểm tra dịch vụ đã chọn
        if not selected_service_ids:
            messages.error(request, 'Vui lòng chọn ít nhất một dịch vụ nail.')
            return render(request, 'customer/booking.html', {
                'services': services, 'today': today.isoformat(), 'max_date': max_date.isoformat(),
                'default_name': contact_name or default_name, 'default_phone': contact_phone or default_phone,
            })

        chosen_services = DichVu.objects.filter(ma_dich_vu__in=selected_service_ids, da_xoa=False)
        total_duration = sum(s.thoi_luong for s in chosen_services)

        # 2. Kiểm tra thông tin liên hệ
        if not contact_name:
            messages.error(request, 'Vui lòng nhập tên người liên hệ.')
            return render(request, 'customer/booking.html', locals())

        if not contact_phone or len(contact_phone) != 10 or not contact_phone.isdigit():
            messages.error(request, 'Số điện thoại liên hệ phải gồm đúng 10 chữ số.')
            return render(request, 'customer/booking.html', locals())

        # 3. Kiểm tra ngày và giờ
        try:
            booking_date = datetime.date.fromisoformat(booking_date_str)
            time_parts = [int(p) for p in booking_time_str.split(':')]
            booking_time = datetime.time(time_parts[0], time_parts[1])
            start_datetime = timezone.make_aware(datetime.datetime.combine(booking_date, booking_time))
        except Exception:
            messages.error(request, 'Ngày hoặc giờ hẹn không hợp lệ.')
            return render(request, 'customer/booking.html', locals())

        if booking_date < today:
            messages.error(request, 'Không thể đặt lịch cho ngày đã qua trong quá khứ.')
            return render(request, 'customer/booking.html', locals())

        # 4. Atomic transaction kiểm tra lại availability và lưu
        with transaction.atomic():
            slots = get_available_slots(booking_date, total_duration)
            matching_slot = next((s for s in slots if s['time_str'] == booking_time_str and s['available']), None)

            if not matching_slot:
                messages.error(
                    request,
                    f'Khung giờ {booking_time_str} ngày {booking_date.strftime("%d/%m/%Y")} vừa hết chỗ tiếp nhận. Quý khách vui lòng chọn khung giờ khác.'
                )
                return render(request, 'customer/booking.html', locals())

            # Tìm hoặc tạo khách hàng
            khach_hang = None
            if request.user.is_authenticated and hasattr(request.user, 'tai_khoan') and request.user.tai_khoan.khach_hang:
                khach_hang = request.user.tai_khoan.khach_hang
            else:
                khach_hang = KhachHang.objects.filter(so_dien_thoai=contact_phone).first()
                if not khach_hang:
                    khach_hang = KhachHang.objects.create(
                        ho_ten=contact_name,
                        so_dien_thoai=contact_phone
                    )

            # Tạo lịch hẹn
            lich_hen = LichHen.objects.create(
                khach_hang=khach_hang,
                ngay_gio_bat_dau=start_datetime,
                ten_lien_he=contact_name,
                so_dien_thoai_lien_he=contact_phone,
                trang_thai='Chờ xác nhận'
            )

            # Lưu chi tiết lịch hẹn (snapshot giá và thời lượng)
            for s in chosen_services:
                ChiTietLichHen.objects.create(
                    lich_hen=lich_hen,
                    dich_vu=s,
                    ten_dich_vu_dat=s.ten_dich_vu,
                    don_gia_dat=s.gia_tien,
                    thoi_luong_dat=s.thoi_luong,
                    ghi_chu_thuc_hien=notes if s == chosen_services[0] else None
                )

            # Thông báo đến Chủ Tiệm
            owner_tk = TaiKhoan.objects.filter(vai_tro='Chủ Tiệm').first()
            if owner_tk:
                send_notification(
                    tai_khoan=owner_tk,
                    tieu_de='Lịch hẹn mới cần xác nhận',
                    noi_dung=f'Khách {contact_name} ({contact_phone}) vừa đặt lịch {lich_hen.ma_lich_hen} lúc {start_datetime.strftime("%H:%M %d/%m/%Y")}.',
                    loai_thong_bao='Lịch mới',
                    lien_ket=f'/owner/appointments/{lich_hen.ma_lich_hen}/'
                )

        messages.success(request, 'Đặt lịch thành công! Tiệm sẽ liên hệ xác nhận trong thời gian sớm nhất.')
        return redirect('customer:booking_success', pk=lich_hen.ma_lich_hen)

    return render(request, 'customer/booking.html', {
        'services': services,
        'today': today.isoformat(),
        'max_date': max_date.isoformat(),
        'default_name': default_name,
        'default_phone': default_phone,
    })


def customer_booking_success(request, pk):
    """Màn hình xác nhận đặt lịch thành công với thông tin tiệm theo SRS."""
    lich_hen = get_object_or_404(LichHen, pk=pk)
    return render(request, 'customer/booking_success.html', {
        'appointment': lich_hen,
        'salon_address': '356/87 Hoàng Diệu, Hòa Cường, Đà Nẵng',
        'salon_hotline': '0905.123.456',
        'salon_hours': '09:00 - 19:00 hàng ngày',
    })


@customer_required
def customer_my_appointments(request):
    """Khách hàng xem danh sách lịch hẹn của chính mình."""
    khach_hang = request.user.tai_khoan.khach_hang
    if not khach_hang:
        appointments = []
    else:
        appointments = LichHen.objects.filter(khach_hang=khach_hang).order_by('-ngay_gio_bat_dau')

    return render(request, 'customer/my_appointments.html', {
        'appointments': appointments,
    })


@customer_required
def customer_reschedule_view(request, pk):
    """
    UC 7.2: Đổi lịch hẹn.
    Khách chọn ngày/giờ mới -> Backend kiểm tra slot trống -> cập nhật lịch mới.
    """
    khach_hang = request.user.tai_khoan.khach_hang
    lich_hen = get_object_or_404(LichHen, pk=pk, khach_hang=khach_hang)

    if lich_hen.trang_thai not in ['Chờ xác nhận', 'Đã xác nhận']:
        messages.error(request, 'Lịch hẹn này không thể đổi ngày giờ.')
        return redirect('customer:my_appointments')

    today = timezone.localdate()
    max_date = today + datetime.timedelta(days=30)
    total_duration = lich_hen.tong_thoi_luong

    if request.method == 'POST':
        new_date_str = request.POST.get('booking_date', '').strip()
        new_time_str = request.POST.get('booking_time', '').strip()

        try:
            new_date = datetime.date.fromisoformat(new_date_str)
            time_parts = [int(p) for p in new_time_str.split(':')]
            new_time = datetime.time(time_parts[0], time_parts[1])
            new_datetime = timezone.make_aware(datetime.datetime.combine(new_date, new_time))
        except Exception:
            messages.error(request, 'Ngày hoặc giờ đổi lịch không hợp lệ.')
            return render(request, 'customer/reschedule.html', locals())

        with transaction.atomic():
            slots = get_available_slots(new_date, total_duration, exclude_appointment_id=lich_hen.pk)
            matching_slot = next((s for s in slots if s['time_str'] == new_time_str and s['available']), None)

            if not matching_slot:
                messages.error(request, f'Khung giờ {new_time_str} ngày {new_date.strftime("%d/%m/%Y")} không còn trống.')
                return render(request, 'customer/reschedule.html', locals())

            old_time_str = lich_hen.ngay_gio_bat_dau.strftime("%H:%M %d/%m/%Y")
            lich_hen.ngay_gio_bat_dau = new_datetime
            lich_hen.save()

            # Thông báo đến Chủ tiệm
            owner_tk = TaiKhoan.objects.filter(vai_tro='Chủ Tiệm').first()
            if owner_tk:
                send_notification(
                    tai_khoan=owner_tk,
                    tieu_de='Khách hàng đã đổi lịch hẹn',
                    noi_dung=f'Khách {lich_hen.ten_lien_he} đã đổi lịch {lich_hen.ma_lich_hen} từ {old_time_str} sang {new_datetime.strftime("%H:%M %d/%m/%Y")}.',
                    loai_thong_bao='Đổi lịch',
                    lien_ket=f'/owner/appointments/{lich_hen.ma_lich_hen}/'
                )

        messages.success(request, f'Đổi lịch hẹn thành công! Lịch hẹn mới lúc {new_datetime.strftime("%H:%M %d/%m/%Y")}.')
        return redirect('customer:my_appointments')

    return render(request, 'customer/reschedule.html', {
        'appointment': lich_hen,
        'today': today.isoformat(),
        'max_date': max_date.isoformat(),
        'total_duration': total_duration,
    })


@customer_required
def customer_cancel_view(request, pk):
    """
    UC 7.3: Hủy lịch hẹn.
    Khách có thể hủy trước giờ hẹn 2 tiếng; nếu dưới 2 tiếng, SRS yêu cầu hiển thị cảnh báo nhưng vẫn ghi nhận hủy.
    """
    khach_hang = request.user.tai_khoan.khach_hang
    lich_hen = get_object_or_404(LichHen, pk=pk, khach_hang=khach_hang)

    if not lich_hen.can_cancel:
        messages.error(request, 'Không thể hủy lịch hẹn đã hoàn thành hoặc đã bị hủy trước đó.')
        return redirect('customer:my_appointments')

    if request.method == 'POST':
        is_late_cancel = lich_hen.is_less_than_two_hours

        with transaction.atomic():
            lich_hen.trang_thai = 'Hủy'
            lich_hen.thoi_diem_huy = timezone.now()
            lich_hen.tai_khoan_huy = request.user.tai_khoan
            lich_hen.save()

            # Thông báo đến Chủ Tiệm
            owner_tk = TaiKhoan.objects.filter(vai_tro='Chủ Tiệm').first()
            late_warning = ' (CẢNH BÁO: HỦY SÁT GIỜ DƯỚI 2 TIẾNG)' if is_late_cancel else ''
            if owner_tk:
                send_notification(
                    tai_khoan=owner_tk,
                    tieu_de=f'Khách hàng đã hủy lịch hẹn {lich_hen.ma_lich_hen}',
                    noi_dung=f'Khách {lich_hen.ten_lien_he} đã hủy lịch hẹn lúc {lich_hen.ngay_gio_bat_dau.strftime("%H:%M %d/%m/%Y")}.{late_warning}',
                    loai_thong_bao='Hủy lịch',
                    lien_ket=f'/owner/appointments/{lich_hen.ma_lich_hen}/'
                )

            # Thông báo đến KTV nếu đã được phân công
            phan_cong = lich_hen.phan_cong_hien_tai
            if phan_cong:
                send_notification(
                    tai_khoan=phan_cong.nhan_vien.tai_khoan,
                    tieu_de=f'Lịch hẹn {lich_hen.ma_lich_hen} đã bị hủy',
                    noi_dung=f'Lịch hẹn của khách {lich_hen.ten_lien_he} lúc {lich_hen.ngay_gio_bat_dau.strftime("%H:%M %d/%m/%Y")} đã bị hủy bởi khách hàng.',
                    loai_thong_bao='Hủy lịch',
                    lien_ket=f'/employee/appointments/{lich_hen.ma_lich_hen}/'
                )

        if is_late_cancel:
            messages.warning(request, 'Lịch hẹn đã được hủy. Lưu ý: Quý khách hủy sát giờ hẹn (dưới 2 tiếng). Cảm ơn quý khách đã báo trước.')
        else:
            messages.success(request, 'Lịch hẹn đã được hủy thành công.')

        return redirect('customer:my_appointments')

    return render(request, 'customer/appointment_cancel_confirm.html', {'appointment': lich_hen})


# =========================================================================
# UC3: THEO DÕI LỊCH HẸN & OWNER DASHBOARD
# =========================================================================

@owner_required
def owner_dashboard(request):
    """Trang tổng quan cho Chủ Tiệm: thống kê lịch hôm nay, doanh thu ước tính, timeline."""
    today = timezone.localdate()
    today_appointments = LichHen.objects.filter(ngay_gio_bat_dau__date=today)

    total_today = today_appointments.count()
    pending_today = today_appointments.filter(trang_thai='Chờ xác nhận').count()
    confirmed_today = today_appointments.filter(trang_thai='Đã xác nhận').count()
    completed_today = today_appointments.filter(trang_thai='Hoàn thành').count()

    recent_appointments = LichHen.objects.all().order_by('-thoi_diem_tao')[:6]

    return render(request, 'owner/dashboard.html', {
        'today': today,
        'total_today': total_today,
        'pending_today': pending_today,
        'confirmed_today': confirmed_today,
        'completed_today': completed_today,
        'recent_appointments': recent_appointments,
    })


@owner_required
def owner_timeline_view(request):
    """UC 3.1: Timeline trực quan theo ngày chia mốc 30 phút từ 09:00 đến 19:00."""
    date_str = request.GET.get('date', '').strip()
    try:
        selected_date = datetime.date.fromisoformat(date_str) if date_str else timezone.localdate()
    except Exception:
        selected_date = timezone.localdate()

    appointments = LichHen.objects.filter(
        ngay_gio_bat_dau__date=selected_date
    ).prefetch_related('chi_tiet', 'phan_cong__nhan_vien').order_by('ngay_gio_bat_dau')

    # Xây dựng các mốc thời gian 30 phút từ 09:00 đến 19:00
    timeline_blocks = []
    current_time = datetime.datetime.combine(selected_date, datetime.time(OPEN_HOUR, 0))
    closing_time = datetime.datetime.combine(selected_date, datetime.time(CLOSE_HOUR, 0))

    while current_time < closing_time:
        block_start = timezone.make_aware(current_time)
        block_end = block_start + datetime.timedelta(minutes=30)

        # Lấy danh sách lịch hẹn giao nhau với block này
        block_appointments = []
        for a in appointments:
            if a.ngay_gio_bat_dau < block_end and block_start < a.ngay_gio_ket_thuc:
                block_appointments.append(a)

        timeline_blocks.append({
            'time_str': block_start.strftime('%H:%M'),
            'time_label': f"{block_start.strftime('%H:%M')} - {block_end.strftime('%H:%M')}",
            'appointments': block_appointments,
            'count': len(block_appointments)
        })

        current_time += datetime.timedelta(minutes=30)

    return render(request, 'owner/timeline.html', {
        'selected_date': selected_date,
        'timeline_blocks': timeline_blocks,
        'appointments': appointments,
    })


@owner_required
def owner_appointments_list(request):
    """Danh sách và tìm kiếm/lọc toàn bộ lịch hẹn."""
    status_filter = request.GET.get('status', '').strip()
    date_filter = request.GET.get('date', '').strip()
    query = request.GET.get('q', '').strip()

    appointments = LichHen.objects.all().order_by('-ngay_gio_bat_dau')

    if status_filter:
        appointments = appointments.filter(trang_thai=status_filter)
    if date_filter:
        try:
            d = datetime.date.fromisoformat(date_filter)
            appointments = appointments.filter(ngay_gio_bat_dau__date=d)
        except Exception:
            pass
    if query:
        appointments = appointments.filter(
            Q(ten_lien_he__icontains=query) | Q(so_dien_thoai_lien_he__icontains=query) | Q(ma_lich_hen__icontains=query)
        )

    return render(request, 'owner/appointments_list.html', {
        'appointments': appointments,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'query': query,
    })


@owner_required
def owner_appointment_detail(request, pk):
    """Xem chi tiết lịch hẹn, thông tin phân công, thanh toán và các nút cập nhật trạng thái."""
    appointment = get_object_or_404(
        LichHen.objects.prefetch_related('chi_tiet', 'phan_cong__nhan_vien'),
        pk=pk
    )
    from apps.accounts.models import NhanVien
    employees = NhanVien.objects.all()

    return render(request, 'owner/appointment_detail.html', {
        'appointment': appointment,
        'employees': employees,
    })


@owner_required
def owner_update_status(request, pk):
    """
    UC 3.2: Cập nhật trạng thái lịch hẹn:
    - Chờ xác nhận -> Đã xác nhận
    - Đã xác nhận -> Hoàn thành (kích hoạt thanh toán)
    - Hủy (giải phóng khung giờ)
    - Không đến
    """
    appointment = get_object_or_404(LichHen, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = ['Chờ xác nhận', 'Đã xác nhận', 'Hoàn thành', 'Hủy', 'Không đến']

        if new_status in valid_statuses:
            with transaction.atomic():
                old_status = appointment.trang_thai
                appointment.trang_thai = new_status
                if new_status == 'Hủy':
                    appointment.thoi_diem_huy = timezone.now()
                    appointment.tai_khoan_huy = request.user.tai_khoan

                appointment.save()

                # Gửi thông báo đến tài khoản khách hàng nếu có
                if appointment.khach_hang and hasattr(appointment.khach_hang, 'tai_khoan'):
                    send_notification(
                        tai_khoan=appointment.khach_hang.tai_khoan,
                        tieu_de=f'Lịch hẹn {appointment.ma_lich_hen} chuyển sang trạng thái: {new_status}',
                        noi_dung=f'Lịch hẹn của bạn lúc {appointment.ngay_gio_bat_dau.strftime("%H:%M %d/%m/%Y")} đã được cập nhật thành "{new_status}".',
                        loai_thong_bao='Trạng thái',
                        lien_ket='/customer/my-appointments/'
                    )

            messages.success(request, f'Đã cập nhật trạng thái lịch hẹn {appointment.ma_lich_hen} sang "{new_status}".')
        else:
            messages.error(request, 'Trạng thái cập nhật không hợp lệ.')

    return redirect('owner:appointment_detail', pk=pk)


# =========================================================================
# JSON API CHO KHUNG GIỜ (AJAX / VANILLA JS DÙNG TỨC THỜI)
# =========================================================================

def api_available_slots(request):
    """API trả về các khung giờ khả dụng cho ngày và tổng thời lượng yêu cầu."""
    date_str = request.GET.get('date', '').strip()
    duration_str = request.GET.get('duration', '30').strip()
    exclude_id = request.GET.get('exclude_id', None)

    try:
        target_date = datetime.date.fromisoformat(date_str)
        total_duration = int(duration_str)
    except Exception:
        return JsonResponse({'error': 'Tham số ngày hoặc thời lượng không hợp lệ.'}, status=400)

    slots = get_available_slots(target_date, total_duration, exclude_appointment_id=exclude_id)
    return JsonResponse({
        'date': date_str,
        'duration': total_duration,
        'slots': slots
    })
