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

  const ytIds = (channels ?? []).map((c) => c.youtube_channel_id as string);
  const snapshots = await fetchYouTubeSnapshots(ytIds);
  const byYtId = new Map((channels ?? []).map((c) => [c.youtube_channel_id, c.id]));

  let inserted = 0;
  let failed = 0;

  for (const snapshot of snapshots) {
    const channelId = byYtId.get(snapshot.id);
    if (!channelId) continue;

    const { error: statsError } = await supabase.from("channel_stats").insert({
      channel_id: channelId,
      subscribers: snapshot.subscribers,
      total_views: snapshot.totalViews,
      video_count: snapshot.videoCount,
    });
    if (statsError) { failed++; continue; }

    const update: Record<string, string | null> = {};
    if (snapshot.name) update.name = snapshot.name;
    if (snapshot.thumbnailUrl) update.thumbnail_url = snapshot.thumbnailUrl;
    if (snapshot.country) update.country = snapshot.country;
    if (snapshot.defaultLanguage) update.language = snapshot.defaultLanguage;
    if (Object.keys(update).length > 0) {
      await supabase.from("channels").update(update).eq("id", channelId);
    }

    inserted++;
  }

  await supabase.rpc("refresh_channel_stats_latest");

  return NextResponse.json({
    ok: true,
    inserted,
    failed,
    total: ytIds.length,
    timestamp: new Date().toISOString(),
  });
}
