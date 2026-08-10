// Shared geometry for the filled beehive-and-bar-chart mark, consumed by
// both the favicon (src/app/icon.tsx, rendered via Satori/ImageResponse)
// and the nav-bar logo (src/components/beehive-stats-mark.tsx, rendered as
// a normal SVG). Kept in one place so the two can never drift apart.
//
// Five stacked pill-shaped bands, narrowest at top, widening toward the
// base, form the classic skep silhouette. Three ascending bars share the
// bottom band's baseline. The two tallest bars rise into BANDS[3] above,
// so every bar's x-range must stay inside that band's flat span — its
// rounded corners start at x=5.7 and x=18.3 — or a bar edge clips across
// the curve and reads as misaligned at small sizes.
export const BEEHIVE_BANDS = [
  { x: 9, y: 2.2, w: 6, h: 3, rx: 1.5 },
  { x: 7.4, y: 5.6, w: 9.2, h: 3, rx: 1.5 },
  { x: 5.8, y: 9, w: 12.4, h: 3, rx: 1.5 },
  { x: 4.2, y: 12.4, w: 15.6, h: 3, rx: 1.5 },
  { x: 2.6, y: 15.8, w: 18.8, h: 4.6, rx: 2 },
] as const;

export const BEEHIVE_BARS = [
  { x: 10.3, h: 3.4 },
  { x: 13.0, h: 5.4 },
  { x: 15.7, h: 7.6 },
] as const;

export const BEEHIVE_BAR_BASELINE = 20.4;
export const BEEHIVE_BAR_WIDTH = 2.1;
