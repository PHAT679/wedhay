import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import KhachHang, NhanVien
from apps.appointments.models import ChiTietLichHen, LichHen
from apps.appointments.services import get_available_slots, lock_booking_capacity
from apps.assignments.models import PhanCong
from apps.services.models import DichVu


MARKER = 'Dữ liệu thử nghiệm timeline chủ tiệm'
SPECS = [
    ('Nguyễn Hồng Nhung', '09:00', 'Chờ xác nhận', 0),
    ('Trần Minh Anh', '10:00', 'Đã xác nhận', 0),
    ('Lê Hoàng Yến', '10:00', 'Chờ xác nhận', 1),
    ('Phạm Thị Mai', '11:00', 'Hủy', 0),
]


class Command(BaseCommand):
    help = 'Tạo một bộ bốn lịch thử nghiệm cho timeline chủ tiệm.'

    def handle(self, *args, **options):
        with transaction.atomic():
            lock_booking_capacity()
            existing = list(LichHen.objects.filter(chi_tiet__ghi_chu_thuc_hien=MARKER).distinct())
            if existing:
                if len(existing) != len(SPECS):
                    raise CommandError('Bộ thử nghiệm hiện có không đầy đủ; không tạo thêm.')
                self.stdout.write('Đã tồn tại: ' + ', '.join(sorted(a.pk for a in existing)))
                return

            staff = list(NhanVien.objects.order_by('ma_nhan_vien')[:2])
            if len(staff) < 2:
                raise CommandError('Cần ít nhất hai nhân viên để phục vụ đồng thời.')
            service = DichVu.objects.filter(da_xoa=False, thoi_luong=30).order_by('ma_dich_vu').first()
            if not service:
                raise CommandError('Không tìm thấy dịch vụ 30 phút đang hoạt động.')
            used_ids = set(LichHen.objects.values_list('pk', flat=True))
            available_ids = [f'LH{i:03d}' for i in range(101, 1000) if f'LH{i:03d}' not in used_ids][:4]
            if len(available_ids) != 4:
                raise CommandError('Không còn đủ mã LHxxx.')
            customer_ids = [f'TLKH{i:03d}' for i in range(1, 5)]
            assignment_ids = [f'TLPC{i:03d}' for i in range(1, 5)]
            phones = [f'098999{i:04d}' for i in range(1, 5)]
            if KhachHang.objects.filter(pk__in=customer_ids).exists() or KhachHang.objects.filter(so_dien_thoai__in=phones).exists() or PhanCong.objects.filter(pk__in=assignment_ids).exists():
                raise CommandError('Mã khách hàng, phân công hoặc số điện thoại thử nghiệm đã tồn tại.')

            today = timezone.localdate()
            day = None
            for offset in range(1, 31):
                candidate = today + datetime.timedelta(days=offset)
                if LichHen.objects.filter(ngay_gio_bat_dau__date=candidate).exists():
                    continue
                available = {slot['time_str']: slot['available'] for slot in get_available_slots(candidate, service.thoi_luong)}
                if all(available.get(time) for _, time, _, _ in SPECS):
                    day = candidate
                    break
            if day is None:
                raise CommandError('Không tìm thấy ngày trống phù hợp trong 30 ngày tới.')

            for i, (name, time, status, staff_index) in enumerate(SPECS):
                if status != 'Hủy':
                    available = {slot['time_str']: slot['available'] for slot in get_available_slots(day, service.thoi_luong)}
                    if not available.get(time):
                        raise CommandError('Không đủ sức chứa tại ' + time)
                customer = KhachHang.objects.create(ma_khach_hang=customer_ids[i], ho_ten='[TEST] ' + name, so_dien_thoai=phones[i])
                appointment = LichHen(
                    ma_lich_hen=available_ids[i], khach_hang=customer,
                    ngay_gio_bat_dau=timezone.make_aware(datetime.datetime.combine(day, datetime.time.fromisoformat(time))),
                    ten_lien_he=name, so_dien_thoai_lien_he=phones[i], trang_thai=status,
                )
                appointment.full_clean()
                appointment.save(force_insert=True)
                ChiTietLichHen.objects.create(lich_hen=appointment, dich_vu=service, ten_dich_vu_dat=service.ten_dich_vu, don_gia_dat=service.gia_tien, thoi_luong_dat=service.thoi_luong, ghi_chu_thuc_hien=MARKER)
                PhanCong.objects.create(ma_phan_cong=assignment_ids[i], lich_hen=appointment, nhan_vien=staff[staff_index], trang_thai_tiep_nhan='Đã tiếp nhận' if status == 'Đã xác nhận' else 'Chờ phản hồi')
        self.stdout.write(f'Tạo mới: 4; ngày: {day.isoformat()}; mã: {", ".join(available_ids)}; dịch vụ: {service.ten_dich_vu}')
