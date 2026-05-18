/**
 * Enrich channel rows with YouTube Data API metadata: country, defaultLanguage,
 * description, thumbnail. Also records a fresh channel_stats row (subscribers,
 * total_views, video_count) so the latest view reflects current numbers rather
 * than the snapshot in the curated spreadsheets.
 *
 * Usage: npx tsx scripts/enrich_youtube.ts
 */
import { config as loadEnv } from "dotenv";
loadEnv({ path: ".env.local" });

import { Client } from "pg";

const YT_KEY = process.env.YOUTUBE_API_KEY!;
if (!YT_KEY) throw new Error("YOUTUBE_API_KEY missing in .env.local");

type YtChannel = {
  id: string;
  snippet?: {
    title?: string;
    description?: string;
    country?: string;
    defaultLanguage?: string;
    publishedAt?: string;
    thumbnails?: {
      high?: { url?: string };
      default?: { url?: string };
    };
  };
  statistics?: {
    subscriberCount?: string;
    viewCount?: string;
    videoCount?: string;
  };
};

async function fetchBatch(ids: string[]): Promise<YtChannel[]> {
  const url = new URL("https://www.googleapis.com/youtube/v3/channels");
  url.searchParams.set("part", "snippet,statistics");
  url.searchParams.set("id", ids.join(","));
  url.searchParams.set("maxResults", "50");
  url.searchParams.set("key", YT_KEY);
  const res = await fetch(url);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`YouTube API ${res.status}: ${body.slice(0, 300)}`);
  }
  const data = (await res.json()) as { items?: YtChannel[] };
  return data.items ?? [];
}

function chunk<T>(arr: T[], size: number): T[][] {
  const out: T[][] = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}

async function main() {
  const ref = process.env.SUPABASE_PROJECT_REF!;
  const password = process.env.SUPABASE_DB_PASSWORD!;
  const pg = new Client({
    connectionString: `postgresql://postgres:${encodeURIComponent(
      password,
    )}@db.${ref}.supabase.co:5432/postgres`,
    ssl: { rejectUnauthorized: false },
  });
  await pg.connect();

  try {
    const { rows } = await pg.query<{ id: string; youtube_channel_id: string }>(
      `select id, youtube_channel_id from public.channels;`,
    );
    console.log(`Enriching ${rows.length} channels…`);

    const idMap = new Map(rows.map((r) => [r.youtube_channel_id, r.id]));
    const allYtIds = rows.map((r) => r.youtube_channel_id);

    let enriched = 0;
    let missing = 0;
    let statsWritten = 0;

    for (const batch of chunk(allYtIds, 50)) {
      const items = await fetchBatch(batch);
      const seen = new Set(items.map((i) => i.id));

      for (const item of items) {
        const dbId = idMap.get(item.id);
        if (!dbId) continue;

        const s = item.snippet ?? {};
        const stats = item.statistics ?? {};
        const thumb = s.thumbnails?.high?.url ?? s.thumbnails?.default?.url ?? null;

        await pg.query(
          `
          update public.channels set
            description = coalesce($2, description),
            country = coalesce($3, country),
            language = coalesce($4, language),
            thumbnail_url = coalesce($5, thumbnail_url),
            created_at_youtube = coalesce(channels.created_at_youtube, $6)
          where id = $1;
          `,
          [
            dbId,
            s.description ?? null,
            s.country ?? null,
            s.defaultLanguage ?? null,
            thumb,
            s.publishedAt ?? null,
          ],
        );
        enriched++;

        const subs = Number(stats.subscriberCount ?? 0);
        const views = Number(stats.viewCount ?? 0);
        const vids = Number(stats.videoCount ?? 0);
        if (subs || views || vids) {
          await pg.query(
            `
            insert into public.channel_stats (channel_id, subscribers, total_views, video_count)
            values ($1, $2, $3, $4);
            `,
            [dbId, subs, views, vids],
          );
          statsWritten++;
        }
      }

      for (const id of batch) {
        if (!seen.has(id)) missing++;
      }
      process.stdout.write(`  enriched: ${enriched}, stats: ${statsWritten}, missing: ${missing}\r`);
    }

    await pg.query(`refresh materialized view public.channel_stats_latest;`);

    console.log("\n\nYouTube enrichment complete.");
    console.log(`  channels enriched: ${enriched}`);
    console.log(`  fresh stats rows: ${statsWritten}`);
    console.log(`  YouTube returned no data for: ${missing}`);
  } finally {
    await pg.end();
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
