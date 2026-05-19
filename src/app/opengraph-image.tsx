import { ImageResponse } from "next/og";
import { getSiteStats } from "@/lib/data";
import { fmtCompact, fmtNumber } from "@/lib/format";
import { OG_SIZE, OG_CONTENT_TYPE, OgFrame } from "@/lib/og";

export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;
export const alt = "Latter-day Stats";

export default async function Image() {
  const stats = await getSiteStats();

  return new ImageResponse(
    (
      <OgFrame eyebrow="Latter-day Stats">
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div
            style={{
              fontSize: 64,
              fontWeight: 700,
              color: "#111827",
              lineHeight: 1.1,
              letterSpacing: "-0.02em",
              maxWidth: 1000,
            }}
          >
            Statistics, research, and creator data on the Latter-day Saint
            community.
          </div>
          {stats && (
            <div
              style={{
                display: "flex",
                gap: 32,
                fontSize: 26,
                color: "#1f4f7a",
                fontFamily: "system-ui, sans-serif",
                fontWeight: 600,
              }}
            >
              <span>{fmtNumber(stats.total_channels)} channels</span>
              <span>·</span>
              <span>{fmtCompact(stats.total_subscribers)} subscribers</span>
              <span>·</span>
              <span>{fmtCompact(stats.total_views)} views</span>
            </div>
          )}
        </div>
      </OgFrame>
    ),
    { ...size },
  );
}
