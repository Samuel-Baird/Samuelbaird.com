/**
 * Run all SQL files in supabase/migrations/ in alphabetical order against the
 * Supabase Postgres database. Connects via the direct connection string
 * built from SUPABASE_PROJECT_REF + SUPABASE_DB_PASSWORD in .env.local.
 *
 * Usage: npx tsx scripts/migrate.ts
 */
import { config as loadEnv } from "dotenv";
loadEnv({ path: ".env.local" });
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { Client } from "pg";

async function main() {
  const ref = process.env.SUPABASE_PROJECT_REF;
  const password = process.env.SUPABASE_DB_PASSWORD;
  if (!ref || !password) {
    throw new Error(
      "Missing SUPABASE_PROJECT_REF or SUPABASE_DB_PASSWORD in .env.local",
    );
  }

  // Connect via the Supavisor session-mode pooler (port 5432 — required for
  // DDL). The direct db.<ref>.supabase.co host is IPv6-only on free tier and
  // doesn't resolve on most networks.
  const host =
    process.env.SUPABASE_POOLER_HOST ?? "aws-1-us-east-1.pooler.supabase.com";
  const connectionString = `postgresql://postgres.${ref}:${encodeURIComponent(
    password,
  )}@${host}:5432/postgres`;

  const client = new Client({
    connectionString,
    ssl: { rejectUnauthorized: false },
  });

  await client.connect();
  console.log("Connected to Supabase Postgres.");

  await client.query(
    `create table if not exists public.schema_migrations (
       filename text primary key,
       applied_at timestamptz not null default now()
     );`,
  );
  const applied = new Set(
    (await client.query<{ filename: string }>("select filename from public.schema_migrations")).rows.map(
      (r) => r.filename,
    ),
  );

  const migrationsDir = join(process.cwd(), "supabase", "migrations");
  const files = readdirSync(migrationsDir)
    .filter((f) => f.endsWith(".sql"))
    .sort();

  for (const file of files) {
    if (applied.has(file)) {
      console.log(`• Skipping ${file} (already applied).`);
      continue;
    }
    const sql = readFileSync(join(migrationsDir, file), "utf8");
    console.log(`\n→ Running ${file}…`);
    await client.query("begin");
    try {
      await client.query(sql);
      await client.query(
        "insert into public.schema_migrations (filename) values ($1)",
        [file],
      );
      await client.query("commit");
      console.log(`  ✓ ${file} applied.`);
    } catch (e) {
      await client.query("rollback");
      throw e;
    }
  }

  await client.end();
  console.log("\nDone.");
}

main().catch((err) => {
  console.error("\nMigration failed:", err);
  process.exit(1);
});
