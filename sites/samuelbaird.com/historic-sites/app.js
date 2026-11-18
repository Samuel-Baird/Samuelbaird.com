// /historic-sites: map, filters and sorting over /data/lds-historic-sites.json.
// The table rows and stats are pre-rendered by scripts/build.mjs (crawlable without JS); this script only
// re-renders the rows when a filter changes. Styles come from /temples/temples.css. Keep CAT in step with build.mjs.
(() => {
  const CAT = { 'Historic site': '#D9B46A', "Visitors' center": '#7E9BBB', Monument: '#8DA27A', Museum: '#C98A5A' };
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const place = (x) => [x.city, x.region, x.country === 'United States' ? '' : x.country].filter(Boolean).join(', ');
  const color = (c) => CAT[c] || '#B9AE96';
  const cat = (c) => `<span class="t-st"><i style="background:${color(c)}"></i>${esc(c)}</span>`;
  const store = { get(k) { try { return localStorage.getItem('historic.' + k) || ''; } catch { return ''; } }, set(k, v) { try { localStorage.setItem('historic.' + k, v); } catch {} } };

  let sites = [];
  let areaOrder = [];
  let map, clusters;
  const markers = new Map();

  const links = (x, sep) => [`<a href="${esc(x.officialUrl)}" rel="noopener">Official${sep ? ' page &#8599;' : ''}</a>`, x.wikipedia && `<a href="${esc(x.wikipedia)}" rel="noopener">Wikipedia${sep ? ' &#8599;' : ''}</a>`].filter(Boolean).join(sep || '');

  const row = (x) => `<tr data-id="${esc(x.id)}"><td>${esc(x.name)}</td><td>${esc(place(x))}</td><td>${cat(x.category)}</td><td class="hide-sm">${esc(x.area || '')}</td><td class="t-links">${links(x)}</td></tr>`;

  function popup(x) {
    const precise = x.coordPrecision === 'site' || x.coordPrecision === 'address';
    const addr = [x.street, place(x)].filter(Boolean).join(', ');
    return `<h3>${esc(x.name)}</h3><p>${esc(addr)}</p><p>${cat(x.category)}</p>`
      + (precise ? '' : `<p><small>Location approximate (${esc(x.coordPrecision)})</small></p>`)
      + `<p>${links(x, ' &middot; ')}</p>`;
  }

  function filtered() {
    const q = $('t-q').value.trim().toLowerCase();
    const c = $('t-cat').value, a = $('t-area').value, sort = $('t-sort').value;
    const list = sites.filter((x) => (!c || x.category === c) && (!a || (x.area || 'Other') === a)
      && (!q || `${x.name} ${x.street} ${place(x)} ${x.area || ''}`.toLowerCase().includes(q)));
    const by = {
      area: (p, r) => areaOrder.indexOf(p.area || 'Other') - areaOrder.indexOf(r.area || 'Other') || p.name.localeCompare(r.name),
      name: (p, r) => p.name.localeCompare(r.name),
      place: (p, r) => (p.region || '~').localeCompare(r.region || '~') || (p.city || '').localeCompare(r.city || '') || p.name.localeCompare(r.name),
    }[sort];
    return list.sort(by);
  }

  function render(fit) {
    const list = filtered();
    $('t-rows').innerHTML = list.length ? list.map(row).join('') : '<tr><td colspan="5">No sites match.</td></tr>';
    $('t-shown').textContent = list.length === sites.length ? '' : `(${list.length} of ${sites.length})`;
    if (!map) return;
    clusters.clearLayers();
    const shown = list.filter((x) => markers.has(x.id)).map((x) => markers.get(x.id));
    clusters.addLayers(shown);
    if (fit && shown.length) map.fitBounds(L.featureGroup(shown).getBounds().pad(0.15), { maxZoom: 15 });
  }

  function initMap() {
    if (!window.L) return;
    map = L.map('t-map', { zoomSnap: 0.5, scrollWheelZoom: false }).setView([40, -98], 4);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors', maxZoom: 19,
    }).addTo(map);
    map.on('focus click', () => map.scrollWheelZoom.enable());
    map.on('blur', () => map.scrollWheelZoom.disable());
    clusters = L.markerClusterGroup({
      showCoverageOnHover: false, maxClusterRadius: 40, spiderfyOnMaxZoom: true,
      iconCreateFunction: (c) => L.divIcon({ className: '', html: `<div class="t-cl">${c.getChildCount()}</div>`, iconSize: [34, 34] }),
    }).addTo(map);
    for (const x of sites) {
      if (x.lat == null) continue;
      const approx = x.coordPrecision === 'city' || x.coordPrecision === 'street';
      markers.set(x.id, L.marker([x.lat, x.lng], {
        title: x.name, alt: x.name,
        icon: L.divIcon({ className: '', html: `<div class="t-pin${approx ? ' approx' : ''}" style="background:${color(x.category)}"></div>`, iconSize: [12, 12] }),
      }).bindPopup(popup(x)));
    }
    $('t-legend').innerHTML = Object.entries(CAT).filter(([k]) => sites.some((x) => x.category === k))
      .map(([l, c]) => `<span><i style="background:${c}"></i>${esc(l)}</span>`).join('') + '<span>Faded pins: location approximate (street or town)</span>';
  }

  function initFilters() {
    const cats = Object.keys(CAT).filter((k) => sites.some((x) => x.category === k));
    $('t-cat').insertAdjacentHTML('beforeend', cats.map((c) => `<option value="${esc(c)}">${esc(c)}</option>`).join(''));
    $('t-area').insertAdjacentHTML('beforeend', areaOrder.map((a) => `<option>${esc(a)}</option>`).join(''));
    for (const id of ['t-cat', 't-area', 't-sort']) {
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

  fetch('/data/lds-historic-sites.json').then((r) => r.json()).then((d) => {
    sites = d.sites;
    areaOrder = [...new Set(sites.map((x) => x.area || 'Other'))];
    initMap();
    initFilters();
    render(false);
  }).catch(() => { $('t-legend').textContent = 'The map could not load. The full list is below.'; });
})();
