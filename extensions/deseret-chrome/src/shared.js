// Settings shared by the popup, options page, background worker and content script.
// Loaded as a classic script (content script, pages) and as a module side effect (background).
(function (root) {
  const FONTS = [
    { id: 'noto', name: 'Noto Sans Deseret', file: 'fonts/NotoSansDeseret.ttf', license: 'OFL 1.1', style: 'Sans serif' },
    { id: 'analecta', name: 'Analecta', file: 'fonts/analecta.ttf', license: 'Public domain', style: 'Serif' },
    { id: 'mellifera', name: 'Mellifera Deseret', file: 'fonts/mellifera.otf', license: 'OFL 1.1', style: 'Serif, 1860s style' },
    { id: 'desalph', name: 'desalph', file: 'fonts/desalph.otf', license: 'OFL 1.1', style: 'Sans serif' },
    { id: 'nomada', name: 'IDC Nomada', file: 'fonts/nomada.otf', license: 'OFL 1.1', style: 'Sans serif' },
    { id: 'system', name: 'Your computer’s font', file: null, license: '', style: 'Whatever your system uses' },
  ];

  const DEFAULTS = {
    strict: false,          // true: words the dictionary lacks stay Latin even if they can be built from parts
    oneAh: false,           // true: write every ah as 𐐂 (no 𐐃 or 𐐉), as most American English says it
    syllabic: true,         // true: the 𐑄, bee 𐐺, gay 𐑀 (a word that is a letter's name is that letter)
    font: 'noto',
    size: 110,              // percent, applied to Deseret letters only (CSS size-adjust)
    everywhere: false,      // convert every page automatically
    sites: {},              // hostname -> true (always convert) | false (never)
    captions: 'off',        // YouTube captions: off (as published) | dsrt (Deseret)
  };

  async function getSettings() {
    const s = await chrome.storage.sync.get(DEFAULTS);
    return { ...DEFAULTS, ...s, sites: { ...(s.sites || {}) } };
  }
  const setSettings = (patch) => chrome.storage.sync.set(patch);

  // Register the chosen Deseret font under `family` from bytes (page CSPs can't block that), covering
  // only Deseret code points so Latin text keeps its own font. Returns the FontFace, or null.
  async function registerFont(family, settings) {
    const pick = FONTS.find((f) => f.id === settings.font) || FONTS[0];
    let src;
    if (pick.file) src = await (await fetch(chrome.runtime.getURL(pick.file))).arrayBuffer();
    if (!src) src = 'local("Segoe UI Historic"), local("Noto Sans Deseret"), local("Apple Symbols")';
    const face = new FontFace(family, src, { unicodeRange: 'U+10400-1044F', sizeAdjust: `${settings.size || 100}%` });
    document.fonts.add(face);
    try { await face.load(); } catch (e) { document.fonts.delete(face); console.warn('[Deseret] font failed to load; using the system font', e); return null; }
    return face;
  }

  root.DSRT_SHARED = { FONTS, DEFAULTS, getSettings, setSettings, registerFont };
})(typeof self !== 'undefined' ? self : window);
