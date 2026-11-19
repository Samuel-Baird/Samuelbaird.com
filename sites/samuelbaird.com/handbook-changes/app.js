// /handbook-changes: search, chapter/kind/release filters and sorting over /data/lds-handbook-changes.json.
// The table rows, release chart and stats are pre-rendered by scripts/build.mjs (crawlable without JS);
// this script only re-renders the rows when a filter or sort changes. Keep KIND in step with build.mjs.
(() => {
  const KIND = {
    revised: { label: 'Revised', color: '#D9B46A' },
    new: { label: 'New', color: '#8DA27A' },
    removed: { label: 'Removed', color: '#B8645A' },
    renumbered: { label: 'Renumbered', color: '#7E9BBB' },
  };
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const kindBadge = (k) => {
    const m = KIND[k] || { label: k, color: '#B9AE96' };
    return `<span class="t-st"><i style="background:${m.color}"></i>${esc(m.label)}</span>`;
  };
  const chapLabel = (x) => (x.chapter === null ? 'Handbook-wide' : `${x.chapter} · ${x.chapterTitle}`);
  const store = {
    get(k) { try { return localStorage.getItem('handbook.' + k) || ''; } catch { return ''; } },
    set(k, v) { try { localStorage.setItem('handbook.' + k, v); } catch {} },
  };

  let changes = [];
  let chapters = {};
  let releases = [];

  const row = (x) => `<tr data-id="${esc(x.id)}"><td><time datetime="${esc(x.date)}">${esc(x.date)}</time></td><td class="hb-sec">${esc(x.section)}</td><td><span class="hb-title">${esc(x.title)}</span><span class="hb-desc">${esc(x.description)}</span></td><td class="hide-sm">${esc(chapLabel(x))}</td><td>${kindBadge(x.kind)}</td><td class="t-links"><a href="${esc(x.sectionUrl)}" rel="noopener">Section</a><a href="${esc(x.announcementUrl)}" rel="noopener">Release</a></td></tr>`;

  function compareSections(a, b) {
    if (a === b) return 0;
    if (a === 'All') return -1;
    if (b === 'All') return 1;
    const pa = a.split(/[.–-]/).map((n) => (Number.isNaN(Number(n)) ? n : Number(n)));
    const pb = b.split(/[.–-]/).map((n) => (Number.isNaN(Number(n)) ? n : Number(n)));
    const len = Math.max(pa.length, pb.length);
    for (let i = 0; i < len; i++) {
      if (pa[i] === undefined) return -1;
      if (pb[i] === undefined) return 1;
      if (pa[i] !== pb[i]) {
        return typeof pa[i] === 'number' && typeof pb[i] === 'number'
          ? pa[i] - pb[i]
          : String(pa[i]).localeCompare(String(pb[i]));
      }
    }
    return 0;
  }

  function filtered() {
    const q = $('t-q').value.trim().toLowerCase();
    const ch = $('t-ch').value;
    const kind = $('t-kind').value;
    const rel = $('t-rel').value;
    const sort = $('t-sort').value;

    const list = changes.filter((x) => {
      if (ch !== '') {
        if (ch === 'all' && x.chapter !== null) return false;
        if (ch !== 'all' && String(x.chapter) !== ch) return false;
      }
      if (kind && x.kind !== kind) return false;
      if (rel && x.release !== rel) return false;
      if (q && !`${x.section} ${x.title} ${x.chapterTitle} ${x.description} ${x.release}`.toLowerCase().includes(q)) return false;
      return true;
    });

    const by = {
      newest: (a, b) => b.date.localeCompare(a.date) || (a.chapter ?? -1) - (b.chapter ?? -1) || compareSections(a.section, b.section),
      oldest: (a, b) => a.date.localeCompare(b.date) || (a.chapter ?? -1) - (b.chapter ?? -1) || compareSections(a.section, b.section),
      section: (a, b) => (a.chapter ?? -1) - (b.chapter ?? -1) || compareSections(a.section, b.section) || b.date.localeCompare(a.date),
    }[sort] || ((a, b) => b.date.localeCompare(a.date));

    return list.sort(by);
  }

  function syncBars() {
    const activeRel = $('t-rel').value;
    document.querySelectorAll('.t-dec div[data-rel]').forEach((el) => {
      el.classList.toggle('is-active', activeRel !== '' && el.dataset.rel === activeRel);
    });
  }

  function render() {
    const list = filtered();
    $('t-rows').innerHTML = list.length ? list.map(row).join('') : '<tr><td colspan="6">No handbook changes match.</td></tr>';
    $('t-shown').textContent = list.length === changes.length ? '' : `(${list.length} of ${changes.length})`;
    syncBars();
  }

  function initFilters() {
    const chOpts = ['<option value="all">Handbook-wide</option>'];
    for (let i = 0; i <= 38; i++) {
      const c = chapters[String(i)];
      if (!c) continue;
      chOpts.push(`<option value="${i}">${i} · ${esc(c.title)}</option>`);
    }
    $('t-ch').insertAdjacentHTML('beforeend', chOpts.join(''));

    const relOpts = releases.map((r) => `<option value="${esc(r.release)}">${esc(r.release)} (${r.count})</option>`);
    $('t-rel').insertAdjacentHTML('beforeend', relOpts.join(''));

    for (const id of ['t-ch', 't-kind', 't-rel', 't-sort']) {
      const saved = store.get(id);
      if (saved && [...$(id).options].some((o) => o.value === saved)) $(id).value = saved;
      $(id).addEventListener('change', () => { store.set(id, $(id).value); render(); });
    }

    let timer;
    $('t-q').addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(render, 120); });

    const dec = document.querySelector('.t-dec');
    if (dec) {
      dec.addEventListener('click', (e) => {
        const bar = e.target.closest('div[data-rel]');
        if (!bar) return;
        const rel = bar.dataset.rel;
        $('t-rel').value = $('t-rel').value === rel ? '' : rel;
        store.set('t-rel', $('t-rel').value);
        render();
      });
    }
  }

  fetch('/data/lds-handbook-changes.json').then((r) => r.json()).then((d) => {
    changes = d.changes || [];
    chapters = d.chapters || {};
    releases = d.releases || [];
    initFilters();
    render();
  }).catch(() => {});
})();
