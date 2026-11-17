// Site-wide background: drifting Deseret letters, brighter where the pointer passes, with a ripple on
// click. Same renderer as Urim (glyphwind.js, MIT, Henry Fan; see LICENSE-glyphwind.txt), tuned for parchment.
(() => {
  if (typeof GlyphWind === 'undefined' || !document.body) return;
  const dark = matchMedia('(prefers-color-scheme: dark)').matches;
  const f = GlyphWind.defaults();
  const seed = crypto.getRandomValues(new Uint32Array(1))[0];
  f.seed = seed;
  f.look = GlyphWind.chooseLook(seed, []);
  f.field = GlyphWind.pattern(seed, f.look);
  f.strength.base = { light: dark ? 0.26 : 0.2, dark: 0.26 };
  f.glow.color.light = dark ? [0.85, 0.66, 0.3] : [0.14, 0.23, 0.31]; // brass by night, Deseret blue by day

  const layer = document.createElement('div');
  layer.className = 'glyph-bg';
  layer.setAttribute('aria-hidden', 'true');
  document.body.prepend(layer);

  const renderer = GlyphWind.create({
    element: layer,
    settings: () => f,
    timing: () => ({ fadeIn: 2500, fadeOut: 500 }),
    onReady: () => { layer.style.opacity = '1'; },
    onError: (e) => console.warn('Background unavailable:', e.message),
  });
  renderer.setRunning(!matchMedia('(prefers-reduced-motion: reduce)').matches);
})();
