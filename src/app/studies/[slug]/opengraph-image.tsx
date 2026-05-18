import { ImageResponse } from "next/og";
import { getStudyBySlug } from "@/lib/data";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";
export const alt = "Latter-day Stats — Study";

export default async function Image({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const study = await getStudyBySlug(slug);

  const title = study?.title ?? "Research Study";
  const authors =
    (study?.authors ?? []).length > 0
      ? study!.authors.slice(0, 2).join(", ") +
        (study!.authors.length > 2 ? " et al." : "")
      : null;
  const year = study?.year ? String(study.year) : null;
  const meta = [authors, year].filter(Boolean).join("  ·  ");

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
        <span
          style={{
            fontSize: 18,
            color: "#6b7280",
            fontFamily: "system-ui, sans-serif",
            letterSpacing: "0.1em",
            textTransform: "uppercase",
          }}
        >
          Latter-day Stats · Academic Study
        </span>

        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div
            style={{
              fontSize: title.length > 60 ? 52 : 64,
              fontWeight: 700,
              color: "#111827",
              lineHeight: 1.1,
              letterSpacing: "-0.02em",
            }}
          >
            {title.length > 110 ? title.slice(0, 108) + "…" : title}
          </div>
          {meta && (
            <div
              style={{
                fontSize: 26,
                color: "#6b7280",
                fontFamily: "system-ui, sans-serif",
              }}
            >
              {meta}
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
