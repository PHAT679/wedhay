from django.db import models
from django.core.validators import MinValueValidator
from apps.accounts.models import get_next_id
from apps.appointments.models import LichHen


class GiaoDich(models.Model):
    PHUONG_THUC_CHOICES = [
        ('Tiền Mặt', 'Tiền Mặt'),
        ('QR', 'Chuyển khoản QR'),
    ]

    TRANG_THAI_CHOICES = [
        ('Thành công', 'Thành công'),
        ('Thất bại', 'Thất bại'),
    ]

    ma_giao_dich = models.CharField(max_length=10, primary_key=True, verbose_name='Mã giao dịch')
    lich_hen = models.OneToOneField(
        LichHen, on_delete=models.CASCADE, related_name='giao_dich',
        verbose_name='Lịch hẹn thanh toán'
    )
    so_tien = models.DecimalField(
        max_digits=12, decimal_places=0,
        validators=[MinValueValidator(1, message='Số tiền thanh toán phải lớn hơn 0.')],
        verbose_name='Số tiền (VNĐ)'
    )
    phuong_thuc = models.CharField(max_length=20, choices=PHUONG_THUC_CHOICES, verbose_name='Phương thức thanh toán')
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, default='Thành công', verbose_name='Trạng thái')
    thoi_diem_giao_dich = models.DateTimeField(auto_now_add=True, verbose_name='Thời điểm giao dịch')
    ma_tham_chieu = models.CharField(max_length=100, blank=True, null=True, verbose_name='Mã tham chiếu / Nội dung CK')

    class Meta:
        db_table = 'GiaoDich'
        verbose_name = 'Giao Dịch'
        verbose_name_plural = 'Giao Dịch'
        ordering = ['-thoi_diem_giao_dich']

    def __str__(self):
        return f"{self.ma_giao_dich} - {self.lich_hen.ma_lich_hen}: {self.so_tien:,.0f} đ ({self.phuong_thuc})"

    def save(self, *args, **kwargs):
        if not self.ma_giao_dich:
            self.ma_giao_dich = get_next_id(GiaoDich, 'GD', 'ma_giao_dich')
        super().save(*args, **kwargs)
