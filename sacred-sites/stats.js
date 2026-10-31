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
const logged = listed.filter((t) => t.sites.length);
const unlogged = listed.filter((t) => !t.sites.length);

const big = [
  [SITES.length, "Sacred sites visited"],
  [listed.length, "Faith traditions"],
  [new Set(SITES.map((s) => s.country)).size, "Countries"],
  [services.length, "Worship services attended"],
];
document.getElementById("big").innerHTML = big.map(([n, l]) => `<div><b>${n}</b><span>${l}</span></div>`).join("");

const dot = (c) => `<span class="dot" style="background:${c.color}"></span>`;
document.getElementById("traditions").innerHTML = [...logged].sort((a, b) => b.sites.length - a.sites.length).map((t) => {
  const bits = [`${t.sites.length} site${t.sites.length > 1 ? "s" : ""}`];
  if (t.services.length) bits.push(`${t.services.length} service${t.services.length > 1 ? "s" : ""}`);
  const other = t.visits.length - t.services.length;
  if (other) bits.push(`${other} other visit${other > 1 ? "s" : ""}`);
  const when = t.first === t.last ? `visited ${fmt(t.first)}` : `${fmt(t.first)} – ${fmt(t.last)}`;
  return `<li><div class="t-name">${dot(t.c)}${esc(t.c.name)}</div><div class="t-meta">${bits.join(" · ")}</div><div class="t-when">${when}</div></li>`;
}).join("") + unlogged.map((t) =>
  `<li class="muted"><div class="t-name">${dot(t.c)}${esc(t.c.name)}</div><div class="t-meta">visited · not yet logged</div><div class="t-when"></div></li>`).join("");

// Visits per year (every logged visit, repeats included).
const byYear = {};
for (const v of allVisits) byYear[v.date.slice(0, 4)] = (byYear[v.date.slice(0, 4)] || 0) + 1;
const max = Math.max(...Object.values(byYear));
document.getElementById("years").innerHTML = Object.entries(byYear).sort().map(([y, n]) =>
  `<div class="bar-row"><span>${y}</span><div class="bar"><i style="width:${(n / max) * 100}%"></i></div><b>${n}</b></div>`).join("");

document.getElementById("notes").textContent =
  `Worship services = church services and feasts (${services.length}). Temple ordinance sessions and open houses are logged as visits but not counted as services. ` +
  `Sacred sites count each place once.`;
