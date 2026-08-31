/**
 * Prints a one-time SQL seed marking every graphic currently in the code
 * registries (DATASETS in src/lib/data-explorer.ts, STUDY_GRAPHICS in
 * src/lib/study-graphics.ts) as published = true in graphic_posts. Run once
 * against production right after migration 0051_graphic_published.sql lands,
 * so the new publish gate doesn't hide anything that was already live.
 *
 * Read-only - this only imports the registries and prints SQL; it does not
 * touch the database itself. Run with `npx tsx scripts/print-published-seed.ts
 * > seed.sql`, inspect seed.sql, then execute it (e.g. via the Supabase MCP's
 * execute_sql).
 */
import { DATASETS, graphicId } from "../src/lib/data-explorer";
import { STUDY_GRAPHICS } from "../src/lib/study-graphics";

function sqlString(s: string): string {
  return `'${s.replace(/'/g, "''")}'`;
}

const rows: { slug: string; id: string }[] = [];

for (const d of DATASETS) {
  for (const g of d.graphics) rows.push({ slug: d.slug, id: graphicId(g) });
}
for (const e of STUDY_GRAPHICS) {
  for (const g of e.graphics) rows.push({ slug: e.studySlug, id: graphicId(g) });
}

if (rows.length === 0) {
  throw new Error("No graphics found in the registries - refusing to print an empty seed.");
}

const values = rows
  .map((r) => `  (${sqlString(r.slug)}, ${sqlString(r.id)}, true)`)
  .join(",\n");

console.log(
  `-- One-time seed: ${rows.length} graphics from the code registries, marked published.\n` +
    `insert into public.graphic_posts (dataset_slug, graphic_id, published)\n` +
    `values\n${values}\n` +
    `on conflict (dataset_slug, graphic_id) do update set published = true, updated_at = now();\n`,
);
