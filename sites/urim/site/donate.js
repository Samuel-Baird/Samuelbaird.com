// /donate: thank-you dialog after choosing a donation link.
(function () {
  var m = document.getElementById('thanks'), last;
  if (!m) return;
  function close() { m.hidden = true; document.body.style.overflow = ''; if (last) last.focus(); }
  document.querySelectorAll('[data-thanks]').forEach(function (a) {
    a.addEventListener('click', function () {
      last = a; m.hidden = false; document.body.style.overflow = 'hidden'; m.querySelector('.x').focus();
    });
  });
  m.querySelectorAll('[data-close]').forEach(function (b) { b.onclick = close; });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !m.hidden) close(); });
})();
