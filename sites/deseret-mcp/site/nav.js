// Mobile menu toggle for the sidebar; closes on Escape or when a link is chosen.
(function () {
  var btn = document.getElementById('menubtn'), side = document.getElementById('sidebar');
  if (!btn || !side) return;
  function set(open) {
    side.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  btn.addEventListener('click', function () { set(!side.classList.contains('open')); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') set(false); });
  side.addEventListener('click', function (e) { if (e.target.closest('a')) set(false); });
})();
