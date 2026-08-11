/**
 * Proves the band integrity checks actually fail the build.
 *
 * A guard nobody has watched fail is a guess. This corrupts an in-memory copy
 * of sources.json four ways — one per check — and asserts each is caught and
 * names the offending path. The file on disk is never touched.
 *
 *   node --experimental-strip-types scripts/stance-check-drill.mjs
 */
import { parseSources, questionsFor } from "../src/app/eternal-increase-timeline/schema.ts";
import raw from "../src/app/eternal-increase-timeline/sources.json" with { type: "json" };

const clone = () => JSON.parse(JSON.stringify(raw));

/** The first quote that answers at least one question. */
function firstAnswering(data) {
  for (const entry of data)
    for (const quote of entry.quotes)
      if (quote.bands && Object.keys(quote.bands).length > 0)
        return { entry, quote };
  throw new Error("no quote with bands — has the re-read been applied?");
}

const cases = [
  {
    name: "answering a question the categories never raise",
    corrupt: (d) => {
      const { quote } = firstAnswering(d);
      // Pick a question this quote is definitely not asked.
      const asked = new Set(questionsFor(quote.categories));
      const spare = ["mother", "progression", "regress", "increase"].find(
        (q) => !asked.has(q),
      );
      quote.bands[spare] = "declines";
    },
    expect: /answers questions that its categories never raise/,
  },
  {
    name: "a band the question does not define",
    corrupt: (d) => {
      const { quote } = firstAnswering(d);
      const q = Object.keys(quote.bands)[0];
      // Legal on the regress scale, meaningless everywhere else.
      quote.bands[q] = q === "regress" ? "literal-begetting" : "infinite";
    },
    expect: /uses band values that the question does not define/,
  },
  {
    name: "a raised question left unanswered",
    corrupt: (d) => {
      const { quote } = firstAnswering(d);
      delete quote.bands[Object.keys(quote.bands)[0]];
    },
    expect: /raise a question they never answer/,
  },
  {
    name: "a review flag with nothing to review",
    corrupt: (d) => {
      for (const entry of d)
        for (const quote of entry.quotes)
          if (questionsFor(quote.categories).length === 0) {
            quote.stanceNeedsReview = true;
            return;
          }
      throw new Error("no unasked quote to flag");
    },
    expect: /flags quotes for review that answer nothing/,
  },
];

let failures = 0;
for (const c of cases) {
  const data = clone();
  c.corrupt(data);
  let caught = null;
  try {
    parseSources(data);
  } catch (e) {
    caught = e.message;
  }
  if (!caught) {
    console.log(`✗ ${c.name}\n    NOT CAUGHT — the build would have accepted this`);
    failures++;
  } else if (!c.expect.test(caught)) {
    console.log(`✗ ${c.name}\n    caught, but by the wrong check: ${caught.split("\n")[0]}`);
    failures++;
  } else {
    console.log(`✓ ${c.name}\n    ${caught.split("\n")[1]?.trim() ?? caught.split("\n")[0]}`);
  }
}

try {
  parseSources(raw);
  console.log("✓ sources.json as committed passes every check");
} catch (e) {
  console.log(`✗ sources.json as committed FAILS: ${e.message.split("\n")[0]}`);
  failures++;
}

process.exit(failures === 0 ? 0 : 1);
