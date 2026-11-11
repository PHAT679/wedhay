from django.db import models
from apps.accounts.models import TaiKhoan, get_next_id


class ThongBao(models.Model):
    LOAI_THONG_BAO_CHOICES = [
        ('Lịch mới', 'Lịch mới'),
        ('Đổi lịch', 'Đổi lịch'),
        ('Hủy lịch', 'Hủy lịch'),
        ('Phân công', 'Phân công'),
        ('Từ chối', 'Từ chối'),
        ('Trạng thái', 'Trạng thái'),
        ('Hệ thống', 'Hệ thống'),
    ]

    ma_thong_bao = models.CharField(max_length=10, primary_key=True, verbose_name='Mã thông báo')
    tai_khoan = models.ForeignKey(TaiKhoan, on_delete=models.CASCADE, related_name='thong_bao', verbose_name='Tài khoản nhận')
    tieu_de = models.CharField(max_length=150, verbose_name='Tiêu đề')
    noi_dung = models.TextField(verbose_name='Nội dung chi tiết')
    loai_thong_bao = models.CharField(max_length=50, choices=LOAI_THONG_BAO_CHOICES, verbose_name='Loại thông báo')
    lien_ket = models.CharField(max_length=255, blank=True, null=True, verbose_name='Đường dẫn liên kết')
    da_doc = models.BooleanField(default=False, verbose_name='Đã đọc')
    thoi_diem_tao = models.DateTimeField(auto_now_add=True, verbose_name='Thời điểm tạo')

    class Meta:
        db_table = 'ThongBao'
        verbose_name = 'Thông Báo'
        verbose_name_plural = 'Thông Báo'
        ordering = ['-thoi_diem_tao']

    def __str__(self):
        return f"[{self.loai_thong_bao}] {self.tieu_de} -> {self.tai_khoan.ten_dang_nhap}"

    def save(self, *args, **kwargs):
        if not self.ma_thong_bao:
            self.ma_thong_bao = get_next_id(ThongBao, 'TB', 'ma_thong_bao')
        super().save(*args, **kwargs)


def send_notification(tai_khoan, tieu_de, noi_dung, loai_thong_bao='Hệ thống', lien_ket=None):
    """Hàm tiện ích tạo thông báo lưu trực tiếp vào CSDL."""
    if not tai_khoan:
        return None
    return ThongBao.objects.create(
        tai_khoan=tai_khoan,
        tieu_de=tieu_de,
        noi_dung=noi_dung,
        loai_thong_bao=loai_thong_bao,
        lien_ket=lien_ket
    )
