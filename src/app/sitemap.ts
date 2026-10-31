import type { MetadataRoute } from "next";
import { createClient } from "@supabase/supabase-js";
import { DATASETS, categorySlug, graphicId } from "@/lib/data-explorer";
import { getGraphicPostMap, isPublished } from "@/lib/graphic-posts";
import { STUDY_GRAPHICS } from "@/lib/study-graphics";

const BASE = "https://latterdaystats.samuelbaird.com";

export const revalidate = 3600;

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const sb = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { auth: { autoRefreshToken: false, persistSession: false } },
  );

  const [channelsRes, studiesRes, postMap] = await Promise.all([
    sb.from("channels").select("slug, updated_at").eq("is_active", true),
    sb.from("studies").select("slug, updated_at"),
    getGraphicPostMap(),
  ]);

  const staticRoutes: MetadataRoute.Sitemap = [
    { url: `${BASE}/`, changeFrequency: "daily", priority: 1.0 },
    { url: `${BASE}/channels`, changeFrequency: "daily", priority: 0.9 },
    { url: `${BASE}/studies`, changeFrequency: "weekly", priority: 0.9 },
    { url: `${BASE}/data-explorer`, changeFrequency: "weekly", priority: 0.8 },
    { url: `${BASE}/connect`, changeFrequency: "monthly", priority: 0.5 },
    { url: `${BASE}/faq`, changeFrequency: "monthly", priority: 0.6 },
    { url: `${BASE}/about`, changeFrequency: "monthly", priority: 0.5 },
    { url: `${BASE}/methodology`, changeFrequency: "monthly", priority: 0.5 },
    { url: `${BASE}/donate`, changeFrequency: "monthly", priority: 0.4 },
    { url: `${BASE}/contact`, changeFrequency: "monthly", priority: 0.3 },
    { url: `${BASE}/terms`, changeFrequency: "yearly", priority: 0.2 },
    { url: `${BASE}/privacy`, changeFrequency: "yearly", priority: 0.2 },
    { url: `${BASE}/dmca`, changeFrequency: "yearly", priority: 0.2 },
    { url: `${BASE}/accessibility`, changeFrequency: "yearly", priority: 0.2 },
  ];

  const channelRoutes: MetadataRoute.Sitemap = (channelsRes.data ?? []).map(
    (c: { slug: string; updated_at: string | null }) => ({
      url: `${BASE}/channels/${c.slug}`,
      lastModified: c.updated_at ? new Date(c.updated_at) : undefined,
      changeFrequency: "daily",
      priority: 0.8,
    }),
  );

  const studyRoutes: MetadataRoute.Sitemap = (studiesRes.data ?? []).map(
    (s: { slug: string; updated_at: string | null }) => ({
      url: `${BASE}/studies/${s.slug}`,
      lastModified: s.updated_at ? new Date(s.updated_at) : undefined,
      changeFrequency: "monthly",
      priority: 0.7,
    }),
  );

  const datasetRoutes: MetadataRoute.Sitemap = DATASETS.flatMap((d) => {
    const published = d.graphics.filter((g) => isPublished(postMap, d.slug, graphicId(g)));
    return [
      { url: `${BASE}/data-explorer/${d.slug}`, changeFrequency: "monthly" as const, priority: 0.7 },
      ...(published.length
        ? [
            {
              url: `${BASE}/data-explorer/${d.slug}/graphics`,
              changeFrequency: "monthly" as const,
              priority: 0.6,
            },
          ]
        : []),
      ...published.map((g) => ({
        url: `${BASE}/data-explorer/${d.slug}/graphics/${graphicId(g)}`,
        changeFrequency: "yearly" as const,
        priority: 0.4,
      })),
    ];
  });

  const studyGraphicsRoutes: MetadataRoute.Sitemap = STUDY_GRAPHICS.flatMap((e) => {
    const published = e.graphics.filter((g) => isPublished(postMap, e.studySlug, graphicId(g)));
    if (published.length === 0) return [];
    return [
      {
        url: `${BASE}/studies/${e.studySlug}/graphics`,
        changeFrequency: "monthly" as const,
        priority: 0.6,
      },
      ...published.map((g) => ({
        url: `${BASE}/studies/${e.studySlug}/graphics/${graphicId(g)}`,
        changeFrequency: "yearly" as const,
        priority: 0.4,
      })),
    ];
  });

  const categorySlugs = [...new Set(DATASETS.filter((d) => d.category).map((d) => categorySlug(d.category!)))];
  const categoryRoutes: MetadataRoute.Sitemap = categorySlugs.map((slug) => ({
    url: `${BASE}/data-explorer/category/${slug}`,
    changeFrequency: "monthly" as const,
    priority: 0.6,
  }));

  return [
    ...staticRoutes,
    ...channelRoutes,
    ...studyRoutes,
    ...datasetRoutes,
    ...studyGraphicsRoutes,
    ...categoryRoutes,
  ];
}
