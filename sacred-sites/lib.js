// Shared helpers for the map, photos and stats pages (loads after data.js).

// Traditions as listed on the site. `match` = denominations in the data; `listed` = shown in the sidebar/stats.
const COMMUNITIES = [
  { name: "Roman Catholic", match: ["Catholic"], color: "#c05621", listed: true },
  { name: "Greek Orthodox", match: ["Greek Orthodox"], color: "#b7791f", listed: true },
  { name: "Anglican (ACNA)", match: ["Anglican"], color: "#6b46c1", listed: true },
  { name: "Southern Baptist Convention (SBC)", match: ["SBC"], color: "#2c7a7b", listed: true },
  { name: "Lutheran (ELCA)", match: ["Lutheran"], color: "#2f855a", listed: true },
  { name: "Jehovah's Witnesses", match: ["Jehovah's Witnesses"], color: "#4a5568", listed: true },
  { name: "The Church of Jesus Christ of Latter-day Saints (LDS)", match: ["LDS"], color: "#2b6cb0", listed: true },
  { name: "Episcopal", match: ["Episcopalian"], color: "#9f7aea", listed: true },
  { name: "Seventh-day Adventist", match: ["SDA"], color: "#d53f8c", listed: true },
  // Not visited yet; used by the wishlist.
  { name: "Jewish", match: ["Jewish"], color: "#00a3c4", listed: false },
  { name: "Other", match: ["Other"], color: "#718096", listed: false },
];

// Broad groupings for the "Show only" filter.
const GROUPS = [
  { key: "catholic", label: "Catholic" },
  { key: "lds", label: "LDS" },
  { key: "protestant", label: "Protestant" },
  { key: "orthodox", label: "Orthodox" },
  { key: "jewish", label: "Jewish" },
  { key: "other", label: "Other" },
];
const GROUP_OF = {
  Catholic: "catholic", LDS: "lds", "Greek Orthodox": "orthodox", Jewish: "jewish",
  Anglican: "protestant", Episcopalian: "protestant", Lutheran: "protestant", SDA: "protestant", SBC: "protestant",
};
const groupOf = (denom) => GROUP_OF[denom] || "other";
const communityOf = (denom) => COMMUNITIES.find((c) => c.match.includes(denom));
const colorOf = (denom) => (communityOf(denom) || {}).color || "#718096";
const labelOf = (denom) => (communityOf(denom) || {}).name || denom;

// What kind of visit it was.
const CATEGORIES = [
  { key: "worship", label: "Attended worship" },
  { key: "interior", label: "Toured interior" },
  { key: "grounds", label: "Visited grounds" },
  { key: "historic", label: "Historical site" },
];
const categoryOf = (type) =>
  /open house|tour/i.test(type) ? "interior" : /grounds/i.test(type) ? "grounds" : /histor/i.test(type) ? "historic" : "worship";
const categoryLabel = (key) => (CATEGORIES.find((c) => c.key === key) || {}).label || key;
// "Worship services" = church services and feasts (temple ordinances are counted separately).
const isService = (type) => /^(worship service|feast\/holiday)$/i.test(type);

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const fmt = (iso) => new Date(iso + "T12:00:00").toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
const photoUrl = (p, w) => `${PHOTO_BASE}${p[0]}=w${w}`;

// Visited sites, newest visit first inside each site.
const SITES = Object.entries(PLACES).map(([id, [name, denom, city, state, lat, lon]]) => ({
  id, name, denom, city, state, country: COUNTRY, lat, lon,
  visits: VISITS.filter((v) => v[1] === id).map(([date, , type, lang, note, video, photos]) => ({
    date, type, lang, note, video, photos, cat: categoryOf(type),
  })).sort((a, b) => b.date.localeCompare(a.date)),
})).filter((s) => s.visits.length);

const WISH = WISHLIST.map(([id, name, denom, city, state, country, lat, lon, note]) => ({
  id, name, denom, city, state, country, lat, lon, note, wish: true, visits: [],
}));

// Every photo with the visit it belongs to.
const ALL_PHOTOS = SITES.flatMap((s) => (PHOTOS[s.id] || []).map((p) => {
  const visit = s.visits.find((v) => v.date === p[3]) || s.visits[0];
  return { site: s, p, date: p[3], visit };
})).sort((a, b) => b.date.localeCompare(a.date));
