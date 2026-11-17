// Photos page: a grid of every matched photo; click one for the details.
let group = null, shown = [], current = 0;
const $ = (id) => document.getElementById(id);
const viewer = $("viewer"), vimg = viewer.querySelector("img");

function renderGrid() {
  shown = ALL_PHOTOS.filter((x) => !group || groupOf(x.site.denom) === group);
  $("count").textContent = `${shown.length} photo${shown.length === 1 ? "" : "s"}${group ? "" : " · newest first"}`;
  $("grid").innerHTML = shown.map((x, i) =>
    `<li><button data-i="${i}" aria-label="${esc(x.site.name)}, ${fmt(x.date)}"><img src="${photoUrl(x.p, 400)}" alt="" loading="lazy" referrerpolicy="no-referrer">` +
    `<span><b>${esc(x.site.name)}</b><small>${fmt(x.date)}</small></span></button></li>`).join("");
  $("groups").querySelectorAll(".chip").forEach((b) => b.setAttribute("aria-pressed", String((b.dataset.g || null) === group)));
}

function open(i) {
  current = (i + shown.length) % shown.length;
  const x = shown[current];
  vimg.src = photoUrl(x.p, 1600);
  vimg.alt = x.site.name;
  $("details").innerHTML =
    `<h3>${esc(x.site.name)}</h3>` +
    `<div>${esc(x.site.city)}, ${esc(x.site.state)}, ${esc(x.site.country)} · ${esc(labelOf(x.site.denom))}</div>` +
    `<div>${fmt(x.date)} · ${esc(x.visit.type)} · <span class="cat cat-${x.visit.cat}">${esc(categoryLabel(x.visit.cat))}</span></div>` +
    (x.visit.note ? `<div class="note">${esc(x.visit.note)}</div>` : "") +
    `<a href="/sacred-sites?site=${encodeURIComponent(x.site.id)}">See on the map &rarr;</a>`;
  viewer.hidden = false;
}

$("groups").innerHTML = `<button class="chip" data-g="">All</button>` + GROUPS.map((g) => {
  const has = ALL_PHOTOS.some((x) => groupOf(x.site.denom) === g.key);
  return `<button class="chip${has ? "" : " zero"}" data-g="${g.key}">${g.label}</button>`;
}).join("");
$("groups").onclick = (e) => { const b = e.target.closest(".chip"); if (b) { group = b.dataset.g || null; renderGrid(); } };
$("grid").onclick = (e) => { const b = e.target.closest("button[data-i]"); if (b) open(+b.dataset.i); };
viewer.querySelector(".close").onclick = () => { viewer.hidden = true; };
viewer.querySelector(".prev").onclick = () => open(current - 1);
viewer.querySelector(".next").onclick = () => open(current + 1);
viewer.onclick = (e) => { if (e.target === viewer) viewer.hidden = true; };
document.addEventListener("keydown", (e) => {
  if (viewer.hidden) return;
  if (e.key === "Escape") viewer.hidden = true;
  if (e.key === "ArrowLeft") open(current - 1);
  if (e.key === "ArrowRight") open(current + 1);
});
renderGrid();
