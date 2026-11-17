// Drifting Deseret letters behind everything, as on samuelbaird.com: a faint field of glyphs carried on
// a slow wind, brightening where the pointer passes, with a brass ripple on click.
// Renderer: /bg/glyphwind.js (MIT, Henry Fan; see /bg/LICENSE-glyphwind.txt), loaded in <head>.
// Kept deliberately faint here so it reads as texture beneath the stars, not as text.
/* global GlyphWind */
async function start() {
  if (typeof GlyphWind === 'undefined' || !document.body) return;
  // The glyph atlas is drawn from the page's Deseret font, so wait for it (or the atlas is blank boxes).
  try { await document.fonts.load('16px "Noto Sans Deseret"', '𐐔'); } catch {}
  if (!document.fonts.check('16px "Noto Sans Deseret"', '𐐔')) return;

  const f = GlyphWind.defaults();
  const seed = crypto.getRandomValues(new Uint32Array(1))[0];
  f.seed = seed;
  f.look = GlyphWind.chooseLook(seed, []);
  f.field = GlyphWind.pattern(seed, f.look);
  f.strength.scale = 0.42;                 // canvas opacity ≈ .33 before the CSS dimming below
  f.surface.glyphCss = 11;                 // Deseret letters are wider than mono Latin
  f.grid.cellCss = 9;
  f.wind.energy = 0.7;                     // a slower drift than samuelbaird.com
  f.glow.color.light = [0.85, 0.66, 0.32]; // click ripple in muted brass, not blue

  const layer = document.createElement('div');
  layer.className = 'glyph-bg';
  layer.setAttribute('aria-hidden', 'true');
  document.getElementById('sky')?.after(layer);

  const renderer = GlyphWind.create({
    element: layer,
    settings: () => f,
    timing: () => ({ fadeIn: 3000, fadeOut: 500 }),
    onReady: () => { layer.style.opacity = '1'; },
    onError: () => layer.remove(),
  });
  renderer.setRunning(!matchMedia('(prefers-reduced-motion: reduce)').matches);
}
start();
