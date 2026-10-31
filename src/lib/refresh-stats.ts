import "server-only";

import { revalidatePath, revalidateTag } from "next/cache";
import type { SupabaseClient } from "@supabase/supabase-js";
import { fetchYouTubeSnapshotsWithRetry } from "@/lib/youtube";
import { logEvent } from "@/lib/log";

export type RefreshSummary = {
  total: number;
  synced: number;
  missing: number;
  failed: number;
  errors: string[];
  timestamp: string;
};

// Shared by the daily cron route and the admin "refresh now" action. Fetches
// YouTube stats for all (active) channels, applies them in two batched writes,
// records per-channel sync status, refreshes the channel_stats_latest
// materialized view, and invalidates the cached public reads so the new
// numbers show up without waiting out the cache TTL.
export async function runStatsRefresh(
  supabase: SupabaseClient,
  { activeOnly = true }: { activeOnly?: boolean } = {},
): Promise<RefreshSummary> {
  let query = supabase
    .from("channels")
    .select("id, youtube_channel_id")
    .not("youtube_channel_id", "is", null);
  if (activeOnly) query = query.eq("is_active", true);
  const { data: channels, error } = await query;
  if (error) throw error;

  const rows = (channels ?? []) as { id: string; youtube_channel_id: string }[];
  const ytIds = rows.map((c) => c.youtube_channel_id);
  const byYtId = new Map(rows.map((c) => [c.youtube_channel_id, c.id]));
  const now = new Date().toISOString();
  const errors: string[] = [];

  const { snapshots, failedIds } = await fetchYouTubeSnapshotsWithRetry(ytIds);
  const matched = snapshots.filter((s) => byYtId.has(s.id));

  // Full overwrite of every YouTube-derived field, as two batched writes
  // instead of two round trips per channel.
  const ytRows = matched.map((s) => ({
    channel_id: byYtId.get(s.id)!,
    name: s.name,
    description: s.description,
    country: s.country,
    default_language: s.defaultLanguage,
    thumbnail_url: s.thumbnailUrl,
    created_at_youtube: s.publishedAt,
    last_synced_at: now,
    last_sync_status: "ok",
    last_sync_error: null,
  }));
  const statsRows = matched.map((s) => ({
    channel_id: byYtId.get(s.id)!,
    subscribers: s.subscribers,
    total_views: s.totalViews,
    video_count: s.videoCount,
  }));

  let synced = 0;
  let failed = 0;
  if (ytRows.length > 0) {
    const { error: ytError } = await supabase
      .from("channel_youtube")
      .upsert(ytRows, { onConflict: "channel_id" });
    if (ytError) {
      failed += ytRows.length;
      errors.push(`channel_youtube upsert: ${ytError.message}`);
    } else {
      const { error: statsError } = await supabase
        .from("channel_stats")
        .insert(statsRows);
      if (statsError) {
        failed += statsRows.length;
        errors.push(`channel_stats insert: ${statsError.message}`);
      } else {
        synced = matched.length;
      }
    }
  }

  // Channels whose YouTube batch failed outright — record the error so it
  // surfaces in admin diagnostics.
  const failedIdSet = new Set(failedIds);
  const errorRows = rows
    .filter((r) => failedIdSet.has(r.youtube_channel_id))
    .map((r) => ({
      channel_id: r.id,
      last_synced_at: now,
      last_sync_status: "error",
      last_sync_error: "YouTube API request failed after retries",
    }));

  // Channels we asked about but YouTube did not return — mark as missing.
  // Do NOT delete the metadata row.
  const seenYtIds = new Set(snapshots.map((s) => s.id));
  const missingRows = rows
    .filter(
      (r) =>
        !seenYtIds.has(r.youtube_channel_id) &&
        !failedIdSet.has(r.youtube_channel_id),
    )
    .map((r) => ({
      channel_id: r.id,
      last_synced_at: now,
      last_sync_status: "missing",
      last_sync_error: `YouTube returned no data for ${r.youtube_channel_id}`,
    }));

  for (const statusRows of [errorRows, missingRows]) {
    if (statusRows.length === 0) continue;
    const { error: statusError } = await supabase
      .from("channel_youtube")
      .upsert(statusRows, { onConflict: "channel_id" });
    if (statusError) errors.push(`sync-status upsert: ${statusError.message}`);
  }
  failed += errorRows.length;

  const { error: refreshError } = await supabase.rpc(
    "refresh_channel_stats_latest",
  );
  if (refreshError) {
    errors.push(`refresh_channel_stats_latest: ${refreshError.message}`);
  }

  // Without this, cached reads serve the old numbers until the TTL expires.
  revalidateTag("channels", { expire: 0 });
  revalidatePath("/");
  revalidatePath("/channels");

  const summary: RefreshSummary = {
    total: ytIds.length,
    synced,
    missing: missingRows.length,
    failed,
    errors,
    timestamp: now,
  };
  logEvent("refresh_stats", { ...summary }, failed > 0 ? "error" : "info");
  return summary;
}
