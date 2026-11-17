/**
 * Seed Supabase with curated channels from the user's xlsx and the two
 * starter study PDFs.
 *
 * Usage: npx tsx scripts/seed.ts
 */
import { config as loadEnv } from "dotenv";
loadEnv({ path: ".env.local" });

import { readFileSync } from "node:fs";
import { basename } from "node:path";
import { Client } from "pg";
import { createClient } from "@supabase/supabase-js";
import * as XLSX from "xlsx";

const XLSX_PATH =
  "C:\\Users\\b13ll\\Downloads\\Latter-day Saint Apologetics Resource Sheet.xlsx";
const PDF_DIR =
  "C:\\Users\\b13ll\\Downloads\\drive-download-20260517T215647Z-3-001";

const STUDIES = [
  {
    file: "Mormons Are No Longer a Majority in Utah-Causes, Consequences, and Implications for the Sociology of Religion.pdf",
    slug: "mormons-no-longer-majority-utah",
    title:
      "Mormons Are No Longer a Majority in Utah: Causes, Consequences, and Implications for the Sociology of Religion",
    authors: ["Ryan T. Cragun", "Rick Phillips"],
    year: 2024,
    source: "Sociology of Religion (working paper)",
    abstract:
      "An empirical examination of the demographic shift in Utah, where members of The Church of Jesus Christ of Latter-day Saints no longer constitute a majority of the state's population. The paper explores the drivers of this transition (in-migration, declining birth rates, religious disaffiliation) and what it implies for the sociological study of Latter-day Saints and religion in the American West.",
    tags: ["demographics", "Utah", "sociology"],
    featured: true,
  },
  {
    file: "called to serve the prosocial behavior of active latter-day saints.pdf",
    slug: "called-to-serve-prosocial-behavior",
    title: "Called to Serve: The Prosocial Behavior of Active Latter-day Saints",
    authors: ["Ram A. Cnaan", "Van Evans", "Daniel W. Curtis"],
    year: 2012,
    source: "University of Pennsylvania School of Social Policy & Practice",
    abstract:
      "A landmark study quantifying the volunteer hours, charitable giving, and civic engagement of active members of The Church of Jesus Christ of Latter-day Saints. The authors find that practicing Latter-day Saints contribute substantially above national averages on multiple measures of prosocial behavior.",
    tags: ["service", "charity", "civic engagement"],
    featured: true,
  },
];

function slugify(s: string) {
  return s
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80);
}

type CuratedRow = {
  channelName: string;
  subscribers: number;
  totalViews: number;
  videoCount: number;
  createdAt: Date | null;
};

function readChannels(): {
  idByName: Map<string, string>;
  curated: CuratedRow[];
} {
  const wb = XLSX.readFile(XLSX_PATH);

  const tableSheet = wb.Sheets["Table"];
  const tableRows = XLSX.utils.sheet_to_json<Record<string, unknown>>(
    tableSheet,
    { defval: null },
  );
  const idByName = new Map<string, string>();
  for (const row of tableRows) {
    const cid = String(row["channelId"] ?? "").trim();
    const name = String(row["Channel name"] ?? "").trim();
    if (cid.startsWith("UC") && name) {
      idByName.set(name, cid);
    }
  }

  const subsSheet = wb.Sheets["Sorted by Subs high to low"];
  // Row 1 is the title, row 2 is the header — start data on row 3.
  const rawAoa = XLSX.utils.sheet_to_json<unknown[]>(subsSheet, {
    header: 1,
    raw: true,
  });
  const dataRows = rawAoa.slice(2);
  const curated: CuratedRow[] = [];
  for (const r of dataRows) {
    if (!r || !r[0]) continue;
    const channelName = String(r[0]).trim();
    if (!channelName) continue;
    const subscribers = Number(r[1] ?? 0);
    const totalViews = Number(r[2] ?? 0);
    const videoCount = Number(r[3] ?? 0);
    const createdRaw = r[5];
    let createdAt: Date | null = null;
    if (createdRaw instanceof Date) createdAt = createdRaw;
    else if (typeof createdRaw === "number") {
      // Excel serial date
      createdAt = new Date(Math.round((createdRaw - 25569) * 86400 * 1000));
    } else if (typeof createdRaw === "string" && createdRaw.length > 0) {
      const d = new Date(createdRaw);
      if (!isNaN(d.getTime())) createdAt = d;
    }
    curated.push({
      channelName,
      subscribers,
      totalViews,
      videoCount,
      createdAt,
    });
  }

  return { idByName, curated };
}

async function main() {
  const ref = process.env.SUPABASE_PROJECT_REF!;
  const password = process.env.SUPABASE_DB_PASSWORD!;
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;

  // pg client for SQL (channels/stats/refresh view)
  const pg = new Client({
    connectionString: `postgresql://postgres:${encodeURIComponent(
      password,
    )}@db.${ref}.supabase.co:5432/postgres`,
    ssl: { rejectUnauthorized: false },
  });
  await pg.connect();

  // supabase-js for Storage uploads
  const supabase = createClient(supabaseUrl, serviceKey, {
    auth: { autoRefreshToken: false, persistSession: false },
  });

  // -------- 1. Channels --------
  const { idByName, curated } = readChannels();
  console.log(`Read ${curated.length} curated rows, ${idByName.size} channelIds`);

  let matched = 0;
  const unmatched: string[] = [];
  const slugsUsed = new Set<string>();

  for (const row of curated) {
    const channelId = idByName.get(row.channelName);
    if (!channelId) {
      unmatched.push(row.channelName);
      continue;
    }
    matched++;

    let slug = slugify(row.channelName);
    if (!slug) slug = channelId.toLowerCase();
    let unique = slug;
    let n = 2;
    while (slugsUsed.has(unique)) unique = `${slug}-${n++}`;
    slugsUsed.add(unique);

    const { rows } = await pg.query(
      `
      insert into channels (youtube_channel_id, name, slug, created_at_youtube)
      values ($1, $2, $3, $4)
      on conflict (youtube_channel_id) do update
        set name = excluded.name,
            created_at_youtube = coalesce(excluded.created_at_youtube, channels.created_at_youtube)
      returning id;
      `,
      [channelId, row.channelName, unique, row.createdAt],
    );
    const channelDbId = rows[0].id as string;

    await pg.query(
      `
      insert into channel_stats (channel_id, subscribers, total_views, video_count)
      values ($1, $2, $3, $4);
      `,
      [channelDbId, row.subscribers, row.totalViews, row.videoCount],
    );
  }

  console.log(`Channels seeded: ${matched}`);
  if (unmatched.length) {
    console.log(`Unmatched names (no channelId): ${unmatched.length}`);
    unmatched.forEach((n) => console.log("  - " + n));
  }

  // Refresh materialized view
  await pg.query(`refresh materialized view channel_stats_latest;`);
  console.log("channel_stats_latest refreshed.");

  // -------- 2. Studies --------
  for (const study of STUDIES) {
    const localPath = `${PDF_DIR}\\${study.file}`;
    const buf = readFileSync(localPath);
    const storageKey = `${study.slug}/${basename(study.file).replace(
      /[^a-zA-Z0-9._-]+/g,
      "_",
    )}`;
    const { error: upErr } = await supabase.storage
      .from("studies")
      .upload(storageKey, buf, {
        contentType: "application/pdf",
        upsert: true,
      });
    if (upErr) {
      console.error(`Upload failed for ${study.slug}:`, upErr.message);
      continue;
    }

    await pg.query(
      `
      insert into studies
        (slug, title, authors, year, source, abstract, tags, pdf_path, featured)
      values
        ($1, $2, $3, $4, $5, $6, $7, $8, $9)
      on conflict (slug) do update set
        title = excluded.title,
        authors = excluded.authors,
        year = excluded.year,
        source = excluded.source,
        abstract = excluded.abstract,
        tags = excluded.tags,
        pdf_path = excluded.pdf_path,
        featured = excluded.featured;
      `,
      [
        study.slug,
        study.title,
        study.authors,
        study.year,
        study.source,
        study.abstract,
        study.tags,
        storageKey,
        study.featured,
      ],
    );
    console.log(`Study seeded: ${study.slug}`);
  }

  await pg.end();
  console.log("\nSeed complete.");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
