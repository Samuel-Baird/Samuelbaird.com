// Site-wide background: drifting gray glyphs, brighter where the pointer passes,
// with a blue ripple on click. Renderer: glyphwind.js (MIT, Henry Fan; see LICENSE-glyphwind.txt).
(() => {
  if (typeof GlyphWind === 'undefined' || !document.body) return;
  const f = GlyphWind.defaults();
  const seed = crypto.getRandomValues(new Uint32Array(1))[0];
  f.seed = seed;
  f.look = GlyphWind.chooseLook(seed, []);
  f.field = GlyphWind.pattern(seed, f.look);
  f.glow.color.light = [0.1, 0.55, 1];

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
