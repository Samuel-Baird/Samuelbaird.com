import { NextRequest, NextResponse } from "next/server";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { fetchYouTubeSnapshots } from "@/lib/youtube";

export const maxDuration = 300;

export async function GET(req: NextRequest) {
  const authHeader = req.headers.get("authorization");
  const cronSecret = process.env.CRON_SECRET;
  if (cronSecret && authHeader !== `Bearer ${cronSecret}`) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const supabase = createSupabaseServiceClient();

  const { data: channels, error } = await supabase
    .from("channels")
    .select("id, youtube_channel_id")
    .eq("is_active", true)
    .not("youtube_channel_id", "is", null);
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  const rows = (channels ?? []) as { id: string; youtube_channel_id: string }[];
  const ytIds = rows.map((c) => c.youtube_channel_id);
  const byYtId = new Map(rows.map((c) => [c.youtube_channel_id, c.id]));

  const snapshots = await fetchYouTubeSnapshots(ytIds);
  const seenYtIds = new Set(snapshots.map((s) => s.id));
  const now = new Date().toISOString();

  let synced = 0;
  let missing = 0;
  let failed = 0;

  // Full overwrite of every YouTube-derived field for every channel YouTube returned.
  for (const snapshot of snapshots) {
    const channelId = byYtId.get(snapshot.id);
    if (!channelId) continue;

    const { error: ytError } = await supabase
      .from("channel_youtube")
      .upsert(
        {
          channel_id: channelId,
          name: snapshot.name,
          description: snapshot.description,
          country: snapshot.country,
          default_language: snapshot.defaultLanguage,
          thumbnail_url: snapshot.thumbnailUrl,
          created_at_youtube: snapshot.publishedAt,
          last_synced_at: now,
          last_sync_status: "ok",
          last_sync_error: null,
        },
        { onConflict: "channel_id" },
      );
    if (ytError) {
      failed++;
      continue;
    }

    const { error: statsError } = await supabase.from("channel_stats").insert({
      channel_id: channelId,
      subscribers: snapshot.subscribers,
      total_views: snapshot.totalViews,
      video_count: snapshot.videoCount,
    });
    if (statsError) {
      failed++;
      continue;
    }

    synced++;
  }

  // Channels we asked about but YouTube did not return — mark as missing so it
  // surfaces in admin diagnostics. Do NOT delete the metadata row.
  for (const row of rows) {
    if (seenYtIds.has(row.youtube_channel_id)) continue;
    await supabase.from("channel_youtube").upsert(
      {
        channel_id: row.id,
        last_synced_at: now,
        last_sync_status: "missing",
        last_sync_error: `YouTube returned no data for ${row.youtube_channel_id}`,
      },
      { onConflict: "channel_id" },
    );
    missing++;
  }

  await supabase.rpc("refresh_channel_stats_latest");

  return NextResponse.json({
    ok: true,
    synced,
    missing,
    failed,
    total: ytIds.length,
    timestamp: now,
  });
}
