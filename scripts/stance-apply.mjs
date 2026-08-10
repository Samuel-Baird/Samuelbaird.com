/**
 * Merges reviewed stance calls back into sources.json.
 *
 * Deliberately incurious: it writes what the review files say and nothing
 * else. It never guesses a stance, never fills a gap from the category's usual
 * meaning, and refuses the whole run if the reviews and the corpus disagree
 * about which calls were needed — a partial merge would leave the file in a
 * state the build rejects for reasons that no longer point at the cause.
 *
 *   node scripts/stance-apply.mjs <result-dir>
 */
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const STANCES = new Set(["affirms", "hedges", "denies"]);
const STANCE_CATEGORIES = new Set([
  "BACKWARD-EXPLICIT",
  "FATHER-MORTAL-EXPERIENCE",
  "FATHER-BECAME-GOD",
  "INFINITE-CHAIN",
  "FATHER-ALWAYS-GOD",
  "BACKWARD-AGNOSTIC",
  "FORWARD-EXPLICIT",
  "FORWARD-EUPHEMISM",
  "SPIRIT-BIRTH-VIVIPAROUS",
  "SPIRIT-BIRTH-ADOPTION",
  "HEAVENLY-MOTHER",
  "DIVINE-PROGRESSION",
]);

const resultDir = process.argv[2];
if (!resultDir) {
  console.error("usage: node scripts/stance-apply.mjs <result-dir>");
  process.exit(1);
}

const sourcesPath = fileURLToPath(
  new URL("../src/app/eternal-increase-timeline/sources.json", import.meta.url),
);
const sources = JSON.parse(readFileSync(sourcesPath, "utf8"));

const reviews = new Map();
const duplicates = [];
for (const file of readdirSync(resultDir).filter((f) => /^result-\d+\.json$/.test(f))) {
  for (const row of JSON.parse(readFileSync(join(resultDir, file), "utf8"))) {
    if (reviews.has(row.quoteId)) duplicates.push(row.quoteId);
    reviews.set(row.quoteId, row);
  }
}

const problems = [];
let applied = 0;
let flagged = 0;

for (const entry of sources) {
  for (const quote of entry.quotes) {
    const needed = quote.categories.filter((c) => STANCE_CATEGORIES.has(c));
    const review = reviews.get(quote.quoteId);

    if (needed.length === 0) {
      if (review) problems.push(`${quote.quoteId}: reviewed but needs no stance`);
      continue;
    }
    if (!review) {
      problems.push(`${quote.quoteId}: needs ${needed.length} stance call(s), no review found`);
      continue;
    }

    const given = Object.keys(review.stance ?? {});
    const missing = needed.filter((c) => !given.includes(c));
    const extra = given.filter((c) => !needed.includes(c));
    const bad = Object.entries(review.stance ?? {}).filter(([, v]) => !STANCES.has(v));
    if (missing.length) problems.push(`${quote.quoteId}: missing stance for ${missing.join(", ")}`);
    if (extra.length) problems.push(`${quote.quoteId}: stance for uncarried category ${extra.join(", ")}`);
    if (bad.length) problems.push(`${quote.quoteId}: invalid value ${bad.map(([k, v]) => `${k}=${v}`).join(", ")}`);
    if (missing.length || extra.length || bad.length) continue;

    // Key order follows the quote's own categories so the diff stays readable.
    quote.stance = Object.fromEntries(needed.map((c) => [c, review.stance[c]]));
    applied += needed.length;
    if (review.confidence === "low") {
      quote.stanceNeedsReview = true;
      flagged++;
    } else {
      delete quote.stanceNeedsReview;
    }
  }
}

if (duplicates.length) {
  problems.unshift(`duplicate reviews across batches: ${[...new Set(duplicates)].join(", ")}`);
}

if (problems.length) {
  console.error(`refusing to write — ${problems.length} problem(s):`);
  for (const p of problems.slice(0, 25)) console.error("  " + p);
  if (problems.length > 25) console.error(`  ...and ${problems.length - 25} more`);
  process.exit(1);
}

writeFileSync(sourcesPath, JSON.stringify(sources, null, 2) + "\n");

const tally = { affirms: 0, hedges: 0, denies: 0 };
for (const e of sources)
  for (const q of e.quotes)
    for (const v of Object.values(q.stance ?? {})) tally[v]++;

console.log(`applied ${applied} stance calls across ${reviews.size} quotes`);
console.log(`  affirms ${tally.affirms}  hedges ${tally.hedges}  denies ${tally.denies}`);
console.log(`  flagged for review: ${flagged} quotes`);
