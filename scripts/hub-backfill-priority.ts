/**
 * Apologetics Hub — one-off: recompute priority_score for every already
 * -analyzed video using the current formula in hub-priority.ts. Needed
 * whenever that formula changes (e.g. the 2026-08-12 recency-multiplier
 * addition) since priority_score is stored, not a generated column.
 *
 * Usage:
 *   npx tsx scripts/hub-backfill-priority.ts        # apply
 *   npx tsx scripts/hub-backfill-priority.ts --dry-run
 */
import { config as loadEnv } from "dotenv";
loadEnv({ path: ".env.local" });

import { createClient } from "@supabase/supabase-js";
import { computePriorityScore } from "./hub-priority";

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

async function main() {
  const dryRun = process.argv.includes("--dry-run");
  const supabase = supabaseClient();

  const { data, error } = await supabase
    .from("hub_videos")
    .select("id, title, published_at, view_count, expected_views, debunkability, priority_score")
    .not("debunkability", "is", null);
  if (error) throw error;

  const rows = data ?? [];
  console.log(`${rows.length} analyzed video(s) to recompute.\n`);

  let changed = 0;
  for (const row of rows) {
    const next = computePriorityScore({
      viewCount: row.view_count,
      expectedViews: row.expected_views,
      debunkability: row.debunkability,
      publishedAt: row.published_at,
    });
    const prev = row.priority_score as number | null;
    if (prev === next) continue;
    changed++;
    console.log(`${row.title.slice(0, 60).padEnd(60)}  ${prev ?? "—"} → ${next ?? "—"}`);
    if (!dryRun) {
      const { error: updateError } = await supabase
        .from("hub_videos")
        .update({ priority_score: next })
        .eq("id", row.id);
      if (updateError) throw updateError;
    }
  }

  console.log(`\n${changed} row(s) ${dryRun ? "would change" : "updated"}.`);
}

main().catch((err) => {
  console.error("\nFailed:", err);
  process.exit(1);
});
