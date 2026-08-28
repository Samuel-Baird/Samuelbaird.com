import type { MetadataRoute } from "next";
import { createClient } from "@supabase/supabase-js";
import { DATASETS, categorySlug, graphicId } from "@/lib/data-explorer";

const BASE = "https://latter-day-stats.vercel.app";

export const revalidate = 3600;

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const sb = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { auth: { autoRefreshToken: false, persistSession: false } },
  );

  // The anon key can only see published claims (RLS), which is exactly the
  // set that belongs in a sitemap — drafts are filtered out by the database.
  const [channelsRes, studiesRes, claimsRes] = await Promise.all([
    sb.from("channels").select("slug, updated_at").eq("is_active", true),
    sb.from("studies").select("slug, updated_at"),
    sb.from("claims").select("slug, updated_at").eq("status", "published"),
  ]);

  const staticRoutes: MetadataRoute.Sitemap = [
    { url: `${BASE}/`, changeFrequency: "daily", priority: 1.0 },
    { url: `${BASE}/channels`, changeFrequency: "daily", priority: 0.9 },
    { url: `${BASE}/studies`, changeFrequency: "weekly", priority: 0.9 },
    { url: `${BASE}/claims`, changeFrequency: "weekly", priority: 0.9 },
    { url: `${BASE}/data-explorer`, changeFrequency: "weekly", priority: 0.8 },
    { url: `${BASE}/timelines`, changeFrequency: "weekly", priority: 0.8 },
    { url: `${BASE}/premium`, changeFrequency: "weekly", priority: 0.7 },
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

  const claimRoutes: MetadataRoute.Sitemap = (claimsRes.data ?? []).map(
    (c: { slug: string; updated_at: string | null }) => ({
      url: `${BASE}/claims/${c.slug}`,
      lastModified: c.updated_at ? new Date(c.updated_at) : undefined,
      changeFrequency: "monthly",
      priority: 0.8,
    }),
  );

  const datasetRoutes: MetadataRoute.Sitemap = DATASETS.flatMap((d) => [
    { url: `${BASE}/data-explorer/${d.slug}`, changeFrequency: "monthly" as const, priority: 0.7 },
    ...(d.graphics.length
      ? [
          {
            url: `${BASE}/data-explorer/${d.slug}/graphics`,
            changeFrequency: "monthly" as const,
            priority: 0.6,
          },
        ]
      : []),
    ...d.graphics.map((g) => ({
      url: `${BASE}/data-explorer/${d.slug}/graphics/${graphicId(g)}`,
      changeFrequency: "yearly" as const,
      priority: 0.4,
    })),
  ]);

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
    ...claimRoutes,
    ...datasetRoutes,
    ...categoryRoutes,
  ];
}
