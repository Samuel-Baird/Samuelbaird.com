import { ImageResponse } from "next/og";
import { OG_SIZE, OG_CONTENT_TYPE, OgFrame, OG_INK, OG_MUTED } from "@/lib/og";

export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;
export const alt = "Latter-day Stats — Compare channels";

export default function Image() {
  return new ImageResponse(
    (
      <OgFrame eyebrow="Latter-day Stats · Compare">
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div
            style={{
              fontSize: 80,
              fontWeight: 700,
              color: OG_INK,
              lineHeight: 1.05,
              letterSpacing: "-0.02em",
            }}
          >
            Compare LDS channels side-by-side
          </div>
          <div
            style={{
              fontSize: 28,
              color: OG_MUTED,
              fontFamily: "system-ui, sans-serif",
            }}
          >
            Overlay subscriber growth across up to four channels.
          </div>
        </div>
      </OgFrame>
    ),
    { ...size },
  );
}
