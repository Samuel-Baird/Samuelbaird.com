import { ImageResponse } from "next/og";
import { getChannelBySlug } from "@/lib/data";
import { fmtCompact } from "@/lib/format";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";
export const alt = "Latter-day Stats — Channel";

export default async function Image({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const channel = await getChannelBySlug(slug);

  const name = channel?.name ?? "Channel";
  const subs = channel?.latest?.subscribers
    ? `${fmtCompact(channel.latest.subscribers)} subscribers`
    : null;
  const views = channel?.latest?.total_views
    ? `${fmtCompact(channel.latest.total_views)} total views`
    : null;
  const stat = [subs, views].filter(Boolean).join("  ·  ");

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "#ffffff",
          padding: "64px 72px",
          fontFamily: "Georgia, serif",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          {channel?.thumbnail_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={channel.thumbnail_url}
              width={80}
              height={80}
              style={{ borderRadius: 40, objectFit: "cover" }}
              alt=""
            />
          )}
          <span
            style={{
              fontSize: 18,
              color: "#6b7280",
              fontFamily: "system-ui, sans-serif",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
            }}
          >
            Latter-day Stats · Channel
          </span>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div
            style={{
              fontSize: 72,
              fontWeight: 700,
              color: "#111827",
              lineHeight: 1.05,
              letterSpacing: "-0.02em",
            }}
          >
            {name}
          </div>
          {stat && (
            <div
              style={{
                fontSize: 28,
                color: "#6b7280",
                fontFamily: "system-ui, sans-serif",
              }}
            >
              {stat}
            </div>
          )}
        </div>

        <div
          style={{
            fontSize: 18,
            color: "#9ca3af",
            fontFamily: "system-ui, sans-serif",
          }}
        >
          latter-day-stats.vercel.app
        </div>
      </div>
    ),
    { ...size },
  );
}
