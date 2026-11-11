document.addEventListener('DOMContentLoaded', () => {
  const account = document.querySelector('.customer-navbar .customer-account details');
  if (!account) return;
  const summary = account.querySelector('summary');
  document.addEventListener('click', event => {
    if (account.open && !account.contains(event.target)) account.open = false;
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && account.open) {
      account.open = false;
      summary.focus();
    }
  });
});
