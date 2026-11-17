// Title reveal, after Urim's: each page <h1> first shows in the Deseret Alphabet, then settles into Latin
// letters word by word. Unlike Urim's decorative stand-in, the Deseret here is the real spelling, given in
// the h1's data-dsrt attribute (written by this server's own to_deseret). Skipped under reduced motion.
(() => {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches || !document.fonts) return;
  const DURATION = 420, STEP = 140, HOLD = 650, FONT_TIMEOUT = 1500;

  function animate(el) {
    const text = el.textContent.trim();
    const dsrt = (el.dataset.dsrt || '').trim();
    if (!text || !dsrt || el.children.length) return;
    const latinWords = text.split(/\s+/), dsrtWords = dsrt.split(/\s+/);
    if (latinWords.length !== dsrtWords.length) return;
    Promise.race([document.fonts.load('1rem "Noto Sans Deseret"', dsrt), new Promise((r) => setTimeout(r, FONT_TIMEOUT))]).then(() => {
      if (!document.fonts.check('1rem "Noto Sans Deseret"', dsrt)) return;
      const frag = document.createDocumentFragment();
      latinWords.forEach((w, i) => {
        if (i) frag.append(' ');
        const word = document.createElement('span');
        word.className = 'dz-word';
        word.setAttribute('aria-hidden', 'true');
        const latin = document.createElement('span');
        latin.textContent = w;
        latin.style.animation = `deseret-in ${DURATION}ms ease-out ${HOLD + i * STEP}ms both`;
        const over = document.createElement('span');
        over.className = 'dz-over';
        over.textContent = dsrtWords[i];
        over.style.animation = `deseret-out ${DURATION}ms ease-in ${HOLD + i * STEP}ms both`;
        word.append(latin, over);
        frag.append(word);
      });
      el.setAttribute('aria-label', text);
      el.textContent = '';
      el.append(frag);
      setTimeout(() => { el.textContent = text; el.removeAttribute('aria-label'); }, HOLD + latinWords.length * STEP + DURATION + 80);
    }).catch(() => { el.textContent = text; });
  }
  const run = () => document.querySelectorAll('h1[data-dsrt]').forEach(animate);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run); else run();
})();
