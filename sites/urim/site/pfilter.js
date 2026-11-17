// /proclamations: live filter over the language folders (matches native and English names, codes).
(function () {
  var input = document.getElementById('lang-filter');
  if (!input) return;
  var items = [].slice.call(document.querySelectorAll('.folder')).map(function (a) { return { li: a.parentNode, q: a.getAttribute('data-q') }; });
  var sections = [].slice.call(document.querySelectorAll('[data-section]'));
  var count = document.getElementById('lang-count'), none = document.getElementById('lang-none');
  function fold(s) { return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim(); }
  items.forEach(function (it) { it.q = fold(it.q); });
  function run() {
    var t = fold(input.value), shown = 0;
    items.forEach(function (it) {
      var on = !t || it.q.indexOf(t) > -1;
      it.li.hidden = !on;
      if (on) shown++;
    });
    sections.forEach(function (s) { s.hidden = !s.querySelector('.folders > li:not([hidden])'); });
    if (none) none.hidden = shown > 0;
    if (count) count.textContent = t ? shown + ' of ' + items.length + ' shown' : items.length + ' in total';
    try { history.replaceState(null, '', t ? '?q=' + encodeURIComponent(input.value) : location.pathname); } catch (e) {}
  }
  try { var q = new URLSearchParams(location.search).get('q'); if (q) input.value = q; } catch (e) {}
  input.addEventListener('input', run);
  run();
})();
