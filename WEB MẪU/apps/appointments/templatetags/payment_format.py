from django import template


register = template.Library()


@register.filter
def payment_vnd(value):
    """Hiển thị số tiền nguyên với dấu chấm phân cách hàng nghìn."""
    return format(value, ',.0f').replace(',', '.')
