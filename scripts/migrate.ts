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

  // Direct connection to the project DB.
  const connectionString = `postgresql://postgres:${encodeURIComponent(
    password,
  )}@db.${ref}.supabase.co:5432/postgres`;

  const client = new Client({
    connectionString,
    ssl: { rejectUnauthorized: false },
  });

  await client.connect();
  console.log("Connected to Supabase Postgres.");

  const migrationsDir = join(process.cwd(), "supabase", "migrations");
  const files = readdirSync(migrationsDir)
    .filter((f) => f.endsWith(".sql"))
    .sort();

  for (const file of files) {
    const sql = readFileSync(join(migrationsDir, file), "utf8");
    console.log(`\n→ Running ${file}…`);
    await client.query(sql);
    console.log(`  ✓ ${file} applied.`);
  }

  await client.end();
  console.log("\nDone.");
}

main().catch((err) => {
  console.error("\nMigration failed:", err);
  process.exit(1);
});
