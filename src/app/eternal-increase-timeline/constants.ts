import type { TagInk } from "@/components/tag";
import type {
  CategoryId,
  CorrelationStatus,
  HearsayGrade,
  Referent,
  SourceEntry,
  SourceType,
  Stance,
  StanceCategoryId,
  SubjectId,
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
 * The questions the corpus can be asked about how settled a teaching was.
 *
 * A subject is a proposition plus the categories that bear on it. `affirms`,
 * `hedges` and `denies` on a quote are always *about the proposition*, never
 * about the category in the abstract — which is why the proposition is written
 * out here and shown to the reader rather than left implicit in a tag name.
 *
 * Subjects come in two widths, and both are wanted. A broad one asks whether a
 * whole position was held; a narrow one asks after a single move inside it, and
 * can show a claim quietly going out of use while the broad question still
 * looks settled. So they overlap rather than partition: `DEFINING_SUBJECT` in
 * schema.ts records which subject's proposition a category's stance actually
 * means, and a narrower subject may read the same category only where its
 * question takes that direction the same way.
 *
 * Heavenly Mother stays its own subject rather than joining eternal increase:
 * a Mother existing and the exalted begetting spirit children are different
 * claims, and merging them would force a direction onto quotes that address
 * only one.
 *
 * `bands` names the three positions in this subject's own words. "Affirms" and
 * "Denies" are accurate but say nothing; on the Father's origin the same two
 * bands are "Became God" and "Always God", which is the actual disagreement and
 * what a reader came to see.
 */
export type Subject = {
  id: SubjectId;
  label: string;
  question: string;
  proposition: string;
  categories: StanceCategoryId[];
  bands: Record<Stance, string>;
};

export const SUBJECTS: Subject[] = [
  {
    id: "father-origin",
    label: "The Father's origin",
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
    bands: {
      affirms: "Became God",
      hedges: "Declines to say",
      denies: "Always God",
    },
  },
  {
    id: "father-mortality",
    label: "A mortal life",
    question: "Did the Father live a mortal life?",
    proposition:
      "God the Father passed through a mortal probation — “as man now is, God once was.”",
    // The narrow half of the origin question. Whether the Father *lived* a
    // mortality is a different claim from whether he had a Father above him,
    // and the two stopped being taught at different times.
    categories: ["FATHER-MORTAL-EXPERIENCE"],
    bands: {
      affirms: "Lived a mortality",
      hedges: "Declines to say",
      denies: "Denied",
    },
  },
  {
    id: "infinite-chain",
    label: "Gods above the Father",
    question: "Is there a chain of Gods above the Father?",
    proposition:
      "The Father has a Father above him, and that succession runs back without end.",
    categories: ["INFINITE-CHAIN"],
    bands: {
      affirms: "A chain without end",
      hedges: "Declines to say",
      denies: "Denied",
    },
  },
  {
    id: "eternal-increase",
    label: "Eternal increase",
    question: "Do the exalted become parents of spirit children?",
    proposition:
      "Exalted men and women beget spirit offspring and so continue the pattern by which we were made.",
    categories: [
      "FORWARD-EXPLICIT",
      "FORWARD-EUPHEMISM",
      "SPIRIT-BIRTH-VIVIPAROUS",
      "SPIRIT-BIRTH-ADOPTION",
    ],
    bands: {
      affirms: "They beget",
      hedges: "Euphemism only",
      denies: "Begetting denied",
    },
  },
  {
    id: "spirit-birth",
    label: "How spirits are born",
    question: "Are spirits begotten, or organized?",
    proposition:
      "Spirit children are literally begotten and born to heavenly parents, rather than organized or adopted from existing intelligences.",
    // Two rival mechanisms rather than a claim and its denial, which is why the
    // bands are named for the positions. The denial band is small and that is
    // the finding: the organized/adopted reading is the minority one, and it
    // belongs to the earliest and the latest ends of the corpus rather than
    // the middle.
    categories: ["SPIRIT-BIRTH-VIVIPAROUS", "SPIRIT-BIRTH-ADOPTION"],
    bands: {
      affirms: "Literally begotten",
      hedges: "Mechanism unstated",
      denies: "Organized, not begotten",
    },
  },
  {
    id: "heavenly-mother",
    label: "Heavenly Mother",
    question: "Is there a Mother in Heaven?",
    proposition:
      "A Heavenly Mother exists and is a parent of the human family.",
    categories: ["HEAVENLY-MOTHER"],
    bands: {
      affirms: "She exists",
      hedges: "Declines to say",
      denies: "Denied",
    },
  },
  {
    id: "divine-progression",
    label: "Divine progression",
    question: "Does God still progress?",
    proposition:
      "God continues to advance in knowledge or perfection, rather than possessing all of it already.",
    categories: ["DIVINE-PROGRESSION"],
    bands: {
      affirms: "Still progressing",
      hedges: "Declines to say",
      denies: "Progression denied",
    },
  },
];

export const SUBJECT_META: Record<SubjectId, Subject> = Object.fromEntries(
  SUBJECTS.map((s) => [s.id, s]),
) as Record<SubjectId, Subject>;

export const STANCE_META: Record<
  Stance,
  { label: string; definition: string }
> = {
  affirms: {
    label: "Affirms",
    definition: "States or plainly teaches the proposition.",
    },
  hedges: {
    label: "Hedges",
    definition:
      "Gestures at it without committing — euphemism, an explicit refusal to say, deliberate ambiguity, or an affirmation withdrawn by its own qualification.",
  },
  denies: {
    label: "Denies",
    definition: "Rejects or corrects the proposition.",
  },
};

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
