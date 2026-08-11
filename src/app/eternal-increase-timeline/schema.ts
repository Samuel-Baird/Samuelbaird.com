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

/**
 * The questions the corpus is asked, and the ordered answers each one takes.
 *
 * A question owns its own scale; a category only decides which questions a
 * quote is asked. That inversion is the point. The previous model ran one
 * affirms/hedges/denies axis across everything, which could not hold a
 * four-valued answer like the regress question, and — worse — welded divinity
 * and mortality into a single claim. They are independent: on this tradition's
 * own terms Jehovah was God before and during his mortal life, so "God once
 * was as man now is" asserts nothing at all about whether there was a time the
 * Father was not God. Only attainment language does that.
 *
 * See docs/timelines/STANCE-TAXONOMY.md for the criteria behind every band.
 */
export const QUESTION_IDS = [
  "divinity",
  "regress",
  "mortality",
  "increase",
  "mother",
  "progression",
] as const;

export type QuestionId = (typeof QUESTION_IDS)[number];

/**
 * Recorded when a quote carries a category that raises a question, but on
 * reading turns out not to speak to it — a mortality passage tagged for the
 * Father's origin that never touches his divinity, say. It is an answer, not a
 * gap: keeping it explicit is what lets the build insist every raised question
 * was actually decided, while still letting the honest answer be "this does
 * not address it". Never drawn.
 */
export const NOT_ADDRESSED = "not-addressed";

/**
 * Bands per question, in the order they are drawn — most committed first.
 *
 * `offScale` marks an answer that is not a rung on the ladder. Declining to
 * say sits genuinely between "not always God" and "always God", but it is not
 * between "infinite regress" and "no regress at all", and drawing it there
 * would invent a position nobody holds.
 */
export const QUESTION_BANDS = {
  divinity: [
    { id: "not-always-god" },
    { id: "declines" },
    { id: "always-god" },
  ],
  regress: [
    { id: "infinite" },
    { id: "indefinite" },
    { id: "finite" },
    { id: "most-high" },
    { id: "declines", offScale: true },
  ],
  mortality: [
    { id: "probation" },
    { id: "already-divine" },
    { id: "declines", offScale: true },
    { id: "denies" },
  ],
  increase: [
    { id: "literal-begetting" },
    { id: "mechanism-unstated" },
    { id: "organized-not-begotten" },
    { id: "declines", offScale: true },
    { id: "denies" },
  ],
  mother: [
    { id: "necessary-for-birth" },
    { id: "parent-mechanism-unstated" },
    { id: "present-role-unstated" },
    { id: "role-capped" },
    { id: "declines", offScale: true },
    { id: "denies" },
  ],
  progression: [
    { id: "knowledge" },
    { id: "dominion-only" },
    { id: "declines", offScale: true },
    { id: "denies" },
  ],
} as const satisfies Record<
  QuestionId,
  readonly { id: string; offScale?: boolean }[]
>;

export type BandId<Q extends QuestionId = QuestionId> =
  (typeof QUESTION_BANDS)[Q][number]["id"];

/**
 * Categories that raise each question. A quote is asked a question when it
 * carries one of these; what it answers is a separate matter entirely, and is
 * read off the excerpt rather than inferred from the tag.
 *
 * BACKWARD-AGNOSTIC raises both divinity and regress on purpose. Splitting it
 * would presume which of the two a source is declining to answer, and sources
 * that decline are rarely that tidy.
 */
export const QUESTION_TRIGGERS: Record<
  QuestionId,
  readonly (typeof CATEGORY_IDS)[number][]
> = {
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

/** Every question a quote's categories put to it. */
export function questionsFor(categories: readonly string[]): QuestionId[] {
  return QUESTION_IDS.filter((q) =>
    QUESTION_TRIGGERS[q].some((c) => categories.includes(c)),
  );
}

const BAND_IDS_BY_QUESTION = Object.fromEntries(
  QUESTION_IDS.map((q) => [
    q,
    new Set<string>([
      ...QUESTION_BANDS[q].map((b) => b.id as string),
      NOT_ADDRESSED,
    ]),
  ]),
) as unknown as Record<QuestionId, ReadonlySet<string>>;

export function isQuestionId(id: string): id is QuestionId {
  return (QUESTION_IDS as readonly string[]).includes(id);
}

export function isBandOf(question: QuestionId, band: string): boolean {
  return BAND_IDS_BY_QUESTION[question].has(band);
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
  // What this quote answers, for each question its categories put to it: one
  // band id per question, or NOT_ADDRESSED where the passage turns out not to
  // speak to it. Required for every question the quote raises; see
  // parseSources.
  //
  // Keyed loosely, like hearsayByQuote above — a record over the question enum
  // would demand every question as a key, and the checks in parseSources pin
  // both keys and values down far better than an enum could, because a legal
  // band depends on which question is being answered.
  bands: z.record(z.string(), z.string()).optional(),
  // Set by the re-read when the answer was not clear-cut. Rendered, never
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

  // An answer to a question the quote was never asked is silently inert — the
  // same failure the hearsayByQuote check above exists to catch.
  const strayBands = entries.flatMap((e) =>
    e.quotes.flatMap((q) => {
      const asked = new Set<string>(questionsFor(q.categories));
      return Object.keys(q.bands ?? {})
        .filter((k) => !isQuestionId(k) || !asked.has(k))
        .map((k) => `${e.id}.${q.quoteId}.bands["${k}"]`);
    }),
  );
  if (strayBands.length > 0) {
    throw new Error(
      `eternal-increase-timeline/sources.json answers questions that its categories never raise:\n  ${strayBands.join("\n  ")}`,
    );
  }

  // A band has to be one this question actually offers. Bands are only unique
  // within a question — "denies" means different things on different scales,
  // and "infinite" is meaningless on all but one — so a value that is legal
  // somewhere is not thereby legal here.
  const badBands = entries.flatMap((e) =>
    e.quotes.flatMap((q) =>
      Object.entries(q.bands ?? {})
        .filter(([k, v]) => isQuestionId(k) && !isBandOf(k, v))
        .map(([k, v]) => `${e.id}.${q.quoteId}.bands["${k}"] = "${v}"`),
    ),
  );
  if (badBands.length > 0) {
    throw new Error(
      `eternal-increase-timeline/sources.json uses band values that the question does not define:\n  ${badBands.join("\n  ")}`,
    );
  }

  // Every question a quote raises must be answered. A missing answer would not
  // fail loudly — the quote would just vanish from that chart, quietly
  // undercounting whichever band it belonged to. That is the worst outcome
  // available here, so it fails the build instead. Answering "not-addressed"
  // is always available and is a real answer, not a way of skipping one.
  const unanswered = entries.flatMap((e) =>
    e.quotes.flatMap((q) =>
      questionsFor(q.categories)
        .filter((question) => !q.bands?.[question])
        .map((question) => `${e.id}.${q.quoteId} does not answer "${question}"`),
    ),
  );
  if (unanswered.length > 0) {
    throw new Error(
      `eternal-increase-timeline/sources.json has quotes whose categories raise a question they never answer:\n  ${unanswered.join("\n  ")}`,
    );
  }

  // A review flag with nothing to review is a leftover.
  const emptyFlags = entries.flatMap((e) =>
    e.quotes
      .filter((q) => q.stanceNeedsReview && !q.bands)
      .map((q) => `${e.id}.${q.quoteId}`),
  );
  if (emptyFlags.length > 0) {
    throw new Error(
      `eternal-increase-timeline/sources.json flags quotes for review that answer nothing:\n  ${emptyFlags.join("\n  ")}`,
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
