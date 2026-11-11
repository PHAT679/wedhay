(() => {
  const account = document.querySelector('.owner-header .overview-account');
  if (!account) return;
  document.addEventListener('click', event => {
    if (account.open && !account.contains(event.target)) account.open = false;
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && account.open) {
      account.open = false;
      account.querySelector('summary').focus();
    }
  });
})();
