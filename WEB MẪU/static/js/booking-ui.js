document.addEventListener('DOMContentLoaded', () => {
  const root = document.querySelector('.emmay-booking');
  const items = [...root.querySelectorAll('.service-select-item')];
  items.forEach(item => {
    item.querySelector('.booking-service-top b').textContent = Number(item.querySelector('input').dataset.price).toLocaleString('vi-VN') + ' đ';
  });
  const search = root.querySelector('#service-search');
  const pager = root.querySelector('#booking-pagination');
  let page = 0;
  function renderServices() {
    const query = search.value.trim().toLocaleLowerCase('vi');
    const matched = items.filter(item => item.querySelector('input').dataset.name.toLocaleLowerCase('vi').includes(query));
    const pages = Math.ceil(matched.length / 6);
    page = Math.max(0, Math.min(page, pages - 1));
    items.forEach(item => { item.hidden = true; });
    matched.slice(page * 6, page * 6 + 6).forEach(item => { item.hidden = false; });
    root.querySelector('#service-empty').hidden = matched.length > 0;
    pager.replaceChildren();
    function button(text, label, target, disabled, dot) {
      const b = document.createElement('button'); b.type = 'button'; b.textContent = text;
      b.setAttribute('aria-label', label); b.disabled = disabled;
      if (dot) { b.className = 'page-dot'; if (target === page) b.setAttribute('aria-current', 'page'); }
      b.addEventListener('click', () => { page = target; renderServices(); }); pager.append(b);
    }
    if (pages > 1) {
      button('←', 'Trang trước', page - 1, page === 0, false);
      for (let i = 0; i < pages; i++) button('', `Trang ${i + 1}`, i, false, true);
      button('→', 'Trang tiếp theo', page + 1, page === pages - 1, false);
    }
  }
  const initial = items.findIndex(item => item.querySelector('input').checked);
  page = initial < 0 ? 0 : Math.floor(initial / 6);
  search.addEventListener('input', () => { page = 0; renderServices(); }); renderServices();
  const form = root.querySelector('form');
  for (const [id, errorId] of [['contact_name', 'name-error'], ['contact_phone', 'phone-error']]) {
    const input = root.querySelector('#' + id), error = root.querySelector('#' + errorId);
    function validate() {
      const empty = !input.value.trim();
      input.setCustomValidity(empty ? 'Vui lòng nhập thông tin' : '');
      const invalid = !input.validity.valid;
      input.setAttribute('aria-invalid', String(invalid)); error.hidden = !invalid;
      error.textContent = invalid ? (empty ? 'Vui lòng nhập thông tin' : 'Số điện thoại phải gồm đúng 10 chữ số.') : '';
    }
    input.addEventListener('invalid', event => { event.preventDefault(); validate(); });
    input.addEventListener('input', () => { if (input.hasAttribute('aria-invalid')) validate(); });
  }
  form.addEventListener('submit', event => {
    if (!root.querySelector('#contact_name').value.trim()) {
      event.preventDefault(); root.querySelector('#contact_name').setCustomValidity('Vui lòng nhập thông tin'); form.reportValidity();
    }
  });
  const date = root.querySelector('#booking_date'), calendar = root.querySelector('#booking-calendar'), toggle = root.querySelector('#calendar-toggle');
  let month;
  const iso = d => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
  function close() { calendar.hidden = true; toggle.setAttribute('aria-expanded', 'false'); }
  function revealCalendar() {
    requestAnimationFrame(() => {
      if (calendar.hidden) return;
      const viewportBottom = window.visualViewport
        ? window.visualViewport.offsetTop + window.visualViewport.height : window.innerHeight;
      const overflow = calendar.getBoundingClientRect().bottom + 12 - viewportBottom;
      if (overflow > 0) window.scrollBy({top: overflow, behavior: 'instant'});
    });
  }
  function renderCalendar() {
    calendar.replaceChildren();
    const head = document.createElement('div'); head.className = 'calendar-head';
    const title = document.createElement('span'); title.textContent = `Tháng ${month.getMonth()+1}, ${month.getFullYear()}`; head.append(title);
    for (const delta of [-1,1]) {
      const b = document.createElement('button'); b.type='button'; b.textContent=delta<0?'‹':'›'; b.setAttribute('aria-label',delta<0?'Tháng trước':'Tháng sau');
      b.onclick=()=>{month=new Date(month.getFullYear(),month.getMonth()+delta,1);renderCalendar();};head.append(b);
    }
    calendar.append(head); const grid=document.createElement('div');grid.className='calendar-days';
    ['T2','T3','T4','T5','T6','T7','CN'].forEach(day=>{const el=document.createElement('span');el.textContent=day;grid.append(el);});
    for(let i=0;i<(month.getDay()+6)%7;i++) grid.append(document.createElement('span'));
    const days=new Date(month.getFullYear(),month.getMonth()+1,0).getDate();
    for(let day=1;day<=days;day++) {
      const value=iso(new Date(month.getFullYear(),month.getMonth(),day));
      const b=document.createElement('button');b.type='button';b.textContent=day;b.disabled=value<date.min||value>date.max;b.setAttribute('aria-label',value);b.setAttribute('aria-pressed',String(value===date.value));
      b.onclick=()=>{date.value=value;date.dispatchEvent(new Event('booking-date-confirmed'));date.dispatchEvent(new Event('change',{bubbles:true}));close();toggle.focus();};grid.append(b);
    } calendar.append(grid); revealCalendar();
  }
  function open() {month=new Date((date.value||date.min)+'T12:00:00');month.setDate(1);calendar.hidden=false;toggle.setAttribute('aria-expanded','true');renderCalendar();}
  toggle.onclick=()=>calendar.hidden?open():close(); date.addEventListener('click',open);
  document.addEventListener('click',e=>{if(!e.target.closest('.booking-date-wrap'))close();});
  calendar.addEventListener('keydown',e=>{if(e.key==='Escape'){close();toggle.focus();}});
});
