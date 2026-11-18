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
    { id: 'custom', name: 'Your own font (upload in Options)', file: null, license: '', style: '' },
  ];

  const DEFAULTS = {
    spelling: 'modern',     // modern | historical (1868-69 printing conventions)
    strict: false,          // true: words the dictionary lacks stay Latin even if they can be built from parts
    font: 'noto',
    size: 110,              // percent, applied to Deseret letters only (CSS size-adjust)
    everywhere: false,      // convert every page automatically
    sites: {},              // hostname -> true (always convert) | false (never)
  };

  async function getSettings() {
    const s = await chrome.storage.sync.get(DEFAULTS);
    return { ...DEFAULTS, ...s, sites: { ...(s.sites || {}) } };
  }
  const setSettings = (patch) => chrome.storage.sync.set(patch);

  root.DSRT_SHARED = { FONTS, DEFAULTS, getSettings, setSettings };
})(typeof self !== 'undefined' ? self : window);
