// /temples: map, filters and sorting over /data/lds-temples.json.
// The table rows, stats and decade chart are pre-rendered by scripts/build.mjs (crawlable without JS);
// this script only re-renders the rows when a filter changes. Keep STATUS in step with build.mjs.
(() => {
  const STATUS = {
    'operating': ['Operating', '#D9B46A'],
    'opening-soon': ['Opening soon', '#8DA27A'],
    'under-renovation': ['Under renovation', '#C98A5A'],
    'under-construction': ['Under construction', '#7E9BBB'],
    'announced': ['Announced', '#B9AE96'],
    'closed': ['Closed', '#9A4446'],
  };
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const fmt = (d) => (d ? `${MONTHS[+d.slice(5, 7) - 1]} ${+d.slice(8, 10)}, ${d.slice(0, 4)}` : '');
  const place = (t) => [t.city, t.region, t.country].filter(Boolean).join(', ') || t.location;
  const label = (s) => (STATUS[s] || [s])[0];
  const color = (s) => (STATUS[s] || [0, '#B9AE96'])[1];
  const store = { get(k) { try { return localStorage.getItem('temples.' + k) || ''; } catch { return ''; } }, set(k, v) { try { localStorage.setItem('temples.' + k, v); } catch {} } };

  let temples = [];
  let map, clusters;
  const markers = new Map();

  function row(t) {
    const links = [`<a href="${esc(t.officialUrl)}" rel="noopener">Official</a>`, t.wikipedia && `<a href="${esc(t.wikipedia)}" rel="noopener">Wikipedia</a>`].filter(Boolean).join('');
    return `<tr data-id="${esc(t.id)}"><td>${esc(t.name)}</td><td>${esc(place(t))}</td><td><span class="t-st"><i style="background:${color(t.status)}"></i>${esc(label(t.status))}</span></td>`
      + `<td class="hide-sm">${t.announced ? `<time datetime="${t.announced}">${fmt(t.announced)}</time>` : ''}</td>`
      + `<td>${t.dedicated ? `<time datetime="${t.dedicated}">${fmt(t.dedicated)}</time>` : ''}</td><td class="t-links">${links}</td></tr>`;
  }

  function popup(t) {
    const precise = t.coordPrecision === 'site' || t.coordPrecision === 'address';
    return `<h3>${esc(t.name)}</h3><p>${esc(place(t))}</p><p><span class="t-st"><i style="background:${color(t.status)}"></i>${esc(label(t.status))}</span></p>`
      + (t.announced ? `<p>Announced ${fmt(t.announced)}</p>` : '')
      + (t.groundbreaking ? `<p>Groundbreaking ${fmt(t.groundbreaking)}</p>` : '')
      + (t.dedicated ? `<p>Dedicated ${fmt(t.dedicated)}</p>` : '')
      + (precise ? '' : `<p><small>Location approximate (${esc(t.coordPrecision)})</small></p>`)
      + `<p><a href="${esc(t.officialUrl)}" rel="noopener">Official page &#8599;</a>${t.wikipedia ? ` &middot; <a href="${esc(t.wikipedia)}" rel="noopener">Wikipedia &#8599;</a>` : ''}</p>`;
  }

  function filtered() {
    const q = $('t-q').value.trim().toLowerCase();
    const st = $('t-status').value, co = $('t-country').value, sort = $('t-sort').value;
    const list = temples.filter((t) => (!st || t.status === st) && (!co || t.country === co)
      && (!q || `${t.name} ${place(t)}`.toLowerCase().includes(q)));
    const by = {
      dedicated: (a, b) => (a.dedicated || '9999').localeCompare(b.dedicated || '9999') || (a.announced || '9999').localeCompare(b.announced || '9999'),
      announced: (a, b) => (b.announced || '').localeCompare(a.announced || ''),
      name: (a, b) => a.name.localeCompare(b.name),
      country: (a, b) => (a.country || '~').localeCompare(b.country || '~') || a.name.localeCompare(b.name),
    }[sort];
    return list.sort(by);
  }

  function render(fit) {
    const list = filtered();
    $('t-rows').innerHTML = list.length ? list.map(row).join('') : '<tr><td colspan="6">No temples match.</td></tr>';
    $('t-shown').textContent = list.length === temples.length ? '' : `(${list.length} of ${temples.length})`;
    if (!map) return;
    clusters.clearLayers();
    const shown = list.filter((t) => markers.has(t.id)).map((t) => markers.get(t.id));
    clusters.addLayers(shown);
    if (fit && shown.length) map.fitBounds(L.featureGroup(shown).getBounds().pad(0.15), { maxZoom: 10 });
  }

  function initMap() {
    if (!window.L) return;
    map = L.map('t-map', { zoomSnap: 0.5, worldCopyJump: true, scrollWheelZoom: false }).setView([25, -30], 2);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors', maxZoom: 18,
    }).addTo(map);
    map.on('focus click', () => map.scrollWheelZoom.enable());
    map.on('blur', () => map.scrollWheelZoom.disable());
    clusters = L.markerClusterGroup({
      showCoverageOnHover: false, maxClusterRadius: 40, spiderfyOnMaxZoom: true,
      iconCreateFunction: (c) => L.divIcon({ className: '', html: `<div class="t-cl">${c.getChildCount()}</div>`, iconSize: [34, 34] }),
    }).addTo(map);
    for (const t of temples) {
      if (t.lat == null) continue;
      const approx = t.coordPrecision === 'city' || t.coordPrecision === 'country';
      const m = L.marker([t.lat, t.lng], {
        title: t.name, alt: t.name,
        icon: L.divIcon({ className: '', html: `<div class="t-pin${approx ? ' approx' : ''}" style="background:${color(t.status)}"></div>`, iconSize: [12, 12] }),
      }).bindPopup(popup(t));
      markers.set(t.id, m);
    }
    $('t-legend').innerHTML = Object.entries(STATUS).filter(([k]) => temples.some((t) => t.status === k))
      .map(([, [l, c]]) => `<span><i style="background:${c}"></i>${l}</span>`).join('') + '<span>Faded pins: location approximate</span>';
  }

  function initFilters() {
    const statuses = Object.keys(STATUS).filter((k) => temples.some((t) => t.status === k));
    $('t-status').insertAdjacentHTML('beforeend', statuses.map((s) => `<option value="${s}">${label(s)}</option>`).join(''));
    const countries = [...new Set(temples.map((t) => t.country).filter(Boolean))].sort();
    $('t-country').insertAdjacentHTML('beforeend', countries.map((c) => `<option>${esc(c)}</option>`).join(''));
    for (const id of ['t-status', 't-country', 't-sort']) {
      const saved = store.get(id);
      if (saved && [...$(id).options].some((o) => o.value === saved)) $(id).value = saved;
      $(id).addEventListener('change', () => { store.set(id, $(id).value); render(id !== 't-sort'); });
    }
    let timer;
    $('t-q').addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(() => render(true), 150); });
    $('t-rows').addEventListener('click', (e) => {
      const tr = e.target.closest('tr[data-id]');
      if (!tr || e.target.closest('a') || !markers.has(tr.dataset.id)) return;
      const m = markers.get(tr.dataset.id);
      $('t-map').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'center' });
      clusters.zoomToShowLayer(m, () => m.openPopup());
    });
  }

  fetch('/data/lds-temples.json').then((r) => r.json()).then((d) => {
    temples = d.temples;
    initMap();
    initFilters();
    render(false);
  }).catch(() => { $('t-legend').textContent = 'The map could not load. The full list is below.'; });
})();
