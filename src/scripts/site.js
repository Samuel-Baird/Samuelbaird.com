// Site behaviour: Latin/Deseret toggle, Deseret title reveal, search, contents menu.
const root = document.documentElement;
const store = {
  get: (k) => { try { return localStorage.getItem(k); } catch { return null; } },
  set: (k, v) => { try { localStorage.setItem(k, v); } catch {} },
};
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

function beeLoader(text) {
  const tpl = document.getElementById('bee-loader-tpl');
  const el = tpl.content.firstElementChild.cloneNode(true);
  el.querySelector('.bee-loader-text').textContent = text;
  return el;
}

/* ---------- Latin / Deseret ---------- */
// Swaps visible text word by word using the build-time table at /deseret-words.json.
// Words not in the table (names, rare words) stay in Latin letters rather than being guessed.
const CASE_OFFSET = 0x28;
const WORD_RE = /[A-Za-z]+(?:['’][A-Za-z]+)*/g;
const SKIP = '.rn,.num,.card-num,script,style,code,pre,svg,textarea,input,select,option,template,[data-no-dsrt],.dsrt,.search-results';
let words = null;
const originals = new Map(); // text node -> Latin text

const upper = (s) => Array.from(s).map((c) => String.fromCodePoint(c.codePointAt(0) - CASE_OFFSET)).join('');
function dsrtWord(w) {
  const d = words[w.toLowerCase().replace(/’/g, "'")];
  if (!d) return w;
  if (w.length > 1 && w === w.toUpperCase()) return upper(d);
  if (w[0] !== w[0].toLowerCase()) { const [f, ...r] = Array.from(d); return upper(f) + r.join(''); }
  return d;
}
async function loadWords() {
  if (words) return words;
  const res = await fetch('/deseret-words.json');
  words = await res.json();
  return words;
}
function toDeseretDom() {
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
    acceptNode: (n) => (!n.nodeValue.trim() || n.parentElement.closest(SKIP)) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT,
  });
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const n of nodes) {
    const latin = n.nodeValue;
    const d = latin.replace(WORD_RE, dsrtWord);
    if (d !== latin) { originals.set(n, latin); n.nodeValue = d; }
  }
  document.querySelectorAll('input[placeholder]').forEach((i) => { i.dataset.ph = i.placeholder; i.placeholder = i.placeholder.replace(WORD_RE, dsrtWord); });
}
function toLatinDom() {
  for (const [n, latin] of originals) n.nodeValue = latin;
  originals.clear();
  document.querySelectorAll('input[data-ph]').forEach((i) => { i.placeholder = i.dataset.ph; });
}
const scriptBtn = document.querySelector('.script-toggle');
async function setScript(mode, persist = true) {
  if (mode === 'dsrt') {
    const loader = words ? null : beeLoader('Setting the type…');
    if (loader) document.body.append(Object.assign(loader, { className: 'bee-loader bee-loader--float' }));
    try { await loadWords(); } catch { loader?.remove(); return; }
    loader?.remove();
    toDeseretDom();
    root.dataset.script = 'dsrt';
    root.lang = 'en-Dsrt';
  } else {
    toLatinDom();
    delete root.dataset.script;
    root.lang = 'en';
  }
  delete root.dataset.scriptPending;
  if (persist) store.set('script', mode);
  scriptBtn?.setAttribute('aria-pressed', String(mode === 'dsrt'));
  if (scriptBtn) {
    scriptBtn.dataset.tip = mode === 'dsrt' ? 'Read in the Latin alphabet' : 'Read in the Deseret alphabet';
    scriptBtn.setAttribute('aria-label', mode === 'dsrt' ? 'Show text in the Latin alphabet' : 'Show text in the Deseret alphabet');
  }
}
scriptBtn?.addEventListener('click', () => setScript(root.dataset.script === 'dsrt' ? 'latn' : 'dsrt'));

/* ---------- title reveal (Deseret, then Latin) ---------- */
// Port of samuelbaird.com/deseret.js; the Deseret spellings are computed at build time (data-dsrt).
function reveal(h1) {
  let parts; try { parts = JSON.parse(h1.dataset.dsrt || 'null'); } catch { return; }
  if (!parts || reduced) return;
  const text = h1.textContent.trim();
  const tokens = text.split(/(\s+)/).filter(Boolean);
  if (tokens.length !== parts.length) return;
  const DURATION = 300, stagger = Math.min(50, 850 / Math.max(text.length, 1));
  const frag = document.createDocumentFragment();
  let seen = 0;
  tokens.forEach((tok, i) => {
    const glyphs = parts[i] ? Array.from(parts[i]) : null;
    if (!glyphs) { frag.append(tok); seen += tok.length; return; }
    const chars = Array.from(tok);
    const word = document.createElement('span');
    word.setAttribute('aria-hidden', 'true');
    word.style.cssText = 'position:relative;display:inline-block';
    const latin = document.createElement('span');
    latin.textContent = tok;
    latin.style.animation = `deseret-in ${DURATION}ms ease-out ${Math.round((seen + chars.length - 1) * stagger)}ms both`;
    const overlay = document.createElement('span');
    overlay.style.cssText = "position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none;font-family:'Noto Sans Deseret',sans-serif;font-size:.8em";
    const step = glyphs.length > 1 ? (chars.length - 1) / (glyphs.length - 1) : 0;
    glyphs.forEach((c, j) => {
      const g = document.createElement('span');
      g.textContent = c;
      g.style.animation = `deseret-out ${DURATION}ms ease-in ${Math.round((seen + j * step) * stagger)}ms both`;
      overlay.append(g);
    });
    word.append(latin, overlay);
    frag.append(word);
    seen += tok.length;
  });
  h1.setAttribute('aria-label', text);
  h1.textContent = '';
  h1.append(frag);
  setTimeout(() => { h1.removeAttribute('aria-label'); h1.textContent = text; }, stagger * text.length + DURATION + 60);
}

/* ---------- search ---------- */
const q = document.getElementById('q');
const box = document.getElementById('search-results');
let index = null, active = -1;
async function loadIndex() {
  if (index) return index;
  box.hidden = false;
  box.replaceChildren(beeLoader('Fetching the index…'));
  index = await (await fetch('/search.json')).json();
  return index;
}
const norm = (s) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
function render(results, term) {
  active = -1;
  if (!term) { box.hidden = true; return; }
  box.hidden = false;
  if (!results.length) {
    const p = document.createElement('p'); p.className = 'r-empty'; p.textContent = `Nothing found for “${term}”.`;
    box.replaceChildren(p); return;
  }
  box.replaceChildren(...results.slice(0, 8).map((r) => {
    const a = document.createElement('a');
    a.href = r.url;
    a.innerHTML = '<span class="r-where"></span><span class="r-title"></span>';
    a.querySelector('.r-where').textContent = r.where;
    a.querySelector('.r-title').textContent = r.title;
    return a;
  }));
}
async function search() {
  const term = q.value.trim();
  if (!term) return render([], '');
  const idx = await loadIndex();
  const t = norm(term);
  const scored = [];
  for (const r of idx) {
    const title = norm(r.title), body = norm(r.text || '');
    let s = 0;
    if (title.startsWith(t)) s += 10; else if (title.includes(t)) s += 6;
    if (body.includes(t)) s += 1 + Math.min(3, body.split(t).length - 2); // more mentions, higher
    if (r.title.includes(term)) s += 4; // exact, e.g. Deseret letters
    if (s) scored.push([s, r]);
  }
  scored.sort((a, b) => b[0] - a[0]);
  render(scored.map((x) => x[1]), term);
}
if (q) {
  q.addEventListener('focus', () => { loadIndex().then(() => { if (!q.value) box.hidden = true; }); });
  q.addEventListener('input', search);
  q.addEventListener('keydown', (e) => {
    const links = [...box.querySelectorAll('a')];
    if (e.key === 'Escape') { q.value = ''; box.hidden = true; return; }
    if (!links.length) return;
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      active = (active + (e.key === 'ArrowDown' ? 1 : -1) + links.length) % links.length;
      links.forEach((l, i) => l.setAttribute('aria-selected', String(i === active)));
    } else if (e.key === 'Enter') {
      (links[active] || links[0]).click();
    }
  });
  document.addEventListener('click', (e) => { if (!e.target.closest('.search')) box.hidden = true; });
}

/* ---------- contents (mobile) ---------- */
const contents = document.querySelector('.contents');
contents?.querySelector('.contents-toggle')?.addEventListener('click', (e) => {
  const open = contents.classList.toggle('open');
  e.currentTarget.setAttribute('aria-expanded', String(open));
});

/* ---------- start ---------- */
const h1 = document.querySelector('h1[data-dsrt]');
if (root.dataset.scriptPending === 'dsrt') setScript('dsrt', false);
else if (h1 && document.fonts) {
  Promise.race([document.fonts.load('1rem "Noto Sans Deseret"', '𐐔'), new Promise((r) => setTimeout(r, 300))])
    .then(() => { if (document.fonts.check('1rem "Noto Sans Deseret"', '𐐔')) reveal(h1); });
}
