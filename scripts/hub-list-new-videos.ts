/**
 * Apologetics Hub — step 1: find new uploads from a tracked critical channel,
 * fetch their public stats, and compute a channel-baseline "expected views"
 * so the insert step can rank them.
 *
 * Talks to Supabase via the anon-URL + service-role key (createClient), not
 * the pg pooler — this repo's .env.local doesn't carry
 * SUPABASE_PROJECT_REF/SUPABASE_DB_PASSWORD (those are only needed for DDL
 * via scripts/migrate.ts), and plain reads/upserts don't need raw SQL.
 *
 * Usage:
 *   npx tsx scripts/hub-list-new-videos.ts --channel <slug-or-youtube-channel-id> [options]
 *
 * Options:
 *   --pages N          Pages of uploads to scan, 50 videos/page (default 2 = 100 videos)
 *   --out <file>       Write JSON to a file instead of stdout
 *   --refresh-stats    Update view_count on existing hub_videos rows for this channel
 *   --mark-removed     Flip hub_videos rows no longer returned by the API to video_status='removed'
 *
 * Output JSON is the input to scripts/hub-insert-analysis.ts after analysis.
 */
import { config as loadEnv } from "dotenv";
loadEnv({ path: ".env.local" });

import { writeFileSync } from "node:fs";
import { createClient } from "@supabase/supabase-js";

const USER_AGENT =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36";

type Args = {
  channel: string;
  pages: number;
  out?: string;
  refreshStats: boolean;
  markRemoved: boolean;
};

function parseArgs(): Args {
  const argv = process.argv.slice(2);
  const get = (flag: string) => {
    const i = argv.indexOf(flag);
    return i >= 0 ? argv[i + 1] : undefined;
  };
  const channel = get("--channel");
  if (!channel) {
    throw new Error(
      "Missing --channel <slug-or-youtube-channel-id>. Example: --channel UCx6OgmoqJbOVRq-Lv1P7SzA (Mormon Stories Podcast).",
    );
  }
  return {
    channel,
    pages: Number(get("--pages") ?? 2),
    out: get("--out"),
    refreshStats: argv.includes("--refresh-stats"),
    markRemoved: argv.includes("--mark-removed"),
  };
}

function supabaseClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) {
    throw new Error(
      "Missing NEXT_PUBLIC_SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env.local",
    );
  }
  return createClient(url, key, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}

function youtubeKey(): string {
  const key = process.env.YOUTUBE_API_KEY;
  if (!key) throw new Error("Missing YOUTUBE_API_KEY in .env.local");
  return key;
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function fetchJson<T>(url: string, attempt = 0): Promise<T> {
  const res = await fetch(url, { headers: { "user-agent": USER_AGENT } });
  if (!res.ok) {
    if (attempt < 2) {
      await sleep([1_000, 4_000][attempt]);
      return fetchJson<T>(url, attempt + 1);
    }
    const body = await res.text();
    throw new Error(`YouTube API ${res.status}: ${body.slice(0, 300)}`);
  }
  return res.json() as Promise<T>;
}

function parseIsoDuration(iso: string | undefined): number | null {
  if (!iso) return null;
  const m = iso.match(/^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$/);
  if (!m) return null;
  const [, h, min, s] = m;
  return (Number(h ?? 0) * 3600) + (Number(min ?? 0) * 60) + Number(s ?? 0);
}

function median(values: number[]): number | null {
  if (values.length === 0) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0
    ? (sorted[mid - 1] + sorted[mid]) / 2
    : sorted[mid];
}

type FetchedVideo = {
  youtube_video_id: string;
  title: string;
  published_at: string;
  duration_seconds: number | null;
  view_count: number;
  thumbnail_url: string | null;
};

async function fetchUploadsPlaylistId(
  youtubeChannelId: string,
  key: string,
): Promise<string> {
  const url = new URL("https://www.googleapis.com/youtube/v3/channels");
  url.searchParams.set("part", "contentDetails");
  url.searchParams.set("id", youtubeChannelId);
  url.searchParams.set("key", key);
  const data = await fetchJson<{
    items?: { contentDetails?: { relatedPlaylists?: { uploads?: string } } }[];
  }>(url.toString());
  const uploads = data.items?.[0]?.contentDetails?.relatedPlaylists?.uploads;
  if (!uploads) {
    throw new Error(
      `Could not resolve uploads playlist for channel ${youtubeChannelId} — is YOUTUBE_API_KEY restricted to only the channels endpoint?`,
    );
  }
  return uploads;
}

async function fetchUploadedVideoIds(
  uploadsPlaylistId: string,
  key: string,
  pages: number,
): Promise<string[]> {
  const ids: string[] = [];
  let pageToken: string | undefined;
  for (let page = 0; page < pages; page++) {
    const url = new URL("https://www.googleapis.com/youtube/v3/playlistItems");
    url.searchParams.set("part", "contentDetails");
    url.searchParams.set("maxResults", "50");
    url.searchParams.set("playlistId", uploadsPlaylistId);
    url.searchParams.set("key", key);
    if (pageToken) url.searchParams.set("pageToken", pageToken);
    const data = await fetchJson<{
      items?: { contentDetails?: { videoId?: string } }[];
      nextPageToken?: string;
    }>(url.toString());
    for (const item of data.items ?? []) {
      if (item.contentDetails?.videoId) ids.push(item.contentDetails.videoId);
    }
    if (!data.nextPageToken) break;
    pageToken = data.nextPageToken;
  }
  return ids;
}

function chunk<T>(arr: T[], size: number): T[][] {
  const out: T[][] = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}

async function fetchVideoDetails(
  ids: string[],
  key: string,
): Promise<FetchedVideo[]> {
  const out: FetchedVideo[] = [];
  for (const batch of chunk(ids, 50)) {
    const url = new URL("https://www.googleapis.com/youtube/v3/videos");
    url.searchParams.set("part", "snippet,statistics,contentDetails");
    url.searchParams.set("id", batch.join(","));
    url.searchParams.set("key", key);
    const data = await fetchJson<{
      items?: {
        id: string;
        snippet?: {
          title?: string;
          publishedAt?: string;
          thumbnails?: {
            high?: { url?: string };
            medium?: { url?: string };
            default?: { url?: string };
          };
        };
        statistics?: { viewCount?: string };
        contentDetails?: { duration?: string };
      }[];
    }>(url.toString());
    for (const item of data.items ?? []) {
      out.push({
        youtube_video_id: item.id,
        title: item.snippet?.title ?? item.id,
        published_at: item.snippet?.publishedAt ?? new Date().toISOString(),
        duration_seconds: parseIsoDuration(item.contentDetails?.duration),
        view_count: Number(item.statistics?.viewCount ?? 0),
        thumbnail_url:
          item.snippet?.thumbnails?.high?.url ??
          item.snippet?.thumbnails?.medium?.url ??
          item.snippet?.thumbnails?.default?.url ??
          null,
      });
    }
  }
  return out;
}

// Present-video ids from a fresh videos.list call, used to detect gone videos
// among the channel's already-ingested rows. Deleted and private videos both
// come back absent from `items` — the public API key can't tell them apart,
// so removed rows are flagged 'removed' and may need manual correction to
// 'private' if that's what actually happened.
async function fetchPresentIds(
  ids: string[],
  key: string,
): Promise<Map<string, { view_count: number }>> {
  const present = new Map<string, { view_count: number }>();
  for (const batch of chunk(ids, 50)) {
    const url = new URL("https://www.googleapis.com/youtube/v3/videos");
    url.searchParams.set("part", "statistics");
    url.searchParams.set("id", batch.join(","));
    url.searchParams.set("key", key);
    const data = await fetchJson<{
      items?: { id: string; statistics?: { viewCount?: string } }[];
    }>(url.toString());
    for (const item of data.items ?? []) {
      present.set(item.id, { view_count: Number(item.statistics?.viewCount ?? 0) });
    }
  }
  return present;
}

async function main() {
  const args = parseArgs();
  const key = youtubeKey();
  const supabase = supabaseClient();

  const { data: channel, error: channelError } = await supabase
    .from("channel_full")
    .select("id, youtube_channel_id, name, slug")
    .or(`slug.eq.${args.channel},youtube_channel_id.eq.${args.channel}`)
    .maybeSingle();
  if (channelError) throw channelError;
  if (!channel) {
    throw new Error(
      `No channel found matching --channel "${args.channel}" (checked slug and youtube_channel_id).`,
    );
  }

  console.log(`Channel: ${channel.name} (${channel.youtube_channel_id})`);

  const uploadsPlaylistId = await fetchUploadsPlaylistId(
    channel.youtube_channel_id,
    key,
  );
  const uploadedIds = await fetchUploadedVideoIds(
    uploadsPlaylistId,
    key,
    args.pages,
  );
  console.log(`Scanned ${uploadedIds.length} recent uploads (${args.pages} page(s)).`);

  const fetched = await fetchVideoDetails(uploadedIds, key);

  // Baseline: median view count of the 15 most recent qualifying uploads —
  // excludes shorts (<120s) and videos <14 days old (too fresh to have
  // stabilized), so a single skewed short or brand-new upload can't distort
  // "expected" for the video actually being ranked.
  const now = Date.now();
  const qualifying = fetched
    .filter((v) => (v.duration_seconds ?? 0) >= 120)
    .filter((v) => now - new Date(v.published_at).getTime() >= 14 * 86_400_000)
    .sort((a, b) => b.published_at.localeCompare(a.published_at))
    .slice(0, 15);
  const expectedViews = median(qualifying.map((v) => v.view_count));
  if (qualifying.length < 8) {
    console.warn(
      `⚠ Only ${qualifying.length} qualifying videos for the baseline (want ≥8) — expected_views is low-confidence. Consider --pages ${args.pages + 2} or override expected_views manually in the analysis JSON.`,
    );
  }
  console.log(
    `Baseline: expected_views=${expectedViews ?? "n/a"} from ${qualifying.length} qualifying uploads.`,
  );

  const { data: existingRows, error: existingError } = await supabase
    .from("hub_videos")
    .select("id, youtube_video_id, video_status")
    .eq("channel_id", channel.id);
  if (existingError) throw existingError;
  const existingIds = new Set((existingRows ?? []).map((r) => r.youtube_video_id));

  const newVideos = fetched
    .filter((v) => !existingIds.has(v.youtube_video_id))
    .map((v) => ({ ...v, expected_views: expectedViews }));
  console.log(`${newVideos.length} new video(s) not yet in hub_videos.`);

  let refreshedCount = 0;
  let removedCount = 0;
  if ((args.refreshStats || args.markRemoved) && existingRows && existingRows.length > 0) {
    const present = await fetchPresentIds(
      existingRows.map((r) => r.youtube_video_id),
      key,
    );
    for (const row of existingRows) {
      const live = present.get(row.youtube_video_id);
      if (live) {
        if (args.refreshStats) {
          const { error } = await supabase
            .from("hub_videos")
            .update({
              view_count: live.view_count,
              view_count_updated_at: new Date().toISOString(),
              ...(row.video_status !== "active" ? { video_status: "active" } : {}),
            })
            .eq("id", row.id);
          if (error) throw error;
          refreshedCount++;
        }
      } else if (args.markRemoved && row.video_status === "active") {
        const { error } = await supabase
          .from("hub_videos")
          .update({ video_status: "removed" })
          .eq("id", row.id);
        if (error) throw error;
        removedCount++;
      }
    }
    if (args.refreshStats) console.log(`Refreshed stats on ${refreshedCount} existing row(s).`);
    if (args.markRemoved) console.log(`Marked ${removedCount} row(s) removed.`);
  }

  const output = {
    channel: {
      id: channel.id,
      slug: channel.slug,
      youtube_channel_id: channel.youtube_channel_id,
      name: channel.name,
    },
    baseline: {
      expected_views: expectedViews,
      sample_size: qualifying.length,
      low_confidence: qualifying.length < 8,
    },
    newVideos,
  };

  const json = JSON.stringify(output, null, 2);
  if (args.out) {
    writeFileSync(args.out, json, "utf8");
    console.log(`Wrote ${args.out}`);
  } else {
    console.log("\n" + json);
  }
}

main().catch((err) => {
  console.error("\nFailed:", err);
  process.exit(1);
});
