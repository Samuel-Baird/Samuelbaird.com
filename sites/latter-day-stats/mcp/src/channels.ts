import { supabase } from "./supabase.js";

// Every active channel is returned, including those tagged Critical: the
// website lists them for everyone, so the MCP server does too.

export type ChannelSummary = {
  slug: string;
  youtube_channel_id: string;
  name: string;
  description: string | null;
  channel_type: string | null;
  channel_types: string[];
  country: string | null;
  language: string | null;
  handle: string | null;
  featured: boolean;
  subscribers: number | null;
  total_views: number | null;
  video_count: number | null;
  stats_captured_at: string | null;
};

function toSummary(row: any): ChannelSummary {
  return {
    slug: row.slug,
    youtube_channel_id: row.youtube_channel_id,
    name: row.name,
    description: row.description,
    channel_type: row.channel_type,
    channel_types: row.channel_types ?? [],
    country: row.country_manual ?? row.country ?? null,
    language: row.language_manual ?? row.language ?? null,
    handle: row.handle,
    featured: row.featured,
    subscribers: row.subscribers,
    total_views: row.total_views,
    video_count: row.video_count,
    stats_captured_at: row.stats_captured_at,
  };
}

export async function listChannels(opts: {
  search?: string;
  type?: string;
  country?: string;
  featuredOnly?: boolean;
  minSubscribers?: number;
  sort?: "subscribers" | "name" | "newest";
  limit?: number;
}): Promise<ChannelSummary[]> {
  const sb = supabase();
  let q = sb.from("channel_full").select("*").eq("is_active", true);

  if (opts.search) q = q.ilike("name", `%${opts.search}%`);
  if (opts.type) q = q.contains("channel_types", [opts.type]);
  if (opts.featuredOnly) q = q.eq("featured", true);

  const { data, error } = await q;
  if (error) throw error;

  let rows = (data ?? []) as any[];

  if (opts.country) {
    const wanted = opts.country.toLowerCase();
    rows = rows.filter(
      (r) => (r.country_manual ?? r.country ?? "").toLowerCase() === wanted,
    );
  }
  if (opts.minSubscribers != null) {
    rows = rows.filter((r) => (r.subscribers ?? 0) >= opts.minSubscribers!);
  }

  const sort = opts.sort ?? "subscribers";
  rows.sort((a, b) => {
    if (sort === "name") return a.name.localeCompare(b.name);
    if (sort === "newest")
      return (
        new Date(b.created_at_youtube ?? 0).getTime() -
        new Date(a.created_at_youtube ?? 0).getTime()
      );
    return (b.subscribers ?? 0) - (a.subscribers ?? 0);
  });

  const limit = Math.min(opts.limit ?? 50, 500);
  return rows.slice(0, limit).map(toSummary);
}

export async function getChannel(opts: {
  slug?: string;
  youtubeChannelId?: string;
}): Promise<ChannelSummary | { stats_history: any[] } | null> {
  if (!opts.slug && !opts.youtubeChannelId) {
    throw new Error("Provide either slug or youtubeChannelId.");
  }
  const sb = supabase();
  let q = sb.from("channel_full").select("*").eq("is_active", true);
  q = opts.slug ? q.eq("slug", opts.slug) : q.eq("youtube_channel_id", opts.youtubeChannelId!);

  const { data, error } = await q.maybeSingle();
  if (error) throw error;
  if (!data) return null;

  const summary = toSummary(data);

  const { data: history, error: histError } = await sb
    .from("channel_stats")
    .select("captured_at, subscribers, total_views, video_count")
    .eq("channel_id", (data as any).id)
    .order("captured_at", { ascending: true })
    .limit(200);
  if (histError) throw histError;

  return { ...summary, stats_history: history ?? [] } as any;
}

export async function listChannelTypes(): Promise<string[]> {
  const sb = supabase();
  const { data, error } = await sb
    .from("channel_full")
    .select("channel_types")
    .eq("is_active", true);
  if (error) throw error;
  const set = new Set<string>();
  for (const row of (data ?? []) as { channel_types: string[] }[]) {
    for (const t of row.channel_types ?? []) set.add(t);
  }
  return [...set].sort();
}
