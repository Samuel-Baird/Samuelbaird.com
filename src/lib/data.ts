import "server-only";
import { createClient } from "@supabase/supabase-js";
import type { Channel, ChannelWithStats, SiteStats, Study } from "./types";

// Read-only public client (anon key). RLS allows select on all public tables.
function publicClient() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { auth: { autoRefreshToken: false, persistSession: false } },
  );
}

export async function getChannelsWithLatest(): Promise<ChannelWithStats[]> {
  const sb = publicClient();
  const { data: channels, error } = await sb
    .from("channels")
    .select("*")
    .eq("is_active", true);
  if (error) throw error;

  const { data: stats, error: sErr } = await sb
    .from("channel_stats_latest")
    .select("*");
  if (sErr) throw sErr;

  const byId = new Map(stats!.map((s) => [s.channel_id, s]));
  return (channels as Channel[]).map((c) => ({
    ...c,
    latest: byId.get(c.id) ?? null,
  }));
}

export async function getChannelBySlug(
  slug: string,
): Promise<ChannelWithStats | null> {
  const sb = publicClient();
  const { data, error } = await sb
    .from("channels")
    .select("*")
    .eq("slug", slug)
    .maybeSingle();
  if (error) throw error;
  if (!data) return null;
  const { data: latest } = await sb
    .from("channel_stats_latest")
    .select("*")
    .eq("channel_id", data.id)
    .maybeSingle();
  return { ...(data as Channel), latest: latest ?? null };
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

export async function getStudies(): Promise<Study[]> {
  const sb = publicClient();
  const { data, error } = await sb
    .from("studies")
    .select("*")
    .order("featured", { ascending: false })
    .order("year", { ascending: false, nullsFirst: false });
  if (error) throw error;
  return (data ?? []) as Study[];
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

export function pdfPublicUrl(pdfPath: string | null): string | null {
  if (!pdfPath) return null;
  const sb = publicClient();
  return sb.storage.from("studies").getPublicUrl(pdfPath).data.publicUrl;
}
