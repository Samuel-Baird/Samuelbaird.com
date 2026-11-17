import { ImageResponse } from "next/og";
import { OG_SIZE, OG_CONTENT_TYPE, OgFrame, OG_INK, OG_MUTED } from "@/lib/og";

export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;
export const alt = "Latter-day Stats — Methodology";

export default function Image() {
  return new ImageResponse(
    (
      <OgFrame eyebrow="Latter-day Stats · Methodology">
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div
            style={{
              fontSize: 88,
              fontWeight: 700,
              color: OG_INK,
              lineHeight: 1.05,
              letterSpacing: "-0.02em",
            }}
          >
            Methodology
          </div>
          <div
            style={{
              fontSize: 28,
              color: OG_MUTED,
              fontFamily: "system-ui, sans-serif",
              maxWidth: 900,
            }}
          >
            How channels are selected, statistics collected, and academic
            studies curated.
          </div>
        </div>
      </OgFrame>
    ),
    { ...size },
  );
}
