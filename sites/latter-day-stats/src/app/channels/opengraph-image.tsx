import { ImageResponse } from "next/og";
import { getSiteStats } from "@/lib/data";
import { fmtCompact, fmtNumber } from "@/lib/format";
import { OG_SIZE, OG_CONTENT_TYPE, OgFrame, OG_INK, OG_MUTED, OG_ACCENT } from "@/lib/og";

export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;
export const alt = "Latter-day Stats — Channels";

export default async function Image() {
  const stats = await getSiteStats();

  return new ImageResponse(
    (
      <OgFrame eyebrow="Latter-day Stats · Channels">
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
            Channel directory
          </div>
          <div
            style={{
              fontSize: 28,
              color: OG_MUTED,
              fontFamily: "system-ui, sans-serif",
              maxWidth: 900,
            }}
          >
            Latter-day Saint YouTube creators, tracked and refreshed regularly.
          </div>
          {stats && (
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
              <span>{fmtNumber(stats.total_channels)} channels</span>
              <span>·</span>
              <span>{fmtCompact(stats.total_subscribers)} subscribers</span>
            </div>
          )}
        </div>
      </OgFrame>
    ),
    { ...size },
  );
}
