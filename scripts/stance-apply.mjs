/**
 * Merges the re-read back into sources.json.
 *
 * Deliberately incurious: it writes what the review files say and nothing
 * else. It never guesses a band, never fills a gap from what a category
 * usually means, and refuses the whole run if the reviews and the corpus
 * disagree about which questions were asked — a partial merge would leave the
 * file failing the build for reasons that no longer point at the cause.
 *
 *   node scripts/stance-apply.mjs <result-dir>
 */
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const NOT_ADDRESSED = "not-addressed";

const TRIGGERS = {
  divinity: ["FATHER-BECAME-GOD", "FATHER-ALWAYS-GOD", "BACKWARD-AGNOSTIC"],
  regress: ["BACKWARD-EXPLICIT", "INFINITE-CHAIN", "BACKWARD-AGNOSTIC"],
  mortality: ["FATHER-MORTAL-EXPERIENCE"],
  increase: [
    "FORWARD-EXPLICIT",
    "FORWARD-EUPHEMISM",
    "SPIRIT-BIRTH-VIVIPAROUS",
    "SPIRIT-BIRTH-ADOPTION",
  ],
  mother: ["HEAVENLY-MOTHER"],
  progression: ["DIVINE-PROGRESSION"],
};

const BANDS = {
  divinity: ["not-always-god", "declines", "always-god"],
  regress: ["infinite", "indefinite", "finite", "most-high", "declines"],
  mortality: ["probation", "already-divine", "declines", "denies"],
  increase: [
    "literal-begetting",
    "mechanism-unstated",
    "organized-not-begotten",
    "declines",
    "denies",
  ],
  mother: [
    "necessary-for-birth",
    "parent-mechanism-unstated",
    "present-role-unstated",
    "role-capped",
    "declines",
    "denies",
  ],
  progression: ["knowledge", "dominion-only", "declines", "denies"],
};

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
let notAddressed = 0;

for (const entry of sources) {
  for (const quote of entry.quotes) {
    const asked = Object.keys(TRIGGERS).filter((q) =>
      TRIGGERS[q].some((t) => quote.categories.includes(t)),
    );
    const review = reviews.get(quote.quoteId);

    if (asked.length === 0) {
      if (review) problems.push(`${quote.quoteId}: reviewed but asked nothing`);
      // The previous model's field is gone; strip any leftovers.
      delete quote.stance;
      delete quote.bands;
      delete quote.stanceNeedsReview;
      continue;
    }
    if (!review) {
      problems.push(`${quote.quoteId}: asked ${asked.length} question(s), no review found`);
      continue;
    }

    const given = Object.keys(review.bands ?? {});
    const missing = asked.filter((q) => !given.includes(q));
    const extra = given.filter((q) => !asked.includes(q));
    const bad = Object.entries(review.bands ?? {}).filter(
      ([q, b]) => asked.includes(q) && b !== NOT_ADDRESSED && !BANDS[q]?.includes(b),
    );
    if (missing.length) problems.push(`${quote.quoteId}: no answer for ${missing.join(", ")}`);
    if (extra.length) problems.push(`${quote.quoteId}: answered unasked ${extra.join(", ")}`);
    if (bad.length)
      problems.push(
        `${quote.quoteId}: invalid band ${bad.map(([q, b]) => `${q}=${b}`).join(", ")}`,
      );
    if (missing.length || extra.length || bad.length) continue;

    delete quote.stance;
    quote.bands = Object.fromEntries(asked.map((q) => [q, review.bands[q]]));
    applied += asked.length;
    notAddressed += asked.filter((q) => review.bands[q] === NOT_ADDRESSED).length;
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

const tally = {};
for (const e of sources)
  for (const q of e.quotes)
    for (const [question, band] of Object.entries(q.bands ?? {})) {
      tally[question] ??= {};
      tally[question][band] = (tally[question][band] ?? 0) + 1;
    }

console.log(`applied ${applied} answers across ${reviews.size} quotes`);
console.log(`  answered "not-addressed": ${notAddressed}`);
console.log(`  flagged for review: ${flagged} quotes`);
for (const [question, bands] of Object.entries(tally)) {
  const parts = Object.entries(bands)
    .sort((a, b) => b[1] - a[1])
    .map(([b, n]) => `${b} ${n}`)
    .join(", ");
  console.log(`  ${question.padEnd(12)} ${parts}`);
}
