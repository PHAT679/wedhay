from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from apps.accounts.models import get_next_id

VALID_DURATIONS = [30, 60, 90, 120, 150, 180]


def validate_thoi_luong(value):
    if value not in VALID_DURATIONS:
        raise ValidationError(f'Thời lượng thực hiện phải là một trong các giá trị: {", ".join(str(d) for d in VALID_DURATIONS)} phút.')


class DichVu(models.Model):
    THOI_LUONG_CHOICES = [
        (30, '30 phút'),
        (60, '60 phút'),
        (90, '90 phút (1h30)'),
        (120, '120 phút (2h)'),
        (150, '150 phút (2h30)'),
        (180, '180 phút (3h)'),
    ]

    ma_dich_vu = models.CharField(max_length=10, primary_key=True, verbose_name='Mã dịch vụ')
    ten_dich_vu = models.CharField(max_length=60, unique=True, verbose_name='Tên dịch vụ')
    gia_tien = models.DecimalField(
        max_digits=12, decimal_places=0,
        validators=[MinValueValidator(1, message='Giá tiền phải là số nguyên dương lớn hơn 0.')],
        verbose_name='Giá tiền (VNĐ)'
    )
    thoi_luong = models.SmallIntegerField(
        choices=THOI_LUONG_CHOICES,
        validators=[validate_thoi_luong],
        verbose_name='Thời lượng (phút)'
    )
    ghi_chu = models.CharField(max_length=255, blank=True, null=True, verbose_name='Ghi chú')
    da_xoa = models.BooleanField(default=False, verbose_name='Đã xóa mềm')

    class Meta:
        db_table = 'DichVu'
        verbose_name = 'Dịch Vụ'
        verbose_name_plural = 'Dịch Vụ'
        ordering = ['ma_dich_vu']

    def __str__(self):
        return f"{self.ten_dich_vu} - {self.gia_tien:,.0f} đ ({self.thoi_luong}p)"

    def clean(self):
        super().clean()
        if self.gia_tien is not None and self.gia_tien <= 0:
            raise ValidationError({'gia_tien': 'Giá tiền phải lớn hơn 0.'})
        if self.thoi_luong not in VALID_DURATIONS:
            raise ValidationError({'thoi_luong': f'Thời lượng phải thuộc {VALID_DURATIONS}.'})

    def save(self, *args, **kwargs):
        if not self.ma_dich_vu:
            self.ma_dich_vu = get_next_id(DichVu, 'DV', 'ma_dich_vu')
        self.full_clean()
        super().save(*args, **kwargs)
