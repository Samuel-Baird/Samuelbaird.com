import type { TagInk } from "@/components/tag";
import { NOT_ADDRESSED } from "./schema";
import type {
  CategoryId,
  CorrelationStatus,
  HearsayGrade,
  QuestionId,
  Referent,
  SourceEntry,
  SourceType,
} from "./schema";

// Tailwind v4 needs complete literal class strings — never build these by
// concatenation (same rule as src/lib/channel-types.ts). Colour now routes
// through the shared 4-ink-family system (src/components/tag.tsx) rather
// than N bright Tailwind pastels: every *_META table below stores a TagInk,
// and callers render <Tag ink={...}> instead of hand-building pill classes.
//
// The hearsay grade stamp is circular (a letterpress-style monogram, not a
// label), so it can't reuse <Tag>'s rounded-rect markup. INK_VARS mirrors
// Tag's own text/ring/bg classes per ink family so that one other shape can
// stay on the same palette without duplicating colour decisions.
export const INK_VARS: Record<
  TagInk,
  { text: string; ring: string; bg: string }
> = {
  ink: {
    text: "text-[color:var(--foreground)]",
    ring: "ring-[color:var(--foreground)]/25",
    bg: "bg-[color:var(--foreground)]/[0.04]",
  },
  accent: {
    text: "text-[color:var(--accent)]",
    ring: "ring-[color:var(--accent)]/35",
    bg: "bg-[color:var(--accent-soft)]",
  },
  oxblood: {
    text: "text-[color:var(--oxblood)]",
    ring: "ring-[color:var(--oxblood)]/35",
    bg: "bg-[color:var(--oxblood-soft)]",
  },
  honey: {
    text: "text-[color:var(--honey)]",
    ring: "ring-[color:var(--honey)]/35",
    bg: "bg-[color:var(--honey-soft)]",
  },
  muted: {
    text: "text-[color:var(--muted)]",
    ring: "ring-[color:var(--border)]",
    bg: "bg-[color:var(--muted-soft)]",
  },
};
//
// Category ink families follow the dataset's own axes rather than being
// arbitrary:
//   - oxblood = backward-direction claims (a Father-above-the-Father, or a
//     succession of Gods) — the doctrinally load-bearing, contested axis.
//   - honey   = forward-direction / "eternal increase" claims (procreation,
//     spirit birth, Heavenly Mother) — the site's namesake axis, given the
//     Deseret accent colour.
//   - accent  = structural/explanatory frameworks (many worlds, tripartite
//     model, ongoing divine progression) rather than first-order claims.
//   - ink     = the orthodox baseline/counter-position (always God).
//   - muted   = meta categories that sit outside the claim axes (declining
//     to answer, or a later retreat/reframe of an earlier teaching).
export const CATEGORY_META: Record<
  CategoryId,
  { label: string; ink: TagInk; definition: string }
> = {
  "BACKWARD-EXPLICIT": {
    label: "Backward: explicit",
    ink: "oxblood",
    definition:
      "States that the Father had a Father, or a God above Him.",
  },
  "FATHER-MORTAL-EXPERIENCE": {
    label: "Father: mortal experience",
    ink: "oxblood",
    definition:
      "God lived a mortal probation — “as man now is, God once was.” Check the referent chip: where it is not “Father,” the source makes the claim without establishing it of the Father.",
  },
  "FATHER-BECAME-GOD": {
    label: "Father: became God",
    ink: "oxblood",
    definition:
      "God attained divinity at some point rather than always possessing it — exaltation, progression to perfection, “attained the state.” Implies but is distinct from having had a mortal experience.",
  },
  "FATHER-ALWAYS-GOD": {
    label: "Father: always God",
    ink: "ink",
    definition:
      "The counter-position: God has always been God, with no prior state of non-divinity. Tagged on denials as well as affirmations elsewhere in the axis; each quote's note states the direction.",
  },
  "BACKWARD-AGNOSTIC": {
    label: "Backward: agnostic",
    ink: "muted",
    definition:
      "Acknowledges the regress question but declines or discourages it.",
  },
  "FORWARD-EXPLICIT": {
    label: "Forward: explicit",
    ink: "honey",
    definition:
      "Exalted humans procreate spirit children or people worlds.",
  },
  "FORWARD-EUPHEMISM": {
    label: "Forward: euphemism",
    ink: "honey",
    definition:
      "“Eternal increase,” “continuation of the seeds,” “eternal families” — no mechanism stated.",
  },
  "SPIRIT-BIRTH-VIVIPAROUS": {
    label: "Spirit birth: viviparous",
    ink: "honey",
    definition:
      "Spirits literally begotten and born of Heavenly Parents.",
  },
  "SPIRIT-BIRTH-ADOPTION": {
    label: "Spirit birth: adoption/organization",
    ink: "honey",
    definition:
      "Spirits organized from eternal intelligence rather than begotten.",
  },
  "TRIPARTITE-FRAMEWORK": {
    label: "Tripartite framework",
    ink: "accent",
    definition:
      "Intelligence → spirit → body as an explicit three-stage model. Reserved for sources that actually articulate three stages — not retrojected onto Abraham 3 or the King Follett Discourse, which state two-stage or unstaged eternalism.",
  },
  "MANY-WORLDS": {
    label: "Many worlds",
    ink: "accent",
    definition:
      "Plural worlds or creations under one God; no succession of Gods implied.",
  },
  "HEAVENLY-MOTHER": {
    label: "Heavenly Mother",
    ink: "honey",
    definition: "A Mother in Heaven is affirmed.",
  },
  "INFINITE-CHAIN": {
    label: "Infinite chain",
    ink: "oxblood",
    definition:
      "Explicit succession-of-Gods language. Requires a succession of Gods, not merely a plurality of worlds.",
  },
  "DIVINE-PROGRESSION": {
    label: "Divine progression",
    ink: "accent",
    definition:
      "Addresses whether God Himself still progresses in knowledge or power. Affirmations (Young, Woodruff) and denials (Joseph Fielding Smith, McConkie: only in dominions) both carry the tag; each quote's note states the direction.",
  },
  "RETREAT-REFRAME": {
    label: "Retreat / reframe",
    ink: "muted",
    definition:
      "Later material that removes, softens, or reframes an earlier teaching.",
  },
};

// Hearsay is a reliability gradient, so it walks the ink families in order
// from strongest provenance to weakest rather than by arbitrary hue:
// ink (first-person) -> accent -> muted (neutral midpoint) -> honey (caution)
// -> oxblood (weakest / no traceable original).
export const HEARSAY_META: Record<
  HearsayGrade,
  { ink: TagInk; description: string; example: string }
> = {
  A: {
    ink: "ink",
    description:
      "First-person text by the speaker, published under their direction.",
    example: "1909 First Presidency statement",
  },
  B: {
    ink: "accent",
    description: "Contemporaneous notes by trained scribes, amalgamated.",
    example: "King Follett Discourse scribal accounts",
  },
  C: {
    ink: "muted",
    description:
      "Contemporaneous secondhand report, including shorthand reports edited for publication.",
    example: "Journal of Discourses via George Watt's shorthand",
  },
  D: {
    ink: "honey",
    description: "Later recollection, years after the fact.",
    example: "Snow's c. 1901 account of the couplet's 1840 origin",
  },
  E: {
    ink: "oxblood",
    description:
      "Attributed via tertiary compilation with no traceable original.",
    example: "Genuinely orphaned attributions; folklore",
  },
};

// Correlation status: accent marks what is currently published, honey/oxblood
// flag the two ways a source has fallen out of current use.
export const STATUS_META: Record<
  CorrelationStatus,
  { label: string; ink: TagInk; dot: string }
> = {
  "current-correlated": {
    label: "Current-correlated",
    ink: "accent",
    dot: "bg-[color:var(--accent)]",
  },
  "historical-official": {
    label: "Historical-official",
    ink: "ink",
    dot: "bg-[color:var(--foreground)]",
  },
  discontinued: {
    label: "Discontinued",
    ink: "honey",
    dot: "bg-[color:var(--honey)]",
  },
  "never-official": {
    label: "Never official",
    ink: "oxblood",
    dot: "bg-[color:var(--oxblood)]",
  },
};

// Referent: father-referent claims are the doctrinally distinctive ones, so
// they get oxblood; son-referent claims require no theogony of the Father
// and read as the "safe" reading, so accent; ambiguous is a caution (honey).
export const REFERENT_META: Record<
  Referent,
  { label: string; short: string; ink: TagInk; definition: string }
> = {
  father: {
    label: "Referent: the Father",
    short: "Father",
    ink: "oxblood",
    definition:
      "The “God” of the key claim is demonstrably God the Father. These are the doctrinally distinctive claims.",
  },
  son: {
    label: "Referent: the Son",
    short: "Son",
    ink: "accent",
    definition:
      "The claim's own warrant points at Christ — a being who was mortal, is now God, and has a Father above him. Requires no theogony for the Father.",
  },
  ambiguous: {
    label: "Referent: ambiguous",
    short: "Ambiguous",
    ink: "honey",
    definition:
      "The referent cannot be settled from the source itself. Later use often exploits exactly this ambiguity.",
  },
  "n/a": {
    label: "Referent: not applicable",
    short: "n/a",
    ink: "muted",
    definition: "The source makes no backward-direction claim about God.",
  },
};

export const SOURCE_TYPE_META: Record<
  SourceType,
  { label: string; ink: TagInk; definition: string }
> = {
  original: {
    label: "Original",
    ink: "accent",
    definition: "First attestation of the teaching.",
  },
  citation: {
    label: "Citation",
    ink: "muted",
    definition:
      "A later source quoting or teaching from an original. Collapsing citations folds these into the originals they cite.",
  },
};

export type Era = {
  id: string;
  label: string;
  range: string;
  startYear: number;
  endYear: number;
};

export const ERAS: Era[] = [
  { id: "foundational", label: "Foundational", range: "1830–1844", startYear: 0, endYear: 1844 },
  { id: "utah", label: "Utah Period", range: "1845–1900", startYear: 1845, endYear: 1899 },
  { id: "official", label: "Official Statements", range: "1900–1950", startYear: 1900, endYear: 1949 },
  { id: "correlated", label: "Correlated Era", range: "1950–2010", startYear: 1950, endYear: 2012 },
  { id: "taper", label: "Gospel Topics Era & Taper", range: "2013–present", startYear: 2013, endYear: 9999 },
];

/**
 * The questions the corpus is asked, with the answers each one takes.
 *
 * Every band carries its criteria in the data rather than in a document, so
 * whoever assigns one — a reader or an agent — is held to the same written
 * rule, and so the page can show that rule to anyone who wants to argue with a
 * placement. The full reasoning is in docs/timelines/STANCE-TAXONOMY.md.
 *
 * Two structural things worth knowing. Bands are ordered by *commitment*, not
 * by magnitude: on the regress question an indefinite chain outranks a finite
 * one because leaving the succession open is a stronger claim than closing it.
 * And `offScale` marks an answer that is not a rung on the ladder at all —
 * declining to say sits genuinely between "not always God" and "always God",
 * but nothing sits between an infinite regress and none, so drawing it there
 * would invent a position no source holds.
 */
export type Band = {
  id: string;
  label: string;
  criteria: string;
  /** Not a rung on the scale; drawn apart from the ordered bands. */
  offScale?: boolean;
};

export type Question = {
  id: QuestionId;
  /** Tab label. */
  label: string;
  /** Asked of every quote the triggering categories reach. */
  question: string;
  /** Shown under the tabs, in the reader's own terms. */
  blurb: string;
  bands: Band[];
};

export const QUESTIONS: Question[] = [
  {
    id: "divinity",
    label: "Divinity",
    question: "Was the Father always God?",
    blurb:
      "Whether the Father has always been God, or came to be one. This is not the mortality question: on this tradition's own terms Jehovah was God before and during his mortal life, so a passage about the Father's mortality says nothing here unless it also speaks of his becoming.",
    bands: [
      {
        id: "not-always-god",
        label: "Not always God",
        criteria:
          "Asserts a change into godhood — attained, became, was exalted to, progressed to being God — or that there was a time he was not God.",
      },
      {
        id: "declines",
        label: "Declines to say",
        criteria:
          "Raises his origin or history and withholds, or is deliberately poised between attainment and eternal divinity.",
      },
      {
        id: "always-god",
        label: "Always God",
        criteria:
          "Asserts the Father has always been God: no beginning to his divinity, no attainment.",
      },
    ],
  },
  {
    id: "regress",
    label: "Regress",
    question: "How many Gods stand above the Father?",
    blurb:
      "An unquantified chain is an indefinite claim, not an infinite one. Reading it as infinite is the most tempting error available here, and the bands are ordered by how strong a claim is being made rather than by how many Gods are counted.",
    bands: [
      {
        id: "infinite",
        label: "Infinite regress",
        criteria:
          "An explicitly endless or numberless succession of Gods above the Father.",
      },
      {
        id: "indefinite",
        label: "Indefinite regress",
        criteria:
          "A chain above the Father with no stated terminus and no stated count — the default reading of an unqualified “his Father had a Father.”",
      },
      {
        id: "finite",
        label: "Finite regress",
        criteria:
          "A bounded chain: a stated count, or a named terminus above the Father.",
      },
      {
        id: "most-high",
        label: "Father is the Most High",
        criteria: "Asserts nothing stands above the Father; he is the terminus.",
      },
      {
        id: "declines",
        label: "Declines to say",
        criteria: "Raises the question and withholds.",
        offScale: true,
      },
    ],
  },
  {
    id: "mortality",
    label: "Mortality",
    question: "Did the Father pass through a mortal life?",
    blurb:
      "Kept apart from the divinity question on purpose. A mortal life and an attained divinity are separate claims, and the middle band is for the pattern this tradition already accepts in Christ — mortal while never ceasing to be God.",
    bands: [
      {
        id: "probation",
        label: "A probation as ours",
        criteria:
          "A mortality like ours: tested, subject to law, able to fall. A probation, not merely an incarnation.",
      },
      {
        id: "already-divine",
        label: "Mortal, already divine",
        criteria:
          "Lived a mortal life while already God — the Jehovah pattern. Incarnation without loss of divinity, or explicit comparison to Christ's mortality.",
      },
      {
        id: "declines",
        label: "Declines to say",
        criteria: "Raises his mortality and withholds its character.",
        offScale: true,
      },
      {
        id: "denies",
        label: "Denies mortality",
        criteria: "Asserts the Father never was mortal.",
      },
    ],
  },
  {
    id: "increase",
    label: "Eternal increase",
    question: "Do the exalted become parents of spirit children?",
    blurb:
      "The distinction that matters is whether a mechanism is stated. Promising posterity without saying how is its own position, and it is the one most of the modern corpus takes.",
    bands: [
      {
        id: "literal-begetting",
        label: "Literally begotten",
        criteria:
          "Spirit children are begotten and born of heavenly parents. Procreation stated, not implied.",
      },
      {
        id: "mechanism-unstated",
        label: "Increase, mechanism unstated",
        criteria:
          "Affirms eternal increase, posterity, or continuation of seed while withholding how it happens.",
      },
      {
        id: "organized-not-begotten",
        label: "Organized, not begotten",
        criteria:
          "Spirits are organized, adopted, or fashioned from pre-existing intelligence — explicitly not begotten.",
      },
      {
        id: "declines",
        label: "Declines to say",
        criteria: "Raises the question and withholds.",
        offScale: true,
      },
      {
        id: "denies",
        label: "Denies increase",
        criteria: "Denies that exalted beings have spirit posterity at all.",
      },
    ],
  },
  {
    id: "mother",
    label: "Heavenly Mother",
    question: "What work does the Mother do?",
    blurb:
      "Her existence is barely contested in this corpus, so asking whether she exists draws a flat line. What moves is how much she is required to do — and a rebuke aimed at praying to her caps her role without denying her.",
    bands: [
      {
        id: "necessary-for-birth",
        label: "Necessary for spirit birth",
        criteria:
          "Required for spirit children to exist. Begetting is said to need a mother, or she is named as bearing spirit offspring.",
      },
      {
        id: "parent-mechanism-unstated",
        label: "A parent, mechanism unstated",
        criteria:
          "Parentage affirmed — we are her children, she is a parent alongside the Father — without asserting how. The “heavenly parents” formula.",
      },
      {
        id: "present-role-unstated",
        label: "Present, role unstated",
        criteria:
          "She exists, or is a consort or exalted wife, with no claim about parentage or generation.",
      },
      {
        id: "role-capped",
        label: "Role capped",
        criteria:
          "Grants her, then restricts what follows: no speculation, no worship, no inference beyond what is given.",
      },
      {
        id: "declines",
        label: "Declines to say",
        criteria: "Raises her and withholds entirely.",
        offScale: true,
      },
      {
        id: "denies",
        label: "Denied",
        criteria: "Denies her, or denies the specific role proposed.",
      },
    ],
  },
  {
    id: "progression",
    label: "Divine progression",
    question: "Does God still progress?",
    blurb:
      "The interesting band is the middle one. Restricting progression to dominion while denying it in knowledge is a distinct position, and it is how the claim was retired rather than simply contradicted.",
    bands: [
      {
        id: "knowledge",
        label: "Progresses in knowledge",
        criteria:
          "God advances in knowledge, truth, or perfection. The strong claim.",
      },
      {
        id: "dominion-only",
        label: "In dominion only",
        criteria:
          "Restricts progression to glory, dominion, or kingdoms while denying growth in knowledge.",
      },
      {
        id: "declines",
        label: "Declines to say",
        criteria: "Raises it and withholds.",
        offScale: true,
      },
      {
        id: "denies",
        label: "Denies progression",
        criteria: "God possesses all knowledge and does not advance.",
      },
    ],
  },
];

export const QUESTION_META: Record<QuestionId, Question> = Object.fromEntries(
  QUESTIONS.map((q) => [q.id, q]),
) as Record<QuestionId, Question>;

/** The band a quote landed in for a question, or null where it answers none. */
export function bandFor(
  quote: { bands?: Record<string, string> },
  question: QuestionId,
): Band | null {
  const id = quote.bands?.[question];
  if (!id || id === NOT_ADDRESSED) return null;
  return QUESTION_META[question].bands.find((b) => b.id === id) ?? null;
}

export function eraFor(entry: SourceEntry): Era {
  const year = Number(entry.date.slice(0, 4));
  return (
    ERAS.find((e) => year >= e.startYear && year <= e.endYear) ??
    ERAS[ERAS.length - 1]
  );
}

/** Hearsay grade for a specific quote, honouring any per-quote override. */
export function hearsayForQuote(entry: SourceEntry, quoteId: string): HearsayGrade {
  return entry.hearsayByQuote?.[quoteId] ?? entry.hearsay;
}

/** Every category asserted anywhere in an entry's quotes. */
export function categoriesOf(entry: SourceEntry): CategoryId[] {
  return [...new Set(entry.quotes.flatMap((q) => q.categories))];
}
