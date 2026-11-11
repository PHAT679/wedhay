document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.owner-services-new').forEach(row => {
    setTimeout(() => row.classList.remove('owner-services-new'), 2000);
  });
  document.querySelectorAll('tr[data-detail-url]').forEach(row => {
    row.addEventListener('click', event => {
      if (event.target.closest('a, button, input, label')) return;
      window.location.assign(row.dataset.detailUrl);
    });
  });
});
