document.addEventListener('DOMContentLoaded', () => {
  const link = document.getElementById('employee-accept-link');
  if (!link) return;
  const error = document.getElementById('employee-accept-error');
  let pending = false;
  link.addEventListener('click', async event => {
    if (event.defaultPrevented) return;
    event.preventDefault();
    if (pending) return;
    pending = true;
    error.hidden = true;
    try {
      const response = await fetch(link.href, {credentials: 'same-origin'});
      if (!response.ok || !response.redirected || new URL(response.url).pathname !== location.pathname) throw new Error();
      openModal('accept-success-modal');
    } catch (_) {
      error.textContent = 'Chưa xác nhận được kết quả. Vui lòng kiểm tra lại lịch hẹn.';
      error.hidden = false;
      pending = false;
    }
  });
});
