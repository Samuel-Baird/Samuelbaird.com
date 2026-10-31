// Map page: filters, timeline, visit categories, wishlist and clustering.
const state = { group: null, denom: null, country: "", year: "", cat: "", wish: false, from: 0, to: 0 };

// Timeline = every month from the first to the last logged visit.
const monthKeys = (() => {
  const dates = VISITS.map((v) => v[0]).sort();
  let [y, m] = dates[0].slice(0, 7).split("-").map(Number);
  const [ey, em] = dates[dates.length - 1].slice(0, 7).split("-").map(Number);
  const out = [];
  while (y < ey || (y === ey && m <= em)) { out.push(`${y}-${String(m).padStart(2, "0")}`); if (++m > 12) { m = 1; y++; } }
  return out;
})();
state.to = monthKeys.length - 1;
const monthLabel = (k) => new Date(k + "-15T12:00:00").toLocaleDateString(undefined, { month: "short", year: "numeric" });
const years = [...new Set(monthKeys.map((k) => k.slice(0, 4)))];

const map = L.map("map").setView([40.6, -111.9], 8);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  maxZoom: 19,
}).addTo(map);

const clusterIcon = (hollow) => (cluster) =>
  L.divIcon({ html: `<span>${cluster.getChildCount()}</span>`, className: "sscluster" + (hollow ? " hollow" : ""), iconSize: [38, 38] });
const makeCluster = (hollow) => L.markerClusterGroup({
  showCoverageOnHover: false, maxClusterRadius: 48, iconCreateFunction: clusterIcon(hollow),
}).addTo(map);
const visitedLayer = makeCluster(false), wishLayer = makeCluster(true);
const markers = {};

// ---- filtering ----
const monthOk = (v) => { const k = v.date.slice(0, 7); return k >= monthKeys[state.from] && k <= monthKeys[state.to]; };
const siteMatches = (s) =>
  (!state.group || groupOf(s.denom) === state.group) &&
  (!state.denom || state.denom.match.includes(s.denom)) &&
  (!state.country || s.country === state.country);
const shownVisits = (s) => s.visits.filter((v) => monthOk(v) && (!state.cat || v.cat === state.cat));
const visibleSites = () => SITES.filter((s) => siteMatches(s) && shownVisits(s).length);
const visibleWish = () => (state.wish ? WISH.filter(siteMatches) : []);

function popupHtml(s) {
  if (s.wish) {
    return `<div class="pop"><h3>${esc(s.name)}</h3><div class="sub">${esc([s.city, s.state, s.country].filter(Boolean).join(", "))} · ${esc(labelOf(s.denom))} · wishlist</div>${s.note ? `<div class="note">${esc(s.note)}</div>` : ""}</div>`;
  }
  const row = (v) => {
    const links = [v.video && `<a href="${esc(v.video)}" target="_blank" rel="noopener">Video</a>`,
                   v.photos && `<a href="${esc(v.photos)}" target="_blank" rel="noopener">Photos</a>`].filter(Boolean).join("");
    return `<li><b>${fmt(v.date)}</b> · ${esc(v.type)}${v.lang && v.lang !== "English" ? " · " + esc(v.lang) : ""}` +
      ` <span class="cat cat-${v.cat}">${esc(categoryLabel(v.cat))}</span>` +
      `${v.note ? `<div class="note">${esc(v.note)}</div>` : ""}${links ? `<div>${links}</div>` : ""}</li>`;
  };
  const vs = shownVisits(s), first = vs[vs.length - 1], repeats = vs.slice(0, -1);
  const rows = row(first) + (repeats.length ? `<li><details><summary>${repeats.length} repeat visit${repeats.length > 1 ? "s" : ""} (not counted)</summary><ul>${repeats.map(row).join("")}</ul></details></li>` : "");
  const pics = (PHOTOS[s.id] || []).length ? `<div class="gallery" data-id="${s.id}"><img alt="${esc(s.name)}" referrerpolicy="no-referrer"><button class="prev" aria-label="Previous photo">&lsaquo;</button><button class="next" aria-label="Next photo">&rsaquo;</button><span class="count"></span></div>` : "";
  return `<div class="pop">${pics}<h3>${esc(s.name)}</h3><div class="sub">${esc(s.city)}, ${esc(s.state)} · ${esc(labelOf(s.denom))} · first visited ${fmt(first.date)}</div><ul>${rows}</ul></div>`;
}

function render() {
  visitedLayer.clearLayers(); wishLayer.clearLayers();
  const sites = visibleSites(), wish = visibleWish();
  for (const s of [...sites, ...wish]) {
    const color = colorOf(s.denom);
    const m = L.circleMarker([s.lat, s.lon], s.wish
      ? { radius: 9, color, weight: 3, fillColor: color, fillOpacity: 0.05 }
      : { radius: 9, color: "#fff", weight: 2, fillColor: color, fillOpacity: 0.9 })
      .bindPopup(popupHtml(s), { maxWidth: 320 });
    (s.wish ? wishLayer : visitedLayer).addLayer(m);
    markers[s.id] = m;
  }
  const all = [...sites, ...wish];
  if (all.length) map.fitBounds(L.latLngBounds(all.map((s) => [s.lat, s.lon])).pad(0.2), { maxZoom: 11, animate: false });

  document.getElementById("sites").innerHTML = all.slice().sort((a, b) => a.name.localeCompare(b.name))
    .map((s) => `<li><button class="site" data-id="${s.id}">${esc(s.name)} <small>· ${esc(s.city)}${s.wish ? " · wishlist" : ""}</small></button></li>`).join("")
    || '<li class="hint">No sites match these filters.</li>';
  document.querySelectorAll(".site").forEach((b) => b.onclick = () => openSite(b.dataset.id));

  const traditions = new Set(sites.map((s) => labelOf(s.denom)));
  const countries = new Set(sites.map((s) => s.country));
  document.getElementById("stats").innerHTML =
    `<div><b>${sites.length}</b><span>${sites.length === 1 ? 'unique site' : 'unique sites'}</span></div><div><b>${traditions.size}</b><span>${traditions.size === 1 ? 'tradition' : 'traditions'}</span></div><div><b>${countries.size}</b><span>${countries.size === 1 ? 'country' : 'countries'}</span></div>`;
  document.getElementById("legend").hidden = !state.wish;
  syncControls();
}

function openSite(id) {
  const m = markers[id]; if (!m) return;
  const layer = m.options.fillOpacity < 0.5 ? wishLayer : visitedLayer;
  layer.zoomToShowLayer(m, () => m.openPopup());
}

// ---- controls ----
const $ = (id) => document.getElementById(id);
function buildControls() {
  $("groups").innerHTML = `<button class="chip" data-g="">All</button>` +
    GROUPS.map((g) => `<button class="chip" data-g="${g.key}">${g.label}</button>`).join("");
  $("groups").onclick = (e) => { const b = e.target.closest(".chip"); if (!b) return; state.group = b.dataset.g || null; render(); };

  $("year").innerHTML = `<option value="">All years</option>` + years.map((y) => `<option>${y}</option>`).join("");
  $("year").onchange = () => {
    state.year = $("year").value;
    const idx = monthKeys.map((k, i) => [k, i]).filter(([k]) => !state.year || k.startsWith(state.year)).map(([, i]) => i);
    state.from = idx[0]; state.to = idx[idx.length - 1]; render();
  };
  $("cat").innerHTML = `<option value="">Any visit type</option>` + CATEGORIES.map((c) => `<option value="${c.key}">${c.label}</option>`).join("");
  $("cat").onchange = () => { state.cat = $("cat").value; render(); };
  $("country").onchange = () => { state.country = $("country").value; render(); };
  $("denom").onchange = () => { const i = $("denom").value; state.denom = i === "" ? null : COMMUNITIES[i]; render(); };

  for (const id of ["from", "to"]) { $(id).max = monthKeys.length - 1; }
  $("from").oninput = () => { state.from = Math.min(+$("from").value, state.to); state.year = ""; render(); };
  $("to").oninput = () => { state.to = Math.max(+$("to").value, state.from); state.year = ""; render(); };
  $("wish").onchange = () => { state.wish = $("wish").checked; render(); };
  $("reset").onclick = () => {
    Object.assign(state, { group: null, denom: null, country: "", year: "", cat: "", from: 0, to: monthKeys.length - 1 });
    render();
  };
}

function syncControls() {
  const pool = [...SITES, ...(state.wish ? WISH : [])];
  document.querySelectorAll("#groups .chip").forEach((b) => {
    const on = (b.dataset.g || null) === state.group;
    b.setAttribute("aria-pressed", String(on));
    b.classList.toggle("zero", !!b.dataset.g && !pool.some((s) => groupOf(s.denom) === b.dataset.g));
  });
  const countries = [...new Set(pool.map((s) => s.country))].sort();
  $("country").innerHTML = `<option value="">All countries</option>` + countries.map((c) => `<option${c === state.country ? " selected" : ""}>${esc(c)}</option>`).join("");
  const comms = COMMUNITIES.map((c, i) => [c, i]).filter(([c]) => pool.some((s) => c.match.includes(s.denom)));
  $("denom").innerHTML = `<option value="">All denominations</option>` +
    comms.map(([c, i]) => `<option value="${i}"${c === state.denom ? " selected" : ""}>${esc(c.name)}</option>`).join("");
  $("year").value = state.year || (state.from === 0 && state.to === monthKeys.length - 1 ? "" : "");
  $("cat").value = state.cat;
  $("from").value = state.from; $("to").value = state.to;
  $("range-label").textContent = `${monthLabel(monthKeys[state.from])} – ${monthLabel(monthKeys[state.to])}`;
  $("wish").checked = state.wish;
  document.querySelectorAll(".com").forEach((b) => b.classList.toggle("active", COMMUNITIES[b.dataset.i] === state.denom));
}

function renderCommunities() {
  $("communities").innerHTML = COMMUNITIES.filter((c) => c.listed).map((c) => {
    const i = COMMUNITIES.indexOf(c);
    const n = SITES.filter((s) => c.match.includes(s.denom)).length;
    return `<li><button class="com ${n ? "" : "off"}" data-i="${i}" ${n ? "" : "disabled"}>` +
      `<span class="dot" style="background:${c.color}"></span>${esc(c.name)}<span class="n">${n ? `${n} site${n > 1 ? "s" : ""}` : "visited · not yet mapped"}</span></button></li>`;
  }).join("");
  document.querySelectorAll(".com").forEach((b) => b.onclick = () => {
    const c = COMMUNITIES[b.dataset.i]; state.denom = state.denom === c ? null : c; render();
  });
}

// ---- photo carousel inside popups + lightbox ----
const box = document.createElement("div");
box.id = "lightbox"; box.hidden = true;
box.innerHTML = '<img alt="" referrerpolicy="no-referrer"><button aria-label="Close">&times;</button>';
document.body.appendChild(box);
box.onclick = () => { box.hidden = true; };
document.addEventListener("keydown", (e) => { if (e.key === "Escape") box.hidden = true; });
map.on("popupopen", (e) => {
  const g = e.popup.getElement().querySelector(".gallery");
  if (!g) return;
  const list = PHOTOS[g.dataset.id]; let i = 0;
  const img = g.querySelector("img"), count = g.querySelector(".count");
  const show = () => { img.src = photoUrl(list[i], 600); count.textContent = `${i + 1} / ${list.length}`; g.classList.toggle("single", list.length < 2); };
  g.querySelector(".prev").onclick = () => { i = (i - 1 + list.length) % list.length; show(); };
  g.querySelector(".next").onclick = () => { i = (i + 1) % list.length; show(); };
  img.onclick = () => { box.querySelector("img").src = photoUrl(list[i], 1600); box.hidden = false; };
  show();
});

buildControls();
renderCommunities();
render();
// Container size isn't final until layout settles; refit then.
let fitted = false;
new ResizeObserver(() => {
  map.invalidateSize();
  if (!fitted && map.getSize().x > 100) {
    fitted = true; render();
    const want = new URLSearchParams(location.search).get("site");
    if (want) setTimeout(() => openSite(want), 300);
  }
}).observe($("map"));
