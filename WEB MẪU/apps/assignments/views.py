from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from apps.accounts.models import NhanVien, TaiKhoan
from apps.accounts.decorators import owner_required, employee_required
from apps.appointments.models import LichHen
from apps.notifications.models import send_notification
from .models import PhanCong


# =========================================================================
# UC5: QUẢN LÝ PHÂN CÔNG NHÂN VIÊN (Dành cho Chủ Tiệm)
# =========================================================================

@owner_required
def owner_assignments_list(request):
    """
    UC 5.1: Danh sách các lịch hẹn cần phân công & tổng quan phân công.
    Lọc các lịch đang Chờ xác nhận hoặc Đã xác nhận.
    """
    appointments = LichHen.objects.filter(
        trang_thai__in=['Chờ xác nhận', 'Đã xác nhận']
    ).prefetch_related('phan_cong__nhan_vien', 'chi_tiet').order_by('ngay_gio_bat_dau')

    employees = NhanVien.objects.all()

    return render(request, 'owner/assignments_list.html', {
        'appointments': appointments,
        'employees': employees,
    })


@owner_required
def owner_assign_staff(request, appointment_pk):
    """
    UC 5.2: Phân công hoặc thay đổi phân công nhân viên kỹ thuật.
    Business Rules:
    - Một nhân viên chỉ phục vụ 1 khách tại 1 thời điểm.
    - Kiểm tra khoảng thời gian dịch vụ: start_A < end_B AND start_B < end_A.
    - Không cho phép trùng lịch.
    - Thông báo cho nhân viên được phân công.
    """
    appointment = get_object_or_404(LichHen, pk=appointment_pk)
    employees = NhanVien.objects.all()

    if appointment.trang_thai in ['Hoàn thành', 'Hủy', 'Không đến']:
        messages.error(request, 'Không thể phân công nhân viên cho lịch hẹn đã hoàn thành hoặc đã hủy.')
        return redirect('owner:appointment_detail', pk=appointment_pk)

    if request.method == 'POST':
        staff_id = request.POST.get('nhan_vien_id')
        if not staff_id:
            messages.error(request, 'Vui lòng chọn nhân viên kỹ thuật.')
            return redirect('owner:appointment_detail', pk=appointment_pk)

        selected_staff = get_object_or_404(NhanVien, pk=staff_id)
        start_A = appointment.ngay_gio_bat_dau
        end_A = appointment.ngay_gio_ket_thuc

        # Kiểm tra trùng lịch của nhân viên được chọn
        active_assignments = PhanCong.objects.filter(
            nhan_vien=selected_staff,
            dang_phu_trach=True,
            trang_thai_tiep_nhan__in=['Chờ phản hồi', 'Đã tiếp nhận'],
            lich_hen__trang_thai__in=['Chờ xác nhận', 'Đã xác nhận']
        ).exclude(lich_hen=appointment).select_related('lich_hen')

        has_conflict = False
        conflict_appointment = None

        for pc in active_assignments:
            start_B = pc.lich_hen.ngay_gio_bat_dau
            end_B = pc.lich_hen.ngay_gio_ket_thuc

            # Hai khoảng thời gian bị trùng khi: start_A < end_B AND start_B < end_A
            if start_A < end_B and start_B < end_A:
                has_conflict = True
                conflict_appointment = pc.lich_hen
                break

        if has_conflict:
            messages.error(
                request,
                f'Nhân viên {selected_staff.ten_nhan_vien} bị trùng lịch với lịch hẹn {conflict_appointment.ma_lich_hen} '
                f'({conflict_appointment.ngay_gio_bat_dau.strftime("%H:%M")} - {conflict_appointment.ngay_gio_ket_thuc.strftime("%H:%M")}). '
                f'Vui lòng chọn nhân viên khác.'
            )
            return redirect('owner:appointment_detail', pk=appointment_pk)

        with transaction.atomic():
            # 1. Hủy phụ trách của phân công cũ (nếu có)
            old_assignment = appointment.phan_cong_hien_tai
            if old_assignment:
                old_assignment.dang_phu_trach = False
                old_assignment.save()

                if old_assignment.nhan_vien != selected_staff:
                    send_notification(
                        tai_khoan=old_assignment.nhan_vien.tai_khoan,
                        tieu_de=f'Thay đổi phân công lịch hẹn {appointment.ma_lich_hen}',
                        noi_dung=f'Chủ tiệm đã chuyển lịch hẹn {appointment.ma_lich_hen} (lúc {appointment.ngay_gio_bat_dau.strftime("%H:%M %d/%m/%Y")}) sang kỹ thuật viên khác.',
                        loai_thong_bao='Phân công',
                        lien_ket='/employee/'
                    )

            # 2. Tạo phân công mới
            new_assignment = PhanCong.objects.create(
                lich_hen=appointment,
                nhan_vien=selected_staff,
                trang_thai_tiep_nhan='Chờ phản hồi',
                dang_phu_trach=True
            )

            # 3. Gửi thông báo đến nhân viên mới
            send_notification(
                tai_khoan=selected_staff.tai_khoan,
                tieu_de=f'Phân công lịch hẹn mới {appointment.ma_lich_hen}',
                noi_dung=f'Bạn được phân công phụ trách lịch hẹn của khách {appointment.ten_lien_he} lúc {appointment.ngay_gio_bat_dau.strftime("%H:%M %d/%m/%Y")}. Vui lòng phản hồi tiếp nhận.',
                loai_thong_bao='Phân công',
                lien_ket=f'/employee/appointments/{appointment.ma_lich_hen}/'
            )

        messages.success(request, f'Đã phân công lịch hẹn cho kỹ thuật viên {selected_staff.ten_nhan_vien}.')
        return redirect('owner:appointment_detail', pk=appointment_pk)

    return redirect('owner:appointment_detail', pk=appointment_pk)


# =========================================================================
# UC2: QUẢN LÝ LỊCH HẸN ĐƯỢC PHÂN CÔNG (Dành cho Nhân Viên)
# =========================================================================

@employee_required
def employee_dashboard(request):
    """UC 2.3: Nhân viên xem danh sách lịch hẹn được phân công cho mình."""
    nhan_vien = request.user.tai_khoan.nhan_vien
    assignments = PhanCong.objects.filter(
        nhan_vien=nhan_vien,
        dang_phu_trach=True
    ).select_related('lich_hen', 'lich_hen__khach_hang').prefetch_related('lich_hen__chi_tiet').order_by('-lich_hen__ngay_gio_bat_dau')

    return render(request, 'employee/dashboard.html', {
        'nhan_vien': nhan_vien,
        'assignments': assignments,
    })


@employee_required
def employee_appointment_detail(request, pk):
    """Nhân viên xem thông tin chi tiết lịch hẹn được phân công."""
    nhan_vien = request.user.tai_khoan.nhan_vien
    appointment = get_object_or_404(LichHen, pk=pk)

    assignment = PhanCong.objects.filter(
        lich_hen=appointment,
        nhan_vien=nhan_vien,
        dang_phu_trach=True
    ).first()

    if not assignment:
        messages.error(request, 'Bạn không được phân công phụ trách lịch hẹn này.')
        return redirect('employee:dashboard')

    return render(request, 'employee/appointment_detail.html', {
        'appointment': appointment,
        'assignment': assignment,
    })


@employee_required
def employee_accept_assignment(request, pk):
    """
    UC 2.1: Nhân viên xác nhận tiếp nhận lịch được phân công.
    Business Rules:
    - Không xác nhận lịch đã hủy.
    - Không xác nhận lại lịch đã xử lý.
    - Tự động chuyển trạng thái lịch sang 'Đã xác nhận' nếu đang 'Chờ xác nhận'.
    """
    nhan_vien = request.user.tai_khoan.nhan_vien
    assignment = get_object_or_404(PhanCong, pk=pk, nhan_vien=nhan_vien, dang_phu_trach=True)
    appointment = assignment.lich_hen

    if appointment.trang_thai in ['Hủy', 'Hoàn thành']:
        messages.error(request, 'Không thể tiếp nhận lịch hẹn đã hoàn thành hoặc đã bị hủy.')
        return redirect('employee:dashboard')

    if assignment.trang_thai_tiep_nhan == 'Đã tiếp nhận':
        messages.info(request, 'Lịch hẹn này đã được bạn tiếp nhận trước đó.')
        return redirect('employee:dashboard')

    with transaction.atomic():
        assignment.trang_thai_tiep_nhan = 'Đã tiếp nhận'
        assignment.thoi_diem_phan_hoi = timezone.now()
        assignment.save()

        # Nếu lịch đang ở trạng thái Chờ xác nhận, chuyển sang Đã xác nhận
        if appointment.trang_thai == 'Chờ xác nhận':
            appointment.trang_thai = 'Đã xác nhận'
            appointment.save()

        # Thông báo cho Chủ Tiệm
        owner_tk = TaiKhoan.objects.filter(vai_tro='Chủ Tiệm').first()
        if owner_tk:
            send_notification(
                tai_khoan=owner_tk,
                tieu_de=f'KTV {nhan_vien.ten_nhan_vien} đã tiếp nhận lịch {appointment.ma_lich_hen}',
                noi_dung=f'Kỹ thuật viên {nhan_vien.ten_nhan_vien} đã xác nhận tiếp nhận phụ trách lịch hẹn lúc {appointment.ngay_gio_bat_dau.strftime("%H:%M %d/%m/%Y")}.',
                loai_thong_bao='Phân công',
                lien_ket=f'/owner/appointments/{appointment.ma_lich_hen}/'
            )

    messages.success(request, f'Bạn đã tiếp nhận phụ trách lịch hẹn {appointment.ma_lich_hen} thành công!')
    return redirect('employee:appointment_detail', pk=appointment.ma_lich_hen)


@employee_required
def employee_reject_assignment(request, pk):
    """
    UC 2.2: Nhân viên từ chối lịch được phân công.
    Business Rules:
    - Từ chối bắt buộc phải nhập lý do.
    - Hủy quyền phụ trách (dang_phu_trach = False).
    - Thông báo khẩn đến Chủ Tiệm để bố trí phân công lại.
    """
    nhan_vien = request.user.tai_khoan.nhan_vien
    assignment = get_object_or_404(PhanCong, pk=pk, nhan_vien=nhan_vien, dang_phu_trach=True)
    appointment = assignment.lich_hen

    if request.method == 'POST':
        ly_do = request.POST.get('ly_do_tu_choi', '').strip()
        if not ly_do:
            messages.error(request, 'Vui lòng nhập lý do từ chối lịch hẹn.')
            return redirect('employee:appointment_detail', pk=appointment.ma_lich_hen)

        with transaction.atomic():
            assignment.trang_thai_tiep_nhan = 'Từ chối'
            assignment.ly_do_tu_choi = ly_do
            assignment.thoi_diem_phan_hoi = timezone.now()
            assignment.dang_phu_trach = False
            assignment.save()

            # Thông báo khẩn cho Chủ Tiệm
            owner_tk = TaiKhoan.objects.filter(vai_tro='Chủ Tiệm').first()
            if owner_tk:
                send_notification(
                    tai_khoan=owner_tk,
                    tieu_de=f'KTV {nhan_vien.ten_nhan_vien} TỪ CHỐI lịch {appointment.ma_lich_hen}',
                    noi_dung=f'Kỹ thuật viên {nhan_vien.ten_nhan_vien} đã từ chối lịch hẹn lúc {appointment.ngay_gio_bat_dau.strftime("%H:%M %d/%m/%Y")}. Lý do: "{ly_do}". Vui lòng phân công lại KTV khác.',
                    loai_thong_bao='Từ chối',
                    lien_ket=f'/owner/appointments/{appointment.ma_lich_hen}/'
                )

        messages.warning(request, f'Bạn đã từ chối lịch hẹn {appointment.ma_lich_hen}. Hệ thống đã gửi thông báo đến Chủ tiệm.')
        return redirect('employee:dashboard')

    return redirect('employee:appointment_detail', pk=appointment.ma_lich_hen)
