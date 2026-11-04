from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


phone_validator = RegexValidator(
    regex=r'^\d{10}$',
    message='Số điện thoại phải đúng 10 chữ số.'
)


def get_next_id(model_class, prefix, field_name='pk'):
    """Tự động sinh mã tự tăng dạng KH001, TK001, NV001..."""
    count = model_class.objects.count() + 1
    new_id = f"{prefix}{count:03d}"
    while model_class.objects.filter(**{field_name: new_id}).exists():
        count += 1
        new_id = f"{prefix}{count:03d}"
    return new_id


class KhachHang(models.Model):
    ma_khach_hang = models.CharField(max_length=10, primary_key=True, verbose_name='Mã khách hàng')
    ho_ten = models.CharField(max_length=50, verbose_name='Họ và tên')
    so_dien_thoai = models.CharField(max_length=10, validators=[phone_validator], verbose_name='Số điện thoại')
    link_facebook = models.CharField(max_length=255, blank=True, null=True, verbose_name='Link Facebook')
    link_zalo = models.CharField(max_length=255, blank=True, null=True, verbose_name='Link Zalo')

    class Meta:
        db_table = 'KhachHang'
        verbose_name = 'Khách Hàng'
        verbose_name_plural = 'Khách Hàng'
        ordering = ['ma_khach_hang']

    def __str__(self):
        return f"{self.ho_ten} ({self.so_dien_thoai})"

    def save(self, *args, **kwargs):
        if not self.ma_khach_hang:
            self.ma_khach_hang = get_next_id(KhachHang, 'KH', 'ma_khach_hang')
        super().save(*args, **kwargs)


class TaiKhoan(models.Model):
    VAI_TRO_CHOICES = [
        ('Chủ Tiệm', 'Chủ Tiệm'),
        ('Nhân Viên', 'Nhân Viên'),
        ('Khách Hàng', 'Khách Hàng'),
    ]

    ma_tai_khoan = models.CharField(max_length=10, primary_key=True, verbose_name='Mã tài khoản')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tai_khoan', verbose_name='Tài khoản User')
    vai_tro = models.CharField(max_length=20, choices=VAI_TRO_CHOICES, verbose_name='Vai trò')
    khach_hang = models.OneToOneField(
        KhachHang, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tai_khoan', verbose_name='Khách hàng liên kết'
    )

    class Meta:
        db_table = 'TaiKhoan'
        verbose_name = 'Tài Khoản'
        verbose_name_plural = 'Tài Khoản'

    def __str__(self):
        return f"{self.user.username} - {self.vai_tro}"

    @property
    def ten_dang_nhap(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.ma_tai_khoan:
            self.ma_tai_khoan = get_next_id(TaiKhoan, 'TK', 'ma_tai_khoan')
        super().save(*args, **kwargs)


class NhanVien(models.Model):
    ma_nhan_vien = models.CharField(max_length=10, primary_key=True, verbose_name='Mã nhân viên')
    tai_khoan = models.OneToOneField(TaiKhoan, on_delete=models.CASCADE, related_name='nhan_vien', verbose_name='Tài khoản')
    ten_nhan_vien = models.CharField(max_length=50, verbose_name='Tên nhân viên')

    class Meta:
        db_table = 'NhanVien'
        verbose_name = 'Nhân Viên'
        verbose_name_plural = 'Nhân Viên'
        ordering = ['ma_nhan_vien']

    def __str__(self):
        return f"{self.ten_nhan_vien} ({self.ma_nhan_vien})"

    def save(self, *args, **kwargs):
        if not self.ma_nhan_vien:
            self.ma_nhan_vien = get_next_id(NhanVien, 'NV', 'ma_nhan_vien')
        super().save(*args, **kwargs)
