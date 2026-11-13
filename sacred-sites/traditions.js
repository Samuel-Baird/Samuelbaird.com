// Traditions page: progress by branch, then every tradition with links, visited places or the nearest places to visit.
const allVisits = SITES.flatMap((s) => s.visits.map((v) => ({ ...v, site: s })));
const services = allVisits.filter((v) => isService(v.type));
const plural = (n, w) => `${n} ${w}${n === 1 ? "" : "s"}`;
const dot = (color) => `<span class="dot" style="background:${color}"></span>`;
const ext = (href, text) => `<a class="btn" href="${esc(href)}" target="_blank" rel="noopener">${text} &#8599;</a>`;
const $ = (id) => document.getElementById(id);

// ---- summary strip ----
const leafList = (n) => (n.match ? [n] : n.children.flatMap(leafList));
const visitedCount = LEAVES.filter(leafVisited).length;
$("big").innerHTML = [
  [SITES.length, "sites visited"],
  [`${visitedCount}<small> / ${LEAVES.length}</small>`, "traditions visited"],
  [new Set(SITES.map((s) => s.country)).size, "countries"],
  [services.length, "worship services"],
].map(([n, l]) => `<div><b>${n}</b><span>${l}</span></div>`).join("");

// ---- progress by branch (the Christian families sit side by side with the other religions) ----
const BRANCHES = TREE.flatMap((n) => (n.name === "Christian" ? n.children : [n]));
$("branches").innerHTML = BRANCHES.map((n) => {
  const ls = leafList(n), v = ls.filter(leafVisited).length, color = (ls[0] || {}).color || "#718096";
  return `<a class="branch" href="#${slugify(n.name)}" style="--c:${color}"><span>${esc(n.name)}</span><i><u style="width:${ls.length ? (v / ls.length) * 100 : 0}%"></u></i><small>${v} / ${ls.length}</small></a>`;
}).join("");

// ---- tree ----
let filter = "all";
const keep = (leaf) => filter === "all" || (filter === "visited") === leafVisited(leaf);
function build(n) {
  if (n.match) return keep(n) ? n : null;
  const kids = n.children.map(build).filter(Boolean);
  return kids.length ? { ...n, kids, count: kids.reduce((t, k) => t + (k.kids ? k.count : 1), 0) } : null;
}
const placeLinks = (s) => [s.site && ext(s.site, "Website"), s.wikiUrl && ext(s.wikiUrl, "Wikipedia"),
  !NO_MAPS.has(s.id) && ext(mapsUrl(s), "Google Maps")].filter(Boolean).join("");
function visitedRow(s) {
  const first = s.visits[s.visits.length - 1].date;
  return `<li><div><b>${esc(s.name)}</b><small>${esc(s.city)}, ${esc(s.state)} · ${plural(s.visits.length, "visit")} · first ${fmt(first)}</small></div><div class="plinks"><a class="btn" href="/sacred-sites?site=${s.id}">On map</a>${placeLinks(s)}</div></li>`;
}
function nearRow(s) {
  const where = [s.city, s.state, s.country].filter(Boolean).join(", ");
  return `<li><div><b>${esc(s.name)}</b><small><em class="miles">${fmtMiles(s.miles)}</em> from Provo · ${esc(where)}${s.note && !/^⭐?\s*$/.test(s.note) ? " · " + esc(s.note.replace(/^⭐\s*/, "")) : ""}</small></div><div class="plinks"><a class="btn" href="/sacred-sites?site=${s.id}">On map</a>${placeLinks(s)}</div></li>`;
}
function leafHtml(n) {
  const sites = leafSites(n).sort((a, b) => a.name.localeCompare(b.name)), visited = sites.length > 0;
  const links = [n.wiki && ext(n.wiki, "Wikipedia"), n.site && ext(n.site, "Official site")].filter(Boolean).join("");
  let body;
  if (visited) body = `<ul class="places">${sites.map(visitedRow).join("")}</ul>`;
  else {
    const near = nearestWish(n, 3);
    body = near.length ? `<p class="nearhead">Nearest to visit</p><ul class="places">${near.map(nearRow).join("")}</ul>`
      : `<p class="hint pad">${esc(TRAD_NOTES[n.label] || "No place saved yet.")}</p>`;
  }
  const status = visited ? `<span class="t-count ok">${plural(sites.length, "site")}</span>` : `<span class="t-count">to visit</span>`;
  return `<details class="tleaf${visited ? " is-visited" : ""}" id="${slugify(n.label)}"><summary>${dot(n.color)}<span class="t-name">${esc(n.label)}</span>${n.kind === "worship" ? '<em class="kind-tag">Worship tradition</em>' : ""}${status}</summary>${links ? `<div class="tlinks">${links}</div>` : ""}${body}</details>`;
}
function groupHtml(n, depth) {
  if (n.match) return leafHtml(n);
  const tag = `h${Math.min(depth + 2, 5)}`;
  return `<section class="tgroup d${depth}" id="${slugify(n.name)}"><${tag}>${esc(n.name)}<small>${plural(n.count, "tradition")}</small></${tag}>${n.kids.map((k) => groupHtml(k, depth + 1)).join("")}</section>`;
}
const treeEl = $("tree");
const drawTree = () => {
  treeEl.innerHTML = TREE.map(build).filter(Boolean).map((n) => groupHtml(n, 1)).join("") || '<p class="hint">Nothing matches this filter.</p>';
};
drawTree();
const openHash = () => {
  const el = location.hash && document.getElementById(decodeURIComponent(location.hash.slice(1)));
  if (!el) return;
  if (el.tagName === "DETAILS") el.open = true;
  el.scrollIntoView({ block: "start" });
};
openHash(); addEventListener("hashchange", openHash);

document.querySelectorAll("#tfilter .chip").forEach((b) => b.onclick = () => {
  filter = b.dataset.f;
  document.querySelectorAll("#tfilter .chip").forEach((c) => c.setAttribute("aria-pressed", String(c === b)));
  drawTree();
});
$("expand").onclick = () => treeEl.querySelectorAll("details").forEach((d) => d.open = true);
$("collapse").onclick = () => treeEl.querySelectorAll("details").forEach((d) => d.open = false);

// ---- visits per year (every logged visit, repeats included) ----
const byYear = {};
for (const v of allVisits) byYear[v.date.slice(0, 4)] = (byYear[v.date.slice(0, 4)] || 0) + 1;
const max = Math.max(...Object.values(byYear));
$("years").innerHTML = Object.entries(byYear).sort().map(([y, n]) =>
  `<div class="bar-row"><span>${y}</span><div class="bar"><i style="width:${(n / max) * 100}%"></i></div><b>${n}</b></div>`).join("");
$("notes").textContent =
  `Worship services = church services and feasts (${services.length}). Temple ordinance sessions and open houses are logged as visits but not counted as services. Sacred sites count each place once. A tradition counts as visited once any site I have been to belongs to it.`;
