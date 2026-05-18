/**
 * One-off: tag a curated list of channels as channel_type='Apologetics'.
 * Idempotent — re-running is safe.
 */
import { config as loadEnv } from "dotenv";
loadEnv({ path: ".env.local" });
import { Client } from "pg";

const APOLOGETICS_NAMES = [
  "2 Converts",
  "Cwic Media",
  "FAIR - Faithful Answers, Informed Response",
  "I think, therefore I Sam",
  "Joseph Smith Foundation",
  "Keystone",
  "Latter-Day Clarity",
  "Saints Unscripted",
  "Stick of Joseph",
  "The Interpreter Foundation",
  "Unshaken",
  "Ward Radio",
  "Scripture Central",
];

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
    const { rows } = await pg.query<{ id: string; name: string; channel_type: string | null }>(
      `update public.channels
       set channel_type = 'Apologetics'
       where name = any($1::text[])
       returning id, name, channel_type;`,
      [APOLOGETICS_NAMES],
    );
    console.log(`Tagged ${rows.length} channels as Apologetics:`);
    for (const r of rows) console.log(`  - ${r.name}`);
  } finally {
    await pg.end();
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
