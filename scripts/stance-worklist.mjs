/**
 * Emits the stance backfill worklist: every (quote, stance-bearing category)
 * pair that needs a direction recorded, batched for parallel review.
 *
 * The corpus records *that* a quote touches a category but not *which way* it
 * leans, and the direction is what the certainty chart is built on. It lives
 * in each quote's prose note today, so this hands the reviewer the note and
 * the excerpt together with the proposition the direction is about.
 *
 *   node scripts/stance-worklist.mjs <out-dir> [batches]
 */
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const SUBJECTS = {
  "father-origin": {
    question: "Was the Father once a mortal man?",
    proposition:
      "God the Father passed through a mortality like ours and attained his exaltation, rather than having always been God.",
    categories: [
      "BACKWARD-EXPLICIT",
      "FATHER-MORTAL-EXPERIENCE",
      "FATHER-BECAME-GOD",
      "INFINITE-CHAIN",
      "FATHER-ALWAYS-GOD",
      "BACKWARD-AGNOSTIC",
    ],
  },
  "eternal-increase": {
    question: "Do the exalted become parents of spirit children?",
    proposition:
      "Exalted men and women beget spirit offspring and so continue the pattern by which we were made.",
    categories: [
      "FORWARD-EXPLICIT",
      "FORWARD-EUPHEMISM",
      "SPIRIT-BIRTH-VIVIPAROUS",
      "SPIRIT-BIRTH-ADOPTION",
    ],
  },
  "heavenly-mother": {
    question: "Is there a Mother in Heaven?",
    proposition: "A Heavenly Mother exists and is a parent of the human family.",
    categories: ["HEAVENLY-MOTHER"],
  },
  "divine-progression": {
    question: "Does God still progress?",
    proposition:
      "God continues to advance in knowledge or perfection, rather than possessing all of it already.",
    categories: ["DIVINE-PROGRESSION"],
  },
};

// What the tag usually means, offered to the reviewer as a starting point and
// never as an answer. A prior that survives the note is fine; a prior that
// overrides the note is the failure mode this whole exercise exists to avoid,
// so contradicting one is a reason to flag, not to reconsider the note.
const PRIORS = {
  "BACKWARD-EXPLICIT": "affirms",
  "FATHER-MORTAL-EXPERIENCE": "affirms",
  "FATHER-BECAME-GOD": "affirms",
  "INFINITE-CHAIN": "affirms",
  "FATHER-ALWAYS-GOD": "denies",
  "BACKWARD-AGNOSTIC": "hedges",
  "FORWARD-EXPLICIT": "affirms",
  "FORWARD-EUPHEMISM": "hedges",
  "SPIRIT-BIRTH-VIVIPAROUS": "affirms",
  "SPIRIT-BIRTH-ADOPTION": "read the note",
  "HEAVENLY-MOTHER": "read the note",
  "DIVINE-PROGRESSION": "read the note",
};

const SUBJECT_OF = Object.fromEntries(
  Object.entries(SUBJECTS).flatMap(([id, s]) =>
    s.categories.map((c) => [c, id]),
  ),
);

const outDir = process.argv[2];
const batches = Number(process.argv[3] ?? 6);
if (!outDir) {
  console.error("usage: node scripts/stance-worklist.mjs <out-dir> [batches]");
  process.exit(1);
}

const sources = JSON.parse(
  await import("node:fs/promises").then((fs) =>
    fs.readFile(
      new URL("../src/app/eternal-increase-timeline/sources.json", import.meta.url),
      "utf8",
    ),
  ),
);

const units = [];
for (const entry of sources) {
  for (const quote of entry.quotes) {
    const cats = quote.categories.filter((c) => c in SUBJECT_OF);
    if (cats.length === 0) continue;
    units.push({
      quoteId: quote.quoteId,
      entryId: entry.id,
      date: entry.dateDisplay,
      speaker: entry.speaker,
      office: entry.office,
      hearsay: entry.hearsay,
      correlationStatus: entry.correlationStatus,
      referent: quote.referent ?? entry.referent,
      implied: quote.implied ?? false,
      excerpt: quote.excerpt,
      note: quote.note ?? "",
      needed: cats.map((c) => ({
        category: c,
        subject: SUBJECT_OF[c],
        question: SUBJECTS[SUBJECT_OF[c]].question,
        proposition: SUBJECTS[SUBJECT_OF[c]].proposition,
        prior: PRIORS[c],
      })),
    });
  }
}

// Chronological, then dealt round-robin, so every batch spans the whole period
// rather than one reviewer seeing only Utah-era rhetoric and another only
// correlated curriculum. Consistency across the eras is the point.
units.sort((a, b) => a.entryId.localeCompare(b.entryId));
mkdirSync(outDir, { recursive: true });
const chunks = Array.from({ length: batches }, () => []);
units.forEach((u, i) => chunks[i % batches].push(u));

chunks.forEach((chunk, i) => {
  writeFileSync(
    join(outDir, `batch-${i + 1}.json`),
    JSON.stringify(chunk, null, 1),
  );
});

console.log(
  `${units.length} quotes, ${units.reduce((n, u) => n + u.needed.length, 0)} stance calls, ${batches} batches`,
);
chunks.forEach((c, i) =>
  console.log(
    `  batch-${i + 1}.json  ${String(c.length).padStart(3)} quotes  ${c.reduce((n, u) => n + u.needed.length, 0)} calls`,
  ),
);
