import "server-only";
import { cache } from "react";
import { unstable_cache } from "next/cache";
import { getGraphic, graphicId, type Graphic } from "@/lib/data-explorer";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { isLive } from "@/lib/graphic-publish";
import { getStudyGraphic } from "@/lib/study-graphics";
import type { GraphicPost } from "@/lib/types";

// graphic_posts (supabase/migrations/0049_graphic_posts.sql,
// 0051_graphic_published.sql, 0054_graphic_publish_at.sql) is RLS deny-all,
// so every read here goes through the service client - safe inside
// unstable_cache since it carries no per-request cookies. `published` +
// `publish_at` gate public visibility everywhere a graphic can be shown,
// and publish_at doubles as the record of when it was posted.
//
// The time comparison happens per request (isLive -> Date.now()), NOT inside
// the cache, so a scheduled graphic goes live on the first request after its
// publish_at even though the row map itself is cached for an hour. Every
// page that consumes the map also reads cookies (getCurrentUser), so those
// renders are dynamic; only sitemap.ts / feed.xml (ISR, 1h) lag behind.
//
// Key format matches the table's unique(dataset_slug, graphic_id): a slug
// (dataset OR study, flat key space - see study-graphics.ts's build guard)
// plus the graphic's stable id (graphicId() in data-explorer.ts).
export type GraphicPostMap = Record<string, GraphicPost>;

function key(slug: string, id: string): string {
  return `${slug}/${id}`;
}

const fetchGraphicPostRows = unstable_cache(
  async (): Promise<GraphicPost[]> => {
    const { data, error } = await createSupabaseServiceClient()
      .from("graphic_posts")
      .select("dataset_slug, graphic_id, published, publish_at");
    if (error) throw error;
    return (data ?? []) as GraphicPost[];
  },
  ["graphic-post-map"],
  { tags: ["graphic-posts"], revalidate: 86400 },
);

/** Every graphic_posts row, as a plain Record keyed `${slug}/${id}` — plain
 * (not a Map) so it serializes straight into client-component props. */
export const getGraphicPostMap = cache(async (): Promise<GraphicPostMap> => {
  const rows = await fetchGraphicPostRows();
  const map: GraphicPostMap = {};
  for (const row of rows) map[key(row.dataset_slug, row.graphic_id)] = row;
  return map;
});

export function isPublished(map: GraphicPostMap, slug: string, id: string): boolean {
  return isLive(map[key(slug, id)]);
}

export function filterPublished<T extends Graphic>(
  map: GraphicPostMap,
  slug: string,
  graphics: T[],
): T[] {
  return graphics.filter((g) => isPublished(map, slug, graphicId(g)));
}

/** Unified registry lookup used by the graphic_posts server actions to
 * confirm a (slug, id) pair actually names a real graphic before writing -
 * datasets first, studies second (see the collision guard in
 * study-graphics.ts's build-time check). */
export function graphicExists(slug: string, id: string): boolean {
  return Boolean(getGraphic(slug, id) ?? getStudyGraphic(slug, id));
}
