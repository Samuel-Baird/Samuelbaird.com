// One eased scroll position shared by every parallax layer, so the layers glide after the page
// instead of stepping with each scroll event. Time constant ~110 ms; instant with reduced motion.
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const subs = new Set();
let y = scrollY, raf = 0, last = 0;
function loop(now) {
  const target = scrollY, dt = Math.min(64, now - (last || now - 16));
  last = now;
  y += (target - y) * (reduced ? 1 : 1 - Math.exp(-dt / 110));
  if (Math.abs(target - y) < 0.05) y = target;
  for (const fn of subs) fn(y);
  if (y === target) { raf = 0; last = 0; } else raf = requestAnimationFrame(loop);
}
addEventListener('scroll', () => { if (!raf) raf = requestAnimationFrame(loop); }, { passive: true });
export function onSmoothScroll(fn) { subs.add(fn); fn(y); }
export const smoothY = () => y;
