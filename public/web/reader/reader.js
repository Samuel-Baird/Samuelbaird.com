// The reader (DESIGN.md Appendix E; §9 rule 5).
// The gsa MCP hands agents links to a page of a book; this is what they
// open, so everything else on the site is scaffolding around it.
//
// PDF.js 6 draws the pages; everything you touch is ours. Its toolbar,
// sidebar and find bar stay in the DOM (the engine needs them) but are
// hidden by reader.css, and this script drives the engine through
// PDFViewerApplication instead. One file serves every place a book opens:
// the shell's full window and the pane beside a conversation (both iframes,
// window.parent.gsaShell is the shell's API), and bare, full screen, on phones.
//
// A classic deferred script (the viewer page's CSP allows only 'self'), so
// it imports the engine itself, in order, and catches startup failures,
// including rejections from PDFViewerApplication.run(). No inline styles
// either: computed values go through the CSSOM (el.style.setProperty).

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = s => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
const coarse = matchMedia("(pointer: coarse)").matches;
const narrow = () => innerWidth <= 720;
const embedded = window.top !== window;
const shell = (() => { try { return embedded ? window.parent.gsaShell || null : null; } catch (_) { return null; } })();
const html = document.documentElement;
// the icons are the site's sprite, beside this script (both carry the deploy's version)
const SPRITE = (() => { try { return new URL("../icons.svg", document.currentScript.src).pathname; } catch (_) { return "/web/icons.svg"; } })();
// The service worker (static/sw.js, README "Opening fast"): the engine stays on the phone
// between launches. Registered with this deploy's version, off this script's address, as the
// shell does (shell/shell.js registerWorker); once it's active and the book is open (the engine
// and its worker loaded, onPagesInit) it's told what this page loaded, so the next open is served
// from its cache. ENGINE_V and engine() are declared with the startup below; warm runs after.
const warmWorker = (() => {
  let v = "";
  try { v = (new URL(document.currentScript.src).pathname.match(/^\/web\/v(\d+)\//) || [])[1] || ""; } catch (_) {}
  if (!v || !("serviceWorker" in navigator)) return () => {};
  let worker = null;
  const warm = () => {
    if (!worker) return;
    const urls = performance.getEntriesByType("resource").map(e => e.name).filter(u => /\/(web\/v\d+|pdfjs)\//.test(u))
      .concat(["build/pdf.mjs", "build/pdf.worker.mjs", "web/viewer.mjs"].map(engine));
    try { worker.postMessage({ type: "warm", urls: [...new Set(urls)] }); } catch (_) {}
  };
  navigator.serviceWorker.register("/sw.js?v=" + v).then(reg => {
    const w = reg.installing || reg.waiting || reg.active;
    if (!w) return;
    const on = () => { worker = w; if (html.classList.contains("loaded")) warm(); };
    if (w.state === "activated") on(); else w.addEventListener("statechange", () => { if (w.state === "activated") on(); });
  }).catch(() => {});
  return warm;
})();
const ic = (name, cls = "") => `<svg class="i${cls ? " " + cls : ""}" aria-hidden="true"><use href="${SPRITE}#${name}"></use></svg>`;
// where this book is open (DESIGN.md §9 rules 1, 5, 7): the shell's full
// window ("window": the bar leaves the sidebar toggle its corner while the
// sidebar is shut, and the foot leaves the player its end), the pane beside
// a conversation ("beside": this bar is the pane's, close and ↗), or bare ("")
const frameKind = (() => { try { const f = window.frameElement; return f?.classList.contains("reader-frame") ? "window" : f?.closest("#beside") ? "beside" : ""; } catch (_) { return ""; } })();
if (frameKind === "window") {
  html.classList.add("in-shell");
  // the shell's body says whether its sidebar is open and its player showing
  const sync = () => { try { const b = window.parent.document.body.classList; html.classList.toggle("side-open", b.contains("side-open")); html.classList.toggle("player-on", b.contains("listening")); } catch (_) {} };
  sync();
  try { new MutationObserver(sync).observe(window.parent.document.body, { attributes: true, attributeFilter: ["class"] }); } catch (_) {}
}
if (frameKind === "beside") html.classList.add("beside");
// beside a conversation on a narrow window the pane is a cover: its way out is ‹, not close
const besideNarrow = () => { try { return window.parent.matchMedia("(max-width: 899px)").matches; } catch (_) { return false; } };
const ls = {
  get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch (_) { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} },
};

/* ---------- the book ----------
   server.py's _viewer() hands us the volume in a meta tag (CSP rules out an
   inline script): path, its /b/ link, its folder and the folder's link. */
const BOOK = (() => {
  let b = null;
  try { b = JSON.parse($('meta[name="gsa-book"]').content); } catch (_) {}
  if (b) return b;
  const f = new URLSearchParams(location.search).get("file") || "";
  const path = decodeURIComponent(f.replace(/^\/files\//, "").replace(/^\/derived\/(.*)\.pdf$/, "$1"));
  // Deseret Wiki: opened from /library/ with ?file=/library/<pdf>&title=<title>; Back goes to the Library
  return { path, url: null, folder: "Library", folderUrl: "/library/", text: false,
           ct: new URLSearchParams(location.search).get("title") || "" };
})();
const FILE = new URLSearchParams(location.search).get("file") || "";
const SITE = location.origin;

// <catalog-parse>
function parseTitle(filename) {
  const stem = filename.replace(/\.[^.]+$/, "");
  const SERIES = [{ pattern:/^(\d+)_Interpreter_PDF$/, title:"Interpreter", subtitle:m => "vol. " + m[1] }];
  for (const series of SERIES) {
    const m = stem.match(series.pattern);
    if (m) return { author:"", title:series.title, subtitle:series.subtitle(m) };
  }
  let title = stem.replace(/_ /g, ": ");
  if (!title.includes(" ")) title = title.replace(/_/g, " ");
  let author = "", subtitle = "";
  const particles = new Set(["de", "von", "van", "der", "al."]);
  const isName = text => {
    const words = text.trim().split(/\s+/);
    return words.length <= 4 && words.every(word =>
      /^[\p{L}.'’\-]+$/u.test(word) && (particles.has(word) || /^\p{Lu}/u.test(word)));
  };
  // Oxford commas and repeated conjunctions join complete names, not words.
  const isNames = (text, requireFinalJoin = false) => {
    if (isName(text)) return true;
    const names = text.split(/, (?:& |and )?| & | and /);
    if (names.length < 2 || !names.every(isName)) return false;
    return !requireFinalJoin || /(?:, | )(?:&|and) [^,]+$/.test(text);
  };
  if (!isNames(title, true)) {
    const dash = title.indexOf(" - ");
    if (dash >= 0 && isNames(title.slice(0, dash)) && !/^\d/.test(title.slice(dash + 3))) {
      author = title.slice(0, dash); title = title.slice(dash + 3);
    } else {
      const commas = [...title.matchAll(/, /g)].reverse();
      for (const comma of commas) {
        const head = title.slice(0, comma.index), rest = title.slice(comma.index + 2);
        if (isNames(head, true) && !/^\d/.test(rest)) {
          author = head; title = rest; break;
        }
      }
    }
  }
  const colon = /: |:(?=\p{Lu})/u.exec(title);
  if (colon) { subtitle = title.slice(colon.index+colon[0].length).trim(); title = title.slice(0,colon.index); }
  return {author, title, subtitle};
}
// </catalog-parse>
// lib/catalog.js titleOf, copied: the catalog's title when it strictly extends the file name's
function titleOf(filename, catalogTitle) {
  const t = parseTitle(filename);
  const c = (catalogTitle || "").trim();
  if (c) {
    const own = (t.subtitle ? t.title + ": " + t.subtitle : t.title).toLowerCase(), cl = c.toLowerCase();
    if (own.length >= 5 && cl !== own && cl.includes(own)) {
      const colon = /: |:(?=\p{Lu})/u.exec(c);
      t.title = colon ? c.slice(0, colon.index) : c;
      t.subtitle = colon ? c.slice(colon.index + colon[0].length).trim() : "";
    }
  }
  return t;
}
// Deseret Wiki: a title handed in the link wins over one parsed from the file name
const NAME = BOOK.ct ? (() => { const c = BOOK.ct, m = /: /.exec(c);
  return { author: "", title: m ? c.slice(0, m.index) : c, subtitle: m ? c.slice(m.index + 2) : "" }; })()
  : titleOf(BOOK.path.split("/").pop() || "", BOOK.ct);
const fullTitle = t => t.subtitle ? `${t.title}: ${t.subtitle}` : t.title;

/* ---------- the instant page (DESIGN.md, the reader: Opening) ----------
   The page you asked for, as the server renders it (a JPEG of ~300 KB, /page/),
   shows while the engine downloads and the book's first bytes arrive; PDF.js's
   own drawing of that page replaces it. A 200 MB commentary opens like a web
   page. Starts here, before the engine import, so the two downloads overlap. */
const INSTANT = (() => {
  // Deseret Wiki: a static site has no /page/ renderer, so no instant page
  return null;
  const m = /[?&]p=(\d+)/.exec(location.search) || /(?:^#|&)page=(\d+)/.exec(location.hash);
  let page = m ? +m[1] : 0;
  if (!page) { const saved = ls.get("gsa-pos", {})[BOOK.path]; page = saved && saved.p > 1 ? saved.p : 1; }
  const url = n => "/page/" + BOOK.path.split("/").map(encodeURIComponent).join("/") + "?p=" + n;
  const box = document.createElement("div");
  box.id = "r-instant"; box.hidden = true; box.classList.toggle("wide", !narrow());
  const img = new Image(); img.alt = ""; img.decoding = "async";
  const it = { page, box, gone: false };
  img.onload = () => {
    if (it.gone) return;
    box.hidden = false;
    const opening = document.getElementById("r-opening");
    if (opening) opening.hidden = true;   // the page itself is the opening state now
    if (page > 1) new Image().src = url(page - 1);   // the neighbours, for a first turn
    new Image().src = url(page + 1);
  };
  img.src = url(page);
  box.append(img); document.body.append(box);
  return it;
})();
function instantGone() {
  loadDone();
  if (!INSTANT || INSTANT.gone) return;
  INSTANT.gone = true;
  INSTANT.box.classList.add("out");
  setTimeout(() => INSTANT.box.remove(), 400);
}

/* ---------- preferences (per device) ---------- */
const PREF = "gsa-reader";
const DEFAULTS = { tone: "paper", layout: "auto", flow: "scroll", fit: "auto", scrub: "bar", hold: false };
const prefs = () => ({ ...DEFAULTS, ...ls.get(PREF, {}) });
const setPref = (k, v) => ls.set(PREF, { ...ls.get(PREF, {}), [k]: v });

// the interface is dark only (tokens.css); a page's tone is about the scan
html.dataset.tone = prefs().tone;
// before the engine's first layout, so its first fit already sees the bands Pages keeps
html.classList.toggle("flow-pages", prefs().flow === "pages");
// phones: the foot as a bar, or tucked behind a button in the corner that opens it as a floating card
html.classList.toggle("scrub-button", prefs().scrub === "button");
html.classList.add("gsa", coarse ? "coarse" : "fine");
// the home-screen app: iOS keeps a page's viewport a status bar short until its root scrolls, and the
// reader's root never does (PDF.js scrolls a box of its own), which left a black band under the foot.
// The document takes the large viewport (reader.css) and the root is nudged once, so iOS lets it have it.
if (navigator.standalone || matchMedia("(display-mode: standalone)").matches) {
  html.classList.add("app");
  addEventListener("load", () => scrollTo(0, 1));
}
addEventListener("storage", e => { if (e.key === PREF) { html.dataset.tone = prefs().tone; paintAa(); } });

// a link that names a page beats the remembered one
const explicitPage = /(^#|&)page=\d+/.test(location.hash) || /[?&]p=\d+/.test(location.search);

/* ---------- what the link asks us to find ----------
   #find= is a passage, found once where the link points (share links, Ask's
   quotes). #hl= (one per term) is the search you came from, every term
   highlighted as the results page highlighted it. PDF.js's own #search=
   would highlight every match with no way to clear it, so an older link's
   search= is read as a passage and taken out before the engine looks. */
const linked = (() => {
  const h = new URLSearchParams(location.hash.slice(1));
  const find = (h.get("find") || h.get("search") || "").replaceAll('"', "").trim();
  const hl = h.getAll("hl").map(t => t.trim()).filter(Boolean);
  if (h.has("search")) {
    h.delete("search"); h.delete("phrase");
    if (find) h.set("find", find);
    setHash(h);
  }
  return find ? { query: find, passage: true } : hl.length ? { query: hl, passage: false } : null;
})();
// the hash only: location.search holds `file=`, which must stay unencoded
function setHash(h) {
  const s = h.toString();
  history.replaceState(history.state, "", location.pathname + location.search + (s ? "#" + s : ""));
}

/* ---------- engine options, before it opens the file ----------
   viewer.mjs dispatches webviewerloaded on parent.document (the shell's,
   when we're its iframe), so listen there and check it's ours. */
const loadTarget = (() => { try { return window.parent.document; } catch (_) { return document; } })();
loadTarget.addEventListener("webviewerloaded", function onLoaded(e) {
  if (e.detail && e.detail.source && e.detail.source !== window) return;
  loadTarget.removeEventListener("webviewerloaded", onLoaded);
  const o = window.PDFViewerApplicationOptions;
  const p = prefs();
  o.set("disablePreferences", true); // GSA owns preferences, including mobile canvas limits
  o.set("disableHistory", true);      // its pushState jumps would land in the shell's history
  o.set("viewOnLoad", 1);             // no per-file position/zoom memory: ours is below
  o.set("sidebarViewOnLoad", 0);
  o.set("annotationEditorMode", -1);  // a reading room, not an annotation studio
  o.set("scrollModeOnLoad", p.flow === "pages" ? 3 : 0);
  o.set("defaultZoomValue", zoomValue(p, false));
  o.set("workerSrc", engine("build/pdf.worker.mjs"));
  o.set("sandboxBundleSrc", engine("build/pdf.sandbox.mjs"));
  // Range loading (2026-10-31): the engine fetches the pages around you in
  // 256 KB pieces instead of streaming the file from byte 0, so a 200 MB
  // commentary reads after a couple of MB; the rest still arrives behind it.
  // (disableAutoFetch, which would stop that, hangs on some scans: measured.)
  // rangeChunkSize isn't a viewer option (o.set dropped it and the engine
  // fell back to 64 KB), so it goes to open() below.
  o.set("disableStream", true);
  if (coarse) {
    // iOS WebKit kills the tab on canvas OOM: cap render resolution (pages
    // CSS-scale beyond the cap — crisp at phone sizes, never OOMs at 3x DPR)
    o.set("maxCanvasPixels", 3145728);
    o.set("maxCanvasDim", 4096);
  }
  // PDF.js does not reject initializedPromise when initialize() fails.
  // Catch run() itself so a worker/localization/startup failure is visible.
  const a = window.PDFViewerApplication;
  const run = a.run.bind(a);
  a.run = (...args) => run(...args).catch(openFailed);
  const open = a.open.bind(a);
  a.open = args => open(args && args.url ? { ...args, rangeChunkSize: 262144 } : args);
  boot(a);
});

function zoomValue(p, spread) {
  if (p.fit === "width") return "page-width";
  if (p.fit === "page") return "page-fit";
  if (p.flow === "pages" || spread) return "page-fit";
  return narrow() ? "page-width" : "auto";
}

/* ---------- the Librarian (LISTEN-ASK.md, typed) ----------
   Ask about the page you're on. Opening the panel sends the pages around it
   to the Mini's Librarian, which reads them while you type; the question
   then gets the short answer asking-while-listening gives, with citations.
   One in this book turns the page here; anything else opens in a new tab.
   Follow-ups stay in the same thread until you go to another page. */
const ASK = { thread: null, page: 0, ctrl: null, busy: false, ready: null, ctx: null };
let docLoaded;
const docReady = new Promise(r => { docLoaded = r; });  // onPagesInit: the pages exist and the page it opens at is settled
const askLabel = n => labels && labels[n - 1] ? labels[n - 1] : String(n);
async function askPages(n) {
  const out = [];
  for (const k of [n - 1, n, n + 1]) {
    if (k < 1 || k > total) continue;
    try {
      const tc = await (await doc.getPage(k)).getTextContent();
      const text = tc.items.map(i => i.str + (i.hasEOL ? "\n" : " ")).join("").replace(/[ \t]+/g, " ").trim().slice(0, 6000);
      out.push({ pdf: k, label: askLabel(k), text: (k === n ? "⟦here⟧ " : "") + text });
    } catch (_) {}
  }
  return out;
}
async function askContext(n) {
  return { mode: "reading", slug: SLUG, path: BOOK.path, book: fullTitle(NAME) || BOOK.path.split("/").pop(),
           author: NAME.author || "", page: askLabel(n), pages: await askPages(n) };
}
const askPost = ({ signal, ...voice }) => fetch("/api/ask", { method: "POST", headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ stance: ls.get("gsa-librarian", {}).stance || "academic", voice }), signal });
// a new thread for the page you're on (once the book has loaded), its pages sent ahead
async function askThread() {
  await docReady;
  const n = want || app.page;  // where the reader is headed, even before PDF.js has landed there
  if (ASK.thread && ASK.page === n) return ASK.ready;
  if (ASK.thread) askPost({ end: ASK.thread }).then(r => r.body && r.body.cancel()).catch(() => {});
  const thread = ASK.thread = Math.random().toString(36).slice(2) + Date.now().toString(36);
  ASK.page = n;
  ASK.ready = askContext(n).then(ctx => {
    ASK.ctx = ctx;
    askPost({ prime: true, context: ctx, thread }).then(r => r.body && r.body.cancel()).catch(() => {});
  });
  return ASK.ready;
}
function askOpened() {
  const q = $("#ask-q");
  q.focus();
  askThread();
}
// plain markdown: paragraphs, > quotes, bold, italic, links; a link to a page of this book turns to it
function askRender(md, streaming) {
  if (streaming) md = md.replace(/\[[^\]]*(\]\([^)]*)?$/, "").replace(/\*+$/, "");
  const inline = t => esc(t).replace(/&gt;/g, ">")
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, text, url) => {
      const m = /\/b\/([a-z0-9-]+)\/(\d+)/.exec(url);
      if (m && m[1] === SLUG) return `<button class="r-cite here" data-page="${m[2]}">${text}</button>`;
      if (!/^(https?:\/\/|\/)/.test(url)) return text;
      return `<a class="r-cite" href="${url}" target="_blank" rel="noopener">${text}</a>`;
    })
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>").replace(/\*([^*]+)\*/g, "<em>$1</em>");
  return md.trim().split(/\n{2,}/).map(b => /^>/.test(b) ? `<blockquote>${inline(b.replace(/^> ?/gm, ""))}</blockquote>` : `<p>${inline(b)}</p>`).join("");
}
const ASK_VERB = { search_concordance: "search", read_pages: "read", get_volume_info: "info", "transcripts.search_transcripts": "audio",
  "transcripts.read_transcript": "listen", "pulpit.search_concordance": "talks", "pulpit.read_paragraphs": "talk", "web.search": "web", "web.fetch": "fetch" };
async function askSend(question) {
  await askThread();
  const body = $("#ask-body"), turn = document.createElement("div");
  turn.className = "r-aturn";
  turn.innerHTML = `<p class="r-aq"></p><div class="r-astep"></div><div class="r-aans"></div>`;
  turn.querySelector(".r-aq").textContent = question;
  body.append(turn);
  body.scrollTop = body.scrollHeight;
  const step = turn.querySelector(".r-astep"), ans = turn.querySelector(".r-aans");
  const ctrl = ASK.ctrl = new AbortController();
  ASK.busy = true; html.classList.add("asking"); askPaint();
  let final = null;
  try {
    const res = await askPost({ text: question, context: ASK.ctx, thread: ASK.thread, signal: ctrl.signal });
    if (!res.ok) throw new Error(res.status === 429 ? "Busy" : "Failed");
    const rd = res.body.getReader(), dec = new TextDecoder();
    let buf = "";
    for (;;) {
      const { value, done } = await rd.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      let i;
      while ((i = buf.indexOf("\n\n")) >= 0) {
        const chunk = buf.slice(0, i); buf = buf.slice(i + 2);
        if (!chunk.startsWith("data: ")) continue;
        const ev = JSON.parse(chunk.slice(6));
        if (ev.type === "step" && !ev.done) {
          const what = /\.(pdf|epub|docx?)$/i.test(ev.what || "") ? parseTitle((ev.what || "").split("/").pop()).title : (ev.what || "");
          step.textContent = `${ASK_VERB[ev.tool] || ev.tool.split(".").pop()} · ${what}`;
        }
        else if (ev.type === "draft") ans.innerHTML = askRender(ev.text, true);
        else if (ev.type === "final") final = ev;
        else if (ev.type === "error") throw new Error("Failed");
        if (body.scrollHeight - body.scrollTop - body.clientHeight < 160) body.scrollTop = body.scrollHeight;
      }
    }
    if (!final) throw new Error("Failed");
    ans.innerHTML = askRender(final.text, false);
    step.remove();
  } catch (e) {
    step.remove();
    ans.innerHTML = `<span class="r-astate">${e.name === "AbortError" ? "Stopped" : esc(e.message === "Busy" ? "Busy" : "Failed")}</span>`;
  } finally {
    if (ASK.ctrl === ctrl) { ASK.ctrl = null; ASK.busy = false; html.classList.remove("asking"); askPaint(); }
  }
}
function askPaint() {
  const go = $("#ask-go"), q = $("#ask-q");
  go.innerHTML = ASK.busy ? ic("stop") : ic("send");
  go.setAttribute("aria-label", ASK.busy ? "Stop" : "Send");
  go.disabled = !ASK.busy && !q.value.trim();
}
function wireAsk() {
  // only when the Mini's Librarian can take it (/api/engines says so), and
  // not beside a conversation, which is already the Librarian
  // Deseret Wiki: no Librarian on a static site
  Promise.resolve([]).then(list => {
    if (frameKind !== "beside" && Array.isArray(list) && list.some(e => e.voice && e.ready)) $("#r-ask").hidden = false;
  }).catch(() => {});
  $("#r-ask").onclick = e => openPanel("panel-ask", e.currentTarget);
  const q = $("#ask-q"), form = $("#ask-form");
  const grow = () => { q.style.setProperty("height", "auto"); q.style.setProperty("height", Math.min(140, q.scrollHeight) + "px"); };
  q.addEventListener("input", () => { grow(); askPaint(); });
  q.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); form.requestSubmit(); } });
  form.onsubmit = e => {
    e.preventDefault();
    if (ASK.busy) { ASK.ctrl && ASK.ctrl.abort(); return; }
    const text = q.value.trim();
    if (!text) return;
    q.value = ""; grow(); askPaint();
    askSend(text);
  };
  $("#ask-body").addEventListener("click", e => {
    const b = e.target.closest("button.r-cite");
    if (!b) return;
    if (narrow()) closeAll();  // a phone's sheet covers the page
    go(+b.dataset.page);
  });
}

/* ‹'s name: the shell's, when we're its iframe; on a phone, what the shell
   said as it handed this page over (book.js, gsa-back); else null, nothing
   behind: opened cold, from an agent's link, say */
function backName() {
  if (shell?.backName) return shell.backName();
  try { const b = JSON.parse(sessionStorage.getItem("gsa-back") || "null"); return b && b.path === BOOK.path ? b.name : null; } catch (_) { return null; }
}

/* ---------- the chrome ----------
   The shell's bar (DESIGN.md §8, §9 rule 5): where you can go on
   the left, where you are in the middle, at most three tools on the right;
   everything else in More, in words. The foot: Contents, the scrubber, the
   page. On phones every popover and panel is a sheet (reader.css). */
function build() {
  const root = document.createElement("div");
  root.id = "gsa-reader";
  // ‹ is Back, named for where it goes; opened cold there's nothing behind, so it's Up, named for the folder.
  // Beside a conversation it closes the book (‹ back to the conversation on a narrow window).
  const back = backName();
  const folder = BOOK.folder.split("/").pop() || "Bookshelf";
  const out = frameKind === "beside"
    ? (besideNarrow() ? { icon: "back", label: "Back to the conversation", name: "" } : { icon: "close", label: "Close the book", name: "" })
    : back != null ? { icon: "back", label: back ? "Back to " + back : "Back", name: back }
    : { icon: "back", label: "Up to " + folder, name: folder };
  const listenRow = BOOK.listen
    ? `<button role="menuitem" id="m-listen">${ic("voice")}Listen<small>AI voice</small></button>`
    : BOOK.canListen ? `<button role="menuitem" id="m-listen">${ic("voice")}Make an audiobook<small>AI voice</small></button>` : "";
  root.innerHTML = `
  <header class="r-bar" id="r-bar">
    <div class="r-zone l"><span class="r-slot"></span><a class="r-ib" id="r-back" href="${esc(BOOK.folderUrl)}" aria-label="${esc(out.label)}" title="${esc(out.label)}">${ic(out.icon)}</a>${out.name ? `<span class="r-backto">${esc(out.name)}</span>` : ""}</div>
    <div class="r-place"><b>${esc(NAME.title || BOOK.path.split("/").pop())}${NAME.subtitle ? `<span class="sub">: ${esc(NAME.subtitle)}</span>` : ""}</b>${NAME.author ? `<small>${esc(NAME.author)}</small>` : ""}</div>
    <div class="r-zone r">
      <button class="r-ib" id="r-ask" aria-label="Ask the Librarian about this page" title="Ask the Librarian about this page" aria-expanded="false" hidden>${ic("librarian")}</button>
      <button class="r-ib" id="r-listen" aria-label="Listen: read aloud by an AI voice" title="Listen (AI voice)"${BOOK.listen ? "" : " hidden"}>${ic("audiobook")}</button>
      <button class="r-ib" id="r-search" aria-label="Search in this book" title="Search in this book (/)" aria-expanded="false">${ic("search")}</button>
      <button class="r-ib" id="r-more" aria-label="More" title="More" aria-expanded="false">${ic("more")}</button>
      ${frameKind === "beside" ? `<a class="r-ib" id="r-whole" href="${esc(BOOK.url || "#")}" aria-label="The whole window" title="The whole window">${ic("external")}</a>` : ""}
    </div>
  </header>
  <footer class="r-foot" id="r-foot">
    <div class="r-fl"><button class="r-ib" id="r-toc" aria-label="Contents" title="Contents (C)" aria-expanded="false">${ic("contents")}</button><button class="r-ib" id="r-hold" aria-label="Hold the page straight" title="Hold the page straight" aria-pressed="false" hidden>${ic("lock")}</button></div>
    <div class="r-scrub"><span class="r-ticks" id="r-ticks" aria-hidden="true"></span><input type="range" id="r-scrub" min="1" max="1" value="1" aria-label="Page"><span class="r-scrubtag" id="r-scrubtag" aria-hidden="true"></span></div>
    <div class="r-where"><span class="r-sec" id="r-sec"></span><button class="r-pg" id="r-pg" aria-haspopup="dialog" aria-expanded="false" title="Go to page (G)"></button></div>
  </footer>
  <button class="r-fab r-frost" id="r-fab" aria-expanded="false" aria-controls="r-foot"></button>
  <button class="r-turn prev r-frost" id="r-prev" aria-label="Previous page">${ic("back")}</button>
  <button class="r-turn next r-frost" id="r-next" aria-label="Next page">${ic("forward")}</button>
  <div class="r-tag r-frost" id="r-tag" aria-hidden="true"></div>

  <div class="r-pop r-menu r-frost" id="pop-more" role="menu" aria-label="More" hidden>
    <button role="menuitem" id="m-display">${ic("textsize")}Display<small id="m-tone"></small></button>
    <button role="menuitem" id="m-mark" aria-pressed="false">${ic("bookmark")}<span>Bookmark this page</span><small class="key">B</small></button>
    ${listenRow}
    <hr>
    <button role="menuitem" id="m-copy">${ic("link")}<span>Copy link to this page</span></button>
    <a role="menuitem" id="m-download" href="${esc(FILE)}" download>${ic("download")}Download</a>
    ${/^\/derived\//.test(FILE) ? `<a role="menuitem" href="/files/${BOOK.path.split("/").map(encodeURIComponent).join("/")}" target="_blank" rel="noopener">${ic("external")}Original file</a>` : ""}
    <a role="menuitem" id="m-drive" href="#" target="_blank" rel="noopener" hidden>${ic("external")}Open in Drive</a>
    ${embedded ? `<a role="menuitem" id="m-tab" href="#" target="_blank" rel="noopener">${ic("external")}Open in a new tab</a>` : ""}
    <button role="menuitem" id="m-full" hidden>${ic("fullscreen")}Full screen<small class="key">F</small></button>
  </div>

  <div class="r-pop r-frost" id="pop-aa" role="dialog" aria-label="Display" hidden>
    <div class="r-row"><span class="r-label">Page</span>
      <div class="r-tones" role="radiogroup" aria-label="Page tone">
        <button class="r-tone paper" data-tone="paper" role="radio"><i></i><span>Paper</span></button>
        <button class="r-tone sepia" data-tone="sepia" role="radio"><i></i><span>Sepia</span></button>
        <button class="r-tone night" data-tone="night" role="radio"><i></i><span>Night</span></button>
      </div></div>
    <div class="r-row r-layout"><span class="r-label">Layout</span>
      <div class="r-tiles" role="radiogroup" aria-label="Layout">
        <button class="r-tile" data-layout="single" role="radio"><i>${ic("layout-single")}</i><span>Single</span></button>
        <button class="r-tile" data-layout="double" role="radio"><i>${ic("layout-double")}</i><span>Two pages</span></button>
        <button class="r-tile" data-layout="auto" role="radio"><i>${ic("layout-auto")}</i><span>Auto</span></button>
      </div></div>
    <div class="r-row"><span class="r-label">Reading</span>
      <div class="r-tiles two" role="radiogroup" aria-label="Reading">
        <button class="r-tile" data-flow="scroll" role="radio"><i>${ic("flow-scroll")}</i><span>Scroll</span></button>
        <button class="r-tile" data-flow="pages" role="radio"><i>${ic("flow-pages")}</i><span>Pages</span></button>
      </div></div>
    <div class="r-row r-scrubrow"><span class="r-label">Scrubber</span>
      <div class="r-seg" role="radiogroup" aria-label="Scrubber">
        <button data-scrub="bar" role="radio">Bar</button><button data-scrub="button" role="radio">Button</button>
      </div></div>
    <div class="r-row"><span class="r-label">Zoom</span>
      <div class="r-zoom">
        <button class="r-ib" id="z-out" aria-label="Zoom out">−</button>
        <div class="r-seg" role="radiogroup" aria-label="Fit"><button data-fit="width" role="radio">Width</button><button data-fit="page" role="radio">Page</button></div>
        <button class="r-ib" id="z-in" aria-label="Zoom in">+</button>
        <span class="r-zval" id="z-val"></span>
      </div></div>
  </div>

  <div class="r-pop r-audio r-frost" id="pop-audio" role="dialog" aria-label="Make an audiobook" hidden>
    <div class="r-atitle">${ic("voice")}Read aloud by an AI voice</div>
    <p class="r-atext" id="a-text" aria-live="polite"></p>
    <div class="r-abar" id="a-bar" hidden><i></i></div>
    <button class="r-fill" id="a-go" hidden></button>
  </div>

  <div class="r-pop r-goto r-frost" id="pop-goto" role="dialog" aria-label="Go to page" hidden>
    <form class="r-gform" id="goto-form" autocomplete="off">
      <input id="goto-q" type="text" inputmode="numeric" enterkeyhint="go" spellcheck="false" autocapitalize="off" placeholder="Page" aria-label="Page" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="goto-list">
      <button class="r-fill" type="submit" id="goto-go" disabled>Go</button>
    </form>
    <div class="r-glist" id="goto-list" role="listbox" aria-label="Pages"></div>
    <p class="r-ghint" id="goto-hint" aria-live="polite"></p>
  </div>

  <aside class="r-panel left r-frost" id="panel-toc" aria-label="Contents" hidden>
    <div class="r-phead">
      <div class="r-seg" role="tablist" id="toc-tabs">
        <button role="tab" data-tab="toc" id="tab-toc">Contents</button>
        <button role="tab" data-tab="pages" id="tab-pages">Pages</button>
        <button role="tab" data-tab="marks" id="tab-marks" hidden>Bookmarks</button>
      </div>
      <b id="toc-title" hidden>Pages</b>
      <button class="r-ib" data-close aria-label="Close">${ic("close")}</button>
    </div>
    <div class="r-pbody" id="toc-body"><ol class="r-toc" id="r-toclist"></ol><div class="r-thumbs" id="r-thumbs" hidden></div><ol class="r-marks" id="r-marks" hidden></ol></div>
  </aside>

  <aside class="r-panel right r-searchp r-frost" id="panel-search" aria-label="Search in this book" hidden>
    <div class="r-phead">
      <form class="r-sform" id="r-sform" role="search">${ic("search", "sm")}<input id="r-sq" type="search" autocomplete="off" spellcheck="false" placeholder="Search in this book" aria-label="Search in this book"></form>
      <button class="r-ib" data-close aria-label="Close">${ic("close")}</button>
    </div>
    <div class="r-ssum" id="r-ssum"></div>
    <div class="r-pbody"><ol class="r-hits" id="r-hits"></ol></div>
  </aside>
  <aside class="r-panel right r-frost" id="panel-ask" aria-label="Ask the Librarian" hidden>
    <div class="r-phead"><b>Ask the Librarian</b><button class="r-ib" data-close aria-label="Close">${ic("close")}</button></div>
    <div class="r-pbody r-askbody" id="ask-body"><p class="r-askhint">About this page: the Librarian reads it and the pages either side before you finish typing, and answers with citations.</p></div>
    <form class="r-aform" id="ask-form" autocomplete="off">
      <textarea id="ask-q" rows="1" placeholder="Ask about this page" aria-label="Ask the Librarian about this page" enterkeyhint="send"></textarea>
      <button type="submit" id="ask-go" aria-label="Send" disabled>${ic("send")}</button>
    </form>
  </aside>
  <div class="r-scrim" id="r-scrim"></div>
  <button class="r-pass r-fill" id="r-pass" hidden>Copy link</button>
  <div class="r-find r-frost" id="r-find" role="status" hidden>
    <button class="r-flabel" id="r-flabel" title="Show every match">${ic("search", "sm")}<span class="r-fq" id="r-fq"></span><span class="r-fn" id="r-fn"></span></button>
    <button class="r-ib r-fstep" id="r-fprev" aria-label="Previous match">${ic("back")}</button>
    <button class="r-ib r-fstep" id="r-fnext" aria-label="Next match">${ic("forward")}</button>
    <button class="r-ib" id="r-fclear" aria-label="Clear the highlight" title="Clear the highlight (Esc)">${ic("close")}</button>
  </div>`;
  document.body.append(root);
  if (!BOOK.url) $("#m-copy").hidden = true;
}

/* ---------- boot ---------- */
// turns a page in Pages mode, played like paper (wirePageTurns)
let pageTurn = dir => dir > 0 ? app.pdfViewer.nextPage() : app.pdfViewer.previousPage();
let app, bus, doc = null, total = 0, labels = null, outline = [], flatToc = [], parity = 2;
// the page the reader is headed for: where the book opened, then every jump
// and every page they turn or scroll to themselves
let want = 0;

function boot(a) {
  app = a;
  if (!document.getElementById("gsa-reader")) build();   // built at script start, before the engine; this is the fallback
  wireChrome();
  wirePopovers();
  wireSheets();
  wireKeys();
  pageTurn = wirePageTurns();
  wirePassage();
  wireGoto();
  wireAudio();
  wireMarks();
  wireAsk();
  // PDF.js lands on a link's page, and when a book's pages differ in size it
  // lands there again once every page has been measured, seconds later. By
  // then the reader may have gone elsewhere: land again where they're headed.
  const setInitialView = app.setInitialView.bind(app);
  app.setInitialView = (hash, opts) => {
    if (app.isInitialViewSet && want) app.initialBookmark = "page=" + want;
    return setInitialView(hash, opts);
  };
  const orig = app.progress.bind(app);
  app.progress = pct => { orig(pct); loadProgress(pct); };
  app.initializedPromise.then(() => {
    bus = app.eventBus;
    bus.on("pagesinit", onPagesInit);
    bus.on("pagechanging", e => onPage(e.pageNumber));
    bus.on("spreadmodechanged", () => { if (total) onPage(app.page); });
    bus.on("pagerendered", e => { judgePage(e.source); if (e.pageNumber === app.page) instantGone(); });
    bus.on("scalechanging", paintZoom);
    bus.on("documentloaded", loadDone);
    bus.on("pagesinit", loadDone);   // the pages exist: a breath before the first one is drawn and the book scrolls
    if (app.pdfDocument) loadDone(); // a load that beat these listeners
    bus.on("documenterror", openFailed);
    bus.on("updatefindmatchescount", e => findCount(e.matchesCount));
    bus.on("updatefindcontrolstate", e => findCount(e.matchesCount, e.state));
    bus.on("find", showFind);
  });
}

async function onPagesInit() {
  quiet(1800);
  doc = app.pdfDocument;
  total = app.pagesCount;
  $("#r-scrub").max = total;
  html.classList.add("loaded");
  warmWorker();
  clearTimeout(openTimer);
  $("#r-opening").hidden = true;
  try { labels = await doc.getPageLabels(); } catch (_) { labels = null; }
  parity = spreadParity(labels);
  // pagesinit comes before PDF.js opens at the link's page; deciding the
  // page now would pin every book to page 1
  if (!app.isInitialViewSet) await new Promise(r => bus.on("documentinit", r, { once: true }));
  let start = app.page;
  if (!explicitPage) {
    const saved = ls.get("gsa-pos", {})[BOOK.path];
    if (saved && saved.p > 1 && saved.p <= total) start = saved.p;
  }
  want = start;
  docLoaded();   // only now: Ask, opened early, sends the pages around where the book opens, not page 1
  quiet();
  applyLayout(true, start);
  onPage(app.page);
  loadOutline();
  paintAa();
  // the chrome stays until you start reading (wireChrome): a first look always shows the way out
  const drive = (() => { try { return sessionStorage.getItem("drive:" + BOOK.path) || ""; } catch (_) { return ""; } })();
  if (drive) { const d = $("#m-drive"); d.href = drive; d.hidden = false; }
  if (linked) {
    // the search panel starts from it too, so its matches are a tap away
    $("#r-sq").value = [].concat(linked.query).map(t => /\s/.test(t) ? `"${t}"` : t).join(" ");
    findIn(linked.query, linked.passage);
  }
}

/* ---------- two-page spreads, the way a book is bound ----------
   PDF.js pairs by PDF index; a book puts even pages on the left. When the
   PDF carries its printed page numbers, vote on which pairing puts even
   numbers left. Without them, the cover stands alone (EVEN mode). */
function spreadParity(labels) {
  if (!labels) return 2;
  let same = 0, diff = 0;
  labels.forEach((l, i) => {
    if (!/^\d+$/.test(l || "")) return;
    ((i + 1 - +l) % 2 === 0) ? same++ : diff++;
  });
  return diff > same ? 1 : 2;  // index and number agree → even indexes go left → EVEN
}
function wantSpread() {
  const l = prefs().layout;
  if (l === "single" || total < 3) return false;
  if (l === "double") return true;
  return innerWidth >= 1080 && innerWidth > innerHeight * 1.15;
}
function applyLayout(first, page = app?.page) {
  if (!app?.pdfViewer || !total) return;
  quiet();
  const v = app.pdfViewer, p = prefs();
  const spread = wantSpread() ? parity : 0, scroll = p.flow === "pages" ? 3 : 0;
  html.classList.toggle("two-up", !!spread);   // not "spread": PDF.js styles .spread { white-space: nowrap }, which then reached every word of ours
  html.classList.toggle("flow-pages", scroll === 3);
  const changed = v.spreadMode !== spread || v.scrollMode !== scroll;
  if (v.scrollMode !== scroll) v.scrollMode = scroll;
  if (v.spreadMode !== spread) v.spreadMode = spread;
  // an explicit zoom in the link (#zoom=) wins on first paint
  if (!(first && /(^#|&)zoom=/.test(location.hash))) {
    const z = zoomValue(p, !!spread);
    v.currentScaleValue = z;
    // and again once the new mode has laid out, against the container's final size
    requestAnimationFrame(() => { v.currentScaleValue = z; if (changed || first) app.page = page; });
  }
  if (changed || first) app.page = page;
}
let resizeT;
addEventListener("resize", () => { clearTimeout(resizeT); resizeT = setTimeout(() => { if (prefs().layout === "auto") applyLayout(); }, 250); });

/* ---------- where you are ---------- */
let saveT, tagT, lastPage = 0;
// a page's printed number, when the PDF carries one that differs from its index
const printed = n => labels && labels[n - 1] && labels[n - 1] !== String(n) ? labels[n - 1] : "";
// every jump goes through here, so a late engine landing can't undo it
function go(n) {
  want = n;
  quiet();
  app.page = n;
}
function onPage(n) {
  if (!total) return;
  // a page you turned or scrolled to yourself; not one a jump or layout passed through
  if (Date.now() >= quietUntil) want = n;
  const label = printed(n);
  // two pages side by side report the left one; name both, so a jump to a
  // right-hand page doesn't look like it landed one short
  const [a, b] = spreadAt(n), la = printed(a), lb = b && printed(b);
  const idx = b ? `${a}–${b}` : `${n}`, lab = b ? (la && lb ? `${la}–${lb}` : la || lb) : label;
  $("#r-pg").textContent = lab ? `p. ${lab} · ${idx} / ${total}` : `${idx} / ${total}`;
  $("#r-pg").setAttribute("aria-label", `Page ${lab ? lab + ", " : ""}${idx} of ${total}. Go to page`);
  $("#r-fab").textContent = lab ? `p. ${lab}` : `${idx} / ${total}`;
  $("#r-fab").setAttribute("aria-label", `Page ${lab ? lab + ", " : ""}${idx} of ${total}. Contents and the scrubber`);
  const s = $("#r-scrub");
  if (!scrubbing) s.value = n;
  s.style.setProperty("--fill", ((n - 1) / Math.max(1, total - 1) * 100).toFixed(2) + "%");
  $(".r-prog i").style.setProperty("width", (n / total * 100).toFixed(2) + "%");
  $("#r-sec").textContent = sectionAt(n)?.title || "";
  markToc(n);
  markThumb(n);
  paintMark(n);
  if (html.classList.contains("chrome-off") && lastPage && n !== lastPage) flashTag(n, label);
  lastPage = n;
  clearTimeout(saveT);
  saveT = setTimeout(() => remember(n), 800);
  trackUrl(n);
}
// the pages showing together: [left, right] in a two-page spread, else [n, 0]
function spreadAt(n) {
  const mode = app?.pdfViewer?.spreadMode || 0;
  if (!mode || (mode === 2 && n === 1)) return [n, 0];
  // ODD pairs 1–2, 3–4…; EVEN keeps the cover alone, then 2–3, 4–5…
  const left = mode === 1 ? n - ((n - 1) % 2) : n - (n % 2);
  return left + 1 <= total ? [left, left + 1] : [left, 0];
}
function flashTag(n, label) {
  const t = $("#r-tag");
  t.textContent = label ? `p. ${label}` : `${n} / ${total}`;
  t.classList.add("on");
  clearTimeout(tagT);
  tagT = setTimeout(() => t.classList.remove("on"), 1100);
}
function remember(n) {
  const all = ls.get("gsa-pos", {});
  all[BOOK.path] = { p: n, n: total, at: Date.now() };
  const keys = Object.keys(all);
  if (keys.length > 300) keys.sort((a, b) => all[a].at - all[b].at).slice(0, keys.length - 300).forEach(k => delete all[k]);
  ls.set("gsa-pos", all);
}
// Keep `p=` on the address bar in step with the page being read. Opened bare
// (every phone, or "new tab ↗"), this URL is what gets shared, and the server
// can't see the #page fragment when an unfurler asks for the card. Inside the
// shell's iframe the shell owns the address bar (it listens itself).
let urlT;
function trackUrl(n) {
  if (embedded) return;
  clearTimeout(urlT);
  urlT = setTimeout(() => {
    // string edits, not URLSearchParams: re-serializing would encode the
    // `file=` path, and the viewer 404s on an encoded one
    let q = location.search, h = location.hash;
    q = /[?&]p=\d+/.test(q) ? q.replace(/([?&])p=\d+/, "$1p=" + n) : q + "&p=" + n;
    h = /(^#|&)page=\d+/.test(h) ? h.replace(/(^#|&)page=\d+/, "$1page=" + n) : (h ? h + "&" : "#") + "page=" + n;
    if (q + h !== location.search + location.hash) history.replaceState(history.state, "", location.pathname + q + h);
  }, 400);
}
function loadProgress(pct) {
  const bar = $(".r-prog");
  if (!bar) return;
  // Servers without Content-Length can report an unknown percentage.
  pct = Number.isFinite(pct) ? Math.min(100, Math.max(0, pct)) : 0;
  // once the book is open the line is done: in range mode the engine keeps
  // fetching the rest of the file behind you and reporting it, and that is
  // not what anyone is waiting for (a 200 MB commentary would "load" for minutes)
  if (WORKING.done) pct = 100;
  WORKING.real = pct;
  bar.classList.toggle("loading", pct < 100);
  // while the engine downloads nothing reports, so the line eases toward 92% on
  // its own (DESIGN.md: the accent means working); the book's real progress
  // shows as soon as it's ahead, and documentloaded fills it
  bar.style.setProperty("--load", (pct >= 100 ? 100 : Math.round(Math.max(4, pct, WORKING.fake) * 10) / 10) + "%");
}
const WORKING = { fake: 4, real: 0, timer: 0, done: false };
// the book is open: the line fills and stays filled (Noah, 2026-10-31: a loading
// bar is about the reader's experience, and may end a hair before the page scrolls)
function loadDone() { if (WORKING.done) return; WORKING.done = true; loadProgress(100); }

/* ---------- the chrome comes and goes ----------
   It leaves when you start reading (scrolling into the book) and comes back
   when you scroll up, reach for an edge with the mouse, tap the middle of
   the page, or open anything from it. */
let chromeLock = 0, quietUntil = 0;
// a jump we made (opening at a page, the scrubber, contents, a search hit)
// scrolls the viewer too; that isn't the reader scrolling away
const quiet = (ms = 900) => { quietUntil = Date.now() + ms; };
function chrome(show) {
  if (!show && (chromeLock || anyOpen())) return;
  html.classList.toggle("chrome-off", !show);
  if (!show) scrubCard(false);
  if (frameKind === "window") shell?.chrome?.(show);
}
/** the foot, behind its button (Display, Scrubber: Button): open as a floating card, or tucked away */
function scrubCard(open) {
  html.classList.toggle("scrub-open", open);
  $("#r-fab")?.setAttribute("aria-expanded", String(open));
}
function anyOpen() { return $$(".r-pop:not([hidden]), .r-panel:not([hidden])").length > 0; }
function wireChrome() {
  const vc = $("#viewerContainer");
  let lastY = 0, touched = 0;
  // only you scroll the bars away: PDF.js's own landings (a link's page, again once every page is
  // measured, seconds on; a find) come with no input, and must never hide the way out
  for (const t of ["wheel", "touchmove", "keydown", "pointerdown"]) addEventListener(t, () => { touched = Date.now(); }, { passive: true, capture: true });
  vc.addEventListener("scroll", () => {
    const y = vc.scrollTop, dy = y - lastY;
    if (Math.abs(dy) < 6) return;
    if (Date.now() < quietUntil || Date.now() - touched > 1200) { lastY = y; return; }
    if (dy > 0 && y > 120) chrome(false);
    else if (dy < -30) chrome(true);
    lastY = y;
  }, { passive: true });
  addEventListener("mousemove", e => {
    if (coarse) return;
    if (e.clientY < 72 || e.clientY > innerHeight - 72) chrome(true);
  }, { passive: true });
  // ‹ does what it says: Back when the shell said there's a step behind, else Up to the folder
  $("#r-back").onclick = e => {
    e.preventDefault();
    if (shell) return shell.back(BOOK.folder);
    if (backName() != null) history.back();
    else location.href = BOOK.folderUrl;
  };
  // beside a conversation: this book in the whole window, the conversation kept for Back
  if ($("#r-whole")) $("#r-whole").onclick = e => { if (shell?.whole) { e.preventDefault(); shell.whole(app.page); } };
  // the volume read aloud (kbook, an AI voice): the shell's Listen view, where
  // the bar plays it; a book without audio yet offers to have it made (wireAudio)
  // a book with an audiobook shows Listen in the bar too, not only in More (Noah, 2026-11-09: "where is the button to listen to the ai audiobook?")
  $("#r-listen").onclick = () => {
    if (shell && shell.listen) return shell.listen(BOOK.listen);
    location.href = BOOK.listen;
  };
  if ($("#m-listen")) $("#m-listen").onclick = () => {
    if (!BOOK.listen) return openAudio($("#r-more"));
    closeAll(true);
    if (shell && shell.listen) return shell.listen(BOOK.listen);
    location.href = BOOK.listen;
  };
  if (BOOK.canListen) audioStatus().then(paintAudio);
  $("#r-prev").onclick = () => pageTurn(-1);
  $("#r-next").onclick = () => pageTurn(1);
  // the scrubber: drag to see where you'd land, let go to go there
  const s = $("#r-scrub");
  s.addEventListener("input", () => { scrubbing = true; scrubTag(+s.value); });
  s.addEventListener("change", () => { scrubbing = false; $("#r-scrubtag").classList.remove("on"); go(+s.value); });
  s.addEventListener("pointerup", () => { if (scrubbing) s.dispatchEvent(new Event("change")); });
}
let scrubbing = false;
function scrubTag(n) {
  const t = $("#r-scrubtag"), s = $("#r-scrub");
  const label = labels && labels[n - 1] && labels[n - 1] !== String(n) ? `p. ${labels[n - 1]}` : `${n}`;
  const sec = sectionAt(n)?.title;
  t.innerHTML = `<b>${esc(label)}</b>${sec ? `<span>${esc(sec)}</span>` : ""}`;
  t.classList.add("on");
  t.style.setProperty("--x", ((n - 1) / Math.max(1, total - 1) * 100).toFixed(2) + "%");
  s.style.setProperty("--fill", ((n - 1) / Math.max(1, total - 1) * 100).toFixed(2) + "%");
}

/* ---------- go to a page ----------
   Books are cited by their printed page numbers, and those rarely match the
   PDF's own (a cover and roman-numbered front matter come first). So what
   you type is matched against the printed numbers first, and the PDF page
   of that number is the alternative; both show where they land, and Enter
   takes the highlighted one. The field opens empty: nothing to select, so
   nothing for a browser to get wrong about the selection. */
function pageMatches(raw) {
  const q = String(raw ?? "").trim().toLowerCase();
  if (!q || !total) return [];
  // "p. 36", "pg 36", "page 36" all mean 36; a label is tried as typed too
  const bare = q.replace(/^(?:page|pg|p)\.?\s*(?=\S)/, "");
  const out = [];
  if (labels) labels.forEach((l, i) => {
    const t = String(l ?? "").trim().toLowerCase();
    if (t && (t === q || t === bare) && out.length < 4) out.push({ n: i + 1, printed: true });
  });
  const n = /^\d+$/.test(bare) ? Number(bare) : 0;
  if (n >= 1 && n <= total && !out.some(o => o.n === n)) out.push({ n, printed: false });
  return out;
}
function wireGoto() {
  const q = $("#goto-q"), list = $("#goto-list"), hint = $("#goto-hint"), goBtn = $("#goto-go");
  let matches = [], active = 0;
  const range = () => labels && labels.some((l, i) => l && l !== String(i + 1))
    ? `A printed page number, or PDF page 1–${total}` : `1–${total}`;
  const paint = () => {
    matches = pageMatches(q.value);
    active = Math.min(active, Math.max(0, matches.length - 1));
    list.innerHTML = matches.map((m, i) => {
      const label = printed(m.n), sec = sectionAt(m.n)?.title || "";
      const head = !label ? `Page ${m.n}` : m.printed ? `p. ${label}` : `PDF page ${m.n}`;
      const sub = [!label ? "" : m.printed ? `PDF page ${m.n}` : `p. ${label}`, sec].filter(Boolean).join(" · ");
      return `<button type="button" class="r-gopt" role="option" id="goto-o${i}" data-i="${i}" aria-selected="${i === active}">` +
        `<b>${esc(head)}</b><span>${esc(sub)}</span></button>`;
    }).join("");
    q.setAttribute("aria-expanded", String(matches.length > 0));
    if (matches.length) q.setAttribute("aria-activedescendant", "goto-o" + active);
    else q.removeAttribute("aria-activedescendant");
    goBtn.disabled = !matches.length;
    const typed = q.value.trim();
    hint.textContent = !typed ? range() : matches.length ? "" : `No page “${typed}”. ${range()}.`;
    hint.hidden = !hint.textContent;
  };
  const commit = i => {
    const m = matches[i];
    if (!m) return;
    q.blur();  // a phone's keyboard goes down with the sheet
    closeAll();
    go(m.n);
  };
  $("#r-pg").onclick = e => {
    const pop = $("#pop-goto");
    if (!pop.hidden) return closeAll();
    q.value = ""; active = 0; paint();
    openPop("pop-goto", e.currentTarget);
    q.focus();  // inside the tap, or iOS won't raise the keyboard
  };
  q.addEventListener("input", () => { active = 0; paint(); });
  q.addEventListener("keydown", e => {
    if (e.key !== "ArrowDown" && e.key !== "ArrowUp") return;
    e.preventDefault();
    if (!matches.length) return;
    active = (active + (e.key === "ArrowDown" ? 1 : -1) + matches.length) % matches.length;
    paint();
  });
  $("#goto-form").addEventListener("submit", e => { e.preventDefault(); commit(active); });
  list.addEventListener("click", e => {
    const b = e.target.closest(".r-gopt");
    if (b) commit(+b.dataset.i);
  });
  // a phone's keyboard covers the bottom of the screen; the sheet rides above it
  const vv = window.visualViewport;
  if (vv) {
    const lift = () => html.style.setProperty("--kb", Math.max(0, innerHeight - vv.height - vv.offsetTop) + "px");
    vv.addEventListener("resize", lift);
    vv.addEventListener("scroll", lift);
  }
}

/* ---------- making an audiobook ----------
   Any book with readable text can be read aloud on the Mini (kbook). The
   request is the site's one control that asks for work (server.py
   audio_request): it's checked and queued at once, and this panel
   follows it until the Listen view can open. */
const SLUG = (BOOK.url || "").replace(/^\/b\//, "");
let audioState = { state: "none" }, audioPoll = 0;
async function audioStatus() {
  try { return await (await fetch("/api/audio-request?slug=" + encodeURIComponent(SLUG))).json(); }
  catch (_) { return { state: "none" }; }
}
function paintAudio(st) {
  audioState = st || audioState;
  const s = audioState, text = $("#a-text"), go = $("#a-go"), bar = $("#a-bar"), btn = $("#m-listen");
  if (!text) return;
  btn?.classList.toggle("r-busy", s.state === "queued" || s.state === "running" || s.state === "checking");
  if (s.state === "done" && s.listen) { BOOK.listen = s.listen; if (btn) btn.innerHTML = ic("voice") + "Listen<small>AI voice</small>"; $("#r-listen").hidden = false; }
  // about 300 words a page, 150 spoken a minute, read ~37x faster than real time
  const est = Math.max(3, Math.round((total || 200) * 300 / 150 / 37 + 1.5));
  const msg = {
    none: `An AI voice can read this book aloud. Making it takes about ${est} minutes; keep reading, and Listen will be in More when it's ready.`,
    checking: `An AI voice can read this book aloud. Making it takes about ${est} minutes; keep reading, and Listen will be in More when it's ready.`,
    queued: `In line${s.position ? ` behind ${s.position} ${s.position > 1 ? "others" : "other"}` : ""}. Ready in about ${s.minutes} min; come back then.`,
    running: `Reading aloud now. About ${s.minutes} min left.`,
    done: "Ready.",
    busy: "Too many books are being read right now. Try again later.",
    full: "No room for more audiobooks right now.",
  }[s.state];
  const why = { unreadable: "This book's text doesn't read cleanly enough to read aloud.",
                long: "This book is too long for one audiobook.",
                unsupported: "This file can't be read aloud.",
                full: "No room for more audiobooks right now." }[s.reason] || "Something went wrong with this one. Try again in an hour.";
  text.textContent = s.state === "failed" ? why : msg || "";
  bar.hidden = s.state !== "running" && s.state !== "checking";
  bar.classList.toggle("r-awork", s.state === "checking");
  bar.firstElementChild.style.width = s.state === "running" ? Math.round((s.progress || 0) * 100) + "%" : "";
  go.hidden = !["none", "checking", "done"].includes(s.state);
  go.disabled = s.state === "checking";
  go.textContent = s.state === "done" ? "Listen" : s.state === "checking" ? "Checking" : "Make the audiobook";
  clearTimeout(audioPoll);
  if ((s.state === "queued" || s.state === "running") && !$("#pop-audio").hidden)
    audioPoll = setTimeout(async () => paintAudio(await audioStatus()), 15000);
}
async function openAudio(btn) {
  openPop("pop-audio", btn);
  paintAudio(await audioStatus());
}
function wireAudio() {
  const go = $("#a-go");
  if (!go) return;
  go.onclick = async () => {
    if (audioState.state === "done") {
      closeAll(true);
      if (shell && shell.listen) return shell.listen(BOOK.listen);
      return void (location.href = BOOK.listen);
    }
    paintAudio({ state: "checking" });
    let st;
    try {
      const r = await fetch("/api/audio-request", { method: "POST", headers: { "Content-Type": "application/json" },
                                                     body: JSON.stringify({ slug: SLUG }) });
      st = await r.json();
    } catch (_) { st = { state: "failed", reason: "error" }; }
    paintAudio(st);
  };
}

/* ---------- popovers and panels ---------- */
/* On a phone every popover and panel is a sheet (gsa.css): it rises from
   the bottom, follows your finger when you drag it down, and goes on a
   firm pull or a flick — the way iOS sheets do. On desktop they simply
   appear and disappear. */
let closing = null;
function show(el, btn) {
  clearTimeout(closing); closing = null;
  $$(".r-pop, .r-panel").forEach(p => { p.classList.remove("out"); p.style.removeProperty("transform"); });
  el.hidden = false;
  btn?.setAttribute("aria-expanded", "true");
  html.classList.add("sheet-open");
  chrome(true);
}
function openPop(id, btn) {
  const pop = $("#" + id), was = !pop.hidden;
  closeAll(!was);
  if (was) return;
  show(pop, btn);
}
function openPanel(id, btn) {
  const p = $("#" + id), was = !p.hidden;
  closeAll(!was);
  if (was) return;
  show(p, btn);
  html.classList.add("panel-" + (p.classList.contains("left") ? "left" : "right"));
  if (id === "panel-search") {
    const q = $("#r-sq"); q.focus(); q.select();
    if (q.value && !$("#r-hits").children.length) runSearch();  // filled from the link
  }
  if (id === "panel-toc") showTab(outline.length ? "toc" : "pages");
  if (id === "panel-ask") askOpened();
}
function closeAll(instant) {
  const open = $$(".r-pop:not([hidden]), .r-panel:not([hidden])");
  // don't leave a phone's keyboard up over a sheet that's leaving
  if (open.some(p => p.contains(document.activeElement))) document.activeElement.blur();
  $$("[aria-expanded]").forEach(b => b.setAttribute("aria-expanded", "false"));
  html.classList.remove("panel-left", "panel-right", "sheet-open");
  const done = () => { open.forEach(p => { p.hidden = true; p.classList.remove("out"); p.style.removeProperty("transform"); }); closing = null; };
  if (instant || !narrow() || !open.length || matchMedia("(prefers-reduced-motion: reduce)").matches) return done();
  open.forEach(p => { p.style.removeProperty("transform"); p.classList.add("out"); });
  closing = setTimeout(done, 300);
}
function wireSheets() {
  $$(".r-pop, .r-panel").forEach(sheet => {
    const grab = document.createElement("div");
    grab.className = "r-grab"; grab.setAttribute("aria-hidden", "true");
    sheet.prepend(grab);
    let y0 = null, t0 = 0, dy = 0, dragging = false;
    sheet.addEventListener("touchstart", e => {
      y0 = null;
      if (!narrow() || e.touches.length !== 1) return;
      // from the grabber or header, always; from a list, only once it's scrolled to the top
      const list = e.target.closest(".r-pbody, .r-hits");
      if (list && list.scrollTop > 0) return;
      y0 = e.touches[0].clientY; t0 = Date.now(); dy = 0; dragging = false;
    }, { passive: true });
    sheet.addEventListener("touchmove", e => {
      if (y0 == null) return;
      const d = e.touches[0].clientY - y0;
      if (!dragging) {
        if (d > 8) { dragging = true; sheet.classList.add("dragging"); document.activeElement?.blur?.(); }
        else if (d < -8) { y0 = null; return; }
        else return;
      }
      e.preventDefault();
      dy = d > 0 ? d : d / 5;  // past the top it resists, like a rubber band
      sheet.style.setProperty("transform", `translateY(${dy}px)`);
      $("#r-scrim").style.setProperty("opacity", String(Math.max(0, 1 - dy / 400)));
    }, { passive: false });
    const end = () => {
      if (!dragging) { y0 = null; return; }
      const v = dy / Math.max(1, Date.now() - t0);
      sheet.classList.remove("dragging");
      $("#r-scrim").style.removeProperty("opacity");
      y0 = null; dragging = false;
      if (dy > 110 || (v > .5 && dy > 30)) {
        sheet.style.setProperty("transform", `translateY(${dy}px)`);
        requestAnimationFrame(() => closeAll());
      } else sheet.style.removeProperty("transform");
    };
    sheet.addEventListener("touchend", end);
    sheet.addEventListener("touchcancel", end);
  });
}
function wirePopovers() {
  $("#m-display").onclick = () => openPop("pop-aa", $("#r-more"));
  $("#r-more").onclick = e => { paintMore(); openPop("pop-more", e.currentTarget); };
  $("#r-search").onclick = e => openPanel("panel-search", e.currentTarget);
  $("#r-toc").onclick = e => openPanel("panel-toc", e.currentTarget);
  $("#r-scrim").onclick = () => closeAll();
  $$("[data-close]").forEach(b => b.onclick = () => closeAll());
  document.addEventListener("pointerdown", e => {
    if (e.target.closest(".r-pop, .r-panel, .r-bar, .r-foot, .r-find")) return;
    if ($$(".r-pop:not([hidden])").length) closeAll();
  }, true);
  // Aa
  $$("[data-tone]").forEach(b => b.onclick = () => { setPref("tone", b.dataset.tone); html.dataset.tone = b.dataset.tone; paintAa(); });
  $$("[data-layout]").forEach(b => b.onclick = () => { setPref("layout", b.dataset.layout); applyLayout(); paintAa(); });
  $$("[data-flow]").forEach(b => b.onclick = () => { setPref("flow", b.dataset.flow); applyLayout(); paintAa(); });
  $$("[data-fit]").forEach(b => b.onclick = () => { setPref("fit", b.dataset.fit); applyLayout(); paintAa(); });
  $$("[data-scrub]").forEach(b => b.onclick = () => { setPref("scrub", b.dataset.scrub); html.classList.toggle("scrub-button", b.dataset.scrub === "button"); scrubCard(false); paintAa(); });
  $("#r-fab").onclick = () => scrubCard(true);
  // a touch anywhere but the card or its button tucks the card away
  document.addEventListener("pointerdown", e => { if (!e.target.closest(".r-foot, .r-fab, .r-pop, .r-panel")) scrubCard(false); }, true);
  $("#z-in").onclick = () => { app.pdfViewer.increaseScale(); setPref("fit", "custom"); paintAa(); };
  $("#z-out").onclick = () => { app.pdfViewer.decreaseScale(); setPref("fit", "custom"); paintAa(); };
  // more
  $("#m-copy").onclick = async () => {
    const url = SITE + BOOK.url + (app.page > 1 ? "/" + app.page : "");
    const b = $("#m-copy");
    try { await navigator.clipboard.writeText(url); b.textContent = "Copied"; }
    catch (_) { b.textContent = url; }
    setTimeout(() => { b.textContent = "Copy link to this page"; closeAll(); }, 1100);
  };
  const fs = embedded ? (() => { try { return window.parent.document; } catch (_) { return null; } })() : document;
  if (fs && fs.fullscreenEnabled) {
    const b = $("#m-full");
    b.hidden = false;
    b.onclick = () => { fs.fullscreenElement ? fs.exitFullscreen() : fs.documentElement.requestFullscreen().catch(() => {}); closeAll(); };
  }
  // search
  let st;
  $("#r-sq").addEventListener("input", () => { clearTimeout(st); st = setTimeout(runSearch, 260); });
  $("#r-sform").onsubmit = e => { e.preventDefault(); clearTimeout(st); runSearch(true); };
  $("#r-flabel").onclick = () => openPanel("panel-search", $("#r-search"));
  $("#r-fprev").onclick = () => stepFind(true);
  $("#r-fnext").onclick = () => stepFind(false);
  $("#r-fclear").onclick = clearFind;
  // contents tabs
  $$("[data-tab]").forEach(b => b.onclick = () => showTab(b.dataset.tab));
}
function paintAa() {
  const p = prefs();
  $$("[data-tone]").forEach(b => b.setAttribute("aria-checked", String(b.dataset.tone === p.tone)));
  $$("[data-layout]").forEach(b => b.setAttribute("aria-checked", String(b.dataset.layout === p.layout)));
  $$("[data-flow]").forEach(b => b.setAttribute("aria-checked", String(b.dataset.flow === p.flow)));
  $$("[data-fit]").forEach(b => b.setAttribute("aria-checked", String(b.dataset.fit === p.fit)));
  $$("[data-scrub]").forEach(b => b.setAttribute("aria-checked", String(b.dataset.scrub === p.scrub)));
  paintZoom();
}
function paintZoom() {
  const v = app?.pdfViewer;
  if (v && $("#z-val")) $("#z-val").textContent = Math.round((v.currentScale || 1) * 100) + "%";
}
function paintMore() {
  $("#m-tone").textContent = { paper: "Paper", sepia: "Sepia", night: "Night" }[prefs().tone] || "";
  const t = $("#m-tab");
  if (t && app) t.href = location.pathname + location.search.replace(/([?&])p=\d+/, "") + "&p=" + app.page + "#page=" + app.page;
}

/* ---------- keys ----------
   PDF.js keeps its own: arrows, space, PgUp/PgDn, n/p, j/k, +/−. */
function wireKeys() {
  addEventListener("keydown", e => {
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName || "");
    if (e.key === "Escape") {
      if (anyOpen()) { closeAll(); e.preventDefault(); e.stopPropagation(); return; }
      if (finding) { clearFind(); e.preventDefault(); return; }
      chrome(html.classList.contains("chrome-off"));
      return;
    }
    if ((e.metaKey || e.ctrlKey) && !e.altKey && e.key.toLowerCase() === "f") {
      e.preventDefault(); e.stopPropagation(); openPanel("panel-search", $("#r-search")); return;
    }
    // PDF.js's own ⌥⌘G / Ctrl+Alt+G focuses its hidden page field
    if ((e.metaKey || e.ctrlKey) && e.altKey && e.code === "KeyG") {
      e.preventDefault(); e.stopPropagation(); if ($("#pop-goto").hidden) $("#r-pg").click(); return;
    }
    if (typing || e.metaKey || e.ctrlKey || e.altKey) return;
    const k = e.key;
    let done = true;
    if (k === "/") openPanel("panel-search", $("#r-search"));
    else if (k === "g" || k === "G") { chrome(true); if ($("#pop-goto").hidden) $("#r-pg").click(); }
    else if (k === "t" || k === "T") cycleTone();
    else if (k === "2") { setPref("layout", wantSpread() ? "single" : "double"); applyLayout(); paintAa(); }
    // [ is the sidebar everywhere in the shell; c (and [ on its own) is Contents
    else if (k === "[" && frameKind === "window" && shell?.sidebar) shell.sidebar();
    else if (k === "[" || k === "c" || k === "C") openPanel("panel-toc", $("#r-toc"));
    else if (k === "f" || k === "F") $("#m-full").hidden || $("#m-full").click();
    // a held key flips straight through; a press turns the page
    else if ((k === "ArrowLeft" || k === "ArrowRight") && html.classList.contains("flow-pages"))
      e.repeat ? (k === "ArrowLeft" ? app.pdfViewer.previousPage() : app.pdfViewer.nextPage()) : pageTurn(k === "ArrowLeft" ? -1 : 1);
    else done = false;
    if (done) { e.preventDefault(); e.stopPropagation(); }
  }, true);
}
function cycleTone() {
  const order = ["paper", "sepia", "night"], t = order[(order.indexOf(prefs().tone) + 1) % 3];
  setPref("tone", t); html.dataset.tone = t; paintAa();
}

/* ---------- Pages: turning the page ----------
   In Pages mode the page turns like paper. A sideways drag lifts the page's
   edge and the fold follows your finger; let go and the turn finishes, or
   the page lies back down. A tap on the outer quarter, the arrow keys, the
   side buttons and a trackpad swipe play the same turn.

   PDF.js is never animated. The turn is drawn by an overlay (.r-curl) from
   copies of pages that are already drawn: the page you're leaving, the page
   beneath it, and the back of the lifted leaf. PDF.js is told to change page
   only once a turn is committed, under the overlay, and the overlay leaves
   when the new page has drawn. Any turn can be cut short (by the next turn,
   a pinch, a jump, a resize, a hidden tab) by finishing it at once, so no
   input ever waits on an animation and there is no lock to get stuck.

   Touch is read from touch events, not pointer events: PDF.js's pinch
   handler (TouchManager) swallows every touch pointerdown at the window. */

// <turn-math>
// the part of a w×h sheet on one side of the fold x = fx + (y − h/2)·t,
// as polygon points: the spine side (left), or the side that lifts
function foldClip(w, h, fx, t, spineSide) {
  const side = (x, y) => (x - (fx + (y - h / 2) * t)) * (spineSide ? -1 : 1);
  const pts = [[0, 0], [w, 0], [w, h], [0, h]], out = [];
  for (let i = 0; i < 4; i++) {
    const a = pts[i], b = pts[(i + 1) % 4], sa = side(...a), sb = side(...b);
    if (sa >= 0) out.push(a);
    if ((sa >= 0) !== (sb >= 0)) {
      const k = sa / (sa - sb);
      out.push([a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k]);
    }
  }
  return out;
}
// the CSS matrix that mirrors a sheet across that fold: the lifted part
// folded over onto the spine side
function foldMirror(h, fx, t) {
  const th = Math.atan(t), a = -Math.cos(2 * th), b = Math.sin(2 * th), d = -a, cy = h / 2;
  return [a, b, b, d, fx - (a * fx + b * cy), cy - (b * fx + d * cy)];
}
// the pages PDF.js shows together with page n (spreadMode 0 none, 1 odd, 2 even)
function spreadOf(n, mode, total) {
  if (n < 1 || n > total) return [];
  if (!mode) return [n];
  const pair = n % 2 !== mode - 1 ? [n, n + 1] : [n - 1, n];
  return pair.filter(i => i >= 1 && i <= total);
}
// does a released drag finish the turn? q: how far it got (0–1);
// v: its speed toward finishing, px/ms (negative: flicked back)
function turnCommits(q, v) {
  if (v < -0.2) return false;
  return q > 0.33 || (v > 0.3 && q > 0.02);
}
// </turn-math>

const easeOut = k => 1 - (1 - k) ** 3;
const easeInOut = k => k < .5 ? 4 * k ** 3 : 1 - (-2 * k + 2) ** 3 / 2;

function wirePageTurns() {
  const vc = $("#viewerContainer"), viewer = $("#viewer");
  const reduced = matchMedia("(prefers-reduced-motion: reduce)");
  const pagesMode = () => html.classList.contains("flow-pages") && total > 0;
  const view = n => app.pdfViewer.getPageView(n - 1);
  const drawn = n => view(n)?.renderingState === 3;  // RenderingStates.FINISHED
  // how far a magnified page can pan sideways; a fitted page a few pixels
  // too wide for the screen (PDF.js's borders, an odd-sized cover) doesn't count
  const pannable = () => { const d = vc.scrollWidth - vc.clientWidth; return d > 32 ? d : 0; };

  /* -- copies of drawn pages, a few kept so a turn never waits on them -- */
  const shots = new Map(), pending = new Map();
  let shotScale = "";
  const MAXPX = coarse ? 1.6e6 : 4e6;  // a phone's canvas memory is small and its tab dies when it runs out
  const keepShot = (n, c) => {
    shots.delete(n); shots.set(n, c);
    while (shots.size > 6) {
      const [k, old] = shots.entries().next().value;
      shots.delete(k);
      if (!old.parentNode) old.width = old.height = 0;  // not on screen in a turn
    }
    return c;
  };
  const freshScale = () => {
    const key = app.pdfViewer.currentScale + ":" + app.pdfViewer.pagesRotation;
    if (key === shotScale) return;
    shotScale = key;
    shots.forEach(c => { if (!c.parentNode) c.width = c.height = 0; });
    shots.clear();
  };
  function shotOf(n) {
    freshScale();
    if (shots.has(n)) return keepShot(n, shots.get(n));
    const src = view(n)?.canvas;
    if (drawn(n) && src?.width) {
      // copy it: PDF.js recycles its canvases as pages come and go
      const k = Math.min(1, Math.sqrt(MAXPX / (src.width * src.height)));
      const c = document.createElement("canvas");
      c.width = Math.max(1, Math.round(src.width * k)); c.height = Math.max(1, Math.round(src.height * k));
      try { c.getContext("2d").drawImage(src, 0, 0, c.width, c.height); return keepShot(n, c); } catch (_) {}
    }
    return null;
  }
  function drawShot(n) {
    if (pending.has(n)) return pending.get(n);
    const key = shotScale;
    const job = (async () => {
      const pv = view(n);
      if (!pv) return null;
      const page = pv.pdfPage || await doc.getPage(n), vp = pv.viewport;
      const k = Math.min(devicePixelRatio || 1, 2, Math.sqrt(MAXPX / (vp.width * vp.height)));
      const c = document.createElement("canvas");
      c.width = Math.max(1, Math.round(vp.width * k)); c.height = Math.max(1, Math.round(vp.height * k));
      await page.render({ canvasContext: c.getContext("2d"), viewport: page.getViewport({ scale: vp.scale * k, rotation: vp.rotation }) }).promise;
      return key === shotScale ? keepShot(n, c) : null;
    })().catch(() => null).finally(() => pending.delete(n));
    pending.set(n, job);
    return job;
  }
  // after a turn lands, have the pages either side ready for the next one
  let warmT;
  const warm = () => {
    clearTimeout(warmT);
    warmT = setTimeout(() => {
      if (!pagesMode() || turn) return;
      freshScale();
      const mode = app.pdfViewer.spreadMode > 0 ? app.pdfViewer.spreadMode : 0;
      const cur = spreadOf(app.page, mode, total);
      for (const n of [...spreadOf(cur.at(-1) + 1, mode, total), ...spreadOf(cur[0] - 1, mode, total)])
        if (view(n)?.renderingState === 0 && !shots.has(n)) drawShot(n);  // and PDF.js isn't drawing it either
    }, 400);
  };

  /* -- the overlay: a page (a shot, or blank paper until one arrives) -- */
  function pageEl(n, box, origin, opts = {}) {
    const el = document.createElement("div");
    el.className = "r-cpg" + (view(n)?.div.classList.contains("gsa-pic") ? " pic" : "");
    el.style.setProperty("left", box.x - origin.x + "px");
    el.style.setProperty("top", box.y - origin.y + "px");
    el.style.setProperty("width", box.w + "px");
    el.style.setProperty("height", box.h + "px");
    if (opts.mirror) el.style.setProperty("transform", "scaleX(-1)");
    // the tone's filter goes on the paper, not on the page's shadow
    const paper = document.createElement("div");
    paper.className = "r-cin";
    el.append(paper);
    const put = shot => {
      if (!shot || paper.querySelector("canvas")) return;
      let c = shot;
      if (shot.parentNode) {  // already used elsewhere in this turn
        c = document.createElement("canvas");
        c.width = shot.width; c.height = shot.height;
        c.getContext("2d").drawImage(shot, 0, 0);
      }
      paper.prepend(c);
      if (opts.wash) paper.querySelector(".r-cwash")?.style.setProperty("background", paperOf(shot));
    };
    if (opts.wash) { const w = document.createElement("i"); w.className = "r-cwash"; paper.append(w); }
    const shot = shotOf(n);
    if (shot) put(shot); else drawShot(n).then(put);
    return el;
  }
  // a scan's paper colour, from its brightest corner, for the leaf's back
  function paperOf(shot) {
    try {
      const c = document.createElement("canvas"), x = c.getContext("2d", { willReadFrequently: true });
      c.width = c.height = 1;
      let best = [255, 255, 255], bl = -1;
      for (const [u, v] of [[0, 0], [.9, 0], [0, .9], [.9, .9]]) {
        x.drawImage(shot, u * shot.width, v * shot.height, shot.width * .1, shot.height * .1, 0, 0, 1, 1);
        const [r, g, b] = x.getImageData(0, 0, 1, 1).data, l = r + g + b;
        if (l > bl) { bl = l; best = [r, g, b]; }
      }
      return `rgb(${best.join(",")})`;   // lint-ok: the scan's own paper, measured
    } catch (_) { return "white"; }
  }
  // where a page sits on screen, without PDF.js's 9px transparent border
  function boxOf(n) {
    const d = view(n)?.div;
    if (!d?.isConnected) return null;
    const r = d.getBoundingClientRect(), cs = getComputedStyle(d);
    const l = parseFloat(cs.borderLeftWidth) || 0, t = parseFloat(cs.borderTopWidth) || 0;
    const w = r.width - l - (parseFloat(cs.borderRightWidth) || 0), h = r.height - t - (parseFloat(cs.borderBottomWidth) || 0);
    return w > 0 && h > 0 ? { x: r.left + l, y: r.top + t, w, h } : null;
  }
  const bounds = boxes => {
    const x = Math.min(...boxes.map(b => b.x)), y = Math.min(...boxes.map(b => b.y));
    return { x, y, w: Math.max(...boxes.map(b => b.x + b.w)) - x, h: Math.max(...boxes.map(b => b.y + b.h)) - y };
  };
  // the pages PDF.js will show next, laid out as it will: side by side,
  // centred where the current ones are
  function layOut(pages, around, gap) {
    const sizes = pages.map(n => ({ n, w: view(n).viewport.width, h: view(n).viewport.height }));
    const width = sizes.reduce((s, p) => s + p.w, 0) + gap * (sizes.length - 1);
    const cx = around.x + around.w / 2, cy = around.y + around.h / 2;
    let x = cx - width / 2;
    return sizes.map(p => { const b = { x, y: cy - p.h / 2, w: p.w, h: p.h }; x += p.w + gap; return b; });
  }

  /* A scene is one turn, drawn at any point p from 0 (the leaf lies flat on
     the right) to 1 (it has turned over onto the left). A turn forward goes
     0 → 1, a turn back 1 → 0. Two shapes:
     - leaf: a two-page spread. The right-hand page lifts and turns about the
       spine; its back is the next spread's left page.
     - sheet: anything else. The whole page (or uneven spread) turns about its
       left edge, its back plain paper with the print showing through. */
  function buildScene(dir) {
    const v = app.pdfViewer, mode = v.spreadMode > 0 ? v.spreadMode : 0;
    const cur = spreadOf(app.page, mode, total);
    const tgt = dir > 0 ? spreadOf(cur.at(-1) + 1, mode, total) : spreadOf(cur[0] - 1, mode, total);
    if (!cur.length || !tgt.length || tgt.some(n => !view(n)?.viewport)) return null;
    const curBoxes = cur.map(boxOf);
    if (curBoxes.some(b => !b)) return null;
    const area = vc.getBoundingClientRect();
    const gap = curBoxes.length === 2 ? curBoxes[1].x - curBoxes[0].x - curBoxes[0].w : 18;
    const tgtBoxes = layOut(tgt, bounds(curBoxes), gap);
    const all = [...curBoxes, ...tgtBoxes];
    const leaf = cur.length === 2 && tgt.length === 2 &&
      all.every(b => Math.abs(b.w - all[0].w) < 2 && Math.abs(b.h - all[0].h) < 2);
    // forward: from = what you see now; backward: the same turn, played in reverse
    const [fromP, fromB, toP, toB] = dir > 0 ? [cur, curBoxes, tgt, tgtBoxes] : [tgt, tgtBoxes, cur, curBoxes];

    const root = document.createElement("div");
    root.className = "r-curl";
    root.setAttribute("aria-hidden", "true");
    for (const [k, val] of [["left", area.left], ["top", area.top], ["width", area.width], ["height", area.height]])
      root.style.setProperty(k, val + "px");
    const origin = { x: area.left, y: area.top };
    const base = document.createElement("div");
    base.className = "r-cbase";
    const front = document.createElement("div"), back = document.createElement("div");
    front.className = "r-cface"; back.className = "r-cface back";
    // the leaf's shadow falls on the pages beneath, not on the desk
    const castBox = document.createElement("div");
    castBox.className = "r-ccast";
    const cast = document.createElement("i"), shadeF = document.createElement("i"), shadeB = document.createElement("i");
    cast.className = "r-cshade cast"; shadeF.className = "r-cshade front"; shadeB.className = "r-cshade back";

    let sheet;  // the box that turns, on screen
    if (leaf) {
      sheet = fromB[1];
      base.append(pageEl(fromP[0], fromB[0], origin), pageEl(toP[1], toB[1], origin));
      front.append(pageEl(fromP[1], sheet, sheet));
      back.append(pageEl(toP[0], sheet, sheet, { mirror: true }));
    } else {
      sheet = bounds(fromB);
      toP.forEach((n, i) => base.append(pageEl(n, toB[i], origin)));
      fromP.forEach((n, i) => {
        front.append(pageEl(n, fromB[i], sheet));
        back.append(pageEl(n, fromB[i], sheet, { wash: true }));
      });
    }
    for (const face of [front, back]) {
      face.style.setProperty("left", sheet.x - origin.x + "px");
      face.style.setProperty("top", sheet.y - origin.y + "px");
      face.style.setProperty("width", sheet.w + "px");
      face.style.setProperty("height", sheet.h + "px");
    }
    front.append(shadeF); back.append(shadeB);
    const under = bounds(leaf ? [fromB[0], toB[1]] : toB);
    for (const [k, val] of [["left", under.x - origin.x], ["top", under.y - origin.y], ["width", under.w], ["height", under.h]])
      castBox.style.setProperty(k, val + "px");
    castBox.append(cast);
    root.append(base, castBox, front, back);
    document.body.append(root);

    const W = sheet.w, H = sheet.h;
    const poly = pts => "polygon(" + pts.map(([x, y]) => `${x.toFixed(1)}px ${y.toFixed(1)}px`).join(",") + ")";
    const strip = (el, x, y, t, width, alpha, leftward) => {
      el.style.setProperty("transform", `translate(${x.toFixed(1)}px,${y.toFixed(1)}px) rotate(${-Math.atan(t)}rad)` +
        `${leftward ? " scaleX(-1)" : ""} translateY(-50%) scaleX(${(Math.max(0, width) / 100).toFixed(3)})`);
      el.style.setProperty("opacity", Math.max(0, Math.min(1, alpha)).toFixed(3));
    };
    return {
      root, leaf, width: W,
      paint(p, tilt) {
        const fx = W * (1 - p), lift = Math.sin(Math.PI * p);
        const t = tilt * Math.sqrt(Math.max(0, lift));
        front.style.setProperty("clip-path", poly(foldClip(W, H, fx, t, true)));
        back.style.setProperty("clip-path", poly(foldClip(W, H, fx, t, false)));
        back.style.setProperty("transform", `matrix(${foldMirror(H, fx, t).map(n => n.toFixed(4)).join(",")})`);
        // a lone sheet turned past three-quarters is lying off its left
        // edge, over the desk: let it go rather than leave it lying there
        back.style.setProperty("opacity", leaf ? "1" : Math.min(1, (1 - p) / .2).toFixed(3));
        strip(shadeF, fx, H / 2, t, Math.min(W * .12, 56), Math.min(1, p * 10) * .9, true);
        strip(shadeB, fx, H / 2, t, W - fx, Math.min(1, p * 10) * (leaf ? 1 : Math.min(1, (1 - p) / .2)), false);
        strip(cast, sheet.x - under.x + fx, sheet.y - under.y + H / 2, t, 16 + W * .3 * lift, Math.sqrt(lift), false);
      },
      // the copies go back to the pool, free for the next turn
      remove() { root.remove(); root.querySelectorAll("canvas").forEach(c => c.remove()); },
    };
  }

  /* -- one turn at a time --
     turn = { scene, dir, q (0–1 toward done), tilt, state: drag | settle | land } */
  let turn = null, bounce = null;
  const pOf = tr => tr.dir > 0 ? tr.q : 1 - tr.q;
  const show = (tr, q) => { tr.q = Math.max(0, Math.min(1, q)); tr.scene?.paint(pOf(tr), tr.tilt); };
  function begin(dir, tilt) {
    finish();
    if (!pagesMode()) return null;
    const mode = app.pdfViewer.spreadMode > 0 ? app.pdfViewer.spreadMode : 0, cur = spreadOf(app.page, mode, total);
    const target = dir > 0 ? spreadOf(cur.at(-1) + 1, mode, total) : spreadOf(cur[0] - 1, mode, total);
    if (!target.length) return null;
    // reduced motion: the same gestures, no picture
    const scene = reduced.matches ? null : buildScene(dir);
    if (!scene && !reduced.matches) return null;
    turn = { scene, dir, target, q: 0, tilt, state: "drag", raf: 0, timer: 0 };
    show(turn, 0);
    return turn;
  }
  // PDF.js changes page under the overlay, the moment a turn is committed
  function commitPage(tr) {
    if (tr.committed) return;
    tr.committed = true;
    go(tr.target[0]);
  }
  function settle(tr, commit, ms, ease) {
    tr.state = "settle";
    tr.commit = commit;
    if (commit) commitPage(tr);
    cancelAnimationFrame(tr.raf); clearTimeout(tr.timer);
    const from = tr.q, to = commit ? 1 : 0, t0 = performance.now();
    if (!tr.scene || ms <= 0 || from === to) return settled(tr);
    const step = now => {
      if (turn !== tr) return;
      const k = Math.min(1, (now - t0) / ms);
      show(tr, from + (to - from) * ease(k));
      if (k < 1) tr.raf = requestAnimationFrame(step); else settled(tr);
    };
    tr.raf = requestAnimationFrame(step);
    // frames can stop (a hidden tab, a busy phone); the turn still ends
    tr.timer = setTimeout(() => settled(tr), ms + 250);
  }
  function settled(tr) {
    if (turn !== tr || tr.state === "land") return;
    cancelAnimationFrame(tr.raf); clearTimeout(tr.timer);
    show(tr, tr.commit ? 1 : 0);
    if (!tr.commit || !tr.scene) return end(tr);
    // hold the finished picture until PDF.js has drawn the page beneath it
    tr.state = "land";
    const t0 = performance.now();
    const check = () => {
      if (turn !== tr) return;
      const pages = spreadOf(app.page, app.pdfViewer.spreadMode > 0 ? app.pdfViewer.spreadMode : 0, total);
      if (pages.every(drawn) || performance.now() - t0 > 1500) {
        tr.scene.root.classList.add("out");
        tr.timer = setTimeout(() => end(tr), 130);
      } else tr.timer = setTimeout(check, 40);
    };
    check();
  }
  function end(tr) {
    if (turn !== tr) return;
    cancelAnimationFrame(tr.raf); clearTimeout(tr.timer);
    tr.scene?.remove();
    turn = null;
    warm();
  }
  // bring whatever is on screen to rest now: a turn being dragged lies back
  // down, one that was let go completes
  function finish() {
    if (bounce) { clearTimeout(bounce.timer); viewer.classList.remove("r-spring"); viewer.style.removeProperty("transform"); bounce = null; }
    const tr = turn;
    if (!tr) return;
    if (tr.state === "drag") tr.commit = false;
    if (tr.commit) commitPage(tr);
    turn = null;
    cancelAnimationFrame(tr.raf); clearTimeout(tr.timer);
    tr.scene?.remove();
  }
  // a turn played for you: taps, keys, buttons, trackpad swipes
  function turnPage(dir) {
    if (!pagesMode()) { dir > 0 ? app.pdfViewer.nextPage() : app.pdfViewer.previousPage(); return; }
    const tr = begin(dir, -.08 * dir);
    if (tr) settle(tr, true, tr.leaf ? 620 : 560, easeInOut);
  }
  // at the first or last page, the page gives a little and springs back
  function stretch(dx) {
    if (!bounce) bounce = { timer: 0 };
    clearTimeout(bounce.timer);
    viewer.classList.remove("r-spring");
    const d = Math.sign(dx) * Math.min(56, Math.abs(dx) * .22);
    viewer.style.setProperty("transform", `translateX(${d.toFixed(1)}px)`);
  }
  function unstretch() {
    if (!bounce) return;
    const b = bounce;
    viewer.classList.add("r-spring");
    viewer.style.removeProperty("transform");
    b.timer = setTimeout(() => { if (bounce === b) { viewer.classList.remove("r-spring"); bounce = null; } }, 340);
  }

  /* -- a drag, from a finger or a mouse -- */
  let g = null;  // { id, x, y, t, mode: null | "turn" | "stretch" | "native", track: [[x, t]] }
  function press(id, x, y) {
    // a finger down catches a turn in flight: let it finish where it was headed
    if (turn && turn.state === "settle") settled(turn);
    g = { id, x, y, t: performance.now(), mode: null, dir: 0, track: [[x, performance.now()]] };
  }
  // returns true when the move is ours (the caller then stops native scrolling)
  function drag(x, y) {
    if (!g || g.mode === "native") return false;
    const dx = x - g.x, dy = y - g.y, now = performance.now();
    g.track.push([x, now]);
    while (g.track.length > 2 && now - g.track[0][1] > 100) g.track.shift();
    if (!g.mode) {
      if (Math.abs(dx) < 8 && Math.abs(dy) < 8) return false;
      if (!pagesMode() || Math.abs(dx) < Math.abs(dy) * 1.2 || String(getSelection() || "")) { g.mode = "native"; return false; }
      // a magnified page pans first; only from its edge does a drag turn
      const pan = pannable();
      if (pan && (dx < 0 ? vc.scrollLeft < pan - 1 : vc.scrollLeft > 1)) { g.mode = "native"; return false; }
      g.mode = "turn";
      getSelection()?.removeAllRanges();
    }
    const dir = dx < 0 ? 1 : -1;
    if (g.mode === "turn" && dir !== g.dir) {
      // first move, or the drag crossed back over where it began
      if (Math.abs(dx) < 4 && g.dir) return true;
      g.dir = dir;
      const r = vc.getBoundingClientRect(), tilt = dir * Math.max(-.12, Math.min(.12, (r.top + r.height / 2 - y) / r.height * .3));
      if (!begin(dir, tilt)) { finish(); g.mode = "stretch"; }
    }
    if (g.mode === "stretch") {
      // the other way may still turn
      const tr = (dx < 0 ? 1 : -1) !== g.dir ? begin(dx < 0 ? 1 : -1, 0) : null;
      if (tr) { g.mode = "turn"; g.dir = tr.dir; }
      else { stretch(dx); return true; }
    }
    if (turn && turn.state === "drag") {
      const r = vc.getBoundingClientRect();
      turn.tilt = turn.dir * Math.max(-.12, Math.min(.12, (r.top + r.height / 2 - y) / r.height * .3));
      show(turn, Math.abs(dx) / ((turn.scene?.width || r.width) * .9));
    }
    return true;
  }
  function lift(x, cancelled) {
    const s = g; g = null;
    if (!s) return;
    if (s.mode === "stretch") { unstretch(); return; }
    const tr = turn;
    if (s.mode !== "turn" || !tr || tr.state !== "drag") return;
    const [x0, t0] = s.track[0], dt = Math.max(1, performance.now() - t0);
    const v = (x - x0) / dt * (tr.dir > 0 ? -1 : 1);
    const commit = !cancelled && turnCommits(tr.q, v);
    const left = commit ? 1 - tr.q : tr.q, w = tr.scene?.width || vc.clientWidth;
    // keep the flick's speed (an ease-out starts at three times its average),
    // never slower than a calm settle
    const ms = Math.max(140, Math.min(140 + left * 380, v > .2 ? 3 * left * w * .9 / v : Infinity));
    settle(tr, commit, ms, easeOut);
  }
  function abandon() {
    const s = g; g = null;
    if (s?.mode === "stretch") unstretch();
    if (turn?.state === "drag") settle(turn, false, 200, easeOut);
  }
  // a tap: the outer quarters turn, the middle brings the bars and back
  function tap(x) {
    const r = vc.getBoundingClientRect(), k = (x - r.left) / r.width;
    if (pagesMode() && k < .25) return turnPage(-1);
    if (pagesMode() && k > .75) return turnPage(1);
    chrome(html.classList.contains("chrome-off"));
  }
  const ignore = t => !vc.contains(t) || t.closest?.("a, button, input, textarea, select, .annotationLayer section, .r-pop, .r-panel");

  // fingers
  window.addEventListener("touchstart", e => {
    if (e.touches.length > 1) { abandon(); return; }  // a pinch belongs to PDF.js
    g = null;
    if (ignore(e.target) || String(getSelection() || "")) return;
    const t = e.touches[0];
    press(t.identifier, t.clientX, t.clientY);
  }, { capture: true, passive: true });
  window.addEventListener("touchmove", e => {
    if (!g || g.id === "mouse") return;
    if (e.touches.length > 1) { abandon(); return; }
    const t = [...e.touches].find(t => t.identifier === g.id);
    if (!t) { abandon(); return; }
    if (drag(t.clientX, t.clientY) && e.cancelable) e.preventDefault();
  }, { capture: true, passive: false });
  window.addEventListener("touchend", e => {
    if (!g || g.id === "mouse") return;
    const t = [...e.changedTouches].find(t => t.identifier === g.id);
    if (!t) return;
    if (!g.mode && performance.now() - g.t < 350 && !String(getSelection() || "")) {
      const x = g.x; g = null;
      // the tap's own click would land on whatever the turn put there
      e.cancelable && e.preventDefault();
      tap(x);
      return;
    }
    lift(t.clientX, false);
  }, { capture: true, passive: false });
  window.addEventListener("touchcancel", () => { if (g && g.id !== "mouse") abandon(); }, { capture: true, passive: true });

  // the mouse: drags from the outer quarters, so the middle stays free for selecting text
  let dragged = false;
  vc.addEventListener("pointerdown", e => {
    if (e.pointerType !== "mouse" || e.button !== 0 || !pagesMode() || ignore(e.target)) return;
    const r = vc.getBoundingClientRect(), k = (e.clientX - r.left) / r.width;
    if (k > .25 && k < .75) return;
    e.preventDefault();
    press("mouse", e.clientX, e.clientY);
    g.pointer = e.pointerId;
    dragged = false;
  });
  vc.addEventListener("pointermove", e => {
    if (g?.id !== "mouse" || e.pointerId !== g.pointer) return;
    if (drag(e.clientX, e.clientY) && !dragged) {
      dragged = true;
      try { vc.setPointerCapture(e.pointerId); } catch (_) {}
    }
  });
  const mouseUp = e => {
    if (g?.id !== "mouse" || e.pointerId !== g.pointer) return;
    e.type === "pointercancel" ? abandon() : lift(e.clientX, false);
  };
  window.addEventListener("pointerup", mouseUp, true);
  window.addEventListener("pointercancel", mouseUp, true);
  vc.addEventListener("click", e => { if (dragged) { dragged = false; e.preventDefault(); e.stopPropagation(); } }, true);

  // a trackpad's sideways swipe: one turn per swipe, its momentum included
  let wheelSum = 0, wheelHeld = false, wheelT;
  vc.addEventListener("wheel", e => {
    if (!pagesMode() || e.ctrlKey || Math.abs(e.deltaX) <= Math.abs(e.deltaY)) return;
    const pan = pannable();
    if (pan && (e.deltaX > 0 ? vc.scrollLeft < pan - 1 : vc.scrollLeft > 1)) return;
    e.preventDefault();
    clearTimeout(wheelT);
    wheelT = setTimeout(() => { wheelHeld = false; wheelSum = 0; }, 200);
    if (wheelHeld) return;
    wheelSum += e.deltaX;
    if (Math.abs(wheelSum) > 40) { wheelHeld = true; turnPage(wheelSum > 0 ? 1 : -1); }
  }, { passive: false });

  // anything that moves the page under a turn ends the turn first
  const stop = () => { g = null; finish(); };
  window.addEventListener("blur", stop);
  window.addEventListener("pagehide", stop);
  window.addEventListener("resize", stop);
  document.addEventListener("visibilitychange", () => { if (document.hidden) stop(); });
  // a magnified page can pan sideways natively; an unmagnified one leaves
  // sideways drags to us (gsa.css sets touch-action from .r-pan)
  // Scroll mode's straight line (Noah, 2026-10-31). A fitted page, or one a
  // few pixels too wide, has no sideways travel at all; a zoomed page pans
  // freely with one finger, so it can be aligned to the margins; then Hold
  // (the foot's lock, a reader preference) freezes it where it is, at any
  // zoom, until it's let go.
  //
  // Locked, the scroller is overflow-x: hidden (.r-lock) and its own
  // sideways offset is 0; where the page sits sideways is a translate on the
  // pages (`shift`, as --r-shift). It has to be: iOS backs the scroller with
  // a native scroll view that clamps to 0 on the next scroll when the box
  // can't scroll sideways, whatever scrollLeft says, so a held page kept as
  // scrollLeft jumped to its left edge on the first stroke (measured on an
  // iPhone; touch-action: pan-y is ignored there, and no script that guesses
  // a stroke's direction is used). The pages move, not #viewer: a transform
  // there makes it the pages' offsetParent, and PDF.js's scrollIntoView then
  // scrolls #viewer instead of the scroller (zooms and jumps went astray).
  // PDF.js still sees the true position — vc.scrollLeft reads shift — so its
  // sharp-detail canvas and its zoom anchoring are for the part on screen.
  // Its writes are kept only when they come from a zoom (a pinch keeps the
  // point under the fingers still); a jump to a page or a search hit leaves a
  // held page where the reader put it. The lock itself never changes under a
  // finger: it's applied when they lift.
  const native = Object.getOwnPropertyDescriptor(Element.prototype, "scrollLeft");
  let locked = false, shift = 0, asked = null;
  Object.defineProperty(vc, "scrollLeft", {
    configurable: true,
    get() { return locked ? asked ?? shift : native.get.call(vc); },
    set(x) {
      if (!locked) return native.set.call(vc, x);
      asked = +x || 0;  // claimed by scalechanging (below), or dropped
      queueMicrotask(() => { asked = null; });
    },
  });
  // the sideways travel the pages have (offsets ignore the translate)
  const travel = () => {
    let right = 0;
    for (let n = 1; n <= total; n++) { const d = view(n)?.div; if (d) right = Math.max(right, d.offsetLeft + d.offsetWidth); }
    return Math.max(0, right - vc.clientWidth);
  };
  const fitted = () => travel() <= 32;
  // put the page x pixels to the left; a page a few pixels too wide sits
  // centred, unless the position is to be kept as it is (a zoom in progress)
  const place = (x, keep) => {
    const t = travel();
    shift = !keep && t <= 32 ? t / 2 : Math.max(0, Math.min(t, x));
    const px = Math.round(shift * devicePixelRatio) / devicePixelRatio;
    vc.style.setProperty("--r-shift", `${-px}px`);
    vc.classList.toggle("r-shift", px !== 0);  // at fit, the pages stay untransformed
  };
  const lockTo = on => {
    if (on === locked) return;
    if (on) {
      const x = native.get.call(vc);
      locked = true;
      place(x, true);
      vc.classList.add("r-lock");
      native.set.call(vc, 0);
    } else {
      const x = shift;
      locked = false; shift = 0;
      vc.style.removeProperty("--r-shift");
      vc.classList.remove("r-lock", "r-shift");
      native.set.call(vc, x);
    }
  };
  // nothing else may move a locked scroller sideways (a focused link, a text
  // selection's autoscroll); a finger can't, there's nowhere to go
  vc.addEventListener("scroll", () => { if (locked && native.get.call(vc)) native.set.call(vc, 0); }, { passive: true });
  const held = () => !!prefs().hold;
  const holdBtn = $("#r-hold");
  if (holdBtn) holdBtn.onclick = () => { setPref("hold", !held()); sync(); };
  let fingers = 0, syncLater = false;
  const sync = () => {
    if (fingers) { syncLater = true; return; }
    syncLater = false;
    vc.classList.toggle("r-pan", pagesMode() && pannable() > 0);
    const wider = !pagesMode() && total > 0 && !fitted();
    if (holdBtn) { holdBtn.hidden = !wider; holdBtn.setAttribute("aria-pressed", String(held())); holdBtn.innerHTML = ic(held() ? "lock" : "unlock"); }
    lockTo(!pagesMode() && total > 0 && (held() || fitted()));
    if (locked) place(shift);
  };
  for (const ev of ["touchstart", "touchend", "touchcancel"])
    window.addEventListener(ev, e => { fingers = e.touches.length; if (!fingers && syncLater) requestAnimationFrame(sync); }, { capture: true, passive: true });
  const observer = new ResizeObserver(sync);
  observer.observe(vc); observer.observe(viewer);
  app.initializedPromise.then(() => {
    const bus = app.eventBus;
    // a zoom: PDF.js has just placed the page (scrollLeft, above); keep it
    // there now, under the fingers, not a frame later
    bus.on("scalechanging", () => { if (locked) { place(asked ?? shift, true); asked = null; } });
    for (const name of ["scalechanging", "rotationchanging", "scrollmodechanged", "spreadmodechanged"])
      bus.on(name, () => { stop(); requestAnimationFrame(sync); });
    bus.on("pagechanging", e => {
      // a jump from elsewhere (contents, search, the scrubber) mid-turn
      if (turn && !(turn.committed && turn.target.includes(e.pageNumber))) finish();
      requestAnimationFrame(sync);
    });
    bus.on("pagerendered", e => { if (!turn && e.pageNumber === app.page) warm(); });
    bus.on("pagesinit", () => requestAnimationFrame(sync));
  });
  return turnPage;
}

/* ---------- night mode, and the pages it shouldn't invert ----------
   Night inverts a page's luminance and keeps its hues (gsa.css), which is
   right for text and wrong for photographs, maps and colour plates: they
   come out as negatives. So each page is looked at as it renders. Measured
   2026-10-07 on eight kinds of page (yellowed scans, white born-digital
   journals, photocopies, an atlas, a colour cover): text pages have under
   2% of their area darker than mid-tone once blurred to 40px and almost no
   saturated pixels; pictures have 6–94% dark area or 10%+ saturated. A
   picture page is dimmed in Night instead of inverted. */
const probe = document.createElement("canvas");
// a true area average: halve until near the size wanted (one big drawImage step only samples, so a
// dense text page kept its black glyph pixels and read as 6-10% dark, a picture)
function shrink(src, w) {
  let cur = src;
  while (cur.width / 2 >= w) {
    const n = document.createElement("canvas"), nx = n.getContext("2d");
    n.width = Math.max(1, Math.round(cur.width / 2)); n.height = Math.max(1, Math.round(cur.height / 2));
    nx.fillStyle = "white"; nx.fillRect(0, 0, n.width, n.height);
    nx.imageSmoothingQuality = "high"; nx.drawImage(cur, 0, 0, n.width, n.height);
    cur = n;
  }
  return cur;
}
function judgePage(view) {
  const c = view?.canvas || view?.div?.querySelector("canvas");
  if (!c || !c.width) return;
  try {
    const x = probe.getContext("2d", { willReadFrequently: true });
    // 1. nearest-neighbour sample: sharp ink and paper values, and colour
    // PDF.js 6 can leave part of a canvas unpainted while it draws a page in pieces; transparent
    // would read as black, so measure on paper
    const onPaper = (w, h, from = c) => { x.fillStyle = "white"; x.fillRect(0, 0, w, h); x.drawImage(from, 0, 0, w, h); };
    probe.width = 200; probe.height = Math.max(1, Math.round(200 * c.height / c.width));
    x.imageSmoothingEnabled = false;
    onPaper(probe.width, probe.height);
    const px = x.getImageData(0, 0, probe.width, probe.height).data, n = px.length / 4;
    const L = new Float32Array(n), C = new Float32Array(n);
    for (let i = 0, j = 0; i < px.length; i += 4, j++) {
      const r = px[i], g = px[i + 1], b = px[i + 2];
      L[j] = .299 * r + .587 * g + .114 * b;
      C[j] = Math.max(r, g, b) - Math.min(r, g, b);
    }
    const Ls = Float32Array.from(L).sort(), Cs = Float32Array.from(C).sort();
    const ink = Ls[Math.floor(n * .03)], paper = Ls[Math.floor(n * .95)];
    // a nearly blank page has almost no ink: don't let paper grain set the scale
    const span = Math.max(70, paper - ink), tint = Cs[n >> 1];  // tint: the paper's own colour (yellowed scans)
    let sat = 0;
    for (let j = 0; j < n; j++) if (C[j] > tint + 40 && L[j] > 30 && L[j] < paper - .15 * span) sat++;
    // 2. area average: text blurs to light grey, pictures stay dark
    const w = 40, h = Math.max(1, Math.round(40 * c.height / c.width));
    probe.width = w; probe.height = h;
    x.imageSmoothingEnabled = true; x.imageSmoothingQuality = "high";
    onPaper(w, h, shrink(c, w));
    const bx = x.getImageData(0, 0, w, h).data;
    let dark = 0;
    for (let i = 0; i < bx.length; i += 4) if (.299 * bx[i] + .587 * bx[i + 1] + .114 * bx[i + 2] < paper - .42 * span) dark++;
    view.div.classList.toggle("gsa-pic", dark / (w * h) > .06 || sat / n > .10);
  } catch (_) { /* a tainted or lost canvas: leave the page as it is */ }
}

/* ---------- contents: the book's own outline, else its pages ---------- */
async function loadOutline() {
  let ol = null;
  try { ol = await doc.getOutline(); } catch (_) {}
  outline = ol || [];
  paintTabs();
  if (!outline.length) return;
  const list = $("#r-toclist");
  const render = (items, depth) => items.map(it => {
    const i = flatToc.length;
    flatToc.push({ title: (it.title || "").trim(), dest: it.dest, url: it.url, page: null, depth });
    const kids = it.items && it.items.length ? `<ol>${render(it.items, depth + 1)}</ol>` : "";
    return `<li class="${kids ? "has" : ""}${depth === 0 && kids ? " open" : ""}">` +
      `${kids ? `<button class="r-tw" aria-label="Show its sections">${ic("forward", "sm")}</button>` : ""}` +
      `<button class="r-ti" data-i="${i}"><span>${esc((it.title || "").trim())}</span><i></i></button>${kids}</li>`;
  }).join("");
  list.innerHTML = render(outline, 0);
  list.querySelectorAll(".r-tw").forEach(b => b.onclick = () => b.parentElement.classList.toggle("open"));
  list.querySelectorAll(".r-ti").forEach(b => b.onclick = () => {
    const it = flatToc[+b.dataset.i];
    quiet();
    if (it.page) want = it.page;
    if (it.dest) app.pdfLinkService.goToDestination(it.dest);
    else if (it.url) window.open(it.url, "_blank", "noopener");
    if (narrow()) closeAll();
  });
  // resolve every entry's page, so the footer can name the section you're in.
  // A few at a time: each lookup can be a range request into a different part
  // of the file, and a book with an entry per page (the Big Liddell, 2,438)
  // sent them all at once, so Chrome refused them (ERR_INSUFFICIENT_RESOURCES)
  // along with the pages you were reading, which stayed blank (2026-11-09).
  let next = 0;
  const resolve = async () => {
    while (next < flatToc.length) {
      const i = next++, it = flatToc[i];
      try {
        let d = it.dest;
        if (typeof d === "string") d = await doc.getDestination(d);
        if (!Array.isArray(d)) continue;
        const ref = d[0];
        it.page = typeof ref === "number" ? ref + 1 : (await doc.getPageIndex(ref)) + 1;
        const b = list.querySelector(`.r-ti[data-i="${i}"] i`);
        if (b) b.textContent = labels && labels[it.page - 1] ? labels[it.page - 1] : it.page;
      } catch (_) {}
    }
  };
  await Promise.all([resolve(), resolve(), resolve(), resolve()]);
  onPage(app.page);
}
function sectionAt(n) {
  let best = null;
  for (const it of flatToc) if (it.page && it.page <= n && (!best || it.page >= best.page)) best = it;
  return best;
}
function markToc(n) {
  const cur = sectionAt(n);
  $$(".r-ti.on").forEach(b => b.classList.remove("on"));
  if (!cur) return;
  const b = $(`.r-ti[data-i="${flatToc.indexOf(cur)}"]`);
  if (b) {
    b.classList.add("on");
    for (let li = b.parentElement.parentElement.closest("li"); li; li = li.parentElement.closest("li")) li.classList.add("open");
  }
}
function showTab(tab) {
  $$("[data-tab]").forEach(b => b.setAttribute("aria-selected", String(b.dataset.tab === tab)));
  $("#r-toclist").hidden = tab !== "toc";
  $("#r-thumbs").hidden = tab !== "pages";
  $("#r-marks").hidden = tab !== "marks";
  if (tab === "pages") buildThumbs();
  if (tab === "marks") return paintMarks();
  const on = tab === "toc" ? $(".r-ti.on") : $(`.r-th[data-p="${app.page}"]`);
  on?.scrollIntoView({ block: "center" });
}
// tabs only when there's more than the pages to show: no outline and no
// bookmarks leaves the panel as just its pages, titled
function paintTabs() {
  const n = marks().length;
  $("#tab-toc").hidden = !outline.length;
  $("#tab-marks").hidden = !n;
  $("#toc-tabs").hidden = !outline.length && !n;
  $("#toc-title").hidden = !$("#toc-tabs").hidden;
}

/* ---------- bookmarks ----------
   More's "Bookmark this page" marks the page you're on (B does too); its
   ribbon turns the accent on a marked page. Marked pages stand as accent
   ticks over the scrubber and in the Contents panel's Bookmarks tab, with
   the section each falls in. Device-local, like positions: localStorage "gsa-marks",
   { path: [{ p, at }] }, the 200 most recently marked books. */
const marks = () => (ls.get("gsa-marks", {})[BOOK.path] || []).slice().sort((a, b) => a.p - b.p);
function setMarks(list) {
  const all = ls.get("gsa-marks", {});
  if (list.length) all[BOOK.path] = list; else delete all[BOOK.path];
  const keys = Object.keys(all);
  if (keys.length > 200) keys.sort((a, b) => Math.max(...all[a].map(m => m.at)) - Math.max(...all[b].map(m => m.at)))
    .slice(0, keys.length - 200).forEach(k => delete all[k]);
  ls.set("gsa-marks", all);
  paintMark(app.page); paintTabs();
  if (!$("#r-marks").hidden) list.length ? paintMarks() : showTab(outline.length ? "toc" : "pages");
}
// a two-page spread is marked when either page is
const markedIn = n => { const [a, b] = spreadAt(n); return marks().find(m => m.p === a || (b && m.p === b)); };
function toggleMark() {
  if (!total) return;
  const n = app.page, on = markedIn(n), list = marks();
  setMarks(on ? list.filter(m => m !== on && m.p !== on.p) : [...list, { p: n, at: Date.now() }]);
  chrome(true);
}
function paintMark(n) {
  const b = $("#m-mark"), on = !!markedIn(n);
  b.classList.toggle("on", on);
  b.setAttribute("aria-pressed", String(on));
  b.querySelector("span").textContent = on ? "Remove the bookmark" : "Bookmark this page";
  const ticks = $("#r-ticks");
  if (ticks.dataset.sig !== JSON.stringify(marks().map(m => m.p)) + total) {
    ticks.dataset.sig = JSON.stringify(marks().map(m => m.p)) + total;
    ticks.replaceChildren(...marks().map(m => {
      const i = document.createElement("i");
      i.style.setProperty("--x", ((m.p - 1) / Math.max(1, total - 1) * 100).toFixed(2) + "%");
      return i;
    }));
  }
}
function paintMarks() {
  $("#r-marks").innerHTML = marks().map(m => {
    const lab = printed(m.p), sec = sectionAt(m.p)?.title || "";
    return `<li><button class="r-mk" data-p="${m.p}"><b>${esc(lab ? "p. " + lab : `${m.p} / ${total}`)}</b>` +
      `${sec ? `<span>${esc(sec)}</span>` : ""}</button>` +
      `<button class="r-ib r-mkx" data-x="${m.p}" aria-label="Remove the bookmark">${ic("close")}</button></li>`;
  }).join("");
}
function wireMarks() {
  $("#m-mark").onclick = () => { toggleMark(); setTimeout(() => closeAll(), 450); };   // let them see it take
  $("#r-marks").onclick = e => {
    const x = e.target.closest("[data-x]"), b = e.target.closest("[data-p]");
    if (x) return setMarks(marks().filter(m => m.p !== +x.dataset.x));
    if (b) { go(+b.dataset.p); if (narrow()) closeAll(); }
  };
  addEventListener("keydown", e => {
    if ((e.key !== "b" && e.key !== "B") || e.metaKey || e.ctrlKey || e.altKey ||
        /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName || "")) return;
    e.preventDefault(); e.stopPropagation(); toggleMark();
  }, true);
  // another tab marking this book
  addEventListener("storage", e => { if (e.key === "gsa-marks" && total) { paintMark(app.page); paintTabs(); } });
}

// page thumbnails, drawn by the same engine as they scroll into view
let thumbsBuilt = false, thumbQ = [], thumbBusy = 0;
function buildThumbs() {
  if (thumbsBuilt || !total) return;
  thumbsBuilt = true;
  const box = $("#r-thumbs");
  // every cell takes the first page's shape, so the grid doesn't jump as they draw
  const v1 = app.pdfViewer.getPageView(0)?.viewport;
  if (v1) box.style.setProperty("--ar", `${v1.width} / ${v1.height}`);
  const cells = [];
  for (let n = 1; n <= total; n++)
    cells.push(`<button class="r-th" data-p="${n}"><span class="r-thc"></span><b>${esc(labels && labels[n - 1] ? labels[n - 1] : n)}</b></button>`);
  box.innerHTML = cells.join("");
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    io.unobserve(e.target);
    thumbQ.push(e.target); pumpThumbs();
  }), { root: $("#toc-body"), rootMargin: "300px" });
  box.querySelectorAll(".r-th").forEach(b => { io.observe(b); b.onclick = () => { go(+b.dataset.p); if (narrow()) closeAll(); }; });
  markThumb(app.page);
}
function pumpThumbs() {
  while (thumbBusy < 2 && thumbQ.length) {
    const cell = thumbQ.shift();
    thumbBusy++;
    drawThumb(cell).finally(() => { thumbBusy--; pumpThumbs(); });
  }
}
async function drawThumb(cell) {
  const page = await doc.getPage(+cell.dataset.p);
  const base = page.getViewport({ scale: 1 }), want = 132, dpr = Math.min(2, devicePixelRatio || 1);
  const vp = page.getViewport({ scale: want / base.width * dpr });
  const c = document.createElement("canvas");
  c.width = Math.round(vp.width); c.height = Math.round(vp.height);
  cell.querySelector(".r-thc").style.setProperty("aspect-ratio", `${base.width} / ${base.height}`);  // a fold-out keeps its shape
  await page.render({ canvasContext: c.getContext("2d"), viewport: vp }).promise;
  cell.querySelector(".r-thc").append(c);
  page.cleanup();
}
function markThumb(n) {
  if (!thumbsBuilt) return;
  $$(".r-th.on").forEach(b => b.classList.remove("on"));
  $(`.r-th[data-p="${n}"]`)?.classList.add("on");
}

/* ---------- search inside the book ----------
   /api/book-search reads the volume's converted text, so it finds words on
   scanned pages that carry no text layer. Opening a hit asks PDF.js to
   highlight the words too, where the PDF has a text layer to highlight. */
let searchSeq = 0;
async function runSearch(enter) {
  const q = $("#r-sq").value.trim(), seq = ++searchSeq, out = $("#r-hits"), sum = $("#r-ssum");
  if (!q) { out.innerHTML = ""; sum.textContent = ""; clearFind(); return; }
  if (!BOOK.text) return pdfFind(q, enter);
  sum.textContent = "";
  html.classList.add("searching");
  let d = null;
  try { d = await (await fetch("/api/book-search?path=" + encodeURIComponent(BOOK.path) + "&q=" + encodeURIComponent(q))).json(); }
  catch (_) {}
  if (seq !== searchSeq) return;
  html.classList.remove("searching");
  if (!d || !d.hits) return pdfFind(q, enter);
  const pages = d.hits.length;
  sum.textContent = d.total ? `${d.total.toLocaleString("en-US")} ${d.total === 1 ? "match" : "matches"} · ${pages}${d.matched === null ? "+" : ""} ${pages === 1 ? "page" : "pages"}` : "No matches";
  out.innerHTML = d.hits.map((h, i) => {
    const snip = esc(h.snippet).replace(/\u0001/g, "<mark>").replace(/\u0002/g, "</mark>");
    const lab = labels && labels[h.page - 1] && labels[h.page - 1] !== String(h.page) ? `p. ${labels[h.page - 1]}` : `p. ${h.page}`;
    return `<li><button class="r-hit" data-i="${i}"><span class="r-hp">${esc(lab)}</span><span class="r-hs">${snip}</span></button></li>`;
  }).join("");
  out.querySelectorAll(".r-hit").forEach(b => b.onclick = () => openHit(d.hits[+b.dataset.i], b));
  if (enter && d.hits.length) out.querySelector(".r-hit").click();
}
function openHit(h, btn) {
  $$(".r-hit.on").forEach(b => b.classList.remove("on"));
  btn.classList.add("on");
  go(h.page);
  quiet(3000);   // PDF.js scrolls to the words once their page has drawn, a second or more on: that isn't you reading on
  if (h.find) bus.dispatch("find", { source: window, type: "", query: h.find, caseSensitive: false,
    entireWord: false, highlightAll: false, findPrevious: false, matchDiacritics: false });
  if (narrow()) closeAll();
}
// no converted text for this volume: fall back to the engine's own find
function pdfFind(q, again) {
  bus.dispatch("find", { source: window, type: again ? "again" : "", query: q, caseSensitive: false,
    entireWord: false, highlightAll: true, findPrevious: false, matchDiacritics: false });
}
function findCount(m, state) {
  if (!m) return;
  if (finding) {
    $("#r-fn").textContent = m.total > 1 ? `${m.current} / ${m.total}` : "";
    $$(".r-fstep").forEach(b => b.hidden = m.total < 2);
    // nothing PDF.js can highlight (a scan without a text layer): no pill,
    // though the panel's own list still finds it
    if (state === 1) $("#r-find").hidden = true;
  }
  if (BOOK.text) return;
  $("#r-ssum").textContent = m.total ? `${m.current} / ${m.total}` : "No matches";
}

/* ---------- the find you're reading with ----------
   Whatever asked for it (a link, the search panel, Ask beside the book), a
   find shows as a pill under the bar: what's highlighted, how many, a step
   either way, and × to clear. Esc clears it too. */
let finding = null;  // the last find PDF.js was asked for, until it's cleared
// a passage is found once, as written; a search's terms are each found
// wherever they appear, as whole words unless one ended in *
function findIn(query, passage) {
  const terms = [].concat(query), prefix = terms.some(t => t.endsWith("*"));
  const q = terms.map(t => t.replace(/\*+$/, "")).filter(Boolean);
  if (!q.length) return;
  quiet(3000);   // the scroll to the first match comes late (openHit)
  bus.dispatch("find", { source: window, type: "", query: q.length > 1 ? q : q[0], caseSensitive: false,
    entireWord: !passage && !prefix, highlightAll: !passage, findPrevious: false, matchDiacritics: false });
}
function showFind(e) {
  if (!e.query || !e.query.length) return;
  finding = e;
  const terms = [].concat(e.query);
  $("#r-fq").textContent = terms.length > 1
    ? terms.map(t => /\s/.test(t) ? `“${t}”` : t).join(" · ")
    : `“${terms[0]}”`;
  if (e.type !== "again") { $("#r-fn").textContent = ""; $$(".r-fstep").forEach(b => b.hidden = true); }
  $("#r-find").hidden = false;
}
function stepFind(back) {
  if (finding) bus.dispatch("find", { ...finding, source: window, type: "again", findPrevious: back });
}
function clearFind() {
  if (!finding) return;
  finding = null;
  searchSeq++;  // a panel search still on its way lands nowhere
  bus.dispatch("findbarclose", { source: window });
  $("#r-find").hidden = true;
  $("#r-sq").value = ""; $("#r-hits").innerHTML = ""; $("#r-ssum").textContent = "";
  html.classList.remove("searching");
  // and out of the address, so a reload doesn't bring it back
  const h = new URLSearchParams(location.hash.slice(1));
  if (h.has("find") || h.has("hl")) { h.delete("find"); h.delete("hl"); setHash(h); }
  shell?.unfind?.();  // the Bookshelf's address bar, when we're its iframe
}

/* ---------- share a highlighted passage ----------
   Select a sentence and a chip offers a link that opens the book at that
   page with the passage found and highlighted, and whose preview card
   quotes it. */
const PASSAGE_WORDS = 14;
function passageFrom(raw) {
  const s = (raw || "").replace(/\s+/g, " ").trim();
  if (!s) return "";
  // a word broken across a line stays hyphenated in the text layer and won't
  // match, so stop at the first one rather than search for what isn't there
  const words = s.split(" ");
  const broken = words.findIndex(w => w.endsWith("-"));
  const kept = (broken > 0 ? words.slice(0, broken) : words).slice(0, PASSAGE_WORDS);
  const out = kept.join(" ");
  return out.length > 160 ? out.slice(0, 160).replace(/\s\S*$/, "") : out;
}
function wirePassage() {
  if (!BOOK.url) return;
  const chip = $("#r-pass");
  let passage = "", t;
  const place = () => {
    const sel = getSelection();
    passage = sel && !sel.isCollapsed && sel.anchorNode && $("#viewer").contains(sel.anchorNode) ? passageFrom(String(sel)) : "";
    if (!passage) { chip.hidden = true; return; }
    const r = sel.getRangeAt(0).getBoundingClientRect();
    if (!r.width && !r.height) { chip.hidden = true; return; }
    chip.textContent = "Copy link";
    chip.hidden = false;
    const w = chip.offsetWidth || 110;
    chip.style.setProperty("left", Math.min(Math.max(10, r.left + r.width / 2 - w / 2), innerWidth - w - 10) + "px");
    chip.style.setProperty("top", Math.min(r.bottom + 10, innerHeight - 56) + "px");
  };
  document.addEventListener("selectionchange", () => { clearTimeout(t); t = setTimeout(place, 140); });
  $("#viewerContainer").addEventListener("scroll", () => { chip.hidden = true; }, { passive: true });
  chip.onclick = async () => {
    const url = SITE + BOOK.url + "/" + app.page + "?find=" + encodeURIComponent(passage);
    try { await navigator.clipboard.writeText(url); chip.textContent = "Copied"; }
    catch (_) { chip.textContent = url; }
    setTimeout(() => { chip.hidden = true; }, 1600);
  };
}


/* ---------- startup: never leave a silent blank reader ---------- */
function openFailed(error) {
  clearTimeout(openTimer);
  console.error("GSA book startup failed:", error);
  loadProgress(100);
  instantGone();
  const status = $("#r-opening");
  status.hidden = false;
  $("#r-opening-message").textContent = "This book couldn’t open. Check your connection and try again.";
  $("#r-retry").hidden = false;
  chrome(true);
}
// The legacy (polyfilled) build: the modern one calls Map.getOrInsertComputed and
// Math.sumPrecise, which iOS lacks before 26.2. Its .mjs files cache for a day, so
// they carry the build in their address; bump this when /pdfjs/ is replaced.
const ENGINE_V = "6.1.200-legacy";
const engine = path => `/pdfjs/${path}?v=${ENGINE_V}`;
$("#r-retry").hidden = true;
$("#r-retry").addEventListener("click", e => { e.preventDefault(); location.reload(); });
const openTimer = setTimeout(() => {
  if (html.classList.contains("loaded") || (INSTANT && !INSTANT.gone && !INSTANT.box.hidden)) return;
  $("#r-opening-message").textContent = "This book is taking longer to open. You can wait or try again.";
  $("#r-retry").hidden = false;
}, 20000);
// The room's frame first (the bar, its title and Back, the foot): with the
// instant page it's on screen before the engine has downloaded, so the wait
// is a book opening in its room, not a picture you can't scroll.
build();
loadProgress(0);
WORKING.timer = setInterval(() => {
  if (WORKING.real >= 100) { clearInterval(WORKING.timer); return; }
  WORKING.fake += (92 - WORKING.fake) * 0.25;   // 64% at 1 s, 83% at 2 s, 89% at 3 s; the real open ends it
  loadProgress(WORKING.real);
}, 250);
(async () => {
  try {
    await import(engine("build/pdf.mjs"));   // absolute: this script lives in /web/reader/, the engine in /pdfjs/
    await import(engine("web/viewer.mjs"));
  } catch (error) { openFailed(error); }
})();
