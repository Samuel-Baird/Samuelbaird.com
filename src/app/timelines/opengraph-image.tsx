import { ImageResponse } from "next/og";
import { OG_SIZE, OG_CONTENT_TYPE, OgFrame, OG_INK, OG_MUTED, OG_ACCENT } from "@/lib/og";
import { TIMELINES } from "./registry";

export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;
export const alt = "Latter-day Stats — Timelines";

export default function Image() {
  const totalSources = TIMELINES.reduce((sum, t) => sum + t.sourceCount, 0);

  return new ImageResponse(
    (
      <OgFrame eyebrow="Latter-day Stats · Timelines">
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div
            style={{
              fontSize: 76,
              fontWeight: 700,
              color: OG_INK,
              lineHeight: 1.05,
              letterSpacing: "-0.02em",
            }}
          >
            Sources over time
          </div>
          <div
            style={{
              fontSize: 28,
              color: OG_MUTED,
              fontFamily: "system-ui, sans-serif",
              maxWidth: 900,
            }}
          >
            How particular teachings have been stated, restated, and
            reframed — traced through primary and official sources.
          </div>
          <div
            style={{
              display: "flex",
              gap: 32,
              fontSize: 26,
              color: OG_ACCENT,
              fontFamily: "system-ui, sans-serif",
              fontWeight: 600,
            }}
          >
            <span>
              {TIMELINES.length} timeline{TIMELINES.length === 1 ? "" : "s"}
            </span>
            <span>·</span>
            <span>{totalSources} sources</span>
          </div>
        </div>
      </OgFrame>
    ),
    { ...size },
  );
}
