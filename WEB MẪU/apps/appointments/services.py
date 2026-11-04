import datetime
from django.utils import timezone
from django.db.models import Q
from apps.accounts.models import NhanVien
from apps.appointments.models import LichHen

OPEN_HOUR = 9
CLOSE_HOUR = 19
LATEST_START_HOUR = 17


def get_available_slots(target_date, total_duration_minutes, exclude_appointment_id=None):
    """
    Tính toán danh sách các khung giờ 30 phút có thể tiếp nhận lịch hẹn.
    Quy tắc:
    - Giờ mở cửa: 09:00 - 19:00
    - Giờ bắt đầu muộn nhất: 17:00
    - start_time + total_duration <= 19:00
    - Mỗi block 30 phút nằm trong khoảng dịch vụ đều phải có: số lịch trùng < tổng số thợ
    - Nếu là ngày hôm nay: giờ bắt đầu phải sau thời điểm hiện tại ít nhất 30 phút
    """
    total_staff = NhanVien.objects.count()
    if total_staff == 0:
        total_staff = 3  # Giá trị mặc định tối thiểu

    # Lấy toàn bộ các lịch hẹn đang hoạt động trong ngày mục tiêu
    day_start = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time(OPEN_HOUR, 0)))
    day_end = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time(CLOSE_HOUR, 0)))

    active_appointments_qs = LichHen.objects.filter(
        ngay_gio_bat_dau__date=target_date,
        trang_thai__in=['Chờ xác nhận', 'Đã xác nhận']
    ).prefetch_related('chi_tiet')

    if exclude_appointment_id:
        active_appointments_qs = active_appointments_qs.exclude(pk=exclude_appointment_id)

    # Chuyển thành danh sách khoảng thời gian [start, end]
    busy_intervals = []
    for lh in active_appointments_qs:
        busy_intervals.append((lh.ngay_gio_bat_dau, lh.ngay_gio_ket_thuc))

    now = timezone.now()
    available_slots = []

    # Duyệt qua các mốc 30 phút từ 09:00 đến 17:00
    current_time = datetime.datetime.combine(target_date, datetime.time(OPEN_HOUR, 0))
    latest_start = datetime.datetime.combine(target_date, datetime.time(LATEST_START_HOUR, 0))
    closing_time = datetime.datetime.combine(target_date, datetime.time(CLOSE_HOUR, 0))

    while current_time <= latest_start:
        slot_start = timezone.make_aware(current_time)
        slot_end = slot_start + datetime.timedelta(minutes=total_duration_minutes)

        # 1. Ràng buộc: slot_end không được vượt quá giờ đóng cửa (19:00)
        aware_close = timezone.make_aware(closing_time)
        if slot_end > aware_close:
            current_time += datetime.timedelta(minutes=30)
            continue

        # 2. Ràng buộc: nếu là ngày hiện tại thì phải cách hiện tại ít nhất 30 phút
        if slot_start <= now + datetime.timedelta(minutes=30):
            available_slots.append({
                'time_str': slot_start.strftime('%H:%M'),
                'datetime': slot_start,
                'available': False,
                'reason': 'Đã quá giờ hẹn trong ngày'
            })
            current_time += datetime.timedelta(minutes=30)
            continue

        # 3. Ràng buộc: kiểm tra mọi block 30 phút trong khoảng [slot_start, slot_end]
        is_slot_valid = True
        sub_check = slot_start
        while sub_check < slot_end:
            sub_next = sub_check + datetime.timedelta(minutes=30)
            # Đếm số lịch trùng tại block này: start_A < end_B AND start_B < end_A
            overlap_count = 0
            for busy_start, busy_end in busy_intervals:
                if busy_start < sub_next and sub_check < busy_end:
                    overlap_count += 1

            if overlap_count >= total_staff:
                is_slot_valid = False
                break
            sub_check = sub_next

        available_slots.append({
            'time_str': slot_start.strftime('%H:%M'),
            'datetime': slot_start,
            'available': is_slot_valid,
            'reason': '' if is_slot_valid else 'Đã kín chỗ trong khung giờ này'
        })

        current_time += datetime.timedelta(minutes=30)

    return available_slots
