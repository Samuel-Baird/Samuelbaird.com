import "server-only";
import { cache } from "react";
import { unstable_cache } from "next/cache";
import { createClient } from "@supabase/supabase-js";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import type { Channel, ChannelWithStats, SiteStats, Study } from "./types";

// Read-only public client (anon key). RLS allows select on all public tables.
function publicClient() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { auth: { autoRefreshToken: false, persistSession: false } },
  );
}

// Public (anon-key) reads are wrapped in unstable_cache, tagged "channels" /
// "studies" / "upvotes" so admin actions and the stats cron can invalidate
// them via revalidateTag. Per-user readers (bookmarks, upvotes, progress) use
// the cookie-bound client and must NOT go inside unstable_cache. Anything
// involving Math.random() also stays outside so shuffles vary per request.

type ChannelFullRow = Channel & {
  stats_captured_at: string | null;
  subscribers: number | null;
  total_views: number | null;
  video_count: number | null;
};

function rowToChannelWithStats(row: ChannelFullRow): ChannelWithStats {
  const {
    stats_captured_at,
    subscribers,
    total_views,
    video_count,
    ...channel
  } = row;
  const latest =
    stats_captured_at !== null && subscribers !== null
      ? {
          channel_id: channel.id,
          captured_at: stats_captured_at,
          subscribers: subscribers ?? 0,
          total_views: total_views ?? 0,
          video_count: video_count ?? 0,
        }
      : null;
  return { ...(channel as Channel), latest };
}

const fetchChannelFullRows = cache(
  unstable_cache(
    async (includeInactive: boolean): Promise<ChannelFullRow[]> => {
      const sb = publicClient();
      let query = sb.from("channel_full").select("*");
      if (!includeInactive) query = query.eq("is_active", true);
      const { data, error } = await query;
      if (error) throw error;
      return (data ?? []) as ChannelFullRow[];
    },
    ["channel-full-rows"],
    { tags: ["channels"], revalidate: 3600 },
  ),
);

export async function getChannelsWithLatest(
  {
    includeInactive = false,
    includeCritical = true,
  }: { includeInactive?: boolean; includeCritical?: boolean } = {},
): Promise<ChannelWithStats[]> {
  // Critical filtering happens outside the cache so premium and non-premium
  // visitors share one cache entry.
  const rows = (await fetchChannelFullRows(includeInactive)).map(
    rowToChannelWithStats,
  );
  if (includeCritical) return rows;
  return rows.filter((c) => {
    const tags = c.channel_types?.length
      ? c.channel_types
      : c.channel_type
        ? [c.channel_type]
        : [];
    return !tags.includes("Critical");
  });
}

const fetchChannelByYouTubeId = unstable_cache(
  async (youtubeChannelId: string): Promise<ChannelFullRow | null> => {
    const sb = publicClient();
    const { data, error } = await sb
      .from("channel_full")
      .select("*")
      .eq("youtube_channel_id", youtubeChannelId)
      .maybeSingle();
    if (error) throw error;
    return (data as ChannelFullRow) ?? null;
  },
  ["channel-by-youtube-id"],
  { tags: ["channels"], revalidate: 3600 },
);

export async function getChannelByYouTubeId(
  youtubeChannelId: string,
): Promise<ChannelWithStats | null> {
  const row = await fetchChannelByYouTubeId(youtubeChannelId);
  return row ? rowToChannelWithStats(row) : null;
}

export async function getChannelByNameLike(
  pattern: string,
): Promise<ChannelWithStats | null> {
  const sb = publicClient();
  const { data, error } = await sb
    .from("channel_full")
    .select("*")
    .ilike("name", pattern)
    .limit(1)
    .maybeSingle();
  if (error) throw error;
  if (!data) return null;
  return rowToChannelWithStats(data as ChannelFullRow);
}

export async function getFeaturedChannelsMix(
  total = 6,
): Promise<ChannelWithStats[]> {
  const all = await getChannelsWithLatest();
  const EXCLUDED_TYPES = new Set(["Critical"]);

  const featured = all.filter((c) => c.featured);
  const used = new Set(featured.map((c) => c.id));

  // Build a category-diverse filler set: one channel per type, shuffled, then
  // repeat until we have enough. This ensures the 6-card grid rarely shows
  // the same category twice in a row.
  const primaryType = (c: ChannelWithStats) =>
    (c.channel_types?.[0] ?? c.channel_type ?? "") || "Other";
  const fillerPool = all.filter((c) => {
    if (used.has(c.id)) return false;
    const tags = c.channel_types?.length
      ? c.channel_types
      : c.channel_type
        ? [c.channel_type]
        : [];
    return !tags.some((t) => EXCLUDED_TYPES.has(t));
  });

  // Group by primary tag, shuffle within each group
  const byType = new Map<string, ChannelWithStats[]>();
  for (const c of fillerPool) {
    const key = primaryType(c);
    if (!byType.has(key)) byType.set(key, []);
    byType.get(key)!.push(c);
  }
  for (const arr of byType.values()) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
  }

  // Round-robin across types to maximise category variety
  const typeQueues = [...byType.values()];
  for (let i = typeQueues.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [typeQueues[i], typeQueues[j]] = [typeQueues[j], typeQueues[i]];
  }
  const diverse: ChannelWithStats[] = [];
  const needed = Math.max(0, total - featured.length);
  let round = 0;
  while (diverse.length < needed) {
    let added = false;
    for (const queue of typeQueues) {
      if (diverse.length >= needed) break;
      if (queue.length > round) {
        diverse.push(queue[round]);
        added = true;
      }
    }
    if (!added) break;
    round++;
  }

  return [...featured, ...diverse];
}

export async function getFeaturedChannelsCarouselPool(
  total = 24,
  { includeCritical = false }: { includeCritical?: boolean } = {},
): Promise<ChannelWithStats[]> {
  const all = await getChannelsWithLatest();
  const EXCLUDED_TYPES = new Set(includeCritical ? [] : ["Critical"]);
  const primaryType = (c: ChannelWithStats) =>
    (c.channel_types?.[0] ?? c.channel_type ?? "") || "Other";

  const eligible = all.filter((c) => {
    const tags = c.channel_types?.length
      ? c.channel_types
      : c.channel_type
        ? [c.channel_type]
        : [];
    return !tags.some((t) => EXCLUDED_TYPES.has(t));
  });
  if (eligible.length === 0) return [];

  // Group by primary tag, shuffle within each group
  const byType = new Map<string, ChannelWithStats[]>();
  for (const c of eligible) {
    const key = primaryType(c);
    if (!byType.has(key)) byType.set(key, []);
    byType.get(key)!.push(c);
  }
  for (const arr of byType.values()) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
  }

  const typeQueues = [...byType.values()];
  for (let i = typeQueues.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [typeQueues[i], typeQueues[j]] = [typeQueues[j], typeQueues[i]];
  }

  // Round-robin across types; loop if we exhaust unique channels (duplicates ok)
  const out: ChannelWithStats[] = [];
  let round = 0;
  while (out.length < total) {
    let added = false;
    for (const queue of typeQueues) {
      if (out.length >= total) break;
      const next = queue[round % queue.length];
      if (next) {
        out.push(next);
        added = true;
      }
    }
    if (!added) break;
    round++;
  }

  // Sprinkle featured into random positions so the eye-catchers aren't clustered
  const featured = eligible.filter((c) => c.featured);
  for (const f of featured) {
    const pos = Math.floor(Math.random() * (out.length + 1));
    out.splice(pos, 0, f);
  }
  return out.slice(0, total);
}

const fetchRecentlyAdded = unstable_cache(
  async (
    days: number,
    limit: number,
    includeStudies: boolean,
  ): Promise<{ channelRows: ChannelFullRow[]; studies: Study[] }> => {
    const since = new Date(Date.now() - days * 86_400_000).toISOString();
    const sb = publicClient();
    const channelsQuery = sb
      .from("channel_full")
      .select("*")
      .eq("is_active", true)
      .gte("created_at", since)
      .order("created_at", { ascending: false })
      .limit(limit);
    const studiesQuery = includeStudies
      ? sb
          .from("studies")
          .select("*")
          .gte("created_at", since)
          .order("created_at", { ascending: false })
          .limit(limit)
      : Promise.resolve({ data: [], error: null } as const);
    const [chRes, sRes] = await Promise.all([channelsQuery, studiesQuery]);
    if (chRes.error) throw chRes.error;
    if (sRes.error) throw sRes.error;
    return {
      channelRows: (chRes.data ?? []) as ChannelFullRow[],
      studies: (sRes.data ?? []) as Study[],
    };
  },
  ["recently-added"],
  { tags: ["channels", "studies"], revalidate: 3600 },
);

export async function getRecentlyAdded(
  days = 30,
  limit = 6,
  {
    studies: includeStudies = true,
    includeCritical = true,
  }: { studies?: boolean; includeCritical?: boolean } = {},
): Promise<{ channels: ChannelWithStats[]; studies: Study[] }> {
  const { channelRows, studies } = await fetchRecentlyAdded(
    days,
    limit,
    includeStudies,
  );
  const channels = channelRows
    .map(rowToChannelWithStats)
    .filter((c) => {
      if (includeCritical) return true;
      const tags = c.channel_types?.length
        ? c.channel_types
        : c.channel_type
          ? [c.channel_type]
          : [];
      return !tags.includes("Critical");
    });
  return { channels, studies };
}

export async function getBookmarkSetForUser(
  userId: string,
): Promise<{ channels: Set<string>; studies: Set<string> }> {
  const sb = await createSupabaseServerClient();
  const { data, error } = await sb
    .from("bookmarks")
    .select("target_type, target_id")
    .eq("user_id", userId);
  if (error) throw error;

  const channels = new Set<string>();
  const studies = new Set<string>();
  for (const row of data ?? []) {
    if (row.target_type === "channel") channels.add(row.target_id);
    if (row.target_type === "study") studies.add(row.target_id);
  }
  return { channels, studies };
}

export async function getBookmarkedChannelsForUser(
  userId: string,
): Promise<ChannelWithStats[]> {
  const sb = await createSupabaseServerClient();
  const { data: bookmarks, error } = await sb
    .from("bookmarks")
    .select("target_id")
    .eq("user_id", userId)
    .eq("target_type", "channel")
    .order("created_at", { ascending: false });
  if (error) throw error;

  const ids = (bookmarks ?? []).map((row) => row.target_id);
  if (ids.length === 0) return [];

  const { data: rows, error: channelError } = await sb
    .from("channel_full")
    .select("*")
    .in("id", ids)
    .eq("is_active", true);
  if (channelError) throw channelError;

  const byChannelId = new Map(
    ((rows ?? []) as ChannelFullRow[]).map((row) => [row.id, row]),
  );
  return ids
    .map((id) => byChannelId.get(id))
    .filter((row): row is ChannelFullRow => Boolean(row))
    .map(rowToChannelWithStats);
}

export async function getBookmarkedStudiesForUser(
  userId: string,
): Promise<Study[]> {
  const sb = await createSupabaseServerClient();
  const { data: bookmarks, error } = await sb
    .from("bookmarks")
    .select("target_id")
    .eq("user_id", userId)
    .eq("target_type", "study")
    .order("created_at", { ascending: false });
  if (error) throw error;

  const ids = (bookmarks ?? []).map((row) => row.target_id);
  if (ids.length === 0) return [];

  const { data: studies, error: studiesError } = await sb
    .from("studies")
    .select("*")
    .in("id", ids);
  if (studiesError) throw studiesError;

  const byStudyId = new Map(
    ((studies ?? []) as Study[]).map((study) => [study.id, study]),
  );
  return ids
    .map((id) => byStudyId.get(id))
    .filter((study): study is Study => Boolean(study));
}

const fetchChannelBySlug = unstable_cache(
  async (slug: string): Promise<ChannelFullRow | null> => {
    const sb = publicClient();
    // Slug is now equal to youtube_channel_id (stable across renames). We accept
    // either field for backwards compatibility with any links still using the old
    // name-based slug.
    const { data, error } = await sb
      .from("channel_full")
      .select("*")
      .or(`slug.eq.${slug},youtube_channel_id.eq.${slug}`)
      .maybeSingle();
    if (error) throw error;
    return (data as ChannelFullRow) ?? null;
  },
  ["channel-by-slug"],
  { tags: ["channels"], revalidate: 3600 },
);

export async function getChannelBySlug(
  slug: string,
): Promise<ChannelWithStats | null> {
  const row = await fetchChannelBySlug(slug);
  return row ? rowToChannelWithStats(row) : null;
}

export const getChannelStatsHistory = unstable_cache(
  async (channelId: string) => {
    const sb = publicClient();
    const { data, error } = await sb
      .from("channel_stats")
      .select("captured_at, subscribers, total_views, video_count")
      .eq("channel_id", channelId)
      .order("captured_at", { ascending: true });
    if (error) throw error;
    return data ?? [];
  },
  ["channel-stats-history"],
  { tags: ["channels"], revalidate: 3600 },
);

export type ChannelMover = ChannelWithStats & {
  baseline_subscribers: number;
  baseline_captured_at: string;
  delta_subscribers: number;
  delta_pct: number;
  history: { captured_at: string; subscribers: number }[];
};

type ChannelMoverRow = {
  channel_id: string;
  baseline_subscribers: number;
  baseline_captured_at: string;
  history: { captured_at: string; subscribers: number }[];
};

// The daily dedupe + baseline computation lives in Postgres
// (get_channel_movers, migration 0031) instead of scanning 30 days of
// channel_stats rows in JS.
const fetchChannelMovers = unstable_cache(
  async (windowDays: number): Promise<ChannelMoverRow[]> => {
    const sb = publicClient();
    const { data, error } = await sb.rpc("get_channel_movers", {
      window_days: windowDays,
    });
    if (error) throw error;
    // Postgres RPC timestamps come back space-separated; normalize to ISO so
    // new Date(...) parses them in every browser (Safari rejects the space).
    const toIso = (ts: string) => ts.replace(" ", "T");
    return ((data ?? []) as ChannelMoverRow[]).map((r) => ({
      ...r,
      baseline_captured_at: toIso(r.baseline_captured_at),
      history: (r.history ?? []).map((p) => ({
        ...p,
        captured_at: toIso(p.captured_at),
      })),
    }));
  },
  ["channel-movers"],
  { tags: ["channels"], revalidate: 3600 },
);

export async function getRisersAndFallers(
  windowDays = 30,
  limit = 5,
): Promise<{ risers: ChannelMover[]; fallers: ChannelMover[] }> {
  const [moverRows, all] = await Promise.all([
    fetchChannelMovers(windowDays),
    getChannelsWithLatest(),
  ]);
  if (moverRows.length === 0) {
    return { risers: [], fallers: [] };
  }
  const byChannelId = new Map(moverRows.map((r) => [r.channel_id, r]));

  const movers: ChannelMover[] = [];
  for (const c of all) {
    const baseline = byChannelId.get(c.id);
    const latest = c.latest;
    if (!baseline || !latest) continue;
    // RPC timestamps use a space separator, table reads use ISO "T" — compare
    // as dates, not strings.
    if (
      Date.parse(baseline.baseline_captured_at) >=
      Date.parse(latest.captured_at)
    )
      continue;
    if (!baseline.baseline_subscribers || baseline.baseline_subscribers <= 0)
      continue;
    const delta = (latest.subscribers ?? 0) - baseline.baseline_subscribers;
    const pct = (delta / baseline.baseline_subscribers) * 100;
    movers.push({
      ...c,
      baseline_subscribers: baseline.baseline_subscribers,
      baseline_captured_at: baseline.baseline_captured_at,
      delta_subscribers: delta,
      delta_pct: pct,
      history: baseline.history ?? [],
    });
  }

  const risers = movers
    .filter((m) => m.delta_subscribers > 0)
    .sort((a, b) => b.delta_pct - a.delta_pct)
    .slice(0, limit);
  const fallers = movers
    .filter((m) => m.delta_subscribers < 0)
    .sort((a, b) => a.delta_pct - b.delta_pct)
    .slice(0, limit);

  return { risers, fallers };
}

export type StudySort = "categories" | "year" | "upvotes";

export type StudiesQuery = {
  query?: string;
  tags?: string[];
  sort?: StudySort;
};

const fetchStudies = unstable_cache(
  async (query: string, tags: string[]): Promise<Study[]> => {
    const sb = publicClient();
    let q = sb.from("studies").select("*");

    if (query) {
      // websearch_to_tsquery via Supabase's textSearch helper
      q = q.textSearch("search_tsv", query, { type: "websearch" });
    }
    if (tags.length > 0) {
      q = q.contains("tags", tags);
    }

    // All sorts come back ordered by year desc; explorer groups by category
    // client-side when sort === "categories".
    q = q.order("year", { ascending: false, nullsFirst: false }).limit(500);

    const { data, error } = await q;
    if (error) throw error;
    return (data ?? []) as Study[];
  },
  ["studies-query"],
  { tags: ["studies"], revalidate: 3600 },
);

export async function getStudies(opts: StudiesQuery = {}): Promise<Study[]> {
  let studies = await fetchStudies(
    (opts.query ?? "").trim(),
    opts.tags ?? [],
  );

  if (opts.sort === "upvotes" && studies.length > 0) {
    const counts = await getUpvoteCountMap(
      "study",
      studies.map((s) => s.id),
    );
    studies = studies.slice().sort((a, b) => {
      const av = counts.get(a.id) ?? 0;
      const bv = counts.get(b.id) ?? 0;
      return bv - av;
    });
  }

  return studies;
}

export const getAllStudyTags = cache(
  unstable_cache(
    async (): Promise<{ value: string; count: number }[]> => {
      const sb = publicClient();
      const { data, error } = await sb.from("studies").select("tags");
      if (error) throw error;
      const counts = new Map<string, number>();
      for (const row of (data ?? []) as { tags: string[] }[]) {
        for (const tag of row.tags ?? []) {
          const trimmed = (tag ?? "").trim();
          if (!trimmed) continue;
          counts.set(trimmed, (counts.get(trimmed) ?? 0) + 1);
        }
      }
      return [...counts.entries()]
        .map(([value, count]) => ({ value, count }))
        .sort((a, b) => a.value.localeCompare(b.value));
    },
    ["all-study-tags"],
    { tags: ["studies"], revalidate: 3600 },
  ),
);

// One small cached fetch of the whole upvote_counts view replaces the old
// per-ID-set queries, so every caller shares a single cache entry.
const fetchAllUpvoteCounts = cache(
  unstable_cache(
    async (): Promise<
      { target_type: string; target_id: string; upvotes: number }[]
    > => {
      const sb = publicClient();
      const { data, error } = await sb
        .from("upvote_counts")
        .select("target_type, target_id, upvotes");
      if (error) throw error;
      return (data ?? []) as {
        target_type: string;
        target_id: string;
        upvotes: number;
      }[];
    },
    ["upvote-counts-all"],
    { tags: ["upvotes"], revalidate: 60 },
  ),
);

export async function getUpvoteCountMap(
  targetType: "channel" | "study",
  targetIds: string[],
): Promise<Map<string, number>> {
  if (targetIds.length === 0) return new Map();
  const wanted = new Set(targetIds);
  const rows = await fetchAllUpvoteCounts();
  return new Map(
    rows
      .filter((r) => r.target_type === targetType && wanted.has(r.target_id))
      .map((row) => [row.target_id, row.upvotes]),
  );
}

export async function getUpvoteSetForUser(
  userId: string,
): Promise<{ channels: Set<string>; studies: Set<string> }> {
  const sb = await createSupabaseServerClient();
  const { data, error } = await sb
    .from("upvotes")
    .select("target_type, target_id")
    .eq("user_id", userId);
  if (error) throw error;
  const channels = new Set<string>();
  const studies = new Set<string>();
  for (const row of data ?? []) {
    if (row.target_type === "channel") channels.add(row.target_id);
    if (row.target_type === "study") studies.add(row.target_id);
  }
  return { channels, studies };
}

const fetchRecentStudies = unstable_cache(
  async (limit: number): Promise<Study[]> => {
    const sb = publicClient();
    const { data, error } = await sb
      .from("studies")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(limit);
    if (error) throw error;
    return (data ?? []) as Study[];
  },
  ["recent-studies"],
  { tags: ["studies"], revalidate: 3600 },
);

const fetchStudiesByIds = unstable_cache(
  async (ids: string[]): Promise<Study[]> => {
    if (ids.length === 0) return [];
    const sb = publicClient();
    const { data, error } = await sb.from("studies").select("*").in("id", ids);
    if (error) throw error;
    return (data ?? []) as Study[];
  },
  ["studies-by-ids"],
  { tags: ["studies"], revalidate: 3600 },
);

// Pool for the homepage carousel: a shuffled mix biased toward both
// recently added studies and the most upvoted ones. Duplicates between
// the two pools are deduped.
export async function getStudiesCarouselMix(limit = 20): Promise<Study[]> {
  const [recent, allCounts] = await Promise.all([
    fetchRecentStudies(limit),
    fetchAllUpvoteCounts(),
  ]);
  if (recent.length === 0) return [];

  const topUpvotedIds = allCounts
    .filter((r) => r.target_type === "study")
    .sort((a, b) => b.upvotes - a.upvotes)
    .slice(0, limit)
    .map((r) => r.target_id)
    .sort(); // stable order so the cache key doesn't churn between requests

  const upvoted = await fetchStudiesByIds(topUpvotedIds);

  const seen = new Set<string>();
  const mix: Study[] = [];
  for (const s of [...recent, ...upvoted]) {
    if (seen.has(s.id)) continue;
    seen.add(s.id);
    mix.push(s);
  }
  for (let i = mix.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [mix[i], mix[j]] = [mix[j], mix[i]];
  }
  return mix.slice(0, limit);
}

export const getStudyBySlug = unstable_cache(
  async (slug: string): Promise<Study | null> => {
    const sb = publicClient();
    const { data, error } = await sb
      .from("studies")
      .select("*")
      .eq("slug", slug)
      .maybeSingle();
    if (error) throw error;
    return (data as Study) ?? null;
  },
  ["study-by-slug"],
  { tags: ["studies"], revalidate: 3600 },
);

export const getSiteStats = cache(
  unstable_cache(
    async (): Promise<SiteStats | null> => {
      const sb = publicClient();
      const { data, error } = await sb
        .from("site_stats")
        .select("*")
        .maybeSingle();
      if (error) throw error;
      return (data as SiteStats) ?? null;
    },
    ["site-stats"],
    { tags: ["channels"], revalidate: 3600 },
  ),
);

export async function getStudyProgressForUser(
  userId: string,
  studyId: string,
): Promise<{ status: "read" | "unread"; notes: string } | null> {
  const sb = await createSupabaseServerClient();
  const { data, error } = await sb
    .from("study_progress")
    .select("status, notes")
    .eq("user_id", userId)
    .eq("study_id", studyId)
    .maybeSingle();
  if (error) throw error;
  if (!data) return null;
  return {
    status: (data.status as "read" | "unread") ?? "unread",
    notes: (data.notes as string) ?? "",
  };
}

const fetchStudiesOverlappingTags = unstable_cache(
  async (studyId: string, tags: string[]): Promise<Study[]> => {
    const sb = publicClient();
    const { data, error } = await sb
      .from("studies")
      .select("*")
      .neq("id", studyId)
      .overlaps("tags", tags);
    if (error) throw error;
    return (data ?? []) as Study[];
  },
  ["studies-overlapping-tags"],
  { tags: ["studies"], revalidate: 3600 },
);

export async function getRelatedStudies(
  studyId: string,
  tags: string[],
  limit = 4,
): Promise<Study[]> {
  if (!tags || tags.length === 0) return [];
  const others = await fetchStudiesOverlappingTags(studyId, tags);
  const a = new Set(tags);
  const scored = others
    .map((s) => {
      const b = new Set(s.tags ?? []);
      let overlap = 0;
      for (const t of b) if (a.has(t)) overlap++;
      const union = new Set([...a, ...b]).size;
      const jaccard = union === 0 ? 0 : overlap / union;
      return { study: s, score: jaccard, year: s.year ?? 0 };
    })
    .filter((s) => s.score > 0)
    .sort((x, y) => y.score - x.score || y.year - x.year)
    .slice(0, limit)
    .map((s) => s.study);
  return scored;
}

export type SearchItem =
  | { kind: "channel"; slug: string; name: string; sub: string | null }
  | { kind: "study"; slug: string; name: string; sub: string | null }
  | { kind: "tag"; slug: string; name: string; sub: string | null };

type SearchChannelRow = {
  slug: string;
  name: string;
  channel_type: string | null;
  channel_types: string[] | null;
};
type SearchStudyRow = {
  slug: string;
  title: string;
  year: number | null;
  authors: string[] | null;
};

const fetchSearchIndexBase = unstable_cache(
  async (): Promise<{
    channelRows: SearchChannelRow[];
    studyRows: SearchStudyRow[];
  }> => {
    const sb = publicClient();
    const [channelsRes, studiesRes] = await Promise.all([
      sb
        .from("channel_full")
        .select("slug, name, channel_type, channel_types")
        .eq("is_active", true),
      sb.from("studies").select("slug, title, year, authors"),
    ]);
    if (channelsRes.error) throw channelsRes.error;
    if (studiesRes.error) throw studiesRes.error;
    return {
      channelRows: (channelsRes.data ?? []) as SearchChannelRow[],
      studyRows: (studiesRes.data ?? []) as SearchStudyRow[],
    };
  },
  ["search-index-base"],
  { tags: ["channels", "studies"], revalidate: 3600 },
);

export async function getSearchIndex(
  { includeCritical = true }: { includeCritical?: boolean } = {},
): Promise<SearchItem[]> {
  const [{ channelRows, studyRows }, tagsRes] = await Promise.all([
    fetchSearchIndexBase(),
    getAllStudyTags(),
  ]);
  const channels: SearchItem[] = channelRows
    .filter((c) => {
      if (includeCritical) return true;
      const tags = c.channel_types?.length
        ? c.channel_types
        : c.channel_type
          ? [c.channel_type]
          : [];
      return !tags.includes("Critical");
    })
    .map((c) => ({
      kind: "channel" as const,
      slug: c.slug,
      name: c.name,
      sub: c.channel_type,
    }));
  const studies: SearchItem[] = studyRows.map((s) => ({
    kind: "study" as const,
    slug: s.slug,
    name: s.title,
    sub: [s.year, (s.authors ?? [])[0]].filter(Boolean).join(" · ") || null,
  }));
  const tags: SearchItem[] = tagsRes.map((t) => ({
    kind: "tag" as const,
    slug: t.value,
    name: t.value,
    sub: `${t.count} ${t.count === 1 ? "study" : "studies"}`,
  }));
  return [...channels, ...studies, ...tags];
}

export type StudyStats = {
  total: number;
  findings: number;
  topics: number;
  yearMin: number | null;
  yearMax: number | null;
  flagged: number;
};

export const getStudyStats = unstable_cache(
  async (): Promise<StudyStats> => {
  const sb = publicClient();
  const { data, error } = await sb
    .from("studies")
    .select("year, tags, findings, flagged_problematic");
  if (error) throw error;
  const rows = (data ?? []) as {
    year: number | null;
    tags: string[] | null;
    findings: string[] | null;
    flagged_problematic: boolean | null;
  }[];
  const topics = new Set<string>();
  let findings = 0;
  let yearMin: number | null = null;
  let yearMax: number | null = null;
  let flagged = 0;
  for (const r of rows) {
    for (const t of r.tags ?? []) if (t?.trim()) topics.add(t.trim());
    findings += (r.findings ?? []).length;
    if (typeof r.year === "number") {
      if (yearMin === null || r.year < yearMin) yearMin = r.year;
      if (yearMax === null || r.year > yearMax) yearMax = r.year;
    }
    if (r.flagged_problematic) flagged++;
  }
  return { total: rows.length, findings, topics: topics.size, yearMin, yearMax, flagged };
  },
  ["study-stats"],
  { tags: ["studies"], revalidate: 3600 },
);

export function pdfPublicUrl(pdfPath: string | null): string | null {
  return storagePublicUrl(pdfPath);
}

export function storagePublicUrl(path: string | null): string | null {
  if (!path) return null;
  const sb = publicClient();
  return sb.storage.from("studies").getPublicUrl(path).data.publicUrl;
}
