import { ImageResponse } from "next/og";

// Code-generated favicon/app icon per Next's `icon.tsx` file convention.
// A filled beehive-and-bar-chart mark: the site's identity (a skep, per
// src/components/beehive-mark.tsx) plus its subject (stats), solid rather
// than line-drawn so it stays legible at 16-32px. Transparent background —
// browsers paint their own tab chrome behind it in both themes.
export const size = { width: 32, height: 32 };
export const contentType = "image/png";

const HONEY = "#d9a441"; // brand honey (dark-mode value — reads well on any tab background)
const INK = "#1a1a1a"; // brand foreground

// Five stacked pill-shaped bands, narrowest at top, widening toward the
// base — the classic skep silhouette, built from simple rounded rects
// rather than hand-fit bezier paths so it holds up at favicon scale.
const BANDS = [
  { x: 9, y: 2.2, w: 6, h: 3, rx: 1.5 },
  { x: 7.4, y: 5.6, w: 9.2, h: 3, rx: 1.5 },
  { x: 5.8, y: 9, w: 12.4, h: 3, rx: 1.5 },
  { x: 4.2, y: 12.4, w: 15.6, h: 3, rx: 1.5 },
  { x: 2.6, y: 15.8, w: 18.8, h: 4.6, rx: 2 },
];

// Three ascending bars sharing the bottom band's baseline, echoing the
// site's stats subject without competing with the hive shape. The tallest
// bar rises into the band above (BANDS[3]), so all three x-positions stay
// inside that band's flat span (its rounded corners start at x=5.7/18.3) —
// straying past that clips a bar's edge across the curve and reads as
// misaligned at favicon scale.
const BARS = [
  { x: 10.3, h: 3.4 },
  { x: 13.0, h: 5.4 },
  { x: 15.7, h: 7.6 },
];
const BAR_BASELINE = 20.4;
const BAR_WIDTH = 2.1;

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <svg width="30" height="30" viewBox="0 0 24 24">
          {BANDS.map((b, i) => (
            <rect
              key={i}
              x={b.x}
              y={b.y}
              width={b.w}
              height={b.h}
              rx={b.rx}
              fill={HONEY}
            />
          ))}
          {BARS.map((b, i) => (
            <rect
              key={i}
              x={b.x}
              y={BAR_BASELINE - b.h}
              width={BAR_WIDTH}
              height={b.h}
              rx={0.6}
              fill={INK}
            />
          ))}
        </svg>
      </div>
    ),
    { ...size },
  );
}
