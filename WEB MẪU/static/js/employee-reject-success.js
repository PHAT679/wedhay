document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('reject-form');
  const reason = document.getElementById('reject-reason');
  const error = document.getElementById('reject-submit-error');
  const button = form.querySelector('button[type="submit"]');
  const success = document.getElementById('reject-success-modal');
  let pending = false;
  form.noValidate = true;

  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (pending) return;
    if (!reason.value.trim()) {
      closeModal('reject-modal');
      openModal('reject-reason-required');
      return;
    }
    pending = true;
    button.disabled = true;
    error.hidden = true;
    try {
      const response = await fetch(form.action, {method:'POST', body:new FormData(form), credentials:'same-origin'});
      if (!response.ok || !response.redirected || new URL(response.url).pathname !== form.dataset.dashboard) {
        error.textContent = 'Không thể xác nhận từ chối. Vui lòng kiểm tra lại lịch hẹn.';
        error.hidden = false;
        button.disabled = false;
        pending = false;
        return;
      }
      closeModal('reject-modal');
      openModal('reject-success-modal');
    } catch (_) {
      error.textContent = 'Chưa xác nhận được kết quả. Vui lòng kiểm tra danh sách lịch hẹn trước khi thử lại.';
      error.hidden = false;
    }
  });

  success.addEventListener('click', event => {
    if (event.target === success) location.assign(form.dataset.dashboard);
  });
});
