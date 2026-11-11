(() => {
  const script = document.currentScript;
  const bell = document.getElementById('notif-bell-btn');
  const dropdown = document.getElementById('notif-dropdown');
  const initial = document.getElementById('owner-unread-rejection-ids');
  if (!script || !bell || !dropdown || !initial) return;
  let known = new Set(JSON.parse(initial.textContent));
  const update = async () => {
    try {
      const response = await fetch(script.dataset.url, {credentials:'same-origin', cache:'no-store'});
      if (!response.ok) return;
      const data = await response.json();
      const newIds = data.rejection_ids.filter(id => !known.has(id));
      known = new Set(data.rejection_ids);
      let counter = bell.querySelector('.bell-counter');
      if (data.count) {
        if (!counter) { counter = document.createElement('span'); counter.className = 'bell-counter'; bell.append(counter); }
        counter.textContent = data.count;
      } else if (counter) counter.remove();
      const header = dropdown.querySelector('.notif-header span');
      if (header) header.textContent = `Thông Báo Mới (${data.count})`;
      const list = dropdown.querySelector('.notif-list');
      if (list) {
        const entries = data.notifications.map(item => {
          const li = document.createElement('li'); li.className = 'notif-item' + (item.unread ? ' unread' : '');
          const a = document.createElement('a'); a.href = item.url; a.style.cssText = 'text-decoration:none;color:inherit;display:block';
          const title = document.createElement('div'); title.className = 'notif-title'; title.textContent = item.title;
          const body = document.createElement('div'); body.style.cssText = 'font-size:12px;color:var(--text-muted);margin-bottom:2px'; body.textContent = item.body.length > 75 ? item.body.slice(0, 72) + '…' : item.body;
          const time = document.createElement('div'); time.className = 'notif-time'; time.textContent = item.time + ' trước';
          a.append(title, body, time); li.append(a); return li;
        });
        if (!entries.length) { const li = document.createElement('li'); li.textContent = 'Chưa có thông báo nào.'; entries.push(li); }
        list.replaceChildren(...entries);
      }
      if (newIds.length) {
        bell.classList.remove('owner-rejection-ring');
        void bell.offsetWidth;
        bell.classList.add('owner-rejection-ring');
      }
    } catch (_) { /* Giữ nguyên số đã hiển thị nếu không tải được. */ }
  };
  bell.addEventListener('animationend', () => bell.classList.remove('owner-rejection-ring'));
  setInterval(update, 15000);
})();
