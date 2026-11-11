document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('booking-form');
  const dialog = document.getElementById('booking-success-dialog');
  const conflict = document.getElementById('booking-conflict');
  const submit = document.getElementById('submit-booking-btn');
  let pending = false;
  let completed = false;
  const error = document.createElement('p');
  error.className = 'booking-error';
  error.setAttribute('role', 'alert');
  error.hidden = true;
  submit.parentElement.prepend(error);
  dialog.addEventListener('cancel', event => event.preventDefault());
  document.getElementById('booking-conflict-close').addEventListener('click', () => conflict.close());
  conflict.addEventListener('close', () => document.getElementById('booking_date').dispatchEvent(new Event('change', {bubbles:true})));
  form.addEventListener('submit', async event => {
    if (event.defaultPrevented) return;
    event.preventDefault();
    if (pending || completed || !form.reportValidity()) return;
    pending = true;
    submit.disabled = true;
    error.hidden = true;
    try {
      const response = await fetch(form.action, {method: 'POST', body: new FormData(form), credentials: 'same-origin', headers: {'X-Requested-With':'XMLHttpRequest'}});
      if (response.headers.get('content-type')?.includes('application/json')) {
        const result = await response.json();
        if (result.slot_conflict) {
          document.getElementById('booking-conflict-title').textContent = result.message;
          conflict.showModal();
          return;
        }
        throw new Error();
      }
      const page = new DOMParser().parseFromString(await response.text(), 'text/html');
      const result = page.querySelector('template#saved-booking-result');
      if (response.ok && response.redirected && result) {
        completed = true;
        dialog.replaceChildren(result.content.cloneNode(true));
        dialog.querySelectorAll('[data-success-price]').forEach(el => {
          const price = Number(el.dataset.successPrice);
          if (Number.isFinite(price)) el.textContent = price.toLocaleString('vi-VN') + ' đ';
        });
        dialog.showModal();
        return;
      }
      const messages = [...page.querySelectorAll('.alert')].map(el => el.querySelector('span')?.textContent || el.textContent);
      error.textContent = messages.join(' ') || 'Không thể xác nhận đặt lịch. Vui lòng kiểm tra thông tin hoặc đăng nhập lại.';
      error.hidden = false;
      document.getElementById('booking_date').dispatchEvent(new Event('change', {bubbles:true}));
    } catch {
      error.textContent = 'Chưa nhận được kết quả từ máy chủ. Vui lòng kiểm tra Lịch Của Tôi trước khi thử lại để tránh đặt trùng.';
      error.hidden = false;
      // Keep submission locked: the server may have saved the booking before connection loss.
    } finally {
      pending = false;
    }
  });
});
