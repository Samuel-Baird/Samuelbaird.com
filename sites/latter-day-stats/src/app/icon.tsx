import { ImageResponse } from "next/og";
import {
  BEEHIVE_BANDS,
  BEEHIVE_BARS,
  BEEHIVE_BAR_BASELINE,
  BEEHIVE_BAR_WIDTH,
} from "@/lib/beehive-stats-mark";

// Code-generated favicon/app icon per Next's `icon.tsx` file convention.
// A filled beehive-and-bar-chart mark: the site's identity (a skep, per
// src/components/beehive-mark.tsx) plus its subject (stats), solid rather
// than line-drawn so it stays legible at 16-32px. Transparent background —
// browsers paint their own tab chrome behind it in both themes. Shares its
// geometry with src/components/beehive-stats-mark.tsx (the same mark, used
// as the nav-bar logo) so the two can't drift apart.
export const size = { width: 32, height: 32 };
export const contentType = "image/png";

const HONEY = "#d9a441"; // brand honey (dark-mode value — reads well on any tab background)
const INK = "#1a1a1a"; // brand foreground

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
          {BEEHIVE_BANDS.map((b, i) => (
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
          {BEEHIVE_BARS.map((b, i) => (
            <rect
              key={i}
              x={b.x}
              y={BEEHIVE_BAR_BASELINE - b.h}
              width={BEEHIVE_BAR_WIDTH}
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
