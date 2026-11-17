// Client-side search over /data/index.json: English term or any Church rendering (reverse lookup).
(function () {
  var BASE = '/urim'; // served at samuelbaird.com/urim
  var q = document.getElementById('q'), out = document.getElementById('results');
  if (!q || !out) return;
  var data = [];
  try { var pre = new URLSearchParams(location.search).get('q'); if (pre) q.value = pre; } catch (e) {}
  function fold(s) { return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim(); }
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  fetch(BASE + '/data/index.json').then(function (r) { return r.json(); }).then(function (d) {
    data = d.map(function (c) {
      c._k = [fold(c.en)].concat(c.pt.map(fold), c.es.map(fold));
      return c;
    });
    if (q.value) run();
  });
  function score(c, t) {
    var best = 0;
    for (var i = 0; i < c._k.length; i++) {
      var k = c._k[i];
      if (k === t) best = Math.max(best, 3);
      else if (k.indexOf(t) === 0) best = Math.max(best, 2);
      else if (k.indexOf(t) > -1) best = Math.max(best, 1);
    }
    return best;
  }
  function run() {
    var t = fold(q.value);
    if (!t) { out.innerHTML = ''; return; }
    var hits = data.map(function (c) { return [score(c, t), c]; })
      .filter(function (x) { return x[0] > 0; })
      .sort(function (a, b) { return b[0] - a[0] || a[1].en.length - b[1].en.length; })
      .slice(0, 30);
    if (!hits.length) { out.innerHTML = '<li class="muted">No match. Try another spelling or the English term.</li>'; return; }
    out.innerHTML = hits.map(function (x) {
      var c = x[1];
      return '<li><a href="' + BASE + '/c/' + c.s + '"><span><b>' + esc(c.en) + '</b><small>' + esc(c.cat) + '</small></span>' +
        '<span><small lang="pt">Português</small><span lang="pt">' + (esc(c.pt.join(', ')) || '&mdash;') + '</span></span>' +
        '<span><small lang="es">Español</small><span lang="es">' + (esc(c.es.join(', ')) || '&mdash;') + '</span></span></a></li>';
    }).join('');
  }
  q.addEventListener('input', run);
})();
