import { config as loadEnv } from "dotenv";
loadEnv({ path: ".env.local" });

import { Client } from "pg";

async function main() {
  const ref = process.env.SUPABASE_PROJECT_REF!;
  const password = process.env.SUPABASE_DB_PASSWORD!;
  const client = new Client({
    connectionString: `postgresql://postgres:${encodeURIComponent(
      password,
    )}@db.${ref}.supabase.co:5432/postgres`,
    ssl: { rejectUnauthorized: false },
  });
  await client.connect();
  const { rows } = await client.query(
    `select table_name from information_schema.tables where table_schema = 'public' order by table_name;`,
  );
  console.log("Tables in public:", rows.map((r) => r.table_name).join(", "));
  const buckets = await client.query(
    `select id, public from storage.buckets where id = 'studies';`,
  );
  console.log("Storage bucket:", buckets.rows);
  await client.end();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
