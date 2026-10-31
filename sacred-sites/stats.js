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
function build(n) {
  if (n.match) {
    const sites = SITES.filter((s) => n.match.includes(s.denom)).sort((a, b) => a.name.localeCompare(b.name));
    const pending = COMMUNITIES.some((c) => c.listed && listedNames.has(c.name) && c.match.some((m) => n.match.includes(m)));
    return sites.length || pending ? { ...n, sites } : null;
  }
  const kids = n.children.map(build).filter(Boolean);
  return kids.length ? { ...n, kids, count: kids.reduce((t, x) => t + (x.sites ? x.sites.length : x.count), 0) } : null;
}
function placeRow(s) {
  const first = s.visits[s.visits.length - 1].date;
  const link = NO_MAPS.has(s.id) ? "" : `<a href="${mapsUrl(s)}" target="_blank" rel="noopener">Google Maps</a>`;
  return `<li><div><b>${esc(s.name)}</b><small>${esc(s.city)}, ${esc(s.state)} · ${plural(s.visits.length, "visit")} · first ${fmt(first)}</small></div>${link}</li>`;
}
function render(n, depth) {
  if (n.sites) {
    const body = n.sites.length ? `<ul class="places">${n.sites.map(placeRow).join("")}</ul>` : `<p class="hint">Visited, not yet logged.</p>`;
    return `<details class="tleaf"><summary>${dot(n.color)}<span class="t-name">${esc(n.label)}</span><span class="t-count">${n.sites.length ? plural(n.sites.length, "site") : "not yet logged"}</span></summary>${body}</details>`;
  }
  const tag = `h${Math.min(depth + 2, 5)}`;
  return `<section class="tgroup d${depth}"><${tag}>${esc(n.name)}${n.count ? `<small>${plural(n.count, "site")}</small>` : ""}</${tag}>${n.kids.map((k) => render(k, depth + 1)).join("")}</section>`;
}
document.getElementById("tree").innerHTML = TREE.map(build).filter(Boolean).map((n) => render(n, 1)).join("");

// Visits per year (every logged visit, repeats included).
const byYear = {};
for (const v of allVisits) byYear[v.date.slice(0, 4)] = (byYear[v.date.slice(0, 4)] || 0) + 1;
const max = Math.max(...Object.values(byYear));
document.getElementById("years").innerHTML = Object.entries(byYear).sort().map(([y, n]) =>
  `<div class="bar-row"><span>${y}</span><div class="bar"><i style="width:${(n / max) * 100}%"></i></div><b>${n}</b></div>`).join("");

document.getElementById("notes").textContent =
  `Worship services = church services and feasts (${services.length}). Temple ordinance sessions and open houses are logged as visits but not counted as services. ` +
  `Sacred sites count each place once.`;
