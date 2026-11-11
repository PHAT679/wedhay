import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import KhachHang, NhanVien
from apps.appointments.models import ChiTietLichHen, LichHen
from apps.appointments.services import get_available_slots, lock_booking_capacity
from apps.assignments.models import PhanCong
from apps.services.models import DichVu


SPECS = [
    ('0000000001', 'Nguyễn Hồng Nhung', '09:30', 'Úp móng & Thiết kế Nail Art Pastel', 'Đã xác nhận', 'Đã tiếp nhận'),
    ('0000000002', 'Trần Minh Anh', '11:00', 'Sơn Gel cao cấp Hàn Quốc', 'Chờ xác nhận', 'Chờ phản hồi'),
    ('0000000003', 'Lê Hoàng Yến', '13:00', 'Chăm sóc móng & Cắt da cơ bản', 'Chờ xác nhận', 'Chờ phản hồi'),
    ('0000000004', 'Phạm Thị Mai', '15:30', 'Sơn Gel cao cấp Hàn Quốc', 'Hủy', 'Chờ phản hồi'),
    ('0000000005', 'Đỗ Quỳnh Như', '17:00', 'Tháo móng cũ & Dưỡng phục hồi móng Collagen', 'Chờ xác nhận', 'Chờ phản hồi'),
]
MARKER = 'Dữ liệu thử nghiệm nhân viên'


class Command(BaseCommand):
    help = 'Tạo 5 lịch thử nghiệm được đánh dấu cho một nhân viên cụ thể.'

    def add_arguments(self, parser):
        parser.add_argument('--employee', required=True, help='Tên đăng nhập nhân viên')
        parser.add_argument('--date', help='Ngày thử nghiệm YYYY-MM-DD (mặc định tìm ngày phù hợp)')
        parser.add_argument('--start', type=int, default=1, help='Số bắt đầu của bộ 5 mã thử nghiệm')

    def handle(self, *args, **options):
        employee = NhanVien.objects.filter(tai_khoan__user__username=options['employee'], tai_khoan__vai_tro='Nhân Viên').first()
        if not employee:
            raise CommandError('Không tìm thấy nhân viên được chỉ định.')
        try:
            requested_day = datetime.date.fromisoformat(options['date']) if options['date'] else None
        except ValueError:
            raise CommandError('Ngày phải có dạng YYYY-MM-DD.')
        today = timezone.localdate()
        start = options['start']
        if not 1 <= start <= 995:
            raise CommandError('Số bắt đầu phải từ 1 đến 995.')
        specs = [(f'{start + index:010d}', *spec[1:]) for index, spec in enumerate(SPECS)]
        ids = [spec[0] for spec in specs]

        with transaction.atomic():
            lock_booking_capacity()
            existing = list(LichHen.objects.filter(pk__in=ids))
            if existing:
                if len(existing) != 5 or any(not PhanCong.objects.filter(lich_hen=record, nhan_vien=employee, dang_phu_trach=True).exists() or not record.chi_tiet.filter(ghi_chu_thuc_hien=MARKER).exists() for record in existing):
                    raise CommandError('Mã đã tồn tại hoặc bộ dữ liệu không đầy đủ; dừng để tránh ghi đè dữ liệu.')
                dates = {timezone.localtime(record.ngay_gio_bat_dau).date() for record in existing}
                if len(dates) != 1 or (requested_day and requested_day not in dates):
                    raise CommandError('Các lịch thử nghiệm hiện có không khớp ngày yêu cầu.')
                self.stdout.write(f'Đã tồn tại: 5; tạo mới: 0; ngày: {dates.pop().isoformat()}')
                return

            services = {}
            for spec in specs:
                name = spec[3]
                if name not in services:
                    service = DichVu.objects.filter(ten_dich_vu=name, da_xoa=False).first()
                    if not service:
                        raise CommandError(f'Thiếu dịch vụ: {name}')
                    services[name] = service
            customer_ids = [f'TSTKH{i:03}' for i in range(start, start + 5)]
            assignment_ids = [f'TSTPC{i:03}' for i in range(start, start + 5)]
            phones = [f'0990000{i:03}' for i in range(start, start + 5)]
            if KhachHang.objects.filter(pk__in=customer_ids).exists() or KhachHang.objects.filter(so_dien_thoai__in=phones).exists() or PhanCong.objects.filter(pk__in=assignment_ids).exists():
                raise CommandError('Mã hồ sơ hoặc số điện thoại thử nghiệm đã tồn tại; không ghi đè.')

            def available(day):
                intervals = []
                for spec in specs:
                    start = timezone.make_aware(datetime.datetime.combine(day, datetime.time.fromisoformat(spec[2])))
                    end = start + datetime.timedelta(minutes=services[spec[3]].thoi_luong)
                    if any(start < previous_end and previous_start < end for previous_start, previous_end in intervals):
                        return False
                    intervals.append((start, end))
                    slots = get_available_slots(day, services[spec[3]].thoi_luong)
                    if not any(slot['time_str'] == spec[2] and slot['available'] for slot in slots):
                        return False
                existing_assignments = PhanCong.objects.filter(nhan_vien=employee, dang_phu_trach=True, lich_hen__trang_thai__in=['Chờ xác nhận', 'Đã xác nhận'], lich_hen__ngay_gio_bat_dau__date=day).select_related('lich_hen').prefetch_related('lich_hen__chi_tiet')
                return not any(start < assignment.lich_hen.ngay_gio_ket_thuc and assignment.lich_hen.ngay_gio_bat_dau < end for assignment in existing_assignments for start, end in intervals)

            days = [requested_day] if requested_day else [today + datetime.timedelta(days=i) for i in range(31)]
            chosen_day = next((day for day in days if today <= day <= today + datetime.timedelta(days=30) and available(day)), None)
            if chosen_day is None:
                raise CommandError('Không có ngày phù hợp trong phạm vi đặt lịch hoặc ngày yêu cầu không khả dụng.')

            for index, (pk, name, start_time, service_name, status, receipt) in enumerate(specs):
                service = services[service_name]
                customer = KhachHang.objects.create(ma_khach_hang=customer_ids[index], ho_ten=f'[TEST] {name}', so_dien_thoai=phones[index])
                appointment = LichHen(ma_lich_hen=pk, khach_hang=customer, ngay_gio_bat_dau=timezone.make_aware(datetime.datetime.combine(chosen_day, datetime.time.fromisoformat(start_time))), ten_lien_he=name, so_dien_thoai_lien_he=phones[index], trang_thai=status)
                appointment.full_clean()
                appointment.save(force_insert=True)
                ChiTietLichHen.objects.create(lich_hen=appointment, dich_vu=service, ten_dich_vu_dat=service.ten_dich_vu, don_gia_dat=service.gia_tien, thoi_luong_dat=service.thoi_luong, ghi_chu_thuc_hien=MARKER)
                PhanCong.objects.create(ma_phan_cong=assignment_ids[index], lich_hen=appointment, nhan_vien=employee, trang_thai_tiep_nhan=receipt, dang_phu_trach=True)
        self.stdout.write(f'Tạo mới: 5; đã tồn tại: 0; nhân viên: {employee.tai_khoan.user.username}; ngày: {chosen_day.isoformat()}')
