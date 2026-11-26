// Progressive enhancement only: confirm destructive actions. Everything works without JS.
document.querySelectorAll('form[data-confirm]').forEach(f => {
  f.addEventListener('submit', e => { if (!window.confirm(f.dataset.confirm)) e.preventDefault(); });
});
