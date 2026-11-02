// Deseret title reveal: each page <h1> briefly shows in the Deseret alphabet, then
// "translates" itself into Latin letter by letter. Port of the Latter-day Stats
// <DeseretTitle> (src/components/deseret-title.tsx); keep the two in step.
//
// Decorative only. The Latin text is always in the HTML, the mapping below is an
// approximate per-letter stand-in (Deseret is phonemic), never real transliteration,
// and nothing meaningful is encoded in it. Skipped under prefers-reduced-motion.
(() => {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches || !document.fonts) return;

  const LOWER = { a:0x10430, b:0x1043A, c:0x1043F, d:0x1043C, e:0x1042F, f:0x10441, g:0x10440, h:0x10438,
    i:0x1042E, j:0x1043E, k:0x1043F, l:0x1044A, m:0x1044B, n:0x1044C, o:0x1042C, p:0x10439, q:0x1043F,
    r:0x10449, s:0x10445, t:0x1043B, u:0x10433, v:0x10442, w:0x10436, x:0x10446, y:0x10437, z:0x10446 };
  const CASE_OFFSET = 0x28; // Deseret capitals sit 0x28 below lowercase
  const toDeseret = (ch) => {
    const lo = LOWER[ch.toLowerCase()];
    if (!lo) return ch;
    return String.fromCodePoint(ch === ch.toLowerCase() ? lo : lo - CASE_OFFSET);
  };

  const DURATION = 300, MAX_STAGGER = 50, STAGGER_BUDGET = 850, FONT_TIMEOUT = 1500;
  const FONT = '1rem "Noto Sans Deseret"';

  function animate(el) {
    const text = el.textContent.trim();
    if (!text || el.children.length) return;
    const sample = Array.from(text).map(toDeseret).join('');
    // The Deseret face is a lazy unicode-range subset, so ask for it with Deseret text.
    Promise.race([document.fonts.load(FONT, sample), new Promise((r) => setTimeout(r, FONT_TIMEOUT))])
      .then(() => {
        if (!document.fonts.check(FONT, sample)) return;
        const stagger = Math.min(MAX_STAGGER, STAGGER_BUDGET / Math.max(text.length, 1));
        // Same break points the browser would use, so wrapping doesn't jump at the end.
        const parts = text.split(/(\s+)/).filter(Boolean)
          .flatMap((p) => (/^\s+$/.test(p) ? [p] : p.split(/(?<=[-–—/])/).filter(Boolean)));
        const frag = document.createDocumentFragment();
        let seen = 0;
        for (const part of parts) {
          if (/^\s+$/.test(part)) { frag.append(part); seen += part.length; continue; }
          const chars = Array.from(part);
          const word = document.createElement('span');
          word.className = 'dz-word';
          word.setAttribute('aria-hidden', 'true');
          const latin = document.createElement('span');
          latin.textContent = part;
          latin.style.animation = `deseret-in ${DURATION}ms ease-out ${Math.round((seen + chars.length - 1) * stagger)}ms both`;
          const over = document.createElement('span');
          over.className = 'dz-over';
          chars.forEach((ch, i) => {
            const g = document.createElement('span');
            g.textContent = toDeseret(ch);
            g.style.animation = `deseret-out ${DURATION}ms ease-in ${Math.round((seen + i) * stagger)}ms both`;
            over.append(g);
          });
          word.append(latin, over);
          frag.append(word);
          seen += chars.length;
        }
        el.setAttribute('aria-label', text);
        el.textContent = '';
        el.append(frag);
        setTimeout(() => { el.textContent = text; el.removeAttribute('aria-label'); }, stagger * text.length + DURATION + 60);
      })
      .catch(() => { el.textContent = text; });
  }

  const run = () => document.querySelectorAll('h1').forEach(animate);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run); else run();
})();
