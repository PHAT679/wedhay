document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('employee-cancel-form');
  if (!form) return;
  const confirmButton = document.getElementById('employee-cancel-submit');
  const error = document.getElementById('employee-cancel-error');
  const success = document.getElementById('employee-cancel-success');
  let pending = false;
  form.onsubmit = null;
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!pending) openModal('employee-cancel-confirm');
  });
  confirmButton.addEventListener('click', async () => {
    if (pending) return;
    pending = true;
    confirmButton.disabled = true;
    error.hidden = true;
    try {
      const response = await fetch(form.action, {method:'POST', body:new FormData(form), credentials:'same-origin'});
      const page = new DOMParser().parseFromString(await response.text(), 'text/html');
      const message = [...page.querySelectorAll('.alert-success')].some(node => node.textContent.includes('Đã hủy lịch hẹn của khách hàng.'));
      const canceled = page.querySelector('.employee-detail-header .employee-status.canceled');
      if (!response.ok || !response.redirected || !message || !canceled) {
        error.textContent = 'Không thể xác nhận đã hủy. Vui lòng kiểm tra lại lịch hẹn.';
        error.hidden = false;
        return;
      }
      closeModal('employee-cancel-confirm');
      openModal('employee-cancel-success');
    } catch (_) {
      error.textContent = 'Chưa xác nhận được kết quả. Vui lòng kiểm tra lại lịch hẹn trước khi thử lại.';
      error.hidden = false;
      return;
    }
  });
  document.querySelectorAll('.employee-cancel-refresh').forEach(button => button.addEventListener('click', () => location.reload()));
  success.addEventListener('click', event => { if (event.target === success) location.reload(); });
});
