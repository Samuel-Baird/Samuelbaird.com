/**
 * Shared pointer-hit-testing for the kit's client charts. Both
 * growth-chart.tsx and comparison-chart.tsx used to carry their own
 * near-identical `handleMouseMove` — this generalizes that logic over an
 * arbitrary list of x-anchored points.
 */

export type NearestOptions = {
  /** SVG viewBox width the points' `t`/`x` values are already projected into. */
  width: number;
};

/**
 * Nearest point to a pointer's x position, by 1D distance along the x axis.
 * Used for line charts, where every series shares one time axis and the
 * reader is scrubbing along it rather than aiming at a specific dot.
 */
export function nearestByX<T extends { x: number }>(
  points: T[],
  pointerX: number,
): T {
  let best = points[0];
  let bestDist = Infinity;
  for (const p of points) {
    const d = Math.abs(p.x - pointerX);
    if (d < bestDist) {
      bestDist = d;
      best = p;
    }
  }
  return best;
}

/** Pointer x position in the SVG's own viewBox units, from a mouse event on
 * an element sized by `viewBox="0 0 width height"` with
 * `preserveAspectRatio="none"`. */
export function svgPointerX(
  e: { clientX: number; currentTarget: { getBoundingClientRect(): DOMRect } },
  width: number,
): number {
  const rect = e.currentTarget.getBoundingClientRect();
  return ((e.clientX - rect.left) / rect.width) * width;
}

/**
 * Whichever 2D point the pointer is closest to, or null past the give-up
 * radius. Hoisted from eternal-increase-timeline/graph-shared.ts.
 *
 * Pointer input is handled by one transparent layer over the whole plot
 * rather than by a hit circle per dot. A comfortable 24px target is wider
 * than the gap between adjacent points on a dense axis, so per-dot targets
 * overlapped and whichever happened to paint last swallowed its neighbours'
 * clicks entirely. Nearest-wins keeps every dot reachable at any width and
 * still forgives an imprecise tap.
 */
export function nearestDot<T extends { pct: number; cy: number }>(
  dots: T[],
  box: DOMRect,
  clientX: number,
  clientY: number,
): T | null {
  const x = clientX - box.left;
  const y = clientY - box.top;
  let best: T | null = null;
  let bestDistance = Infinity;
  for (const dot of dots) {
    const dx = (dot.pct / 100) * box.width - x;
    const dy = dot.cy - y;
    const distance = dx * dx + dy * dy;
    if (distance < bestDistance) {
      bestDistance = distance;
      best = dot;
    }
  }
  return bestDistance <= 22 * 22 ? best : null;
}
