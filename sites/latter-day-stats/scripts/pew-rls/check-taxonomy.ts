/**
 * Checks the site's religion picker against Pew's own codebook: every
 * substantive FAMILY category should appear exactly once in
 * RELIGION_OPTIONS, and nothing should claim a code Pew doesn't have.
 *
 * The taxonomy was transcribed by hand from the codebook, so this is the
 * thing that says the transcription is still right - run it after touching
 * either side.
 *
 *   npx tsx scripts/pew-rls/check-taxonomy.ts
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import {
  RELIGION_OPTIONS,
  RELIGION_OPTIONS_BY_GROUP,
} from "../../src/lib/evangelical-quiz/demographics";

type Codebook = {
  variables: { variable: string; values?: { value: string; label: string }[] }[];
};

/** Pew's "no information on religious affiliation" back-code, not a religion. */
const FAMILY_NONRESPONSE = 999;

const codebookPath = join(
  process.cwd(),
  "docs/datasets/pew-rls-2023-24/codebook.json",
);
const codebook = JSON.parse(readFileSync(codebookPath, "utf8")) as Codebook;

const family = codebook.variables.find((v) => v.variable === "FAMILY");
if (!family?.values) throw new Error("FAMILY not found in codebook.json");

const pewCodes = new Set(
  family.values.map((v) => Number(v.value)).filter((n) => n !== FAMILY_NONRESPONSE),
);
const pewLabel = new Map(family.values.map((v) => [Number(v.value), v.label]));

const problems: string[] = [];

// Every option's code exists in Pew, and no two options share one.
const seen = new Map<number, string>();
for (const option of RELIGION_OPTIONS) {
  if (option.rlsFamily === null) continue;
  if (!pewCodes.has(option.rlsFamily)) {
    problems.push(`${option.slug}: FAMILY ${option.rlsFamily} is not in the codebook`);
  }
  const already = seen.get(option.rlsFamily);
  if (already) {
    problems.push(`FAMILY ${option.rlsFamily} claimed by both ${already} and ${option.slug}`);
  }
  seen.set(option.rlsFamily, option.slug);
}

// Nothing in Pew's list is missing from ours.
for (const code of [...pewCodes].sort((a, b) => a - b)) {
  if (!seen.has(code)) {
    problems.push(`FAMILY ${code} (${pewLabel.get(code)}) has no option`);
  }
}

// Slugs are the stored identifier; a duplicate would silently merge answers.
const slugs = new Set<string>();
for (const option of RELIGION_OPTIONS) {
  if (slugs.has(option.slug)) problems.push(`duplicate slug: ${option.slug}`);
  slugs.add(option.slug);
}

// The picker must be able to show every non-retired option.
const pickable = RELIGION_OPTIONS.filter((o) => !o.retired).length;
const grouped = RELIGION_OPTIONS_BY_GROUP.reduce((n, g) => n + g.options.length, 0);
if (pickable !== grouped) {
  problems.push(`${pickable} pickable options but ${grouped} reachable through a group`);
}

if (problems.length > 0) {
  console.error(`✗ ${problems.length} problem(s):`);
  for (const p of problems) console.error(`  - ${p}`);
  process.exit(1);
}

console.log(
  `✓ ${seen.size}/${pewCodes.size} FAMILY categories mapped, ` +
    `${pickable} pickable options, no duplicates.`,
);
