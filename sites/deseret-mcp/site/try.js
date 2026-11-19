// Front-page "Try it": calls this site's own MCP endpoint (to_deseret / from_deseret) and shows the
// result with its report of unknown and derived words. Nothing typed here is stored.
(function () {
  var box = document.getElementById('try');
  if (!box) return;
  var input = document.getElementById('try-in'), out = document.getElementById('try-out'), report = document.getElementById('try-report');
  var status = document.getElementById('try-status'), go = document.getElementById('try-go');
  var mode = 'to';
  var samples = { to: input.value, from: '𐐜 𐐔𐐯𐑆𐐲𐑉𐐯𐐻 𐐈𐑊𐑁𐐲𐐺𐐯𐐻 𐐶𐐪𐑆 𐐲𐐹𐑉𐐭𐑂𐐼 𐐺𐐴 𐑄 𐐡𐐨𐐾𐐲𐑌𐐻𐑅 𐐮𐑌 1854.' };
  var id = 0;

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function line(label, items) {
    var p = el('p'); p.append(el('span', 'small-caps muted', label + ' '));
    var c = el('span', 'chips'); items.forEach(function (i) { c.append(i); }); p.append(c); return p;
  }

  function setMode(m) {
    samples[mode] = input.value;
    mode = m;
    ['to', 'from'].forEach(function (t) { document.getElementById('mode-' + t).setAttribute('aria-selected', t === m ? 'true' : 'false'); });
    input.value = samples[m];
    input.classList.toggle('dsrt-in', m === 'from');
    input.setAttribute('aria-label', m === 'to' ? 'English text' : 'Deseret text');
    run();
  }

  function run() {
    var text = input.value;
    if (!text.trim()) { out.textContent = ''; report.textContent = ''; return; }
    var my = ++id;
    status.textContent = 'Working…';
    go.disabled = true;
    fetch('/api/mcp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json, text/event-stream' },
      body: JSON.stringify({ jsonrpc: '2.0', id: my, method: 'tools/call', params: { name: mode === 'to' ? 'to_deseret' : 'from_deseret', arguments: { text: text } } }),
    }).then(function (r) { return r.json(); }).then(function (j) {
      if (my !== id) return;
      var res = j.result || {};
      if (res.isError) throw new Error(res.content && res.content[0].text);
      var s = res.structuredContent;
      out.className = 'out ' + (mode === 'to' ? 'dsrt' : 'latin');
      out.textContent = mode === 'to' ? s.deseret : s.latin;
      report.textContent = '';
      if (mode === 'to') {
        report.append(el('p', 'muted', s.stats.words + ' words: ' + s.stats.from_dictionary + ' from the dictionary, ' + s.stats.derived + ' built from their parts, ' + s.stats.unknown + ' left in Latin letters.'));
        if (s.unknown.length) report.append(line('Not transliterated', s.unknown.slice(0, 30).map(function (u) { return el('span', 'chip unk', u.word); })));
        if (s.derived.length) report.append(line('Built from parts', s.derived.slice(0, 30).map(function (d) { var c = el('span', 'chip der', d.word); c.title = d.from; c.append(el('span', 'd', d.deseret)); return c; })));
        if (s.heteronyms) report.append(line('Check the sense', s.heteronyms.map(function (h) { return el('span', 'chip', h.word); })));
      } else {
        report.append(el('p', 'muted', s.stats.words + ' words: ' + s.stats.matched + ' matched the dictionary, ' + s.stats.respelled + ' respelled letter by letter.'));
        if (s.ambiguous.length) report.append(line('Homophones', s.ambiguous.slice(0, 20).map(function (a) { return el('span', 'chip der', a.chose + ' / ' + a.also.slice(0, 3).join(' / ')); })));
        if (s.respelled.length) report.append(line('Respelled', s.respelled.slice(0, 20).map(function (r) { return el('span', 'chip unk', r.respelled); })));
      }
      status.textContent = '';
    }).catch(function (e) {
      if (my !== id) return;
      status.textContent = 'Could not reach the server' + (e && e.message ? ': ' + e.message : '') + '.';
    }).then(function () { if (my === id) go.disabled = false; });
  }

  document.getElementById('mode-to').addEventListener('click', function () { setMode('to'); });
  document.getElementById('mode-from').addEventListener('click', function () { setMode('from'); });
  go.addEventListener('click', run);
  input.addEventListener('keydown', function (e) { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) run(); });
  run();
})();
