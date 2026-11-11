document.addEventListener('DOMContentLoaded', () => {
  const root = document.querySelector('.customer-appointments');
  const rows = [...root.querySelectorAll('.appointment-row')];
  root.querySelectorAll('.appointment-price').forEach(el => {
    const amount = Number(el.textContent.replace(/[^0-9]/g, ''));
    el.textContent = amount.toLocaleString('vi-VN') + ' đ';
  });
  const nav = root.querySelector('.appointments-pagination');
  const pages = Math.ceil(rows.length / 5);
  let page = 1;
  function render() {
    rows.forEach((row, index) => { row.hidden = Math.floor(index / 5) !== page - 1; });
    nav.replaceChildren();
    if (pages === 0) return;
    function button(text, label, target, disabled = false) {
      const b = document.createElement('button'); b.type = 'button'; b.textContent = text;
      b.setAttribute('aria-label', label); b.disabled = disabled;
      if (text === String(page)) b.setAttribute('aria-current', 'page');
      b.onclick = () => {page = target; render();}; nav.append(b);
    }
    button('«', 'Trang đầu', 1, page === 1); button('‹', 'Trang trước', page - 1, page === 1);
    let previous = 0;
    for (let i = 1; i <= pages; i++) {
      if (i !== 1 && i !== pages && Math.abs(i - page) > 1) continue;
      if (previous && i - previous > 1) {const dots = document.createElement('span'); dots.textContent = '…'; nav.append(dots);}
      button(String(i), 'Trang ' + i, i); previous = i;
    }
    button('›', 'Trang tiếp theo', page + 1, page === pages); button('»', 'Trang cuối', pages, page === pages);
  }
  render();
});
