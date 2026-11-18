// Content script: switches the page's text between Latin and Deseret.
// - Only text node values change (never the DOM structure), so React/Vue/YouTube-style apps keep working,
//   and the original text is kept so switching back is exact.
// - The chosen Deseret font is registered through the FontFace API from bytes (unaffected by the page's
//   CSP) with unicode-range limited to Deseret, and prepended to each touched element's font stack, so
//   Latin letters and icon fonts keep their own fonts.
// - New content (infinite scroll, SPA navigation, live captions) is converted as it appears.
(() => {
  if (window.__dsrtLoaded) return;
  window.__dsrtLoaded = true;
  const { getSettings, registerFont } = self.DSRT_SHARED;

  const LATIN = /\p{Script=Latin}/u;
  const DSRT = /[\u{10400}-\u{1044F}]/u;
  const SKIP = 'script,style,noscript,textarea,input,select,option,code,pre,kbd,samp,var,svg,math,template,iframe,'
    + '[contenteditable=""],[contenteditable="true"],[translate="no"],.notranslate,[data-no-dsrt],'
    + '.ytp-caption-window-container,.dsrt-cap'; // YouTube captions belong to captions.js
  const ICON_FONT = /icon|material|awesome|symbol|glyph|fontello|dashicons/i;
  const FAMILY = 'DeseretReader';
  const CHUNK = 300;

  let active = false;
  let direction = 'dsrt';
  let settings = null;
  let face = null;
  let observer = null;
  let stats = { words: 0, unknown: 0 };
  let originalTitle = null;
  const texts = new Map();            // Text node -> { orig, conv }
  const styled = new Map();           // Element -> { value, priority } of its inline font-family before us
  const iconCache = new WeakMap();    // Element -> boolean

  // ---------- fonts ----------
  async function loadFont() {
    if (face) { document.fonts.delete(face); face = null; }
    if (direction === 'dsrt') face = await registerFont(FAMILY, settings);
  }

  // ---------- which text to touch ----------
  const wanted = (s) => (direction === 'dsrt' ? LATIN.test(s) : DSRT.test(s));
  function isIcon(el) {
    if (iconCache.has(el)) return iconCache.get(el);
    const v = ICON_FONT.test(getComputedStyle(el).fontFamily) || ICON_FONT.test(el.className?.baseVal ?? el.className ?? '');
    iconCache.set(el, v);
    return v;
  }
  function eligible(node) {
    const el = node.parentElement;
    if (!el || !node.nodeValue || !wanted(node.nodeValue)) return false;
    if (el.closest(SKIP) || el.isContentEditable) return false;
    return !isIcon(el);
  }
  function collect(root, out) {
    if (root.nodeType === Node.TEXT_NODE) { if (eligible(root)) out.push(root); return; }
    if (root.nodeType !== Node.ELEMENT_NODE && root.nodeType !== Node.DOCUMENT_NODE) return;
    if (root.nodeType === Node.ELEMENT_NODE && root.closest(SKIP)) return;
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, { acceptNode: (n) => (eligible(n) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT) });
    for (let n = w.nextNode(); n; n = w.nextNode()) out.push(n);
  }

  // ---------- convert and apply ----------
  async function request(list) {
    const res = await chrome.runtime.sendMessage({ type: 'convert', texts: list, direction, spelling: settings.spelling, strict: settings.strict });
    if (!res || res.error) throw new Error(res?.error || 'no reply from background');
    stats.words += res.stats.words;
    stats.unknown += res.stats.unknown;
    return res.out;
  }

  function styleParent(el) {
    if (direction !== 'dsrt' || styled.has(el)) return;
    styled.set(el, { value: el.style.getPropertyValue('font-family'), priority: el.style.getPropertyPriority('font-family') });
    const fam = getComputedStyle(el).fontFamily;
    el.style.setProperty('font-family', `"${FAMILY}", ${fam}`, 'important');
  }

  async function convertNodes(nodes) {
    const fresh = nodes.filter((n) => { const t = texts.get(n); return !t || n.nodeValue !== t.conv; });
    if (!fresh.length) return;
    const unique = [...new Set(fresh.map((n) => n.nodeValue))];
    const map = new Map();
    for (let i = 0; i < unique.length; i += CHUNK) {
      const part = unique.slice(i, i + CHUNK);
      const out = await request(part);
      part.forEach((s, j) => map.set(s, out[j]));
      if (!active) return;
    }
    pause();
    for (const n of fresh) {
      const orig = n.nodeValue;
      const conv = map.get(orig);
      if (conv == null || conv === orig || !n.isConnected) continue;
      texts.set(n, { orig, conv }); // orig is the page's current text (new or changed since last time)
      n.nodeValue = conv;
      if (n.parentElement) styleParent(n.parentElement);
    }
    resume();
  }

  async function convertTitle() {
    if (!document.title || !wanted(document.title)) return;
    originalTitle ??= document.title;
    const [t] = await request([originalTitle]);
    if (active) document.title = t;
  }

  // ---------- watching for new content ----------
  let queue = new Set();
  let timer = null;
  function onMutations(records) {
    for (const r of records) {
      if (r.type === 'characterData') queue.add(r.target);
      else r.addedNodes.forEach((n) => queue.add(n));
    }
    clearTimeout(timer);
    timer = setTimeout(flush, 150);
  }
  function flush() {
    const roots = [...queue];
    queue = new Set();
    const nodes = [];
    for (const r of roots) if (r.isConnected) collect(r, nodes);
    if (nodes.length) convertNodes(nodes).catch((e) => console.warn('[Deseret]', e));
  }
  const pause = () => observer?.disconnect();
  const resume = () => { if (active && observer) observer.observe(document.body, { childList: true, subtree: true, characterData: true }); };

  // ---------- on / off ----------
  const remember = (on) => chrome.runtime.sendMessage({ type: 'tab-set', active: on, direction, host: location.hostname }).catch(() => {});

  async function activate(dir, { save = true } = {}) {
    if (active) restore();
    settings = await getSettings();
    direction = dir || 'dsrt';
    active = true;
    stats = { words: 0, unknown: 0 };
    if (save) remember(true);
    await loadFont();
    observer = new MutationObserver(onMutations);
    const nodes = [];
    collect(document.body, nodes);
    try {
      await convertNodes(nodes);
      await convertTitle();
    } catch (e) {
      console.warn('[Deseret]', e);
    }
    resume();
  }

  function restore() {
    active = false;
    observer?.disconnect();
    observer = null;
    clearTimeout(timer);
    queue = new Set();
    for (const [n, t] of texts) if (n.isConnected && n.nodeValue === t.conv) n.nodeValue = t.orig;
    texts.clear();
    for (const [el, old] of styled) {
      if (old.value) el.style.setProperty('font-family', old.value, old.priority);
      else el.style.removeProperty('font-family');
    }
    styled.clear();
    if (originalTitle != null) { document.title = originalTitle; originalTitle = null; }
    if (face) { document.fonts.delete(face); face = null; }
  }

  // Deseret-heavy page (e.g. a Deseret Wiki page in Deseret mode): default to reading it in Latin.
  function guessDirection() {
    const sample = (document.body.innerText || '').slice(0, 20000);
    const d = (sample.match(/[\u{10400}-\u{1044F}]/gu) || []).length;
    const l = (sample.match(/\p{Script=Latin}/gu) || []).length;
    return d > l ? 'latin' : 'dsrt';
  }

  chrome.runtime.onMessage.addListener((msg, _s, reply) => {
    if (msg.type === 'toggle') { if (active) { restore(); remember(false); } else activate(guessDirection()); reply({ ok: true }); }
    else if (msg.type === 'set') { (msg.direction ? activate(msg.direction) : Promise.resolve((restore(), remember(false)))).then(() => reply(status())); return true; }
    else if (msg.type === 'status') reply(status());
    return false;
  });
  const status = () => ({ active, direction, stats, host: location.hostname, suggested: guessDirection() });

  // Re-apply when the spelling, font or size changes while the page is converted.
  chrome.storage.onChanged.addListener((changes, area) => {
    if (!active) return;
    const keys = Object.keys(changes);
    if (area === 'sync' && keys.some((k) => ['spelling', 'strict', 'font', 'size'].includes(k))) activate(direction, { save: false });
    if (area === 'local' && keys.includes('customFont') && settings?.font === 'custom') activate(direction, { save: false });
  });

  // On load: sites marked "always" (or every site when "everywhere" is on), else whatever this tab was
  // showing on this site before (so moving between pages keeps Deseret on).
  (async () => {
    const s = await getSettings();
    const rule = s.sites[location.hostname];
    if (rule === true || (s.everywhere && rule !== false)) return activate('dsrt', { save: false });
    const prev = await chrome.runtime.sendMessage({ type: 'tab-get' }).catch(() => null);
    if (prev && prev.host === location.hostname) activate(prev.direction, { save: false });
  })();
})();
