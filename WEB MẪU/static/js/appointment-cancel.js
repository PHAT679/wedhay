document.addEventListener('DOMContentLoaded', () => {
  const root = document.querySelector('.customer-appointments');
  const dialog = document.getElementById('cancel-dialog');
  const form = document.getElementById('cancel-form');
  const keep = document.getElementById('cancel-keep');
  const confirm = document.getElementById('cancel-confirm');
  const error = document.getElementById('cancel-error');
  const banner = document.getElementById('cancel-success');
  let selected = null, busy = false;
  root.addEventListener('click', event => {
    const link = event.target.closest('[data-cancel-appointment]');
    if (!link) return;
    event.preventDefault();
    if (busy) return;
    selected = link; form.action = link.href;
    error.hidden = true; error.textContent = '';
    dialog.showModal(); keep.focus();
  });
  keep.addEventListener('click', () => { if (!busy) dialog.close(); });
  dialog.addEventListener('cancel', event => { if (busy) event.preventDefault(); });
  banner.querySelector('button').addEventListener('click', () => { banner.hidden = true; });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (busy || !selected) return;
    busy = true; confirm.disabled = true; keep.disabled = true;
    confirm.textContent = 'Đang xử lý...'; error.hidden = true;
    try {
      const response = await fetch(form.action, {method:'POST', body:new FormData(form), headers:{'X-Requested-With':'XMLHttpRequest'}, signal:AbortSignal.timeout(20000)});
      const json = response.headers.get('content-type')?.includes('application/json');
      const data = json ? await response.json() : {};
      if (!response.ok || data.success !== true) {
        const fallback = response.status === 403 ? 'Phiên đăng nhập hoặc CSRF không hợp lệ. Vui lòng tải lại trang.' : response.status === 404 ? 'Lịch hẹn không tồn tại hoặc bạn không có quyền hủy.' : 'Không thể hủy lịch hẹn. Vui lòng thử lại.';
        throw new Error(data.message || fallback);
      }
      const row = selected.closest('.appointment-row');
      const badge = document.createElement('span'); badge.className = 'badge badge-canceled'; badge.textContent = 'Đã hủy';
      row.cells[4].replaceChildren(badge);
      const dash = document.createElement('span'); dash.textContent = '—'; row.cells[5].replaceChildren(dash);
      dialog.close(); banner.hidden = false;
    } catch (reason) {
      error.textContent = reason.name === 'TimeoutError' || reason.name === 'TypeError' ? 'Chưa xác nhận được kết quả từ máy chủ. Vui lòng kiểm tra lại danh sách trước khi thử lại.' : reason.message;
      error.hidden = false;
    } finally {
      busy = false; confirm.disabled = false; keep.disabled = false; confirm.textContent = 'Xác Nhận Hủy Lịch';
    }
  });
});
