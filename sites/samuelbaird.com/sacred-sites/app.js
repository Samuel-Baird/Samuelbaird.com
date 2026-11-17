// Map page: glyph markers, clustering, filters, popups with links.
const state = { group: null, denom: null, country: "", year: "", cat: "", show: "visited" };
const $ = (id) => document.getElementById(id);
const years = [...new Set(VISITS.map((v) => v[0].slice(0, 4)))].sort();

const map = L.map("map", { zoomSnap: 0.5, worldCopyJump: true }).setView([40.4, -111.8], 8);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  maxZoom: 19,
}).addTo(map);

// Clusters keep the crowded Wasatch Front readable; they split as you zoom in.
const clusters = L.markerClusterGroup({
  showCoverageOnHover: false, maxClusterRadius: 38, spiderfyOnMaxZoom: true,
  iconCreateFunction: (c) => {
    const n = c.getChildCount();
    return L.divIcon({ className: "", html: `<div class="cl"><b>${n}</b></div>`, iconSize: [38, 38] });
  },
}).addTo(map);
let markers = {};

// Provo, home base.
L.marker([PROVO.lat, PROVO.lon], {
  icon: L.divIcon({ className: "", html: '<div class="home-mk"><i></i><span>Provo</span></div>', iconSize: [64, 22], iconAnchor: [8, 11] }),
  interactive: false, keyboard: false, zIndexOffset: -500,
}).addTo(map);

// ---- filtering ----
const siteMatches = (s) =>
  (!state.group || groupOf(s.denom) === state.group) &&
  (!state.denom || state.denom.match.includes(s.denom)) &&
  (!state.country || s.country === state.country);
const shownVisits = (s) => s.visits.filter((v) => (!state.year || v.date.startsWith(state.year)) && (!state.cat || v.cat === state.cat));
const visibleSites = () => state.show === "wish" ? [] : SITES.filter((s) => siteMatches(s) && shownVisits(s).length);
// Year and visit type only describe visits, so wishlist places ignore them.
const visibleWish = () => (state.show === "visited" ? [] : WISH.filter(siteMatches));

const linkRow = (s) => {
  const a = [s.site && ["Website", s.site], s.wikiUrl && ["Wikipedia", s.wikiUrl]].filter(Boolean)
    .map(([t, u]) => `<a href="${esc(u)}" target="_blank" rel="noopener">${t} &#8599;</a>`);
  const anchor = leafAnchor(s.denom);
  if (anchor) a.push(`<a href="/sacred-sites/traditions#${anchor}">Tradition</a>`);
  return a.length ? `<div class="links">${a.join("")}</div>` : "";
};
// One "Google Maps" button; clicking it opens the embedded Google Maps card (rating, website, directions).
const gmapsHtml = (s) => NO_MAPS.has(s.id) ? "" :
  `<div class="gmaps"><button type="button" class="gm-toggle" data-id="${s.id}" aria-expanded="false">Google Maps</button></div><div class="gm-embed" hidden></div>`;
const headHtml = (s, tag) => `<div class="pop-head" style="--c:${colorOf(s.denom)}">${glyphSvg(glyphOf(s.denom), 16)}<span>${esc(labelOf(s.denom))}</span>${tag ? `<em>${tag}</em>` : ""}</div>`;

function popupHtml(s) {
  if (s.wish) {
    const place = [s.city, s.state, s.country].filter(Boolean).join(", ");
    return `<div class="pop">${headHtml(s, "wishlist")}<h3>${esc(s.name)}</h3><div class="sub">${esc(place)} · ${fmtMiles(milesFromProvo(s))} from Provo</div>${s.note ? `<div class="note">${esc(s.note)}</div>` : ""}${linkRow(s)}${gmapsHtml(s)}</div>`;
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
  return `<div class="pop">${headHtml(s)}${pics}<h3>${esc(s.name)}</h3><div class="sub">${esc(s.city)}, ${esc(s.state)} · first visited ${fmt(first.date)}</div>${linkRow(s)}${gmapsHtml(s)}<ul>${rows}</ul></div>`;
}

const markerIcon = (s) => L.divIcon({
  className: "",
  html: `<div class="mk ${s.wish ? "wish" : "visited"}" style="--c:${colorOf(s.denom)}">${glyphSvg(glyphOf(s.denom), 16)}</div>`,
  iconSize: [32, 32], iconAnchor: [16, 16], popupAnchor: [0, -18], tooltipAnchor: [0, -16],
});

function render({ fit = true } = {}) {
  clusters.clearLayers(); markers = {};
  const sites = visibleSites(), wish = visibleWish(), all = [...sites, ...wish];
  for (const s of all) {
    const m = L.marker([s.lat, s.lon], { icon: markerIcon(s), title: s.name, riseOnHover: true })
      .bindPopup(popupHtml(s), { maxWidth: 320 })
      .bindTooltip(`${esc(s.name)}<small>${esc(labelOf(s.denom))}${s.wish ? " · wishlist" : ""}</small>`, { direction: "top", className: "mk-tip" });
    clusters.addLayer(m);
    markers[s.id] = m;
  }
  if (fit && all.length) map.fitBounds(L.latLngBounds(all.map((s) => [s.lat, s.lon])).pad(0.2), { maxZoom: 11, animate: true, duration: 0.8 });

  const counted = state.show === "wish" ? wish : sites;
  const traditions = new Set(counted.map((s) => labelOf(s.denom)));
  const countries = new Set(counted.map((s) => s.country));
  const one = (n, a, b) => (n === 1 ? a : b);
  $("stats").innerHTML =
    `<div><b>${counted.length}</b><span>${one(counted.length, "site", "sites")}</span></div><div><b>${traditions.size}</b><span>${one(traditions.size, "tradition", "traditions")}</span></div><div><b>${countries.size}</b><span>${one(countries.size, "country", "countries")}</span></div>`;
  $("legend").hidden = false;
  syncControls();
}

// Opens a site's popup, expanding any cluster that hides it. Wishlist places switch the map to include the wishlist.
function openSite(id) {
  if (!markers[id]) {
    const s = [...SITES, ...WISH].find((x) => x.id === id); if (!s) return;
    Object.assign(state, { group: null, denom: null, country: "", year: "", cat: "", show: s.wish ? "both" : "visited" });
    render({ fit: false });
  }
  const m = markers[id]; if (!m) return;
  clusters.zoomToShowLayer(m, () => { map.flyTo(m.getLatLng(), Math.max(map.getZoom(), 13), { duration: 0.8 }); m.openPopup(); });
}

// ---- controls ----
function buildControls() {
  $("groups").innerHTML = `<button class="chip" data-g="">All</button>` +
    GROUPS.map((g) => `<button class="chip" data-g="${g.key}">${g.label}</button>`).join("");
  $("groups").onclick = (e) => { const b = e.target.closest(".chip"); if (!b) return; state.group = b.dataset.g || null; render(); };
  $("year").innerHTML = `<option value="">All years</option>` + years.map((y) => `<option>${y}</option>`).join("");
  $("year").onchange = () => { state.year = $("year").value; render(); };
  $("cat").innerHTML = `<option value="">Any visit type</option>` + CATEGORIES.map((c) => `<option value="${c.key}">${c.label}</option>`).join("");
  $("cat").onchange = () => { state.cat = $("cat").value; render(); };
  $("country").onchange = () => { state.country = $("country").value; render(); };
  $("denom").onchange = () => { const i = $("denom").value; state.denom = i === "" ? null : COMMUNITIES[i]; render(); };
  document.querySelectorAll("#show .chip").forEach((b) => b.onclick = () => { state.show = b.dataset.show; render(); });
  $("reset").onclick = () => { Object.assign(state, { group: null, denom: null, country: "", year: "", cat: "" }); render(); };
  $("glyphs").innerHTML = GLYPH_KEY.map(([k, label]) => `<li>${glyphSvg(k, 14)}<span>${label}</span></li>`).join("");

  // Phone layout: the panel is a collapsible sheet so the map keeps most of the screen.
  const panel = $("panel"), tg = $("panel-toggle");
  tg.onclick = () => {
    const open = panel.classList.toggle("collapsed") === false;
    tg.setAttribute("aria-expanded", String(open));
    setTimeout(() => map.invalidateSize(), 50);
  };
}

function syncControls() {
  const pool = [...(state.show === "wish" ? [] : SITES), ...(state.show === "visited" ? [] : WISH)];
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
  $("year").value = state.year;
  $("cat").value = state.cat;
  document.querySelectorAll("#show .chip").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.show === state.show)));
}

// ---- photo carousel inside popups + lightbox ----
const box = document.createElement("div");
box.id = "lightbox"; box.hidden = true;
box.innerHTML = '<img alt="" referrerpolicy="no-referrer"><button aria-label="Close">&times;</button>';
document.body.appendChild(box);
box.onclick = () => { box.hidden = true; };
document.addEventListener("keydown", (e) => { if (e.key === "Escape") box.hidden = true; });
map.on("popupopen", (e) => {
  const tg = e.popup.getElement().querySelector(".gm-toggle");
  if (tg) tg.onclick = () => {
    const wrap = tg.parentElement.nextElementSibling, open = wrap.hidden;
    if (open && !wrap.firstChild) {
      const iframe = document.createElement("iframe");
      iframe.src = mapsEmbedUrl([...SITES, ...WISH].find((x) => x.id === tg.dataset.id));
      iframe.loading = "lazy"; iframe.referrerPolicy = "no-referrer-when-downgrade";
      iframe.title = "Google Maps preview"; iframe.allowFullscreen = true;
      wrap.appendChild(iframe);
    }
    wrap.hidden = !open; tg.setAttribute("aria-expanded", String(open));
    // popup.update() would rebuild the content and drop the iframe; just re-measure and keep it in view.
    e.popup._updateLayout(); e.popup._updatePosition(); e.popup._adjustPan();
  };
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
render();
// Container size isn't final until layout settles; refit then, and handle ?site=<id> deep links.
let fitted = false;
new ResizeObserver(() => {
  map.invalidateSize();
  if (!fitted && map.getSize().x > 100) {
    fitted = true; render({ fit: true });
    const want = new URLSearchParams(location.search).get("site");
    if (want) setTimeout(() => openSite(want), 300);
  }
}).observe($("map"));
