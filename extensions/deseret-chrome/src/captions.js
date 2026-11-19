// YouTube captions in Deseret (youtube.com and embedded players).
// Modes (setting `captions`, shared with the popup and the in-player button):
//   off  - captions exactly as YouTube shows them
//   dsrt - each caption line in Deseret
// YouTube rebuilds caption lines constantly (word by word for auto captions), so this watches the
// caption container and re-renders; conversions are cached per line. A line whose words are mostly not
// English (e.g. a Spanish track) is left as is rather than mangled.
(() => {
  if (window.__dsrtCaptions) return;
  window.__dsrtCaptions = true;
  const { getSettings, setSettings, registerFont } = self.DSRT_SHARED;

  const FAMILY = 'DeseretCaptions';
  const MODES = ['off', 'dsrt'];
  const LABEL = { off: 'English captions', dsrt: 'Deseret captions' };
  const WORDS = /\p{Script=Latin}+(?:['’]\p{Script=Latin}+)*/gu;
  let settings = null;
  let mode = 'off';
  let face = null;
  let container = null;
  let observer = null;
  const cache = new Map(); // caption text -> Deseret text (or the same text when left alone)

  // ---------- conversion ----------
  async function ensure(texts) {
    const missing = [...new Set(texts)].filter((t) => !cache.has(t));
    if (!missing.length) return;
    const res = await chrome.runtime.sendMessage({ type: 'convert', texts: missing, direction: 'dsrt', strict: settings.strict });
    if (!res || res.error) return;
    missing.forEach((t, i) => {
      const out = res.out[i];
      const total = (t.match(WORDS) || []).length;
      const left = (out.match(WORDS) || []).length;
      cache.set(t, total && left / total > 0.5 ? t : out); // mostly unknown: probably not English
    });
    if (cache.size > 5000) cache.delete(cache.keys().next().value);
  }

  // ---------- rendering ----------
  const segments = () => (container ? [...container.querySelectorAll('.ytp-caption-segment')] : []);
  // A segment's English text: what YouTube last wrote (if it changed it) or what we saved before replacing.
  function original(seg) {
    if (seg.dataset.dsrtShown !== undefined && seg.textContent === seg.dataset.dsrtShown) return seg.dataset.dsrtOrig;
    return seg.textContent;
  }
  function deseretFont(el) {
    if (el.dataset.dsrtFont !== undefined) return;
    el.dataset.dsrtFont = el.style.fontFamily || '';
    el.style.fontFamily = `"${FAMILY}", ${getComputedStyle(el).fontFamily}`;
  }
  function plainFont(el) {
    if (el.dataset.dsrtFont === undefined) return;
    el.style.fontFamily = el.dataset.dsrtFont;
    delete el.dataset.dsrtFont;
  }

  let busy = false, again = false;
  async function render() {
    if (busy) { again = true; return; }
    busy = true;
    try {
      const segs = segments();
      const texts = segs.map(original);
      if (mode !== 'off') await ensure(texts.filter((t) => /\p{Script=Latin}/u.test(t)));
      pause();
      segs.forEach((seg, i) => {
        const orig = texts[i];
        const conv = cache.get(orig);
        if (mode === 'dsrt' && conv && conv !== orig) {
          seg.dataset.dsrtOrig = orig;
          seg.dataset.dsrtShown = conv;
          if (seg.textContent !== conv) seg.textContent = conv;
          deseretFont(seg);
        } else {
          if (seg.dataset.dsrtShown !== undefined && seg.textContent === seg.dataset.dsrtShown) seg.textContent = orig;
          delete seg.dataset.dsrtOrig;
          delete seg.dataset.dsrtShown;
          plainFont(seg);
        }
      });
      resume();
    } finally {
      busy = false;
      if (again) { again = false; render(); }
    }
  }

  // ---------- watching ----------
  let timer = null;
  const schedule = () => { clearTimeout(timer); timer = setTimeout(render, 30); };
  const pause = () => observer?.disconnect();
  const resume = () => { if (container && observer) observer.observe(container, { childList: true, subtree: true, characterData: true }); };
  function attach() {
    const c = document.querySelector('.ytp-caption-window-container');
    if (c && c !== container) {
      observer?.disconnect();
      container = c;
      observer = new MutationObserver(schedule);
      resume();
      schedule();
    }
    addButton();
  }

  // ---------- player button ----------
  const BTN_CLASS = 'dsrt-cc-btn';
  function addButton() {
    const controls = document.querySelector('.ytp-right-controls');
    if (!controls) return;
    let btn = controls.querySelector('.' + BTN_CLASS);
    if (!btn) {
      btn = document.createElement('button');
      btn.className = `ytp-button ${BTN_CLASS}`;
      btn.type = 'button';
      btn.innerHTML = '<span class="dsrt-cc-glyph">\u{10414}</span><span class="dsrt-cc-dot"></span>';
      btn.addEventListener('click', (e) => { e.stopPropagation(); cycle(); });
      const cc = controls.querySelector('.ytp-subtitles-button');
      controls.insertBefore(btn, cc ? cc.nextSibling : controls.firstChild);
    }
    btn.dataset.mode = mode;
    btn.title = `${LABEL[mode]} (click to switch, Alt+Shift+C)`;
    btn.setAttribute('aria-label', LABEL[mode]);
    btn.setAttribute('aria-pressed', String(mode !== 'off'));
  }
  function injectStyle() {
    if (document.getElementById('dsrt-cc-style')) return;
    const st = document.createElement('style');
    st.id = 'dsrt-cc-style';
    st.textContent = `.${BTN_CLASS}{position:relative;display:inline-flex!important;align-items:center;justify-content:center;vertical-align:top}
.${BTN_CLASS} .dsrt-cc-glyph{font:500 22px/1 "${FAMILY}","Segoe UI Historic","Noto Sans Deseret",sans-serif;color:#fff;opacity:.9}
.${BTN_CLASS} .dsrt-cc-dot{position:absolute;left:28%;right:28%;bottom:22%;height:3px;border-radius:2px;background:transparent}
.${BTN_CLASS}[data-mode="dsrt"] .dsrt-cc-dot{background:#D9B46A}`;
    document.documentElement.appendChild(st);
  }

  // ---------- mode ----------
  function turnOnCC() {
    const cc = document.querySelector('.ytp-subtitles-button');
    if (cc && cc.getAttribute('aria-pressed') === 'false') cc.click();
  }
  async function cycle() {
    const next = MODES[(MODES.indexOf(mode) + 1) % MODES.length];
    await setSettings({ captions: next });
    if (next !== 'off') turnOnCC();
  }
  async function apply(newSettings) {
    const fontChanged = !settings || ['font', 'size'].some((k) => settings[k] !== newSettings[k]);
    const spellChanged = settings && ['strict', 'oneAh', 'syllabic'].some((k) => settings[k] !== newSettings[k]);
    settings = newSettings;
    mode = settings.captions === 'off' || !settings.captions ? 'off' : 'dsrt'; // older 'both' setting -> Deseret
    if (spellChanged) cache.clear();
    if (mode !== 'off' && (fontChanged || !face)) {
      if (face) document.fonts.delete(face);
      face = await registerFont(FAMILY, settings);
    }
    addButton();
    schedule();
  }

  chrome.storage.onChanged.addListener(async (changes, area) => {
    if (area === 'sync' && Object.keys(changes).some((k) => ['captions', 'strict', 'oneAh', 'syllabic', 'font', 'size'].includes(k))) apply(await getSettings());
  });
  chrome.runtime.onMessage.addListener((msg, _s, reply) => {
    if (msg.type === 'captions-cycle') { cycle(); reply({ ok: true }); }
    else if (msg.type === 'captions-set' && MODES.includes(msg.mode)) { setSettings({ captions: msg.mode }).then(() => { if (msg.mode !== 'off') turnOnCC(); reply({ ok: true }); }); return true; }
    return false;
  });

  injectStyle();
  getSettings().then(apply);
  // The player appears late and YouTube navigates without page loads; keep looking for it.
  document.addEventListener('yt-navigate-finish', attach);
  setInterval(attach, 1500);
  attach();
})();
