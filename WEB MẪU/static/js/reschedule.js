document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('reschedule-form');
  const date = form.elements.booking_date;
  const slots = document.getElementById('slots-container');
  const loading = document.getElementById('slots-loading');
  const button = document.getElementById('submit-btn');
  const dialog = document.getElementById('reschedule-feedback');
  const icon = document.getElementById('reschedule-feedback-icon');
  const title = document.getElementById('reschedule-feedback-title');
  const label = button.textContent;
  let saved = false, busy = false, pending = false, version = 0, refreshAfterConflict = false;
  function feedback(message, success = false) {
    saved = success;
    const noSlots = message.replace(/[.]$/, '') === 'Ngày chọn không còn khung giờ trống';
    dialog.classList.toggle('no-slots-warning', noSlots);
    title.textContent = message;
    icon.textContent = success ? '✓' : '!';
    icon.style.background = success ? '#e3f5e8' : noSlots ? '#e889ad' : '#fde5ee';
    icon.style.color = success ? '#36964c' : noSlots ? '#fff' : '#e889ad';
    if (!dialog.open) dialog.showModal();
  }
  document.getElementById('reschedule-feedback-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => { if (saved) location.assign(form.dataset.returnUrl); else if (refreshAfterConflict) { refreshAfterConflict = false; loadSlots(false); } });
  async function loadSlots(showEmptyWarning = true) {
    const current = ++version;
    slots.replaceChildren();
    if (!date.value || !date.checkValidity()) { pending = false; loading.style.display = 'none'; return; }
    pending = true; loading.style.display = 'block';
    try {
      const response = await fetch(`/api/slots/?${new URLSearchParams({date:date.value,duration:form.dataset.duration,exclude_id:form.dataset.appointment})}`, {signal:AbortSignal.timeout(15000)});
      if (!response.ok) throw new Error();
      const data = await response.json();
      if (current !== version) return;
      if (!Array.isArray(data.slots)) throw new Error();
      const values = data.slots;
      if (!values.some(s => s.available)) {
        if (showEmptyWarning === true) feedback('Ngày chọn không còn khung giờ trống');
        return;
      }
      values.forEach(s => {
        const wrapper = document.createElement('div'); wrapper.className = 'slot-radio-btn' + (s.available ? '' : ' disabled');
        const text = document.createElement(s.available ? 'label' : 'div'); text.className = 'slot-label'; text.textContent = s.time_str;
        if (s.available) {
          const input = document.createElement('input'); input.type = 'radio'; input.name = 'booking_time'; input.value = s.time_str; input.id = `slot-${s.time_str}`; input.required = true;
          text.htmlFor = input.id; wrapper.append(input);
        } else { wrapper.title = s.reason || ''; }
        wrapper.append(text); slots.append(wrapper);
      });
    } catch (_) {
      if (current === version) feedback('Không tải được khung giờ. Vui lòng chọn lại ngày để thử lại.');
    } finally {
      if (current === version) { pending = false; loading.style.display = 'none'; }
    }
  }
  date.addEventListener('change', () => loadSlots());
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (busy) return;
    if (!date.value) return feedback('Vui lòng chọn ngày hẹn mới.');
    if (!date.checkValidity()) return feedback('Ngày hẹn không hợp lệ. Đặt trước tối đa 30 ngày.');
    if (pending) return feedback('Đang tải khung giờ. Vui lòng chờ trong giây lát.');
    if (!slots.querySelector('input:checked')) return feedback('Vui lòng chọn khung giờ mới.');
    busy = true; button.disabled = true; button.textContent = 'Đang xử lý...';
    const data = new FormData(form);
    try {
      const response = await fetch(form.action, {method:'POST',body:data,headers:{'X-Requested-With':'XMLHttpRequest'},signal:AbortSignal.timeout(20000)});
      if (!response.headers.get('content-type')?.includes('application/json')) throw new Error();
      const result = await response.json();
      if (!response.ok || result.success !== true) { refreshAfterConflict = result.slot_conflict === true; feedback(result.message || 'Không thể đổi lịch. Vui lòng thử lại.'); }
      else feedback('Đổi lịch hẹn thành công', true);
    } catch (_) { feedback('Chưa xác nhận được kết quả từ máy chủ. Vui lòng kiểm tra danh sách lịch hẹn trước khi thử lại.'); }
    finally { busy = false; button.disabled = false; button.textContent = label; }
  });
  loadSlots(false);
});
