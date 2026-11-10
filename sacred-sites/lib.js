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
const SITES = Object.entries(PLACES).map(([id, [name, denom, city, state, lat, lon]]) => ({
  id, name, denom, city, state, country: COUNTRY, lat, lon,
  visits: VISITS.filter((v) => v[1] === id).map(([date, , type, lang, note, video, photos]) => ({
    date, type, lang, note, video, photos, cat: categoryOf(type),
  })).sort((a, b) => b.date.localeCompare(a.date)),
})).filter((s) => s.visits.length);

const WISH = WISHLIST.map(([id, name, denom, city, state, country, lat, lon, note, q]) => ({
  id, name, denom, city, state, country, lat, lon, note, q, wish: true, visits: [],
}));

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
const WIKI = "https://en.wikipedia.org/wiki/";
const specLeaf = (spec, group) => {
  const label = typeof spec === "string" ? spec : spec.l;
  const match = typeof spec === "string" ? [spec] : spec.m || [spec.l];
  const c = COMMUNITIES.find((x) => x.match.some((m) => match.includes(m)));
  const obj = typeof spec === "string" ? {} : spec;
  return { label, match, group, wiki: obj.w ? WIKI + obj.w : "", site: obj.s || "", color: (c || {}).color || GROUP_COLOR[group] };
};
const specNode = (spec, group) =>
  Array.isArray(spec) ? { name: spec[0], children: spec[1].map((s) => specNode(s, group)) } : specLeaf(spec, group);
const branch = (name, group, specs) => ({ name, group, children: specs.map((s) => specNode(s, group)) });
const TREE = [
  { name: "Christian", children: [
    branch("Catholic", "catholic", [
      ["Latin tradition", [
        { l: "Latin (Roman) Catholic Church", m: ["Catholic"], w: "Latin_Church", s: "https://www.vatican.va/" },
        { l: "Traditional Latin Mass (worship experience)", w: "Tridentine_Mass", s: "https://fssp.org/" },
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
      ["Eastern Orthodox", [{ l: "Greek Orthodox", m: ["Greek Orthodox"] }, "Russian Orthodox (Old Believer)"]],
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
  ] },
  branch("Jewish", "jewish", [{ l: "Jewish (general)", m: ["Jewish"] }, "Reform", "Conservative"]),
  branch("Islamic", "other", [{ l: "Islam (general)", m: ["Islam"] }, "Sunni", "Shia", "Sufi", "Nation of Islam"]),
  branch("Middle-Eastern, Additional", "other", ["Mandaean", "Yazidi", "Druze", "Zoroastrian", "Bah\u00e1\u02bc\u00ed Faith"]),
  branch("Dharmic Religions", "other", [
    ["Hindu", ["Pan-Denominational Hindu", "Bochasanwasi Akshar Purushottam Swaminarayan Sanstha (BAPS)", "International Society for Krishna Consciousness (ISKCON)", "The Vedanta Society"]],
    ["Sikh", ["Mainstream Sikh", "Sikh Dharma International"]],
    "Jain",
    ["Buddhist", ["Zen Buddhist", "Tibetan Buddhist", "Soka Gakkai International (SGI)", "Chinese Esoteric Buddhist", "Won Buddhist", "New Kadampa Tradition (NKT-IKBU)"]],
  ]),
  branch("Asian, Additional", "other", ["Taoist", ["Shint\u014d", ["Konk\u014dky\u014d"]], "Tenrikyo", "Happy Science", "Seich\u014d-no-Ie", "Falun Gong", "Cao Dai"]),
  branch("New Age and/or Western Esoteric", "other", [
    ["Thelema/Thelemic-derived", ["Ordo Templi Orientis", "Ecclesia Babalon"]],
    "Santa Muerte", "Spiritualism", "Builders of the Adytum (BOTA)", "Unity Church (New Thought/Christian)", "Eckankar",
    "Fourth Way (Gurdjieff)", "Full Circle", "Urantia", "Self-Realization Fellowship (SRF)",
    ["Theosophy", ["The Theosophical Society", "United Lodge of Theosophists (ULT)", "Share International"]],
    "Ecclesia Gnostica", ["The Gnostic Society", ["Besant Lodge"]], "The Rosicrucian Fellowship (Mount Ecclesia)", "The Lemurian Fellowship",
  ]),
  branch("UFO/Extraterrestrial New Religious Movement", "other", ["Aetherius Society", "Church of Scientology", "International Ra\u00ebl\u00efan Movement", "Unarius Academy of Science"]),
  branch("Neo-Paganism / Pagan Reconstructionist", "other", [
    "Wicca", ["Ukrainian Pagan", ["Native Ukrainian National Faith (RUNVira)"]],
    ["Nordic Pagan (Asatru)", ["Asatru (Inclusive)", "Asatru Folk Assembly"]],
    ["Armenian Hetanist", ["Order of the Children of Ari"]],
  ]),
  branch("Humanistic, Atheistic, and/or Secular", "other", [
    ["Contemporary Satanism", ["The Satanic Temple (TST)", "The Church of Satan / LaVeyan Satanism"]],
    ["Secular Humanist", ["Humanist Society of Greater Phoenix"]],
    "Unitarian Universalist",
  ]),
  branch("Other", "other", [{ l: "Other", m: ["Other"] }]),
];
// Lookup by denomination, and make sure every leaf has a COMMUNITIES entry (colors, filters).
const LEAVES = [];
(function walk(nodes, group) { for (const n of nodes) { if (n.children) walk(n.children, n.group || group); else LEAVES.push({ ...n, group: n.group || group }); } })(TREE);
const LEAF_BY_DENOM = {};
for (const lf of LEAVES) for (const m of lf.match) LEAF_BY_DENOM[m] = lf;
for (const lf of LEAVES) {
  if (!COMMUNITIES.some((c) => c.match.some((m) => lf.match.includes(m)))) COMMUNITIES.push({ name: lf.label, match: lf.match, color: lf.color, listed: false });
}
