/**
 * Emits the re-read worklist: every quote, with each question its categories
 * put to it and the bands that question offers.
 *
 * This is a re-read rather than a relabel. The previous model ran one
 * affirms/hedges/denies axis across every question, which could not express a
 * four-valued answer and — worse — treated the Father's divinity and his
 * mortality as one claim. Nothing recorded under it can be mechanically
 * translated, so every answer is assigned from the excerpt again.
 *
 *   node scripts/stance-worklist.mjs <out-dir> [batches]
 */
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const QUESTIONS = {
  divinity: {
    question: "Was the Father always God?",
    guidance:
      "Not the mortality question. On this tradition's own terms Jehovah was God before and during his mortal life, so mortality language alone answers nothing here — only language about becoming, attaining, or always having been God does.",
    triggers: ["FATHER-BECAME-GOD", "FATHER-ALWAYS-GOD", "BACKWARD-AGNOSTIC"],
    bands: [
      ["not-always-god", "Asserts a change into godhood — attained, became, was exalted to, progressed to being God — or that there was a time he was not God."],
      ["declines", "Raises his origin or history and withholds, or is deliberately poised between attainment and eternal divinity."],
      ["always-god", "Asserts the Father has always been God: no beginning to his divinity, no attainment."],
    ],
  },
  regress: {
    question: "How many Gods stand above the Father?",
    guidance:
      "An unquantified chain is INDEFINITE, never infinite. Promoting it is the most tempting error here — an unbounded-sounding phrase is not a claim about infinity.",
    triggers: ["BACKWARD-EXPLICIT", "INFINITE-CHAIN", "BACKWARD-AGNOSTIC"],
    bands: [
      ["infinite", "An explicitly endless or numberless succession of Gods above the Father."],
      ["indefinite", "A chain above the Father with no stated terminus and no stated count — the default reading of an unqualified 'his Father had a Father'."],
      ["finite", "A bounded chain: a stated count, or a named terminus above the Father."],
      ["most-high", "Asserts nothing stands above the Father; he is the terminus."],
      ["declines", "Raises the question and withholds."],
    ],
  },
  mortality: {
    question: "Did the Father pass through a mortal life?",
    guidance:
      "Separate from the divinity question. The second band is for the pattern this tradition already accepts in Christ: mortal while never ceasing to be God.",
    triggers: ["FATHER-MORTAL-EXPERIENCE"],
    bands: [
      ["probation", "A mortality like ours: tested, subject to law, able to fall. A probation, not merely an incarnation."],
      ["already-divine", "Lived a mortal life while already God — the Jehovah pattern. Incarnation without loss of divinity, or explicit comparison to Christ's mortality."],
      ["declines", "Raises his mortality and withholds its character."],
      ["denies", "Asserts the Father never was mortal."],
    ],
  },
  increase: {
    question: "Do the exalted become parents of spirit children?",
    guidance:
      "The distinction that matters is whether a mechanism is stated. Promising posterity without saying how is its own position.",
    triggers: [
      "FORWARD-EXPLICIT",
      "FORWARD-EUPHEMISM",
      "SPIRIT-BIRTH-VIVIPAROUS",
      "SPIRIT-BIRTH-ADOPTION",
    ],
    bands: [
      ["literal-begetting", "Spirit children are begotten and born of heavenly parents. Procreation stated, not implied."],
      ["mechanism-unstated", "Affirms eternal increase, posterity, or continuation of seed while withholding how it happens."],
      ["organized-not-begotten", "Spirits are organized, adopted, or fashioned from pre-existing intelligence — explicitly not begotten."],
      ["declines", "Raises the question and withholds."],
      ["denies", "Denies that exalted beings have spirit posterity at all."],
    ],
  },
  mother: {
    question: "What work does the Mother do?",
    guidance:
      "A role scale, not an existence scale. Her existence is barely contested here. A rebuke aimed at a practice — praying to her, the fitness of a hymn — caps her role and does not deny her. 'Heavenly parents' alone affirms parentage, not mechanism, and never reaches the top band.",
    triggers: ["HEAVENLY-MOTHER"],
    bands: [
      ["necessary-for-birth", "Required for spirit children to exist. Begetting is said to need a mother, or she is named as bearing spirit offspring."],
      ["parent-mechanism-unstated", "Parentage affirmed — we are her children, she is a parent alongside the Father — without asserting how."],
      ["present-role-unstated", "She exists, or is a consort or exalted wife, with no claim about parentage or generation."],
      ["role-capped", "Grants her, then restricts what follows: no speculation, no worship, no inference beyond what is given."],
      ["declines", "Raises her and withholds entirely."],
      ["denies", "Denies her, or denies the specific role proposed."],
    ],
  },
  progression: {
    question: "Does God still progress?",
    guidance:
      "The middle band is the interesting one: restricting progression to dominion while denying it in knowledge is a distinct position, and it is how the claim was retired rather than simply contradicted.",
    triggers: ["DIVINE-PROGRESSION"],
    bands: [
      ["knowledge", "God advances in knowledge, truth, or perfection. The strong claim."],
      ["dominion-only", "Restricts progression to glory, dominion, or kingdoms while denying growth in knowledge."],
      ["declines", "Raises it and withholds."],
      ["denies", "God possesses all knowledge and does not advance."],
    ],
  },
};

const outDir = process.argv[2];
const batches = Number(process.argv[3] ?? 12);
if (!outDir) {
  console.error("usage: node scripts/stance-worklist.mjs <out-dir> [batches]");
  process.exit(1);
}

const sources = JSON.parse(
  readFileSync(
    new URL("../src/app/eternal-increase-timeline/sources.json", import.meta.url),
    "utf8",
  ),
);

const units = [];
for (const entry of sources) {
  for (const quote of entry.quotes) {
    const asked = Object.entries(QUESTIONS)
      .filter(([, q]) => q.triggers.some((t) => quote.categories.includes(t)))
      .map(([id, q]) => ({
        id,
        question: q.question,
        guidance: q.guidance,
        bands: q.bands.map(([band, criteria]) => ({ band, criteria })),
      }));
    if (asked.length === 0) continue;
    units.push({
      quoteId: quote.quoteId,
      entryId: entry.id,
      date: entry.dateDisplay,
      speaker: entry.speaker,
      office: entry.office,
      referent: quote.referent ?? entry.referent,
      categories: quote.categories,
      excerpt: quote.excerpt,
      note: quote.note ?? "",
      asked,
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

chunks.forEach((chunk, i) =>
  writeFileSync(join(outDir, `batch-${i + 1}.json`), JSON.stringify(chunk, null, 1)),
);

const decisions = units.reduce((n, u) => n + u.asked.length, 0);
console.log(`${units.length} quotes, ${decisions} answers, ${batches} batches`);
chunks.forEach((c, i) =>
  console.log(
    `  batch-${i + 1}.json  ${String(c.length).padStart(3)} quotes  ${c.reduce((n, u) => n + u.asked.length, 0)} answers`,
  ),
);
