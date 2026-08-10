const USER_AGENT =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36";

export type YtChannelSnapshot = {
  id: string;
  name: string;
  description: string | null;
  country: string | null;
  defaultLanguage: string | null;
  publishedAt: string | null;
  thumbnailUrl: string | null;
  subscribers: number;
  totalViews: number;
  videoCount: number;
};

export async function resolveHandleToChannelId(
  handleSlug: string,
): Promise<string | null> {
  const response = await fetch(
    `https://www.youtube.com/@${encodeURIComponent(handleSlug)}`,
    { headers: { "user-agent": USER_AGENT } },
  );
  const body = await response.text();
  const patterns = [
    /"channelId":"(UC[\w-]{20,})"/,
    /"externalId":"(UC[\w-]{20,})"/,
    /<link rel="canonical" href="https:\/\/www\.youtube\.com\/channel\/(UC[\w-]{20,})"/,
  ];

  for (const pattern of patterns) {
    const match = body.match(pattern);
    if (match) return match[1];
  }

  return null;
}

export function parseHandleInput(
  raw: string,
):
  | { kind: "handle"; handleSlug: string; handle: string }
  | { kind: "id"; id: string }
  | null {
  const text = raw.trim();
  if (!text) return null;

  const idMatch = text.match(/^(UC[\w-]{20,})$/);
  if (idMatch) return { kind: "id", id: idMatch[1] };

  const handleMatch = text.match(/(?:youtube\.com\/)?@([^/?#\s]+)/i);
  if (!handleMatch) return null;

  const handleSlug = handleMatch[1].trim();
  if (!handleSlug) return null;
  return { kind: "handle", handleSlug, handle: `@${handleSlug}` };
}

async function fetchSnapshotBatch(
  ids: string[],
  key: string,
): Promise<YtChannelSnapshot[]> {
  const url = new URL("https://www.googleapis.com/youtube/v3/channels");
  url.searchParams.set("part", "snippet,statistics");
  url.searchParams.set("id", ids.join(","));
  url.searchParams.set("key", key);

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`YouTube API request failed: ${response.status}`);
  }

  const json = (await response.json()) as {
    items?: Array<{
      id: string;
      snippet?: {
        title?: string;
        description?: string;
        country?: string;
        defaultLanguage?: string;
        publishedAt?: string;
        thumbnails?: { high?: { url?: string }; default?: { url?: string } };
      };
      statistics?: {
        subscriberCount?: string;
        viewCount?: string;
        videoCount?: string;
      };
    }>;
  };

  return (json.items ?? []).map((item) => ({
    id: item.id,
    name: item.snippet?.title ?? item.id,
    description: item.snippet?.description ?? null,
    country: item.snippet?.country ?? null,
    defaultLanguage: item.snippet?.defaultLanguage ?? null,
    publishedAt: item.snippet?.publishedAt ?? null,
    thumbnailUrl:
      item.snippet?.thumbnails?.high?.url ??
      item.snippet?.thumbnails?.default?.url ??
      null,
    subscribers: Number(item.statistics?.subscriberCount ?? 0),
    totalViews: Number(item.statistics?.viewCount ?? 0),
    videoCount: Number(item.statistics?.videoCount ?? 0),
  }));
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

// Each 50-id batch is retried independently; a batch that still fails after
// retries reports its ids in failedIds instead of sinking the whole run.
export async function fetchYouTubeSnapshotsWithRetry(
  channelIds: string[],
): Promise<{ snapshots: YtChannelSnapshot[]; failedIds: string[] }> {
  const key = process.env.YOUTUBE_API_KEY;
  if (!key) throw new Error("Missing YOUTUBE_API_KEY");

  const snapshots: YtChannelSnapshot[] = [];
  const failedIds: string[] = [];
  const backoffsMs = [1_000, 4_000];

  for (let i = 0; i < channelIds.length; i += 50) {
    const ids = channelIds.slice(i, i + 50);
    if (ids.length === 0) continue;

    for (let attempt = 0; ; attempt++) {
      try {
        snapshots.push(...(await fetchSnapshotBatch(ids, key)));
        break;
      } catch (err) {
        if (attempt >= backoffsMs.length) {
          failedIds.push(...ids);
          console.error(
            `YouTube batch failed after ${attempt + 1} attempts:`,
            err,
          );
          break;
        }
        await sleep(backoffsMs[attempt]);
      }
    }
  }

  return { snapshots, failedIds };
}

export async function fetchYouTubeSnapshots(
  channelIds: string[],
): Promise<YtChannelSnapshot[]> {
  const { snapshots, failedIds } =
    await fetchYouTubeSnapshotsWithRetry(channelIds);
  if (failedIds.length > 0) {
    throw new Error(
      `YouTube API request failed for ${failedIds.length} channel(s).`,
    );
  }
  return snapshots;
}

export function slugifyName(name: string): string {
  return name
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80)
    .replace(/-+$/g, "");
}
