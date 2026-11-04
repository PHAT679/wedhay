from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import KhachHang, phone_validator


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'auth-control',
            'placeholder': 'Nhập tên đăng nhập hoặc email',
            'id': 'id_username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'auth-control',
            'placeholder': 'Nhập mật khẩu',
            'id': 'id_password',
            'autocomplete': 'current-password',
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'id': 'id_remember_me'})
    )


class RegisterForm(forms.Form):
    ho_ten = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'auth-control',
            'placeholder': 'Nhập họ và tên đầy đủ',
        })
    )
    so_dien_thoai = forms.CharField(
        max_length=10,
        required=True,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'auth-control',
            'placeholder': 'Nhập số điện thoại (10 chữ số)',
        })
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'auth-control',
            'placeholder': 'Chọn tên đăng nhập',
        })
    )
    password = forms.CharField(
        min_length=6,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'auth-control',
            'placeholder': 'Mật khẩu tối thiểu 6 ký tự',
            'id': 'id_reg_password',
        })
    )

    def clean_so_dien_thoai(self):
        sdt = self.cleaned_data['so_dien_thoai'].strip()
        if not sdt.isdigit() or len(sdt) != 10:
            raise ValidationError('Số điện thoại phải gồm đúng 10 chữ số.')
        return sdt

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('Tên đăng nhập này đã được sử dụng.')
        return username


class KhachHangForm(forms.ModelForm):
    class Meta:
        model = KhachHang
        fields = ['ho_ten', 'so_dien_thoai', 'link_facebook', 'link_zalo']
        widgets = {
            'ho_ten': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập họ tên khách hàng'}),
            'so_dien_thoai': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số điện thoại 10 số'}),
            'link_facebook': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Link trang cá nhân Facebook (nếu có)'}),
            'link_zalo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số điện thoại hoặc link Zalo'}),
        }

    def clean_so_dien_thoai(self):
        sdt = self.cleaned_data['so_dien_thoai'].strip()
        if not sdt.isdigit() or len(sdt) != 10:
            raise ValidationError('Số điện thoại phải gồm đúng 10 chữ số.')
        return sdt
