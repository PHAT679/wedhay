from django.db import models
from apps.accounts.models import NhanVien, get_next_id
from apps.appointments.models import LichHen


class PhanCong(models.Model):
    TRANG_THAI_CHOICES = [
        ('Chờ phản hồi', 'Chờ phản hồi'),
        ('Đã tiếp nhận', 'Đã tiếp nhận'),
        ('Từ chối', 'Từ chối'),
    ]

    ma_phan_cong = models.CharField(max_length=10, primary_key=True, verbose_name='Mã phân công')
    lich_hen = models.ForeignKey(LichHen, on_delete=models.CASCADE, related_name='phan_cong', verbose_name='Lịch hẹn')
    nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE, related_name='phan_cong', verbose_name='Nhân viên kỹ thuật')
    thoi_diem_phan_cong = models.DateTimeField(auto_now_add=True, verbose_name='Thời điểm phân công')
    trang_thai_tiep_nhan = models.CharField(
        max_length=20, choices=TRANG_THAI_CHOICES, default='Chờ phản hồi',
        verbose_name='Trạng thái tiếp nhận'
    )
    ly_do_tu_choi = models.CharField(max_length=250, blank=True, null=True, verbose_name='Lý do từ chối')
    thoi_diem_phan_hoi = models.DateTimeField(null=True, blank=True, verbose_name='Thời điểm phản hồi')
    dang_phu_trach = models.BooleanField(default=True, verbose_name='Đang phụ trách')

    class Meta:
        db_table = 'PhanCong'
        verbose_name = 'Phân Công'
        verbose_name_plural = 'Phân Công'
        ordering = ['-thoi_diem_phan_cong']
        constraints = [
            models.UniqueConstraint(
                fields=['lich_hen'],
                condition=models.Q(dang_phu_trach=True),
                name='unique_active_assignment_per_appointment'
            )
        ]

    def __str__(self):
        return f"{self.ma_phan_cong}: {self.nhan_vien.ten_nhan_vien} -> {self.lich_hen.ma_lich_hen} ({self.trang_thai_tiep_nhan})"

    def save(self, *args, **kwargs):
        if not self.ma_phan_cong:
            self.ma_phan_cong = get_next_id(PhanCong, 'PC', 'ma_phan_cong')
        super().save(*args, **kwargs)
