// /hymns: search, edition and change filters, and per-hymn history over /data/lds-hymns.json.
// The table rows and stats are pre-rendered by scripts/build.mjs (crawlable without JS); this script only
// re-renders the rows when a filter changes. Keep CHANGE and the row markup in step with build.mjs.
(() => {
  const CHANGE = { added: ['Added', '#8DA27A'], kept: ['Kept', '#7E9BBB'], removed: ['Removed', '#C98A5A'] };
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const store = { get(k) { try { return localStorage.getItem('hymns.' + k) || ''; } catch { return ''; } }, set(k, v) { try { localStorage.setItem('hymns.' + k, v); } catch {} } };
  const fold = (s) => String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[’']/g, '');

  let hymns = [], editions = [], ed = {}, order = [], history = {}, byId = new Map();

  const change = (c) => c ? `<span class="t-st"><i style="background:${CHANGE[c][1]}"></i>${CHANGE[c][0]}</span>` : '';
  const num = (h) => h.number ?? (h.previousNumber != null ? `<s title="Number in the previous edition">${h.previousNumber}</s>` : '');
  const row = (h) => `<tr data-id="${esc(h.id)}" tabindex="0" aria-expanded="false"><td class="h-no">${num(h)}</td>`
    + `<td><b>${esc(h.title || h.firstLine)}</b>${h.title && h.firstLine ? `<span class="h-fl">${esc(h.firstLine)}</span>` : ''}</td>`
    + `<td>${esc(ed[h.edition].short)}</td><td class="hide-sm">${esc(h.text || '')}</td><td>${change(h.change)}</td>`
    + `<td class="t-links"><a href="${esc(h.source)}" rel="noopener">Source</a></td></tr>`;

  function detail(h) {
    const others = (history[h.hymnKey] || []).map((s) => { const [e, n] = s.split(':'); return byId.get(`${e}-${n}`); }).filter(Boolean)
      .sort((a, b) => ed[a.edition].year - ed[b.edition].year);
    const facts = [
      ['Text', h.text], ['Music', h.music], ['Tune', h.tune], ['Written', h.yearWritten],
      ["Author's religion", h.authorDenomination && `${h.authorDenomination} <small>(Wikidata)</small>`],
      ['Section', h.section],
      !h.firstLine && ['First line', 'Not in the source yet (see Known gaps below)'],
      h.handEntered === 'verify' && ['Note', 'Entered by hand from a scan; still to check against the page image'],
      h.change === 'removed' && ['Removed', `Was no. ${h.previousNumber} in ${esc(ed[ed[h.edition].previous].short)}; not in ${esc(ed[h.edition].short)}`],
      h.change === 'kept' && ['Kept', `Was no. ${h.previousNumber} in ${esc(ed[ed[h.edition].previous].short)}`],
    ].filter((f) => f && f[1] != null && f[1] !== '');
    const missing = editions.filter((e) => !others.some((o) => o.edition === e.id)).map((e) => esc(e.short) + (e.partial ? ' (so far)' : ''));
    return `<tr class="h-detail"><td colspan="6">`
      + (facts.length ? `<dl>${facts.map(([k, v]) => `<dt>${k}</dt><dd>${typeof v === 'number' ? v : (/<small>|Was no\./.test(v) ? v : esc(v))}</dd>`).join('')}</dl>` : '')
      + `<p class="small"><b>In ${others.length} of ${editions.length} editions here:</b></p><ol>`
      + others.map((o) => `<li${o.id === h.id ? ' class="cur"' : ''}><a href="${esc(o.source)}" rel="noopener">${esc(ed[o.edition].short)}</a> <span>no. ${o.number}</span></li>`).join('')
      + `</ol>${missing.length ? `<p class="small">Not in: ${missing.join(', ')}.</p>` : ''}</td></tr>`;
  }

  function filtered() {
    const q = fold($('t-q').value.trim());
    const e = $('h-ed').value, c = $('h-ch').value;
    return hymns.filter((h) => (!e || h.edition === e) && (!c || h.change === c)
      && (!q || String(h.number) === q || fold(`${h.title} ${h.firstLine} ${h.text} ${h.music} ${h.tune}`).includes(q)))
      .sort((a, b) => order.indexOf(a.edition) - order.indexOf(b.edition) || (a.number ?? 1e6) - (b.number ?? 1e6) || (a.previousNumber ?? 0) - (b.previousNumber ?? 0));
  }

  function note() {
    const e = ed[$('h-ed').value], c = $('h-ch').value;
    let t = '';
    if (c && e && !e.previous) t = `${e.short} has no change status: ${e.id === '1835' ? 'it is the first book, so every hymn in it is new.' : 'the book before it is not in the dataset yet.'}`;
    else if (c === 'removed' && e?.partial) t = `${e.short} is still being released, so nothing is marked removed yet.`;
    else if (c && !e) t = 'Changes compare 1841 with 1835, and Hymns—For Home and Church with 1985.';
    $('h-note').textContent = t;
  }

  function render() {
    const list = filtered();
    const shown = list.slice(0, 1200);
    $('t-rows').innerHTML = shown.length ? shown.map(row).join('') : '<tr><td colspan="6">No hymns match.</td></tr>';
    $('t-shown').textContent = list.length === hymns.length ? '' : `(${list.length} of ${hymns.length})`;
    note();
  }

  function toggle(tr) {
    const open = tr.getAttribute('aria-expanded') === 'true';
    const next = tr.nextElementSibling;
    if (next && next.classList.contains('h-detail')) next.remove();
    tr.setAttribute('aria-expanded', String(!open));
    if (!open) tr.insertAdjacentHTML('afterend', detail(byId.get(tr.dataset.id)));
  }

  function init() {
    $('h-ed').insertAdjacentHTML('beforeend', order.map((id) => `<option value="${esc(id)}">${esc(ed[id].short)}</option>`).join(''));
    for (const id of ['h-ed', 'h-ch']) {
      const saved = store.get(id);
      if (saved && [...$(id).options].some((o) => o.value === saved)) $(id).value = saved;
      $(id).addEventListener('change', () => { store.set(id, $(id).value); render(); });
    }
    let timer;
    $('t-q').addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(render, 150); });
    $('t-rows').addEventListener('click', (e) => {
      const tr = e.target.closest('tr[data-id]');
      if (tr && !e.target.closest('a')) toggle(tr);
    });
    $('t-rows').addEventListener('keydown', (e) => {
      const tr = e.target.closest('tr[data-id]');
      if (tr && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); toggle(tr); }
    });
  }

  fetch('/data/lds-hymns.json').then((r) => r.json()).then((d) => {
    hymns = d.hymns; editions = d.editions; history = d.history;
    ed = Object.fromEntries(editions.map((e) => [e.id, e]));
    order = editions.map((e) => e.id).reverse();
    byId = new Map(hymns.map((h) => [h.id, h]));
    init();
    render();
  }).catch(() => { $('h-note').textContent = 'Search could not load. The full list is below.'; });
})();
