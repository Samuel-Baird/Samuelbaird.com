/**
 * Ingest influencer channel metadata from the March 2026 YouTube workbook.
 *
 * Usage: npx tsx scripts/ingest_influencers.ts
 */
import { config as loadEnv } from "dotenv";
loadEnv({ path: ".env.local" });

import { Client } from "pg";
import * as XLSX from "xlsx";

const XLSX_PATH =
  "C:\\Users\\b13ll\\Downloads\\Copy of LDS Influencer Spreadsheet.xlsx";
const SHEET_NAME = "March. 2026 YouTube (by Views)";
const USER_AGENT =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36";
const CONCURRENCY = 8;

type InfluencerRow = {
  rowNumber: number;
  channelType: string | null;
  channelName: string;
  city: string | null;
  state: string | null;
  ownedBy: string | null;
  totalViews: number;
  subscribers: number;
  videoCount: number;
  createdAt: Date | null;
  handle: string;
  handleSlug: string;
};

type ResolvedRow = InfluencerRow & {
  youtubeChannelId: string | null;
};

type ExistingChannel = {
  id: string;
  youtube_channel_id: string;
  slug: string;
};

function cleanString(value: unknown): string | null {
  const text = String(value ?? "").trim();
  return text.length > 0 ? text : null;
}

function parseNumber(value: unknown): number {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  const text = String(value ?? "").replace(/[^0-9.-]+/g, "");
  const parsed = Number(text);
  return Number.isFinite(parsed) ? parsed : 0;
}

function parseExcelDate(value: unknown): Date | null {
  if (value instanceof Date && !isNaN(value.getTime())) return value;
  if (typeof value === "number" && Number.isFinite(value)) {
    const date = new Date(Math.round((value - 25569) * 86400 * 1000));
    return isNaN(date.getTime()) ? null : date;
  }
  if (typeof value === "string" && value.trim()) {
    const date = new Date(value);
    return isNaN(date.getTime()) ? null : date;
  }
  return null;
}

function parseHandle(value: unknown): { handle: string; handleSlug: string } | null {
  const text = String(value ?? "").trim();
  const match = text.match(/@([^/?#\s]+)/);
  if (!match) return null;
  const handleSlug = match[1].trim();
  if (!handleSlug) return null;
  return { handle: `@${handleSlug}`, handleSlug };
}

function normalizeChannelType(value: unknown): string | null {
  const raw = cleanString(value);
  if (!raw) return null;
  return raw === "Anti-Church" ? "Critical" : raw;
}

function slugify(value: string): string {
  return value
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80)
    .replace(/-+$/g, "");
}

function uniqueSlug(baseValue: string, usedSlugs: Set<string>): string {
  const base = slugify(baseValue) || "channel";
  let candidate = base;
  let n = 2;
  while (usedSlugs.has(candidate)) {
    const suffix = `-${n++}`;
    candidate = `${base.slice(0, 80 - suffix.length).replace(/-+$/g, "")}${suffix}`;
  }
  usedSlugs.add(candidate);
  return candidate;
}

function readRows(): InfluencerRow[] {
  const wb = XLSX.readFile(XLSX_PATH, { cellDates: true });
  const sheet = wb.Sheets[SHEET_NAME];
  if (!sheet) throw new Error(`Missing sheet: ${SHEET_NAME}`);

  const rows = XLSX.utils.sheet_to_json<unknown[]>(sheet, {
    header: 1,
    raw: true,
    defval: null,
  });

  const dataRows = rows.slice(2);
  const influencers: InfluencerRow[] = [];

  for (const [index, row] of dataRows.entries()) {
    if (!row) continue;
    const channelName = cleanString(row[6]);
    const handleInfo = parseHandle(row[23]);
    if (!channelName || !handleInfo) continue;

    influencers.push({
      rowNumber: index + 3,
      channelType: normalizeChannelType(row[4]),
      channelName,
      city: cleanString(row[7]),
      state: cleanString(row[8]),
      ownedBy: cleanString(row[10]),
      totalViews: parseNumber(row[11]),
      subscribers: parseNumber(row[14]),
      videoCount: parseNumber(row[17]),
      createdAt: parseExcelDate(row[22]),
      handle: handleInfo.handle,
      handleSlug: handleInfo.handleSlug,
    });
  }

  return influencers;
}

function extractChannelId(html: string): string | null {
  const patterns = [
    /"channelId":"(UC[\w-]{20,})"/,
    /"externalId":"(UC[\w-]{20,})"/,
    /<link rel="canonical" href="https:\/\/www\.youtube\.com\/channel\/(UC[\w-]{20,})"/,
  ];
  for (const pattern of patterns) {
    const match = html.match(pattern);
    if (match) return match[1];
  }
  return null;
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function resolveHandle(row: InfluencerRow): Promise<ResolvedRow> {
  const url = `https://www.youtube.com/@${encodeURIComponent(row.handleSlug)}`;

  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      await sleep(Math.floor(Math.random() * 100));
      const response = await fetch(url, {
        headers: { "user-agent": USER_AGENT },
      });
      const body = await response.text();
      const youtubeChannelId = extractChannelId(body);
      if (!youtubeChannelId) {
        console.warn(
          `Row ${row.rowNumber}: unresolved handle ${row.handle} (${response.status})`,
        );
      }
      return { ...row, youtubeChannelId };
    } catch (error) {
      if (attempt === 1) {
        console.warn(
          `Row ${row.rowNumber}: network error resolving ${row.handle}:`,
          error,
        );
        return { ...row, youtubeChannelId: null };
      }
      await sleep(250);
    }
  }

  return { ...row, youtubeChannelId: null };
}

async function mapWithConcurrency<T, U>(
  values: T[],
  concurrency: number,
  fn: (value: T) => Promise<U>,
): Promise<U[]> {
  const results = new Array<U>(values.length);
  let nextIndex = 0;

  async function worker() {
    while (nextIndex < values.length) {
      const index = nextIndex++;
      results[index] = await fn(values[index]);
    }
  }

  await Promise.all(
    Array.from({ length: Math.min(concurrency, values.length) }, () => worker()),
  );
  return results;
}

async function main() {
  const ref = process.env.SUPABASE_PROJECT_REF;
  const password = process.env.SUPABASE_DB_PASSWORD;
  if (!ref || !password) {
    throw new Error(
      "Missing SUPABASE_PROJECT_REF or SUPABASE_DB_PASSWORD in .env.local",
    );
  }

  const rows = readRows();
  console.log(`Read ${rows.length} processable influencer rows.`);

  const resolved = await mapWithConcurrency(rows, CONCURRENCY, resolveHandle);
  const unresolved = resolved.filter((row) => !row.youtubeChannelId);
  const processable = resolved.filter(
    (row): row is ResolvedRow & { youtubeChannelId: string } =>
      Boolean(row.youtubeChannelId),
  );

  const pg = new Client({
    connectionString: `postgresql://postgres:${encodeURIComponent(
      password,
    )}@db.${ref}.supabase.co:5432/postgres`,
    ssl: { rejectUnauthorized: false },
  });
  await pg.connect();

  try {
    const existingResult = await pg.query<ExistingChannel>(
      `select id, youtube_channel_id, slug from public.channels;`,
    );
    const existingByYoutubeId = new Map(
      existingResult.rows.map((row) => [row.youtube_channel_id, row]),
    );
    const usedSlugs = new Set(existingResult.rows.map((row) => row.slug));

    let existingMatches = 0;
    let newlyInserted = 0;
    const typeHistogram = new Map<string, number>();

    for (const row of processable) {
      const existing = existingByYoutubeId.get(row.youtubeChannelId);
      const slug = existing?.slug ?? uniqueSlug(row.channelName, usedSlugs);
      if (existing) existingMatches++;
      else newlyInserted++;

      const typeKey = row.channelType ?? "(none)";
      typeHistogram.set(typeKey, (typeHistogram.get(typeKey) ?? 0) + 1);

      const result = await pg.query<{ id: string; slug: string }>(
        `
        insert into public.channels (
          youtube_channel_id,
          name,
          slug,
          channel_type,
          city,
          state,
          owned_by,
          handle,
          created_at_youtube
        )
        values ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        on conflict (youtube_channel_id) do update
          set name = excluded.name,
              channel_type = excluded.channel_type,
              city = excluded.city,
              state = excluded.state,
              owned_by = excluded.owned_by,
              handle = excluded.handle,
              created_at_youtube = coalesce(
                excluded.created_at_youtube,
                public.channels.created_at_youtube
              )
        returning id, slug;
        `,
        [
          row.youtubeChannelId,
          row.channelName,
          slug,
          row.channelType,
          row.city,
          row.state,
          row.ownedBy,
          row.handle,
          row.createdAt,
        ],
      );

      const channelDbId = result.rows[0].id;
      existingByYoutubeId.set(row.youtubeChannelId, {
        id: channelDbId,
        youtube_channel_id: row.youtubeChannelId,
        slug: result.rows[0].slug,
      });

      await pg.query(
        `
        insert into public.channel_stats (
          channel_id,
          subscribers,
          total_views,
          video_count
        )
        values ($1, $2, $3, $4);
        `,
        [channelDbId, row.subscribers, row.totalViews, row.videoCount],
      );
    }

    await pg.query(`refresh materialized view public.channel_stats_latest;`);

    console.log("\nIngest summary");
    console.log(`Total rows processed: ${rows.length}`);
    console.log(`Channels upserted: ${processable.length}`);
    console.log(`  matched existing UC: ${existingMatches}`);
    console.log(`  newly inserted: ${newlyInserted}`);
    console.log(`Unresolved handles: ${unresolved.length}`);
    console.log("Types histogram:");
    for (const [type, count] of [...typeHistogram.entries()].sort()) {
      console.log(`  ${type}: ${count}`);
    }
  } finally {
    await pg.end();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
