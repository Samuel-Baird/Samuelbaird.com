import { z } from "zod";

export const CATEGORY_IDS = [
  "BACKWARD-EXPLICIT",
  "FATHER-MORTAL-EXPERIENCE",
  "FATHER-BECAME-GOD",
  "FATHER-ALWAYS-GOD",
  "BACKWARD-AGNOSTIC",
  "FORWARD-EXPLICIT",
  "FORWARD-EUPHEMISM",
  "SPIRIT-BIRTH-VIVIPAROUS",
  "SPIRIT-BIRTH-ADOPTION",
  "TRIPARTITE-FRAMEWORK",
  "MANY-WORLDS",
  "HEAVENLY-MOTHER",
  "INFINITE-CHAIN",
  "DIVINE-PROGRESSION",
  "RETREAT-REFRAME",
] as const;

export const HEARSAY_GRADES = ["A", "B", "C", "D", "E"] as const;

export const CORRELATION_STATUSES = [
  "current-correlated",
  "historical-official",
  "discontinued",
  "never-official",
] as const;

export const REFERENTS = ["father", "son", "ambiguous", "n/a"] as const;

export const SOURCE_TYPES = ["original", "citation"] as const;

export const STANCES = ["affirms", "hedges", "denies"] as const;

/**
 * Categories that carry a stance. The excluded three are deliberate:
 * RETREAT-REFRAME describes an operation performed on an earlier teaching
 * rather than a position on it, and MANY-WORLDS and TRIPARTITE-FRAMEWORK are
 * explanatory frameworks — "affirming" a framework says nothing about how
 * settled a doctrine was, which is the only thing the stance chart measures.
 */
export const STANCE_CATEGORY_IDS = [
  "BACKWARD-EXPLICIT",
  "FATHER-MORTAL-EXPERIENCE",
  "FATHER-BECAME-GOD",
  "FATHER-ALWAYS-GOD",
  "BACKWARD-AGNOSTIC",
  "INFINITE-CHAIN",
  "FORWARD-EXPLICIT",
  "FORWARD-EUPHEMISM",
  "SPIRIT-BIRTH-VIVIPAROUS",
  "SPIRIT-BIRTH-ADOPTION",
  "HEAVENLY-MOTHER",
  "DIVINE-PROGRESSION",
] as const satisfies readonly (typeof CATEGORY_IDS)[number][];

export type StanceCategoryId = (typeof STANCE_CATEGORY_IDS)[number];

export const SUBJECT_IDS = [
  "father-origin",
  "father-mortality",
  "infinite-chain",
  "eternal-increase",
  "spirit-birth",
  "heavenly-mother",
  "divine-progression",
] as const;

export type SubjectId = (typeof SUBJECT_IDS)[number];

/**
 * The subject whose proposition a category's stance was judged against.
 *
 * Subjects may share a category — the broad "was the Father once mortal"
 * question and the narrow "did he live a mortality" one both read
 * FATHER-MORTAL-EXPERIENCE — but only one of them defines what the recorded
 * direction *means*. That one is here, and it is the proposition shown to
 * whoever assigns a stance. A subject may only borrow a category when its own
 * question reads the same direction the same way; where it would not, the
 * category needs its own stance field, not a second interpretation of this one.
 */
export const DEFINING_SUBJECT: Record<StanceCategoryId, SubjectId> = {
  "BACKWARD-EXPLICIT": "father-origin",
  "FATHER-MORTAL-EXPERIENCE": "father-origin",
  "FATHER-BECAME-GOD": "father-origin",
  "FATHER-ALWAYS-GOD": "father-origin",
  "BACKWARD-AGNOSTIC": "father-origin",
  "INFINITE-CHAIN": "father-origin",
  "FORWARD-EXPLICIT": "eternal-increase",
  "FORWARD-EUPHEMISM": "eternal-increase",
  "SPIRIT-BIRTH-VIVIPAROUS": "eternal-increase",
  "SPIRIT-BIRTH-ADOPTION": "eternal-increase",
  "HEAVENLY-MOTHER": "heavenly-mother",
  "DIVINE-PROGRESSION": "divine-progression",
};

const STANCE_CATEGORY_SET: ReadonlySet<string> = new Set(STANCE_CATEGORY_IDS);

export function isStanceCategory(id: string): id is StanceCategoryId {
  return STANCE_CATEGORY_SET.has(id);
}

const witnessSchema = z.object({
  scribe: z.string().min(1),
  url: z.url().optional(),
  note: z.string().optional(),
});

const quoteSchema = z.object({
  quoteId: z.string().min(1),
  // May be empty: some quotes are recorded as context for a neighbouring
  // claim rather than as evidence for a category of their own.
  categories: z.array(z.enum(CATEGORY_IDS)),
  excerpt: z.string().min(1),
  // Per-quote override of the source-level referent. Backward-direction
  // quotes should always carry one.
  referent: z.enum(REFERENTS).optional(),
  // True when the categories are read into the quote rather than stated by
  // it — rendered as an "implied" marker on the pills.
  implied: z.boolean().optional(),
  // Where this quote stands on the proposition behind each of its
  // stance-bearing categories: does it teach the thing, gesture at it without
  // committing, or reject it? The direction used to live only in prose, which
  // meant the corpus could not be asked the one question it exists to answer —
  // how settled a teaching was at a given moment. Required for every
  // stance-bearing category on the quote; see parseSources.
  //
  // Keyed loosely, like hearsayByQuote above: a record over the category enum
  // demands *every* category as a key, and the checks in parseSources pin the
  // keys down far better than the enum could anyway — they require each one to
  // be a category this particular quote actually carries.
  stance: z.record(z.string(), z.enum(STANCES)).optional(),
  // Set by the backfill when the reading was not clear-cut. Rendered, never
  // hidden: dropping unreviewed quotes would bias the bands in exactly the
  // direction the completeness check exists to prevent.
  stanceNeedsReview: z.boolean().optional(),
  note: z.string().optional(),
});

const sourceEntrySchema = z
  .object({
    id: z.string().min(1),
    sourceType: z.enum(SOURCE_TYPES),
    // Originals this source quotes or teaches from. Required for citations.
    citesId: z.array(z.string().min(1)).optional(),
    date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "date must be YYYY-MM-DD"),
    dateDisplay: z.string().min(1),
    datePrecision: z.enum(["day", "month", "year"]),
    title: z.string().min(1),
    speaker: z.string().min(1),
    office: z.string().min(1),
    venue: z.string().min(1),
    url: z.url(),
    hearsay: z.enum(HEARSAY_GRADES),
    // Per-quote hearsay override, for sources whose quotes do not share a
    // single provenance (e.g. Snow's couplet: the 1840 origin story is a late
    // recollection, the couplet as published doctrine is first-person).
    hearsayByQuote: z.record(z.string(), z.enum(HEARSAY_GRADES)).optional(),
    correlationStatus: z.enum(CORRELATION_STATUSES),
    referent: z.enum(REFERENTS),
    witnesses: z.array(witnessSchema).optional(),
    quotes: z.array(quoteSchema).min(1),
    notes: z.string().min(1),
    needsVerification: z.boolean().optional(),
  })
  .refine((e) => e.sourceType === "original" || (e.citesId?.length ?? 0) > 0, {
    message: "a citation must name at least one original in citesId",
    path: ["citesId"],
  });

const sourcesSchema = z.array(sourceEntrySchema);

export type SourceEntry = z.infer<typeof sourceEntrySchema>;
export type Quote = z.infer<typeof quoteSchema>;
export type Witness = z.infer<typeof witnessSchema>;
export type CategoryId = (typeof CATEGORY_IDS)[number];
export type Stance = (typeof STANCES)[number];
export type HearsayGrade = (typeof HEARSAY_GRADES)[number];
export type CorrelationStatus = (typeof CORRELATION_STATUSES)[number];
export type Referent = (typeof REFERENTS)[number];
export type SourceType = (typeof SOURCE_TYPES)[number];

// Runs at module scope of a statically prerendered page, so a hand-edit typo
// in sources.json fails `next build` rather than surfacing at runtime.
export function parseSources(raw: unknown): SourceEntry[] {
  const result = sourcesSchema.safeParse(raw);
  if (!result.success) {
    throw new Error(
      `eternal-increase-timeline/sources.json is invalid:\n${z.prettifyError(result.error)}`,
    );
  }
  const entries = result.data;

  // Referential integrity: every citesId must resolve, or the citation graph
  // and the collapse-to-originals view silently lose edges.
  const ids = new Set(entries.map((e) => e.id));
  const dangling = entries.flatMap((e) =>
    (e.citesId ?? [])
      .filter((target) => !ids.has(target))
      .map((target) => `${e.id} -> ${target}`),
  );
  if (dangling.length > 0) {
    throw new Error(
      `eternal-increase-timeline/sources.json has unresolved citesId references:\n  ${dangling.join("\n  ")}`,
    );
  }

  const dupeIds = entries
    .map((e) => e.id)
    .filter((id, i, all) => all.indexOf(id) !== i);
  if (dupeIds.length > 0) {
    throw new Error(
      `eternal-increase-timeline/sources.json has duplicate ids: ${[...new Set(dupeIds)].join(", ")}`,
    );
  }

  const quoteIds = entries.flatMap((e) => e.quotes.map((q) => q.quoteId));
  const dupeQuotes = quoteIds.filter((id, i, all) => all.indexOf(id) !== i);
  if (dupeQuotes.length > 0) {
    throw new Error(
      `eternal-increase-timeline/sources.json has duplicate quoteIds: ${[...new Set(dupeQuotes)].join(", ")}`,
    );
  }

  // hearsayByQuote keys must name quotes that exist on the same entry.
  const strayOverrides = entries.flatMap((e) => {
    const own = new Set(e.quotes.map((q) => q.quoteId));
    return Object.keys(e.hearsayByQuote ?? {})
      .filter((k) => !own.has(k))
      .map((k) => `${e.id}.hearsayByQuote["${k}"]`);
  });
  if (strayOverrides.length > 0) {
    throw new Error(
      `eternal-increase-timeline/sources.json has hearsayByQuote keys with no matching quote:\n  ${strayOverrides.join("\n  ")}`,
    );
  }

  // Stance keys must name a category the quote actually carries, and one that
  // takes a stance at all. A stance recorded against a category the quote does
  // not hold is silently inert — the same failure the hearsayByQuote check
  // above exists to catch.
  const strayStance = entries.flatMap((e) =>
    e.quotes.flatMap((q) => {
      const own = new Set(q.categories);
      return Object.keys(q.stance ?? {})
        .filter((c) => !own.has(c as CategoryId) || !isStanceCategory(c))
        .map((c) => `${e.id}.${q.quoteId}.stance["${c}"]`);
    }),
  );
  if (strayStance.length > 0) {
    throw new Error(
      `eternal-increase-timeline/sources.json has stance keys that name a category the quote does not carry, or one that takes no stance:\n  ${strayStance.join("\n  ")}`,
    );
  }

  // Every stance-bearing category on a quote must state its direction. A
  // missing stance would not fail loudly — the quote would just vanish from
  // the certainty chart, quietly undercounting whichever band it belonged to.
  // That is the worst outcome available here, so it fails the build instead,
  // and a future author tagging a new quote gets told to state the direction.
  const missingStance = entries.flatMap((e) =>
    e.quotes.flatMap((q) =>
      q.categories
        .filter(isStanceCategory)
        .filter((c) => !q.stance?.[c])
        .map((c) => `${e.id}.${q.quoteId} is missing stance for ${c}`),
    ),
  );
  if (missingStance.length > 0) {
    throw new Error(
      `eternal-increase-timeline/sources.json has quotes tagged with a stance-bearing category but no stance:\n  ${missingStance.join("\n  ")}`,
    );
  }

  // A review flag with nothing to review is a leftover.
  const emptyFlags = entries.flatMap((e) =>
    e.quotes
      .filter((q) => q.stanceNeedsReview && !q.stance)
      .map((q) => `${e.id}.${q.quoteId}`),
  );
  if (emptyFlags.length > 0) {
    throw new Error(
      `eternal-increase-timeline/sources.json flags quotes for stance review that carry no stance:\n  ${emptyFlags.join("\n  ")}`,
    );
  }

  // mrm.org is a discovery aid only — see docs/timelines/SOURCING.md. It must
  // never be published as a citation, so a URL on that host fails the build.
  const disallowedHost = /^https?:\/\/([a-z0-9-]+\.)*mrm\.org(\/|$)/i;
  const banned = entries
    .filter((e) => disallowedHost.test(e.url))
    .map((e) => `${e.id} -> ${e.url}`);
  if (banned.length > 0) {
    throw new Error(
      `eternal-increase-timeline/sources.json cites a research-aid-only host that must not be published:\n  ${banned.join("\n  ")}`,
    );
  }

  return entries;
}
