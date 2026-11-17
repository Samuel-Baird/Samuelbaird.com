import { ImageResponse } from "next/og";
import { getStudyBySlug } from "@/lib/data";
import { OG_SIZE, OG_CONTENT_TYPE, OgFrame, OG_INK, OG_MUTED } from "@/lib/og";

export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;
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
      <OgFrame eyebrow="Latter-day Stats · Academic Study">
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div
            style={{
              fontSize: title.length > 60 ? 52 : 64,
              fontWeight: 700,
              color: OG_INK,
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
                color: OG_MUTED,
                fontFamily: "system-ui, sans-serif",
              }}
            >
              {meta}
            </div>
          )}
        </div>
      </OgFrame>
    ),
    { ...size },
  );
}
