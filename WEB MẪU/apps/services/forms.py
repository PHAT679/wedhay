from django import forms
from django.core.exceptions import ValidationError
from .models import DichVu, VALID_DURATIONS


class DichVuForm(forms.ModelForm):
    class Meta:
        model = DichVu
        fields = ['ten_dich_vu', 'gia_tien', 'thoi_luong', 'ghi_chu']
        widgets = {
            'ten_dich_vu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Sơn Gel Hàn Quốc'}),
            'gia_tien': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: 150000', 'min': '1000', 'step': '1000'}),
            'thoi_luong': forms.Select(attrs={'class': 'form-select'}),
            'ghi_chu': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mô tả chi tiết các bước dịch vụ'}),
        }

    def clean_ten_dich_vu(self):
        ten = self.cleaned_data['ten_dich_vu'].strip()
        qs = DichVu.objects.filter(ten_dich_vu__iexact=ten, da_xoa=False)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Tên dịch vụ này đã tồn tại trong hệ thống.')
        return ten

    def clean_gia_tien(self):
        gia = self.cleaned_data.get('gia_tien')
        if gia is None or gia <= 0:
            raise ValidationError('Giá tiền phải là số nguyên dương lớn hơn 0.')
        return gia

    def clean_thoi_luong(self):
        thoi_luong = self.cleaned_data.get('thoi_luong')
        if thoi_luong not in VALID_DURATIONS:
            raise ValidationError(f'Thời lượng phải thuộc danh sách hợp lệ: {VALID_DURATIONS} phút.')
        return thoi_luong
