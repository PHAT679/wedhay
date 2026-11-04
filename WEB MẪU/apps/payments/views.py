import urllib.parse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from apps.accounts.decorators import owner_required
from apps.appointments.models import LichHen
from apps.notifications.models import send_notification
from .models import GiaoDich


@owner_required
def payment_checkout_view(request, appointment_pk):
    """
    Luồng thanh toán dịch vụ (Section 11).
    Hỗ trợ Tiền mặt hoặc QR VietQR theo đúng SRS.
    """
    appointment = get_object_or_404(LichHen, pk=appointment_pk)
    total_amount = appointment.tong_tien

    # Tạo URL VietQR chuẩn
    # Cú pháp: https://img.vietqr.io/image/{bank_id}-{account_no}-compact2.png?amount={amount}&addInfo={memo}&accountName={name}
    bank_id = 'MB'
    account_no = '0905123456'
    account_name = 'TIEM NAIL EMMAY BEAUTY'
    memo = f"EMMAY {appointment.ma_lich_hen}"
    memo_encoded = urllib.parse.quote(memo)
    acc_name_encoded = urllib.parse.quote(account_name)

    vietqr_url = (
        f"https://img.vietqr.io/image/{bank_id}-{account_no}-compact2.png"
        f"?amount={int(total_amount)}&addInfo={memo_encoded}&accountName={acc_name_encoded}"
    )

    if request.method == 'POST':
        method = request.POST.get('phuong_thuc')  # 'Tiền Mặt' hoặc 'QR'

        if method not in ['Tiền Mặt', 'QR']:
            messages.error(request, 'Phương thức thanh toán không hợp lệ.')
            return redirect('owner:appointment_detail', pk=appointment_pk)

        with transaction.atomic():
            # 1. Tạo hoặc cập nhật GiaoDich
            giao_dich, _ = GiaoDich.objects.update_or_create(
                lich_hen=appointment,
                defaults={
                    'so_tien': total_amount,
                    'phuong_thuc': method,
                    'trang_thai': 'Thành công',
                    'ma_tham_chieu': memo if method == 'QR' else 'TIEN_MAT_TAI_QUAY'
                }
            )

            # 2. Đổi trạng thái Lịch Hẹn sang Hoàn thành
            appointment.trang_thai = 'Hoàn thành'
            appointment.save()

            # 3. Gửi thông báo đến khách hàng
            if appointment.khach_hang and hasattr(appointment.khach_hang, 'tai_khoan'):
                send_notification(
                    tai_khoan=appointment.khach_hang.tai_khoan,
                    tieu_de=f'Thanh toán thành công lịch hẹn {appointment.ma_lich_hen}',
                    noi_dung=f'Quý khách đã thanh toán {total_amount:,.0f} đ bằng hình thức {method}. Cảm ơn quý khách đã tin tưởng tiệm nail Emmay Beauty!',
                    loai_thong_bao='Trạng thái',
                    lien_ket='/customer/my-appointments/'
                )

        messages.success(
            request,
            f'Đã xác nhận thanh toán {total_amount:,.0f} đ ({method}) cho lịch hẹn {appointment.ma_lich_hen}. Lịch hẹn chuyển sang trạng thái "Hoàn thành".'
        )
        return redirect('owner:appointment_detail', pk=appointment_pk)

    return render(request, 'owner/payment_checkout.html', {
        'appointment': appointment,
        'total_amount': total_amount,
        'vietqr_url': vietqr_url,
        'memo': memo,
        'account_name': account_name,
        'account_no': account_no,
        'bank_id': bank_id,
    })
