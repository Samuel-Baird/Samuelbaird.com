import { ImageResponse } from "next/og";
import { getChannelBySlug } from "@/lib/data";
import { fmtCompact } from "@/lib/format";
import { OG_SIZE, OG_CONTENT_TYPE, OgFrame, OG_INK, OG_MUTED } from "@/lib/og";

export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;
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
      <OgFrame eyebrow="Latter-day Stats · Channel">
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
            {channel?.thumbnail_url && (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={channel.thumbnail_url}
                width={80}
                height={80}
                style={{ borderRadius: 4, objectFit: "cover" }}
                alt=""
              />
            )}
            <div
              style={{
                fontSize: 72,
                fontWeight: 700,
                color: OG_INK,
                lineHeight: 1.05,
                letterSpacing: "-0.02em",
              }}
            >
              {name}
            </div>
          </div>
          {stat && (
            <div
              style={{
                fontSize: 28,
                color: OG_MUTED,
                fontFamily: "system-ui, sans-serif",
              }}
            >
              {stat}
            </div>
          )}
        </div>
      </OgFrame>
    ),
    { ...size },
  );
}
