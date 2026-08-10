/**
 * Proves the stance integrity checks actually fail the build.
 *
 * A guard nobody has watched fail is a guess. This corrupts an in-memory copy
 * of sources.json three ways — one per check — and asserts each is caught and
 * names the offending path. The file on disk is never touched.
 *
 *   node --experimental-strip-types scripts/stance-check-drill.mjs
 */
import { parseSources } from "../src/app/eternal-increase-timeline/schema.ts";
import raw from "../src/app/eternal-increase-timeline/sources.json" with { type: "json" };

const clone = () => JSON.parse(JSON.stringify(raw));

/** The first quote carrying at least one stance, wherever it happens to be. */
function firstStanced(data) {
  for (const entry of data)
    for (const quote of entry.quotes)
      if (quote.stance && Object.keys(quote.stance).length > 0)
        return { entry, quote };
  throw new Error("no stanced quote found — is the backfill applied?");
}

const cases = [
  {
    name: "stance key naming a category the quote does not carry",
    corrupt: (d) => {
      const { quote } = firstStanced(d);
      quote.stance["MANY-WORLDS"] = "affirms";
    },
    expect: /stance keys that name a category/,
  },
  {
    name: "stance-bearing category with no direction",
    corrupt: (d) => {
      const { quote } = firstStanced(d);
      delete quote.stance[Object.keys(quote.stance)[0]];
    },
    expect: /tagged with a stance-bearing category but no stance/,
  },
  {
    name: "review flag with nothing to review",
    corrupt: (d) => {
      // A quote with no categories at all, so it needs no stance.
      for (const entry of d)
        for (const quote of entry.quotes)
          if (quote.categories.length === 0) {
            quote.stanceNeedsReview = true;
            return;
          }
      throw new Error("no uncategorised quote to flag");
    },
    expect: /flags quotes for stance review that carry no stance/,
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

// And the real file must still pass.
try {
  parseSources(raw);
  console.log("✓ sources.json as committed passes every check");
} catch (e) {
  console.log(`✗ sources.json as committed FAILS: ${e.message.split("\n")[0]}`);
  failures++;
}

process.exit(failures === 0 ? 0 : 1);
