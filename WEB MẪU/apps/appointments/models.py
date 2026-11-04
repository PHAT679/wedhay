from datetime import timedelta
from django.db import models
from django.utils import timezone
from apps.accounts.models import KhachHang, TaiKhoan, phone_validator, get_next_id
from apps.services.models import DichVu


class LichHen(models.Model):
    TRANG_THAI_CHOICES = [
        ('Chờ xác nhận', 'Chờ xác nhận'),
        ('Đã xác nhận', 'Đã xác nhận'),
        ('Hoàn thành', 'Hoàn thành'),
        ('Hủy', 'Hủy'),
        ('Không đến', 'Không đến'),
    ]

    ma_lich_hen = models.CharField(max_length=10, primary_key=True, verbose_name='Mã lịch hẹn')
    khach_hang = models.ForeignKey(KhachHang, on_delete=models.PROTECT, related_name='lich_hen', verbose_name='Khách hàng')
    tai_khoan_huy = models.ForeignKey(
        TaiKhoan, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='lich_hen_da_huy', verbose_name='Tài khoản hủy'
    )
    ngay_gio_bat_dau = models.DateTimeField(verbose_name='Ngày giờ bắt đầu')
    ten_lien_he = models.CharField(max_length=100, verbose_name='Tên liên hệ')
    so_dien_thoai_lien_he = models.CharField(
        max_length=10, validators=[phone_validator], verbose_name='SĐT liên hệ'
    )
    trang_thai = models.CharField(
        max_length=30, choices=TRANG_THAI_CHOICES, default='Chờ xác nhận',
        verbose_name='Trạng thái'
    )
    thoi_diem_huy = models.DateTimeField(null=True, blank=True, verbose_name='Thời điểm hủy')
    thoi_diem_tao = models.DateTimeField(auto_now_add=True, verbose_name='Thời điểm tạo')

    class Meta:
        db_table = 'LichHen'
        verbose_name = 'Lịch Hẹn'
        verbose_name_plural = 'Lịch Hẹn'
        ordering = ['-ngay_gio_bat_dau']

    def __str__(self):
        return f"{self.ma_lich_hen} - {self.ten_lien_he} ({self.ngay_gio_bat_dau.strftime('%d/%m/%Y %H:%M')}) - {self.trang_thai}"

    @property
    def tong_tien(self):
        """Tính tổng số tiền dựa trên đơn giá thời điểm đặt (ChiTietLichHen)."""
        return sum(ct.don_gia_dat for ct in self.chi_tiet.all())

    @property
    def tong_thoi_luong(self):
        """Tính tổng thời lượng dịch vụ dựa trên thời lượng lúc đặt (phút)."""
        return sum(ct.thoi_luong_dat for ct in self.chi_tiet.all())

    @property
    def ngay_gio_ket_thuc(self):
        """Thời điểm kết thúc ước tính = Bắt đầu + Tổng thời lượng."""
        return self.ngay_gio_bat_dau + timedelta(minutes=self.tong_thoi_luong)

    @property
    def can_cancel(self):
        """Kiểm tra xem có được hủy lịch không (chỉ hủy được khi Chờ xác nhận hoặc Đã xác nhận)."""
        return self.trang_thai in ['Chờ xác nhận', 'Đã xác nhận']

    @property
    def is_less_than_two_hours(self):
        """Kiểm tra thời gian còn lại đến giờ hẹn có dưới 2 tiếng không."""
        now = timezone.now()
        diff = self.ngay_gio_bat_dau - now
        return diff.total_seconds() < 2 * 3600

    @property
    def phan_cong_hien_tai(self):
        """Lấy phân công đang phụ trách hiện tại (DangPhuTrach = True)."""
        return self.phan_cong.filter(dang_phu_trach=True).first()

    def save(self, *args, **kwargs):
        if not self.ma_lich_hen:
            self.ma_lich_hen = get_next_id(LichHen, 'LH', 'ma_lich_hen')
        super().save(*args, **kwargs)


class ChiTietLichHen(models.Model):
    lich_hen = models.ForeignKey(LichHen, on_delete=models.CASCADE, related_name='chi_tiet', verbose_name='Lịch hẹn')
    dich_vu = models.ForeignKey(DichVu, on_delete=models.PROTECT, related_name='chi_tiet_lich_hen', verbose_name='Dịch vụ gốc')
    ten_dich_vu_dat = models.CharField(max_length=60, verbose_name='Tên dịch vụ lúc đặt')
    don_gia_dat = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Đơn giá lúc đặt')
    thoi_luong_dat = models.SmallIntegerField(verbose_name='Thời lượng lúc đặt (phút)')
    ghi_chu_thuc_hien = models.CharField(max_length=255, blank=True, null=True, verbose_name='Ghi chú thực hiện')

    class Meta:
        db_table = 'ChiTietLichHen'
        verbose_name = 'Chi Tiết Lịch Hẹn'
        verbose_name_plural = 'Chi Tiết Lịch Hẹn'
        unique_together = ('lich_hen', 'dich_vu')

    def __str__(self):
        return f"{self.lich_hen.ma_lich_hen} - {self.ten_dich_vu_dat} ({self.don_gia_dat:,.0f} đ)"
