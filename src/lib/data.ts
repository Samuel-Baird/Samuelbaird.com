import "server-only";
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

export async function getChannelsWithLatest(): Promise<ChannelWithStats[]> {
  const sb = publicClient();
  const { data, error } = await sb
    .from("channel_full")
    .select("*")
    .eq("is_active", true);
  if (error) throw error;
  return (data as ChannelFullRow[]).map(rowToChannelWithStats);
}

export async function getChannelByYouTubeId(
  youtubeChannelId: string,
): Promise<ChannelWithStats | null> {
  const sb = publicClient();
  const { data, error } = await sb
    .from("channel_full")
    .select("*")
    .eq("youtube_channel_id", youtubeChannelId)
    .maybeSingle();
  if (error) throw error;
  if (!data) return null;
  return rowToChannelWithStats(data as ChannelFullRow);
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
  const featured = all.filter((c) => c.featured);
  const used = new Set(featured.map((c) => c.id));
  const fillerPool = all.filter(
    (c) => !used.has(c.id) && c.channel_type !== "Critical",
  );

  const needed = Math.max(0, total - featured.length);
  const shuffled = [...fillerPool];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  const fillers = shuffled.slice(0, needed);

  return [...featured, ...fillers];
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

export async function getChannelBySlug(
  slug: string,
): Promise<ChannelWithStats | null> {
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
  if (!data) return null;
  return rowToChannelWithStats(data as ChannelFullRow);
}

export async function getChannelStatsHistory(channelId: string) {
  const sb = publicClient();
  const { data, error } = await sb
    .from("channel_stats")
    .select("captured_at, subscribers, total_views, video_count")
    .eq("channel_id", channelId)
    .order("captured_at", { ascending: true });
  if (error) throw error;
  return data ?? [];
}

export type ChannelMover = ChannelWithStats & {
  baseline_subscribers: number;
  baseline_captured_at: string;
  delta_subscribers: number;
  delta_pct: number;
  history: { captured_at: string; subscribers: number }[];
};

export async function getRisersAndFallers(
  windowDays = 30,
  limit = 5,
): Promise<{ risers: ChannelMover[]; fallers: ChannelMover[] }> {
  const sb = publicClient();
  const since = new Date(
    Date.now() - windowDays * 24 * 60 * 60 * 1000,
  ).toISOString();

  const { data: rows, error } = await sb
    .from("channel_stats")
    .select("channel_id, captured_at, subscribers")
    .gte("captured_at", since)
    .order("captured_at", { ascending: true });
  if (error) throw error;

  type Row = { channel_id: string; captured_at: string; subscribers: number };
  const baselineByChannel = new Map<string, Row>();
  const historyByChannel = new Map<string, { captured_at: string; subscribers: number }[]>();
  for (const r of (rows ?? []) as Row[]) {
    if (!baselineByChannel.has(r.channel_id)) {
      baselineByChannel.set(r.channel_id, r);
    }
    const arr = historyByChannel.get(r.channel_id) ?? [];
    arr.push({ captured_at: r.captured_at, subscribers: r.subscribers });
    historyByChannel.set(r.channel_id, arr);
  }
  if (baselineByChannel.size === 0) {
    return { risers: [], fallers: [] };
  }

  const all = await getChannelsWithLatest();
  const movers: ChannelMover[] = [];
  for (const c of all) {
    const baseline = baselineByChannel.get(c.id);
    const latest = c.latest;
    if (!baseline || !latest) continue;
    if (baseline.captured_at >= latest.captured_at) continue;
    if (!baseline.subscribers || baseline.subscribers <= 0) continue;
    const delta = (latest.subscribers ?? 0) - baseline.subscribers;
    const pct = (delta / baseline.subscribers) * 100;
    movers.push({
      ...c,
      baseline_subscribers: baseline.subscribers,
      baseline_captured_at: baseline.captured_at,
      delta_subscribers: delta,
      delta_pct: pct,
      history: historyByChannel.get(c.id) ?? [],
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

export type StudySort = "featured" | "year" | "upvotes";

export type StudiesQuery = {
  query?: string;
  tags?: string[];
  sort?: StudySort;
};

export async function getStudies(opts: StudiesQuery = {}): Promise<Study[]> {
  const sb = publicClient();
  let q = sb.from("studies").select("*");

  if (opts.query && opts.query.trim()) {
    // websearch_to_tsquery via Supabase's textSearch helper
    q = q.textSearch("search_tsv", opts.query.trim(), { type: "websearch" });
  }
  if (opts.tags && opts.tags.length > 0) {
    q = q.contains("tags", opts.tags);
  }

  if (opts.sort === "upvotes") {
    // Order applied after join below.
    q = q.order("year", { ascending: false, nullsFirst: false });
  } else if (opts.sort === "year") {
    q = q.order("year", { ascending: false, nullsFirst: false });
  } else {
    q = q
      .order("featured", { ascending: false })
      .order("year", { ascending: false, nullsFirst: false });
  }

  const { data, error } = await q;
  if (error) throw error;
  let studies = (data ?? []) as Study[];

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

export async function getAllStudyTags(): Promise<{ value: string; count: number }[]> {
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
}

export async function getUpvoteCountMap(
  targetType: "channel" | "study",
  targetIds: string[],
): Promise<Map<string, number>> {
  if (targetIds.length === 0) return new Map();
  const sb = publicClient();
  const { data, error } = await sb
    .from("upvote_counts")
    .select("target_id, upvotes")
    .eq("target_type", targetType)
    .in("target_id", targetIds);
  if (error) throw error;
  return new Map(
    ((data ?? []) as { target_id: string; upvotes: number }[]).map((row) => [
      row.target_id,
      row.upvotes,
    ]),
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

export async function getFeaturedStudies(limit = 2): Promise<Study[]> {
  const sb = publicClient();
  const { data, error } = await sb
    .from("studies")
    .select("*")
    .eq("featured", true)
    .order("year", { ascending: false, nullsFirst: false })
    .limit(limit);
  if (error) throw error;
  return (data ?? []) as Study[];
}

export async function getStudyBySlug(slug: string): Promise<Study | null> {
  const sb = publicClient();
  const { data, error } = await sb
    .from("studies")
    .select("*")
    .eq("slug", slug)
    .maybeSingle();
  if (error) throw error;
  return (data as Study) ?? null;
}

export async function getSiteStats(): Promise<SiteStats | null> {
  const sb = publicClient();
  const { data, error } = await sb.from("site_stats").select("*").maybeSingle();
  if (error) throw error;
  return (data as SiteStats) ?? null;
}

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

export async function getRelatedStudies(
  studyId: string,
  tags: string[],
  limit = 4,
): Promise<Study[]> {
  if (!tags || tags.length === 0) return [];
  const sb = publicClient();
  const { data, error } = await sb
    .from("studies")
    .select("*")
    .neq("id", studyId)
    .overlaps("tags", tags);
  if (error) throw error;
  const others = (data ?? []) as Study[];
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

export async function getSearchIndex(): Promise<SearchItem[]> {
  const sb = publicClient();
  const [channelsRes, studiesRes, tagsRes] = await Promise.all([
    sb.from("channel_full").select("slug, name, channel_type").eq("is_active", true),
    sb.from("studies").select("slug, title, year, authors"),
    getAllStudyTags(),
  ]);
  if (channelsRes.error) throw channelsRes.error;
  if (studiesRes.error) throw studiesRes.error;

  const channels: SearchItem[] = (channelsRes.data ?? []).map(
    (c: { slug: string; name: string; channel_type: string | null }) => ({
      kind: "channel" as const,
      slug: c.slug,
      name: c.name,
      sub: c.channel_type,
    }),
  );
  const studies: SearchItem[] = (studiesRes.data ?? []).map(
    (s: { slug: string; title: string; year: number | null; authors: string[] | null }) => ({
      kind: "study" as const,
      slug: s.slug,
      name: s.title,
      sub: [s.year, (s.authors ?? [])[0]].filter(Boolean).join(" · ") || null,
    }),
  );
  const tags: SearchItem[] = tagsRes.map((t) => ({
    kind: "tag" as const,
    slug: t.value,
    name: t.value,
    sub: `${t.count} ${t.count === 1 ? "study" : "studies"}`,
  }));
  return [...channels, ...studies, ...tags];
}

export function pdfPublicUrl(pdfPath: string | null): string | null {
  if (!pdfPath) return null;
  const sb = publicClient();
  return sb.storage.from("studies").getPublicUrl(pdfPath).data.publicUrl;
}
