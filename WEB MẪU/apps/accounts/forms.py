from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import KhachHang, phone_validator


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'auth-control',
            'placeholder': 'Nhập tên tài khoản',
            'id': 'id_username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        required=False,
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
        error_messages={'required': 'Vui lòng nhập đầy đủ thông tin'},
        widget=forms.TextInput(attrs={
            'class': 'auth-control',
            'placeholder': 'Nhập họ và tên đầy đủ',
            'id': 'id_ho_ten',
            'autocomplete': 'name',
        })
    )
    so_dien_thoai = forms.CharField(
        max_length=10,
        required=True,
        error_messages={'required': 'Vui lòng nhập đầy đủ thông tin'},
        widget=forms.TextInput(attrs={
            'class': 'auth-control',
            'placeholder': 'Nhập số điện thoại',
            'id': 'id_so_dien_thoai',
            'autocomplete': 'tel',
        })
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        error_messages={'required': 'Vui lòng nhập đầy đủ thông tin'},
        widget=forms.TextInput(attrs={
            'class': 'auth-control',
            'placeholder': 'Chọn tên đăng nhập',
            'id': 'id_username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        min_length=6,
        required=True,
        error_messages={
            'required': 'Vui lòng nhập đầy đủ thông tin',
            'min_length': 'Mật khẩu tối thiểu 6 kí tự',
        },
        widget=forms.PasswordInput(attrs={
            'class': 'auth-control',
            'placeholder': 'Nhập mật khẩu',
            'id': 'id_password',
            'autocomplete': 'new-password',
        })
    )

    def clean_so_dien_thoai(self):
        sdt = self.cleaned_data.get('so_dien_thoai', '').strip()
        if not sdt.isdigit() or len(sdt) != 10:
            raise ValidationError('Số điện thoại không hợp lệ')
        khach_hang = KhachHang.objects.filter(so_dien_thoai=sdt).first()
        if khach_hang and hasattr(khach_hang, 'tai_khoan'):
            raise ValidationError('Số điện thoại đã được liên kết với tài khoản khác.')
        return sdt

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('Tên đăng nhập đã tồn tại, vui lòng chọn tên khác.')
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


class DichVuNhapHoacChonField(forms.ModelChoiceField):
    def to_python(self, value):
        if value not in self.empty_values:
            service = self.queryset.filter(ten_dich_vu=value).first()
            if service is not None:
                return service
        return super().to_python(value)


class KhachHangUpdateForm(KhachHangForm):
    lien_ket = forms.CharField(required=False, max_length=255)
    dich_vu_truc_tiep = forms.ModelChoiceField(queryset=None, required=False, empty_label='Chọn dịch vụ')

    class Meta(KhachHangForm.Meta):
        fields = ['ho_ten', 'so_dien_thoai', 'dich_vu_truc_tiep']

    def __init__(self, *args, **kwargs):
        from apps.services.models import DichVu
        from django.db.models import Q
        super().__init__(*args, **kwargs)
        self._link_field = 'link_facebook' if self.instance.link_facebook else 'link_zalo'
        self.fields['lien_ket'].initial = getattr(self.instance, self._link_field) or ''
        self.fields['dich_vu_truc_tiep'].queryset = DichVu.objects.filter(Q(da_xoa=False) | Q(pk=self.instance.dich_vu_truc_tiep_id)).order_by('ten_dich_vu')
        self.fields['dich_vu_truc_tiep'].label_from_instance = lambda service: service.ten_dich_vu

    def save(self, commit=True):
        customer = super().save(commit=False)
        link = self.cleaned_data.get('lien_ket', '').strip()
        link_field = self._link_field
        if not customer.link_facebook and not customer.link_zalo and link:
            link_field = 'link_zalo' if 'zalo' in link.casefold() or link.isdigit() else 'link_facebook'
        setattr(customer, link_field, link)
        if commit:
            customer.save()
            self.save_m2m()
        return customer


class KhachHangCreateForm(KhachHangForm):
    lien_ket = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={
        'placeholder': 'Nhập liên kết nếu khách hàng cung cấp',
    }))
    dich_vu_truc_tiep = DichVuNhapHoacChonField(
        queryset=None, required=True,
        widget=forms.TextInput(attrs={'list': 'customer-service-options', 'placeholder': 'Nhập hoặc chọn dịch vụ', 'autocomplete': 'off'}),
        error_messages={'invalid_choice': 'Vui lòng chọn dịch vụ có trong danh sách.'},
    )

    class Meta(KhachHangForm.Meta):
        fields = ['ho_ten', 'so_dien_thoai', 'dich_vu_truc_tiep']
        widgets = {
            'ho_ten': forms.TextInput(attrs={'placeholder': 'Nhập họ và tên khách hàng'}),
            'so_dien_thoai': forms.TextInput(attrs={'placeholder': 'Nhập số điện thoại gồm 10 chữ số', 'inputmode': 'numeric'}),
        }

    def __init__(self, *args, **kwargs):
        from apps.services.models import DichVu
        super().__init__(*args, **kwargs)
        self.fields['dich_vu_truc_tiep'].queryset = DichVu.objects.filter(da_xoa=False).order_by('ten_dich_vu')
        self.fields['dich_vu_truc_tiep'].label_from_instance = lambda service: service.ten_dich_vu
        self.fields['ho_ten'].error_messages['required'] = 'Vui lòng nhập tên khách hàng.'
        self.fields['so_dien_thoai'].error_messages['required'] = 'Số điện thoại phải gồm đúng 10 chữ số.'
        self.fields['dich_vu_truc_tiep'].error_messages['required'] = 'Vui lòng chọn dịch vụ.'

    def clean_so_dien_thoai(self):
        phone = super().clean_so_dien_thoai()
        if KhachHang.objects.filter(so_dien_thoai=phone).exists():
            raise ValidationError('Số điện thoại này đã tồn tại.')
        return phone

    def save(self, commit=True):
        customer = super().save(commit=False)
        link = self.cleaned_data.get('lien_ket', '').strip()
        if link:
            if 'zalo' in link.casefold() or link.isdigit():
                customer.link_zalo = link
            else:
                customer.link_facebook = link
        if commit:
            customer.save()
            self.save_m2m()
        return customer

