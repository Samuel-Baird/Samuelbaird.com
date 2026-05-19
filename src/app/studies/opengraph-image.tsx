import { ImageResponse } from "next/og";
import { OG_SIZE, OG_CONTENT_TYPE, OgFrame } from "@/lib/og";

export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;
export const alt = "Latter-day Stats — Research library";

export default function Image() {
  return new ImageResponse(
    (
      <OgFrame eyebrow="Latter-day Stats · Research">
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div
            style={{
              fontSize: 88,
              fontWeight: 700,
              color: "#111827",
              lineHeight: 1.05,
              letterSpacing: "-0.02em",
            }}
          >
            Research library
          </div>
          <div
            style={{
              fontSize: 28,
              color: "#6b7280",
              fontFamily: "system-ui, sans-serif",
              maxWidth: 900,
            }}
          >
            Curated academic studies relating to the Latter-day Saint community.
          </div>
        </div>
      </OgFrame>
    ),
    { ...size },
  );
}
