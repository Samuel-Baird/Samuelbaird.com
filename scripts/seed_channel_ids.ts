/**
 * Seed `channels` metadata rows from channel_ids.txt.
 *
 * After running this, trigger /api/cron/refresh-stats (or the admin "Refresh
 * stats now" button) to populate channel_youtube + an initial channel_stats
 * row for each ID. Per-channel user metadata (state, owned_by, socials, etc.)
 * is filled in the Supabase dashboard or via /admin/channels.
 *
 * Usage: npx tsx scripts/seed_channel_ids.ts
 */
import { config as loadEnv } from "dotenv";
loadEnv({ path: ".env.local" });

import { readFileSync } from "node:fs";
import { Client } from "pg";

function readIds(): string[] {
  const text = readFileSync("channel_ids.txt", "utf8");
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("#"));
}

async function main() {
  const ref = process.env.SUPABASE_PROJECT_REF!;
  const password = process.env.SUPABASE_DB_PASSWORD!;
  if (!ref || !password) {
    throw new Error("SUPABASE_PROJECT_REF and SUPABASE_DB_PASSWORD must be set in .env.local");
  }

  const ids = readIds();
  if (ids.length === 0) {
    console.log("No channel IDs in channel_ids.txt — nothing to seed.");
    return;
  }

  const pg = new Client({
    connectionString: `postgresql://postgres:${encodeURIComponent(
      password,
    )}@db.${ref}.supabase.co:5432/postgres`,
    ssl: { rejectUnauthorized: false },
  });
  await pg.connect();

  try {
    let inserted = 0;
    let skipped = 0;
    for (const id of ids) {
      const { rowCount } = await pg.query(
        `insert into public.channels (youtube_channel_id, slug, is_active)
         values ($1, $1, true)
         on conflict (youtube_channel_id) do nothing;`,
        [id],
      );
      if (rowCount && rowCount > 0) inserted++;
      else skipped++;
    }
    console.log(`\nDone. Inserted ${inserted}, already present ${skipped}.`);
    console.log("Next: hit /api/cron/refresh-stats to pull YouTube data and stats.");
  } finally {
    await pg.end();
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
