// Stats page: totals plus a line for each tradition visited.
const allVisits = SITES.flatMap((s) => s.visits.map((v) => ({ ...v, site: s })));
const services = allVisits.filter((v) => isService(v.type));
const listed = COMMUNITIES.filter((c) => c.listed).map((c) => {
  const sites = SITES.filter((s) => c.match.includes(s.denom));
  const visits = allVisits.filter((v) => c.match.includes(v.site.denom));
  const dates = visits.map((v) => v.date).sort();
  return {
    c, sites, visits, services: visits.filter((v) => isService(v.type)),
    first: dates[0], last: dates[dates.length - 1],
  };
});

const big = [
  [SITES.length, "Sacred sites visited"],
  [listed.length, "Faith traditions"],
  [new Set(SITES.map((s) => s.country)).size, "Countries"],
  [services.length, "Worship services attended"],
];
document.getElementById("big").innerHTML = big.map(([n, l]) => `<div><b>${n}</b><span>${l}</span></div>`).join("");

const dot = (color) => `<span class="dot" style="background:${color}"></span>`;
const plural = (n, w) => `${n} ${w}${n === 1 ? "" : "s"}`;
const listedNames = new Set(listed.map((t) => t.c.name));

// Build the tree, dropping branches with nothing visited.
let showWish = false;
function build(n) {
  if (n.match) {
    if (showWish) return { ...n, sites: SITES.filter((s) => n.match.includes(s.denom)).sort((a, b) => a.name.localeCompare(b.name)) };
    const sites = SITES.filter((s) => n.match.includes(s.denom)).sort((a, b) => a.name.localeCompare(b.name));
    const pending = COMMUNITIES.some((c) => c.listed && listedNames.has(c.name) && c.match.some((m) => n.match.includes(m)));
    return sites.length || pending ? { ...n, sites } : null;
  }
  const kids = n.children.map(build).filter(Boolean);
  return kids.length || (showWish && n.children.length) ? { ...n, kids, count: kids.reduce((t, x) => t + (x.sites ? x.sites.length : x.count), 0) } : null;
}
function placeRow(s) {
  const first = s.visits[s.visits.length - 1].date;
  const link = NO_MAPS.has(s.id) ? "" : `<a href="${mapsUrl(s)}" target="_blank" rel="noopener">Google Maps</a>`;
  return `<li><div><b>${esc(s.name)}</b><small>${esc(s.city)}, ${esc(s.state)} · ${plural(s.visits.length, "visit")} · first ${fmt(first)}</small></div>${link}</li>`;
}
function render(n, depth) {
  if (n.sites) {
    const wish = showWish && !n.sites.length && !n.match.some((m) => listedNames.has(labelOf(m)));
    const body = wish ? `<p class="hint">Wishlist: not visited yet.</p>` : n.sites.length ? `<ul class="places">${n.sites.map(placeRow).join("")}</ul>` : `<p class="hint">Visited, not yet logged.</p>`;
    return `<details class="tleaf"><summary>${dot(n.color)}<span class="t-name"${n.wiki || n.site ? ` data-wiki="${esc(n.wiki)}" data-site="${esc(n.site)}" tabindex="0"` : ""}>${esc(n.label)}</span>${n.kind === "worship" ? '<em class="kind-tag">Worship tradition</em>' : ""}<span class="t-count">${wish ? '<em class="wish-tag">wishlist</em>' : n.sites.length ? plural(n.sites.length, "site") : "not yet logged"}</span></summary>${body}</details>`;
  }
  const tag = `h${Math.min(depth + 2, 5)}`;
  return `<section class="tgroup d${depth}"><${tag}>${esc(n.name)}${n.count ? `<small>${plural(n.count, "site")}</small>` : ""}</${tag}>${n.kids.map((k) => render(k, depth + 1)).join("")}</section>`;
}
const treeEl = document.getElementById("tree");
const drawTree = () => { treeEl.innerHTML = TREE.map(build).filter(Boolean).map((n) => render(n, 1)).join(""); };
drawTree();
document.getElementById("wish-toggle").addEventListener("change", (e) => { showWish = e.target.checked; hidePop(); drawTree(); });

// Hover/focus card with outside links for a tradition.
const pop = document.createElement("div");
pop.className = "tpop"; pop.hidden = true; document.body.appendChild(pop);
let popTimer;
function hidePop() { clearTimeout(popTimer); pop.hidden = true; }
function showPop(el) {
  clearTimeout(popTimer);
  const links = [["Wikipedia", el.dataset.wiki], ["Official website", el.dataset.site]].filter(([, u]) => u);
  pop.innerHTML = `<b>${esc(el.textContent)}</b>` + links.map(([t, u]) => `<a href="${esc(u)}" target="_blank" rel="noopener">${t} &#8599;</a>`).join("");
  pop.hidden = false;
  const r = el.getBoundingClientRect();
  pop.style.left = Math.max(8, Math.min(r.left + scrollX, scrollX + innerWidth - pop.offsetWidth - 8)) + "px";
  pop.style.top = r.bottom + scrollY + 4 + "px";
}
const later = () => { popTimer = setTimeout(hidePop, 250); };
treeEl.addEventListener("mouseover", (e) => { const t = e.target.closest(".t-name[data-wiki]"); if (t) showPop(t); });
treeEl.addEventListener("mouseout", (e) => { if (e.target.closest(".t-name[data-wiki]")) later(); });
treeEl.addEventListener("focusin", (e) => { const t = e.target.closest(".t-name[data-wiki]"); if (t) showPop(t); });
treeEl.addEventListener("focusout", later);
pop.addEventListener("mouseenter", () => clearTimeout(popTimer));
pop.addEventListener("mouseleave", later);
document.addEventListener("keydown", (e) => { if (e.key === "Escape") hidePop(); });

// Visits per year (every logged visit, repeats included).
const byYear = {};
for (const v of allVisits) byYear[v.date.slice(0, 4)] = (byYear[v.date.slice(0, 4)] || 0) + 1;
const max = Math.max(...Object.values(byYear));
document.getElementById("years").innerHTML = Object.entries(byYear).sort().map(([y, n]) =>
  `<div class="bar-row"><span>${y}</span><div class="bar"><i style="width:${(n / max) * 100}%"></i></div><b>${n}</b></div>`).join("");

document.getElementById("notes").textContent =
  `Worship services = church services and feasts (${services.length}). Temple ordinance sessions and open houses are logged as visits but not counted as services. ` +
  `Sacred sites count each place once.`;
