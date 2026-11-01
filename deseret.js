/* Deseret title reveal: vanilla port of DeseretTitle (latter-day-stats,
   src/components/deseret-title.tsx) and its glyph map (src/lib/deseret.ts).
   Keep the mapping, timings, and keyframes (tokens.css) in sync with that repo.
   Decorative only: the H1 is real Latin text in the HTML, and the reveal is
   skipped under reduced motion or if the Deseret face doesn't load. */
(function () {
  "use strict";
  var LOWER = {
    a: 0x10430, b: 0x1043A, c: 0x1043F, d: 0x1043C, e: 0x1042F, f: 0x10441,
    g: 0x10440, h: 0x10438, i: 0x1042E, j: 0x1043E, k: 0x1043F, l: 0x1044A,
    m: 0x1044B, n: 0x1044C, o: 0x1042C, p: 0x10439, q: 0x1043F, r: 0x10449,
    s: 0x10445, t: 0x1043B, u: 0x10433, v: 0x10442, w: 0x10436, x: 0x10446,
    y: 0x10437, z: 0x10446
  };
  var CASE_OFFSET = 0x28; // Deseret capitals sit 0x28 below lowercase
  var DURATION_MS = 300, MAX_STAGGER_MS = 50, TOTAL_STAGGER_BUDGET_MS = 850, FONT_TIMEOUT_MS = 300;
  var FONT = '1rem "Noto Sans Deseret"';

  function toDeseretChar(ch) {
    var cp = LOWER[ch.toLowerCase()];
    if (!cp) return ch;
    return String.fromCodePoint(ch === ch.toLowerCase() ? cp : cp - CASE_OFFSET);
  }

  function loadFont() {
    var link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "https://fonts.googleapis.com/css2?family=Noto+Sans+Deseret&display=swap";
    document.head.appendChild(link);
  }

  function reveal(h1, text) {
    var stagger = Math.min(MAX_STAGGER_MS, TOTAL_STAGGER_BUDGET_MS / Math.max(text.length, 1));
    // Same break points as the original: whitespace is its own token, words also break after - – — /.
    var parts = [];
    text.split(/(\s+)/).forEach(function (p) {
      if (p === "") return;
      if (/^\s+$/.test(p)) parts.push(p);
      else p.split(/(?<=[-–—/])/).forEach(function (q) { if (q) parts.push(q); });
    });
    var frag = document.createDocumentFragment(), seen = 0;
    parts.forEach(function (part) {
      if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); seen += part.length; return; }
      var chars = Array.from(part);
      var word = document.createElement("span");
      word.setAttribute("aria-hidden", "true");
      word.style.cssText = "position:relative;display:inline-block";
      var latin = document.createElement("span");
      latin.textContent = part;
      latin.style.animation = "deseret-in " + DURATION_MS + "ms ease-out " +
        Math.round((seen + chars.length - 1) * stagger) + "ms both";
      var overlay = document.createElement("span");
      overlay.style.cssText = "position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none;font-family:'Noto Sans Deseret',sans-serif";
      chars.forEach(function (c, i) {
        var g = document.createElement("span");
        g.textContent = toDeseretChar(c);
        g.style.animation = "deseret-out " + DURATION_MS + "ms ease-in " +
          Math.round((seen + i) * stagger) + "ms both";
        overlay.appendChild(g);
      });
      word.appendChild(latin);
      word.appendChild(overlay);
      frag.appendChild(word);
      seen += part.length;
    });
    h1.setAttribute("aria-label", text);
    h1.textContent = "";
    h1.appendChild(frag);
    setTimeout(function () {
      h1.removeAttribute("aria-label");
      h1.textContent = text;
    }, stagger * text.length + DURATION_MS + 60);
  }

  function init() {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var h1 = document.querySelector("h1");
    if (!h1 || !document.fonts) return;
    var text = h1.textContent.trim();
    if (!text) return;
    loadFont();
    Promise.race([
      document.fonts.load(FONT),
      new Promise(function (r) { setTimeout(r, FONT_TIMEOUT_MS); })
    ]).then(function () {
      if (document.fonts.check(FONT)) reveal(h1, text);
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
