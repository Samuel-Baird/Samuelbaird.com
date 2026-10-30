// Worldview communities. `match` lists sheet denominations that count toward each.
// Communities you have visited that have no logged visit yet (e.g. SBC) show as "visited, not yet mapped".
const COMMUNITIES = [
  { name: "Roman Catholic", match: ["Catholic"], color: "#c05621" },
  { name: "Greek Orthodox", match: ["Greek Orthodox"], color: "#b7791f" },
  { name: "Anglican (ACNA)", match: ["Anglican"], color: "#6b46c1" },
  { name: "Southern Baptist Convention (SBC)", match: ["SBC"], color: "#2c7a7b" },
  { name: "Lutheran (ELCA)", match: ["Lutheran"], color: "#2f855a" },
  { name: "Jehovah's Witnesses", match: ["Jehovah's Witnesses"], color: "#4a5568" },
  { name: "The Church of Jesus Christ of Latter-day Saints (LDS)", match: ["LDS"], color: "#2b6cb0" },
  // Also present in the visit log:
  { name: "Episcopal", match: ["Episcopalian"], color: "#9f7aea" },
  { name: "Seventh-day Adventist", match: ["SDA"], color: "#d53f8c" },
];
const colorOf = (denom) => (COMMUNITIES.find((c) => c.match.includes(denom)) || {}).color || "#888";
const communityOf = (denom) => COMMUNITIES.find((c) => c.match.includes(denom));

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const fmt = (iso) => new Date(iso + "T12:00:00").toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });

// Group visits by place
const sites = Object.entries(PLACES).map(([id, [name, denom, city, state, lat, lon]]) => ({
  id, name, denom, city, state, lat, lon,
  visits: VISITS.filter((v) => v[1] === id).sort((a, b) => b[0].localeCompare(a[0])),
})).filter((s) => s.visits.length);

const map = L.map("map").setView([40.6, -111.9], 8);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  maxZoom: 19,
}).addTo(map);

const layer = L.layerGroup().addTo(map);
let filter = null;

function popupHtml(s) {
  const row = ([date, , type, lang, note, video, photos]) => {
    const links = [video && `<a href="${esc(video)}" target="_blank" rel="noopener">Video</a>`,
                   photos && `<a href="${esc(photos)}" target="_blank" rel="noopener">Photos</a>`].filter(Boolean).join("");
    return `<li><b>${fmt(date)}</b> · ${esc(type)}${lang && lang !== "English" ? " · " + esc(lang) : ""}` +
      `${note ? `<div class="note">${esc(note)}</div>` : ""}${links ? `<div>${links}</div>` : ""}</li>`;
  };
  const first = s.visits[s.visits.length - 1], repeats = s.visits.slice(0, -1);
  const rows = row(first) + (repeats.length ? `<li><details><summary>${repeats.length} repeat visit${repeats.length > 1 ? "s" : ""} (not counted)</summary><ul>${repeats.map(row).join("")}</ul></details></li>` : "");
  const label = (communityOf(s.denom) || {}).name || s.denom;
  const pics = (PHOTOS[s.id] || []).length ? `<div class="gallery" data-id="${s.id}"><img alt="${esc(s.name)}" referrerpolicy="no-referrer"><button class="prev" aria-label="Previous photo">&lsaquo;</button><button class="next" aria-label="Next photo">&rsaquo;</button><span class="count"></span></div>` : "";
  return `<div class="pop">${pics}<h3>${esc(s.name)}</h3><div class="sub">${esc(s.city)}, ${esc(s.state)} · ${esc(label)} · first visited ${fmt(first[0])}</div><ul>${rows}</ul></div>`;
}

const markers = {};
function render() {
  layer.clearLayers();
  const shown = sites.filter((s) => !filter || filter.match.includes(s.denom));
  shown.forEach((s) => {
    const r = 9;
    const m = L.circleMarker([s.lat, s.lon], { radius: r, color: "#fff", weight: 2, fillColor: colorOf(s.denom), fillOpacity: 0.9 })
      .bindPopup(popupHtml(s), { maxWidth: 320 }).addTo(layer);
    markers[s.id] = m;
  });
  if (shown.length) map.fitBounds(L.latLngBounds(shown.map((s) => [s.lat, s.lon])).pad(0.2), { maxZoom: 11, animate: false });

  document.getElementById("sites").innerHTML = shown
    .slice().sort((a, b) => a.name.localeCompare(b.name))
    .map((s) => `<li><button class="site" data-id="${s.id}">${esc(s.name)} <small>· ${s.city}</small></button></li>`).join("");
  document.querySelectorAll(".site").forEach((b) => b.onclick = () => {
    const s = sites.find((x) => x.id === b.dataset.id);
    map.setView([s.lat, s.lon], 13); markers[s.id].openPopup();
  });
}

function renderCommunities() {
  document.getElementById("communities").innerHTML = COMMUNITIES.map((c, i) => {
    const vs = sites.filter((s) => c.match.includes(s.denom));
    const n = vs.reduce((t, s) => t + s.visits.length, 0);
    const label = n ? `${vs.length} site${vs.length > 1 ? "s" : ""}` : "visited · not yet mapped";
    return `<li><button class="com ${n ? "" : "off"} ${filter === c ? "active" : ""}" data-i="${i}" ${n ? "" : "disabled"}>` +
      `<span class="dot" style="background:${c.color}"></span>${esc(c.name)}<span class="n">${label}</span></button></li>`;
  }).join("");
  document.querySelectorAll(".com").forEach((b) => b.onclick = () => {
    const c = COMMUNITIES[b.dataset.i];
    filter = filter === c ? null : c;
    renderCommunities(); render();
  });
}

document.getElementById("stats").innerHTML =
  `<div><b>${sites.length}</b><span>unique sites</span></div>` +
  `<div><b>${new Set(sites.map((s) => (communityOf(s.denom) || {}).name)).size}</b><span>communities</span></div>`;
renderCommunities();
render();
// Container size isn't final until layout settles; refit then.
let fitted = false;
new ResizeObserver(() => {
  map.invalidateSize();
  if (!fitted && map.getSize().x > 100) { fitted = true; render(); }
}).observe(document.getElementById("map"));

// Photo carousel inside popups + fullscreen lightbox
const photoUrl = (p, w) => `${PHOTO_BASE}${p[0]}=w${w}`;
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
  const show = () => {
    img.src = photoUrl(list[i], 600);
    count.textContent = `${i + 1} / ${list.length}`;
    g.classList.toggle("single", list.length < 2);
  };
  g.querySelector(".prev").onclick = () => { i = (i - 1 + list.length) % list.length; show(); };
  g.querySelector(".next").onclick = () => { i = (i + 1) % list.length; show(); };
  img.onclick = () => { box.querySelector("img").src = photoUrl(list[i], 1600); box.hidden = false; };
  show();
});
