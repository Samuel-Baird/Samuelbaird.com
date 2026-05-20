import type { MetadataRoute } from "next";
import { createClient } from "@supabase/supabase-js";

const BASE = "https://latter-day-stats-ap81.vercel.app";

export const revalidate = 3600;

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const sb = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { auth: { autoRefreshToken: false, persistSession: false } },
  );

  const [channelsRes, studiesRes] = await Promise.all([
    sb.from("channels").select("slug, updated_at").eq("is_active", true),
    sb.from("studies").select("slug, updated_at"),
  ]);

  const staticRoutes: MetadataRoute.Sitemap = [
    { url: `${BASE}/`, changeFrequency: "daily", priority: 1.0 },
    { url: `${BASE}/channels`, changeFrequency: "daily", priority: 0.9 },
    { url: `${BASE}/studies`, changeFrequency: "weekly", priority: 0.9 },
    { url: `${BASE}/beta`, changeFrequency: "weekly", priority: 0.7 },
    { url: `${BASE}/about`, changeFrequency: "monthly", priority: 0.5 },
    { url: `${BASE}/methodology`, changeFrequency: "monthly", priority: 0.5 },
    { url: `${BASE}/contact`, changeFrequency: "monthly", priority: 0.3 },
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

  return [...staticRoutes, ...channelRoutes, ...studyRoutes];
}
