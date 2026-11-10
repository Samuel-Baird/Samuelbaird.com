// Shared helpers for the map, photos and stats pages (loads after data.js).

const WIKI = "https://en.wikipedia.org/wiki/";
const wikiHref = (w) => !w ? "" : /^https?:/.test(w) ? w : WIKI + w;

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
  { name: "Presbyterian", match: ["Presbyterian"], color: "#c53030", listed: false },
  { name: "Eastern Orthodox (other jurisdictions)", match: ["Eastern Orthodox"], color: "#b7791f", listed: false },
  { name: "Community of Christ", match: ["Community of Christ"], color: "#dd6b20", listed: false },
  { name: "Other Latter Day Saint movements", match: ["Restoration (non-LDS)"], color: "#38a169", listed: false },
  { name: "Neo-Pentecostal", match: ["Neo-Pentecostal"], color: "#d69e2e", listed: false },
  { name: "Islam", match: ["Islam"], color: "#319795", listed: false },
  { name: "Other", match: ["Other"], color: "#718096", listed: false },
];

// Broad groupings for the "Show only" filter.
const GROUPS = [
  { key: "catholic", label: "Catholic" },
  { key: "lds", label: "LDS" },
  { key: "protestant", label: "Protestant" },
  { key: "restoration", label: "Restorationist" },
  { key: "orthodox", label: "Orthodox" },
  { key: "jewish", label: "Jewish" },
  { key: "other", label: "Other" },
];
const GROUP_OF = {
  Catholic: "catholic", LDS: "lds", "Greek Orthodox": "orthodox", Jewish: "jewish",
  Anglican: "protestant", Episcopalian: "protestant", Lutheran: "protestant", SBC: "protestant",
  Presbyterian: "protestant", "Neo-Pentecostal": "protestant", "Eastern Orthodox": "orthodox",
  SDA: "restoration", "Jehovah's Witnesses": "restoration",
  "Community of Christ": "restoration", "Restoration (non-LDS)": "restoration",
};
const groupOf = (denom) => GROUP_OF[denom] || (LEAF_BY_DENOM[denom] || {}).group || "other";
const communityOf = (denom) => COMMUNITIES.find((c) => c.match.includes(denom));
const colorOf = (denom) => (communityOf(denom) || {}).color || (LEAF_BY_DENOM[denom] || {}).color || "#718096";
const labelOf = (denom) => (communityOf(denom) || {}).name || (LEAF_BY_DENOM[denom] || {}).label || denom;

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

// Google Maps links. Skipped for events held outside a church building (JW gathering, UVU campus mass).
// Also skipped for Benbow Farm (private property).
const NO_MAPS = new Set(["jw", "uvu", "w-benbow"]);
const mapsQuery = (s) => encodeURIComponent(s.q || [s.name, s.city, s.state].filter(Boolean).join(", "));
const mapsUrl = (s) => `https://www.google.com/maps/search/?api=1&query=${mapsQuery(s)}`;
const mapsEmbedUrl = (s) => `https://www.google.com/maps?q=${mapsQuery(s)}&ll=${s.lat},${s.lon}&output=embed`;

// Visited sites, newest visit first inside each site.
const linksOf = (id) => ({ site: (PLACE_LINKS[id] || {}).site || "", wikiUrl: wikiHref((PLACE_LINKS[id] || {}).wiki) });
const SITES = Object.entries(PLACES).map(([id, [name, denom, city, state, lat, lon]]) => ({
  id, name, denom, city, state, country: COUNTRY, lat, lon, ...linksOf(id),
  visits: VISITS.filter((v) => v[1] === id).map(([date, , type, lang, note, video, photos]) => ({
    date, type, lang, note, video, photos, cat: categoryOf(type),
  })).sort((a, b) => b.date.localeCompare(a.date)),
})).filter((s) => s.visits.length);

const WISH = WISHLIST.map(([id, name, denom, city, state, country, lat, lon, note, q]) => ({
  id, name, denom, city, state, country, lat, lon, note, q, wish: true, visits: [], ...linksOf(id),
}));

// Distance from Provo, Utah (home base) in miles.
const PROVO = { lat: 40.2338, lon: -111.6585 };
const milesBetween = (a, b) => {
  const r = (d) => (d * Math.PI) / 180, dLat = r(b.lat - a.lat), dLon = r(b.lon - a.lon);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(r(a.lat)) * Math.cos(r(b.lat)) * Math.sin(dLon / 2) ** 2;
  return 3958.8 * 2 * Math.asin(Math.sqrt(h));
};
const milesFromProvo = (s) => milesBetween(PROVO, s);
const fmtMiles = (m) => (m < 10 ? m.toFixed(1) : Math.round(m).toLocaleString("en-US")) + " mi";

// Every photo with the visit it belongs to.
const ALL_PHOTOS = SITES.flatMap((s) => (PHOTOS[s.id] || []).map((p) => {
  const visit = s.visits.find((v) => v.date === p[3]) || s.visits[0];
  return { site: s, p, date: p[3], visit };
})).sort((a, b) => b.date.localeCompare(a.date));

// Faith tree for the stats page and the backend schema for traditions. Branches follow
// theapotheosisnarrative.wordpress.com/worldview-communities-sites-visited. Nothing is shown publicly until a
// leaf has a visited site (or is `listed`), so unvisited leaves are placeholders: to log a first visit, give
// the place a denomination equal to the leaf's label (or to the short key used by existing data, see `m`).
const GROUP_COLOR = { catholic: "#c05621", orthodox: "#b7791f", protestant: "#2c7a7b", restoration: "#38a169", jewish: "#00a3c4", other: "#718096" };
// spec: "Label" | { l: "Label", m: [denominations in the data] } | ["Group name", [specs...]]
const specLeaf = (spec, group) => {
  const label = typeof spec === "string" ? spec : spec.l;
  const match = typeof spec === "string" ? [spec] : spec.m || [spec.l];
  const c = COMMUNITIES.find((x) => x.match.some((m) => match.includes(m)));
  const obj = typeof spec === "string" ? {} : spec;
  const L = TRAD_LINKS[label] || {};
  return { label, match, group, wiki: wikiHref(L.w || obj.w), site: L.s || obj.s || "", kind: obj.k || "denomination", color: (c || {}).color || GROUP_COLOR[group] };
};
const specNode = (spec, group) =>
  Array.isArray(spec) ? { name: spec[0], children: spec[1].map((s) => specNode(s, group)) } : specLeaf(spec, group);
const branch = (name, group, specs) => ({ name, group, children: specs.map((s) => specNode(s, group)) });
const TREE = [
  { name: "Christian", children: [
    branch("Catholic", "catholic", [
      ["Latin tradition", [
        { l: "Latin (Roman) Catholic Church", m: ["Catholic"], w: "Latin_Church", s: "https://www.vatican.va/" },
        { l: "Traditional Latin Mass", k: "worship", w: "Tridentine_Mass", s: "https://fssp.org/" },
        { l: "Anglican Ordinariate (Latin Church)", w: "Personal_ordinariate", s: "https://ordinariate.net/" },
      ]],
      ["Byzantine tradition", [
        { l: "Ruthenian Byzantine Catholic", w: "Ruthenian_Greek_Catholic_Church", s: "https://archpitt.org/" },
        { l: "Ukrainian Greek Catholic", w: "Ukrainian_Greek_Catholic_Church", s: "https://ugcc.ua/" },
        { l: "Melkite Greek Catholic", w: "Melkite_Greek_Catholic_Church", s: "https://melkite.org/" },
        { l: "Romanian Greek Catholic", w: "Romanian_Greek_Catholic_Church" },
        { l: "Russian Greek Catholic", w: "Russian_Greek_Catholic_Church" },
        { l: "Greek Byzantine Catholic", w: "Greek_Byzantine_Catholic_Church" },
        { l: "Slovak Greek Catholic", w: "Slovak_Greek_Catholic_Church" },
        { l: "Hungarian Greek Catholic", w: "Hungarian_Greek_Catholic_Church" },
        { l: "Bulgarian Greek Catholic", w: "Bulgarian_Greek_Catholic_Church" },
        { l: "Macedonian Greek Catholic", w: "Macedonian_Greek_Catholic_Church" },
        { l: "Belarusian Greek Catholic", w: "Belarusian_Greek_Catholic_Church" },
        { l: "Albanian Greek Catholic", w: "Albanian_Greek_Catholic_Church" },
        { l: "Italo-Albanian Catholic", w: "Italo-Albanian_Catholic_Church" },
        { l: "Greek Catholic Church of Croatia and Serbia", w: "Greek_Catholic_Church_of_Croatia_and_Serbia" },
      ]],
      ["Other Eastern Catholic traditions", [
        { l: "Maronite Catholic (West Syriac)", w: "Maronite_Church" },
        { l: "Syriac Catholic (West Syriac)", w: "Syriac_Catholic_Church" },
        { l: "Syro-Malankara Catholic (West Syriac)", w: "Syro-Malankara_Catholic_Church" },
        { l: "Chaldean Catholic (East Syriac)", w: "Chaldean_Catholic_Church" },
        { l: "Syro-Malabar Catholic (East Syriac)", w: "Syro-Malabar_Catholic_Church" },
        { l: "Coptic Catholic (Alexandrian)", w: "Coptic_Catholic_Church" },
        { l: "Ethiopian Catholic (Alexandrian)", w: "Ethiopian_Catholic_Church" },
        { l: "Eritrean Catholic (Alexandrian)", w: "Eritrean_Catholic_Church" },
        { l: "Armenian Catholic (Armenian)", w: "Armenian_Catholic_Church" },
      ]],
      "Gnostic Catholic",
    ]),
    branch("Orthodox", "orthodox", [
      ["Eastern Orthodox", [{ l: "Greek Orthodox", m: ["Greek Orthodox"] }, { l: "Eastern Orthodox (other jurisdictions)", m: ["Eastern Orthodox"] }, "Russian Orthodox (Old Believer)"]],
      ["Oriental Orthodox", ["Armenian Apostolic"]],
    ]),
    branch("Protestant", "protestant", [
      ["Anglican", [{ l: "The Episcopal Church (TEC)", m: ["Episcopalian"] }, { l: "Anglican Church in North America (ACNA)", m: ["Anglican"] }]],
      ["Baptist", [{ l: "Southern Baptist Convention (SBC)", m: ["SBC"] }, "American Baptist Churches USA (ABCUSA)", "Independent Fundamentalist Baptist (IFB)", "Reformed Baptist (Calvinist)"]],
      ["Presbyterian", [{ l: "Presbyterian Church (U.S.A.)", m: ["Presbyterian"] }, "Presbyterian Church in America (PCA)", "Orthodox Presbyterian Church (OPC)"]],
      ["Lutheran", [{ l: "Evangelical Lutheran Church in America (ELCA)", m: ["Lutheran"] }, "Lutheran Church \u2013 Missouri Synod", "Lutheran Congregations in Mission for Christ (LCMC)", "Wisconsin Evangelical Lutheran Synod (WELS)", "Evangelical Lutheran Synod (ELS)"]],
      ["Methodist", ["United Methodist Church (UMC)", "African Methodist Episcopal Church (AME)"]],
      "United Church of Christ (UCC)",
      "Christian Church (Disciples of Christ) (DOC)",
      ["Non-Denominational Evangelical", ["Charismatic Non-Denominational"]],
      { l: "Neo-Pentecostal", m: ["Neo-Pentecostal"] },
      "Church of the Nazarene",
      ["Molokan (Spiritual Christian)", ["First Russian Christian Molokan Church"]],
      ["Radical Pietist", ["Society of Separatists of Zoar"]],
    ]),
    branch("Restorationist and/or Non-Trinitarian", "restoration", [
      { l: "Jehovah's Witnesses", m: ["Jehovah's Witnesses"] },
      "Christian Scientist",
      "Oneness Pentecostal",
      "United Society of Believers in Christ's Second-Coming (Shakers)",
      ["Adventist", [{ l: "Seventh-day Adventist", m: ["SDA"] }, "Millerite"]],
      ["Swedenborgian", ["Boston Society of the New Jerusalem"]],
      "Oneida Community",
      "Iglesia Ni Cristo",
      "Iglesia La Luz del Mundo",
      "World Church of Messiah",
      ["Latter Day Saint", [
        { l: "The Church of Jesus Christ of Latter-day Saints (LDS)", m: ["LDS"] },
        { l: "Fundamentalist Church of Jesus Christ of Latter-day Saints (FLDS)", m: ["FLDS"] },
        "Independent Fundamentalist Mormon",
        { l: "Community of Christ (CoC)", m: ["Community of Christ"] },
        "Reorganized Church of Jesus Christ of Latter-day Saints Branch (RLDS)",
        "The Remnant (Snufferite)",
        "The Church of Jesus Christ (Bickertonite)",
        "The Restoration Church of Jesus Christ (RCJC)",
        { l: "Other Latter Day Saint movements", m: ["Restoration (non-LDS)"] },
      ]],
    ]),
    branch("Gnostic Christian", "other", [
      { l: "Ecclesia Gnostica (sacramental Christian Gnosticism)", w: "Ecclesia_Gnostica" },
      { l: "Apostolic Johannite Church (Johannine Christianity)", w: "Apostolic_Johannite_Church", s: "https://apostolicjohannite.org/" },
      "\u00c9glise Gnostique Apostolique (French Gnostic revival)",
      "Ecclesia Gnostica Mysteriorum (mystical, less dogmatic)",
      "Ecclesia Pistis Sophia (Sophian; Christian Kabbalah)",
      "Ecclesia Sophiana (Cathar influences, Syriac-style liturgy)",
      "Gnostic Church of Valentinus (Valentinian revival, Austin TX)",
    ]),
  ] },
  branch("Jewish", "jewish", [{ l: "Jewish (general)", m: ["Jewish"] }, "Reform", "Conservative"]),
  branch("Islamic", "other", [{ l: "Islam (general)", m: ["Islam"] }, "Sunni", "Shia", "Sufi", "Nation of Islam"]),
  branch("Middle-Eastern, Additional", "other", ["Mandaean", "Zoroastrian", "Bah\u00e1\u02bc\u00ed Faith"]),
];
// Lookup by denomination, and make sure every leaf has a COMMUNITIES entry (colors, filters).
const LEAVES = [];
(function walk(nodes, group) { for (const n of nodes) { if (n.children) walk(n.children, n.group || group); else LEAVES.push({ ...n, group: n.group || group }); } })(TREE);
const LEAF_BY_DENOM = {};
for (const lf of LEAVES) for (const m of lf.match) LEAF_BY_DENOM[m] = lf;
for (const lf of LEAVES) {
  if (!COMMUNITIES.some((c) => c.match.some((m) => lf.match.includes(m)))) COMMUNITIES.push({ name: lf.label, match: lf.match, color: lf.color, listed: false });
}

// Visited / to-visit helpers shared by the map and the Traditions page.
const leafSites = (leaf) => SITES.filter((s) => leaf.match.includes(s.denom));
const leafVisited = (leaf) => leafSites(leaf).length > 0;
// Wishlist places for a tradition, nearest to Provo first.
const nearestWish = (leaf, n = 3) => WISH.filter((w) => leaf.match.includes(w.denom))
  .map((w) => ({ ...w, miles: milesFromProvo(w) })).sort((a, b) => a.miles - b.miles).slice(0, n);

// Marker glyph per tradition (see GLYPHS in app.js).
const glyphOf = (denom) => {
  const g = groupOf(denom);
  if (g === "orthodox") return "orthodox";
  if (g === "catholic" || g === "protestant") return "cross";
  if (g === "lds") return "spire";
  if (g === "jewish") return "star";
  if (/islam|sunni|shia|sufi/i.test(denom)) return "crescent";
  if (g === "restoration") return "flame";
  return "sun";
};

// Inline SVG glyphs (24x24 viewBox, drawn in currentColor).
const GLYPHS = {
  cross: '<path d="M12 3.5v17M6.5 9h11" stroke-width="2.6" fill="none"/>',
  orthodox: '<path d="M12 3v18M8.5 6.4h7M6 11.2h12M9 17.6l6-2.4" stroke-width="2.1" fill="none"/>',
  spire: '<path d="M12 2.5l3.3 18.5H8.7z" stroke="none"/>',
  star: '<path d="M12 4l7 12H5zM12 20L5 8h14z" stroke-width="1.8" fill="none"/>',
  crescent: '<path d="M15.5 4a8 8 0 1 0 0 16 6.6 6.6 0 1 1 0-16z" stroke="none"/>',
  flame: '<path d="M12 2.5c.9 4.2 5.2 5.8 5.2 10.5a5.2 5.2 0 0 1-10.4 0c0-2 .9-3.2 2-4.2.2 1.5.9 2.2 1.6 2.4C10.2 8.6 10.9 5.4 12 2.5z" stroke="none"/>',
  sun: '<circle cx="12" cy="12" r="4.2" stroke="none"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1" stroke-width="1.8" fill="none"/>',
};
const glyphSvg = (key, px = 16) => `<svg class="glyph" viewBox="0 0 24 24" width="${px}" height="${px}" fill="currentColor" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${GLYPHS[key] || GLYPHS.sun}</svg>`;
const GLYPH_KEY = [["cross", "Catholic / Protestant"], ["orthodox", "Orthodox"], ["spire", "LDS"], ["flame", "Restorationist"], ["star", "Jewish"], ["crescent", "Islamic"], ["sun", "Other"]];
const slugify = (t) => t.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const leafAnchor = (denom) => { const lf = LEAF_BY_DENOM[denom]; return lf ? slugify(lf.label) : ""; };
