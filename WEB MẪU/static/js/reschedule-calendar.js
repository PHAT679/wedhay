document.addEventListener('DOMContentLoaded', () => {
  const date = document.querySelector('.customer-reschedule #booking_date');
  if (!date) return;
  // Retain the original date field, min/max validation and change listener.
  const wrap = document.createElement('div'); wrap.className = 'reschedule-date-wrap';
  date.before(wrap); wrap.append(date); date.hidden = true;
  const toggle = document.createElement('button'); toggle.type = 'button'; toggle.className = 'reschedule-date-toggle'; toggle.id = 'reschedule-date-toggle';
  toggle.setAttribute('aria-labelledby','reschedule-date-label reschedule-date-value');
  toggle.setAttribute('aria-expanded','false'); toggle.setAttribute('aria-controls','reschedule-calendar');
  toggle.innerHTML = '<span id="reschedule-date-value"></span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="3" y="4" width="18" height="17" rx="3"/><path d="M3 9h18M8 2v5M16 2v5"/></svg>';
  document.getElementById('reschedule-date-label').htmlFor = toggle.id;
  const calendar = document.createElement('div'); calendar.id = 'reschedule-calendar'; calendar.className = 'reschedule-calendar'; calendar.hidden = true; calendar.setAttribute('aria-label','Lịch chọn ngày mới');
  wrap.append(toggle,calendar);
  let month;
  const iso = d => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
  const sync = () => { toggle.querySelector('span').textContent = date.value ? date.value.split('-').reverse().join('/') : 'DD/MM/YYYY'; };
  function close() { calendar.hidden = true; toggle.setAttribute('aria-expanded','false'); }
  function reveal() {
    requestAnimationFrame(() => {
      if (calendar.hidden) return;
      calendar.style.left = '0px';
      const bounds = calendar.getBoundingClientRect();
      if (bounds.right > innerWidth - 16) calendar.style.left = `${Math.min(0, innerWidth - 16 - bounds.right)}px`;
      const overflow = calendar.getBoundingClientRect().bottom + 12 - innerHeight;
      if (overflow > 0) window.scrollBy({top:overflow,behavior:'instant'});
    });
  }
  function render() {
    calendar.replaceChildren();
    const head = document.createElement('div'); head.className = 'reschedule-calendar-head';
    const title = document.createElement('span'); title.textContent = `Tháng ${month.getMonth()+1}, ${month.getFullYear()}`; title.setAttribute('aria-live','polite'); head.append(title);
    for (const delta of [-1,1]) {
      const button = document.createElement('button'); button.type='button'; button.textContent=delta<0?'‹':'›'; button.setAttribute('aria-label',delta<0?'Tháng trước':'Tháng sau');
      button.addEventListener('click',()=>{month=new Date(month.getFullYear(),month.getMonth()+delta,1);render();calendar.querySelectorAll('.reschedule-calendar-head button')[delta<0?0:1].focus();});head.append(button);
    }
    calendar.append(head);
    const grid=document.createElement('div');grid.className='reschedule-calendar-days';
    ['T2','T3','T4','T5','T6','T7','CN'].forEach(day=>{const el=document.createElement('span');el.textContent=day;grid.append(el);});
    for(let i=0;i<(month.getDay()+6)%7;i++) grid.append(document.createElement('span'));
    for(let day=1;day<=new Date(month.getFullYear(),month.getMonth()+1,0).getDate();day++) {
      const value=iso(new Date(month.getFullYear(),month.getMonth(),day));
      const button=document.createElement('button');button.type='button';button.textContent=day;button.disabled=(date.min && value<date.min)||(date.max && value>date.max);button.setAttribute('aria-label',value.split('-').reverse().join('/'));button.setAttribute('aria-pressed',String(value===date.value));
      button.addEventListener('click',()=>{date.value=value;sync();date.dispatchEvent(new Event('change',{bubbles:true}));close();toggle.focus();});grid.append(button);
    }
    calendar.append(grid);reveal();
  }
  toggle.addEventListener('click',()=>{if(!calendar.hidden) return close();month=new Date((date.value||date.min)+'T12:00:00');month.setDate(1);calendar.hidden=false;toggle.setAttribute('aria-expanded','true');render();});
  document.addEventListener('click',event=>{if(!event.composedPath().includes(wrap))close();});
  wrap.addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();close();toggle.focus();}});
  wrap.addEventListener('focusout',event=>{if(event.relatedTarget && !wrap.contains(event.relatedTarget))close();});
  date.addEventListener('change',sync);sync();
});

