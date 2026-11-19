// Per-site menus for the shared sidebar. Each site lists its own pages ("main", with an engraved icon
// from assets/sprite.svg) and optional "shelves" (secondary sections, marked with a coloured bar).
// The "Projects" shelf and the samuelbaird.com links are added to every site from projects.json.
//
// target: where scripts/family-sync.mjs writes the assets and how it stamps the chrome in.
//   static -> public dir; every *.html under it with <!--family:...--> markers is patched in place
//   next   -> public dir for assets, plus a generated component file
//   self   -> assets only; the site's own build renders the chrome (samuelbaird.com)
//   astro  -> the Deseret Wiki renders its own sidebar (Sidebar.astro) from a synced JSON copy
export const SITES = {
  'samuelbaird.com': {
    name: 'Samuel Baird',
    project: null,
    home: 'https://samuelbaird.com',
    // samuelbaird.com stamps the chrome itself in scripts/build.mjs (nav/foot markers); sync only copies assets.
    target: { type: 'self', dir: 'sites/samuelbaird.com' },
    main: [
      { href: '/', label: 'Home', icon: 'i-skep', exact: true },
      { href: '/projects', label: 'Projects', icon: 'i-comb' },
      { href: '/sacred-sites', label: 'Sacred Sites', icon: 'i-wagon' },
      { href: '/temples', label: 'Temples', icon: 'i-sunmoon' },
      { href: '/historic-sites', label: 'Historic Sites', icon: 'i-lamp' },
      { href: '/hymns', label: 'Hymns', icon: 'i-primer' },
      { href: '/handbook-changes', label: 'Handbook Changes', icon: 'i-primer' },
      { href: '/books', label: 'Reading', icon: 'i-books' },
      { href: '/collection', label: 'Collection', icon: 'i-sego' },
    ],
    shelves: [
      { href: '/data', label: 'Open data', color: '#8DA27A' },
      { href: '/faq', label: 'FAQ', color: '#7E9BBB' },
      { href: '/donate', label: 'Donate', color: '#B8645A' },
    ],
    foot: [{ href: '/about', label: 'About Samuel Baird', icon: 'i-eye' }],
  },
  urim: {
    name: 'Urim',
    project: 'urim',
    target: { type: 'static', dir: 'sites/urim/site' },
    main: [
      { href: '/', label: 'Atlas', icon: 'i-eye', exact: true },
      { href: '/variants', label: 'Variants', icon: 'i-sorts' },
      { href: '/proclamations', label: 'Proclamations', icon: 'i-primer' },
    ],
    shelves: [
      { href: '/connect', label: 'Use with AI', color: '#7E9BBB' },
      { href: '/donate', label: 'Donate', color: '#B8645A' },
      { href: 'mailto:ithinksamofficial@gmail.com?subject=Urim', label: 'Contact', color: '#8DA27A' },
    ],
    foot: [{ href: '/about', label: 'Method & data', icon: 'i-lamp' }],
  },
  'deseret-mcp': {
    name: 'Deseret MCP',
    project: 'deseret-mcp',
    target: { type: 'static', dir: 'sites/deseret-mcp/site' },
    main: [
      { href: '/', label: 'Try it', icon: 'i-primer', exact: true },
      { href: '/connect', label: 'Use with AI', icon: 'i-sorts' },
      { href: '/about', label: 'Method & data', icon: 'i-lamp' },
    ],
    shelves: [
      { href: 'https://deseret.wiki/', label: 'Deseret Wiki', color: '#C9A45C' },
      { href: 'mailto:ithinksamofficial@gmail.com?subject=Deseret%20MCP', label: 'Contact', color: '#8DA27A' },
    ],
    foot: [],
  },
  'latter-day-stats': {
    name: 'Latter-day Stats',
    project: 'latter-day-stats',
    target: { type: 'next', dir: 'sites/latter-day-stats', publicDir: 'public', component: 'src/components/family-chrome.generated.ts' },
    main: [
      { href: '/', label: 'Home', icon: 'i-skep', exact: true },
      { href: '/channels', label: 'Channels', icon: 'i-eye' },
      { href: '/studies', label: 'Studies', icon: 'i-books' },
      { href: '/data-explorer', label: 'Data Explorer', icon: 'i-comb' },
    ],
    shelves: [
      { href: '/connect', label: 'Use with AI', color: '#7E9BBB' },
      { href: '/contact', label: 'Contact', color: '#8DA27A' },
      { href: '/donate', label: 'Donate', color: '#B8645A' },
    ],
    foot: [{ href: '/about', label: 'About Latter-day Stats', icon: 'i-lamp' }],
  },
  omni: {
    name: 'Omni',
    project: 'omni',
    target: { type: 'next', dir: 'sites/omni', publicDir: 'public', component: 'src/components/family-chrome.generated.ts' },
    main: [{ href: '/', label: 'Connect', icon: 'i-comb', exact: true }],
    shelves: [],
    foot: [],
  },
  peepstone: {
    name: 'Peepstone',
    project: 'peepstone',
    target: { type: 'next', dir: 'sites/peepstone', publicDir: 'public', component: 'app/family-chrome.generated.ts' },
    main: [{ href: '/', label: 'Connect', icon: 'i-lamp', exact: true }],
    shelves: [],
    foot: [],
  },
  'deseret-wiki': {
    name: 'Deseret Wiki',
    project: 'deseret-wiki',
    target: { type: 'astro', dir: 'sites/deseret-wiki', data: 'src/data/family.json' },
  },
};
