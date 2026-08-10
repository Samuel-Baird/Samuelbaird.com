import type {
  CategoryId,
  CorrelationStatus,
  HearsayGrade,
  Referent,
  SourceEntry,
  SourceType,
} from "./schema";

// Tailwind v4 needs complete literal class strings — never build these by
// concatenation (same rule as src/lib/channel-types.ts).

export const CATEGORY_META: Record<
  CategoryId,
  { label: string; pill: string; definition: string }
> = {
  "BACKWARD-EXPLICIT": {
    label: "Backward: explicit",
    pill: "bg-blue-50 text-blue-900 ring-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:ring-blue-800/50",
    definition:
      "States that the Father had a Father, or a God above Him.",
  },
  "BACKWARD-MORTALITY": {
    label: "Backward: mortality",
    pill: "bg-sky-50 text-sky-900 ring-sky-200 dark:bg-sky-950/40 dark:text-sky-300 dark:ring-sky-800/50",
    definition:
      "God underwent mortality; no Father-above is stated.",
  },
  "BACKWARD-AGNOSTIC": {
    label: "Backward: agnostic",
    pill: "bg-indigo-50 text-indigo-900 ring-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 dark:ring-indigo-800/50",
    definition:
      "Acknowledges the regress question but declines or discourages it.",
  },
  "FORWARD-EXPLICIT": {
    label: "Forward: explicit",
    pill: "bg-emerald-50 text-emerald-900 ring-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:ring-emerald-800/50",
    definition:
      "Exalted humans procreate spirit children or people worlds.",
  },
  "FORWARD-EUPHEMISM": {
    label: "Forward: euphemism",
    pill: "bg-teal-50 text-teal-900 ring-teal-200 dark:bg-teal-950/40 dark:text-teal-300 dark:ring-teal-800/50",
    definition:
      "“Eternal increase,” “continuation of the seeds,” “eternal families” — no mechanism stated.",
  },
  "SPIRIT-BIRTH-VIVIPAROUS": {
    label: "Spirit birth: viviparous",
    pill: "bg-purple-50 text-purple-900 ring-purple-200 dark:bg-purple-950/40 dark:text-purple-300 dark:ring-purple-800/50",
    definition:
      "Spirits literally begotten and born of Heavenly Parents.",
  },
  "SPIRIT-BIRTH-ADOPTION": {
    label: "Spirit birth: adoption/organization",
    pill: "bg-fuchsia-50 text-fuchsia-900 ring-fuchsia-200 dark:bg-fuchsia-950/40 dark:text-fuchsia-300 dark:ring-fuchsia-800/50",
    definition:
      "Spirits organized from eternal intelligence rather than begotten.",
  },
  "TRIPARTITE-FRAMEWORK": {
    label: "Tripartite framework",
    pill: "bg-violet-50 text-violet-900 ring-violet-200 dark:bg-violet-950/40 dark:text-violet-300 dark:ring-violet-800/50",
    definition:
      "Intelligence → spirit → body as an explicit three-stage model. Reserved for sources that actually articulate three stages — not retrojected onto Abraham 3 or the King Follett Discourse, which state two-stage or unstaged eternalism.",
  },
  "MANY-WORLDS": {
    label: "Many worlds",
    pill: "bg-cyan-50 text-cyan-900 ring-cyan-200 dark:bg-cyan-950/40 dark:text-cyan-300 dark:ring-cyan-800/50",
    definition:
      "Plural worlds or creations under one God; no succession of Gods implied.",
  },
  "HEAVENLY-MOTHER": {
    label: "Heavenly Mother",
    pill: "bg-amber-50 text-amber-900 ring-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:ring-amber-800/50",
    definition: "A Mother in Heaven is affirmed.",
  },
  "INFINITE-CHAIN": {
    label: "Infinite chain",
    pill: "bg-slate-100 text-slate-800 ring-slate-200 dark:bg-slate-800/50 dark:text-slate-300 dark:ring-slate-700/60",
    definition:
      "Explicit succession-of-Gods language. Requires a succession of Gods, not merely a plurality of worlds.",
  },
  "DIVINE-PROGRESSION": {
    label: "Divine progression",
    pill: "bg-rose-50 text-rose-900 ring-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:ring-rose-800/50",
    definition:
      "Addresses whether God Himself still progresses in knowledge or power. Affirmations (Young, Woodruff) and denials (Joseph Fielding Smith, McConkie: only in dominions) both carry the tag; each quote's note states the direction.",
  },
  "RETREAT-REFRAME": {
    label: "Retreat / reframe",
    pill: "bg-orange-50 text-orange-900 ring-orange-200 dark:bg-orange-950/40 dark:text-orange-300 dark:ring-orange-800/50",
    definition:
      "Later material that removes, softens, or reframes an earlier teaching.",
  },
};

export const HEARSAY_META: Record<
  HearsayGrade,
  { badge: string; description: string; example: string }
> = {
  A: {
    badge:
      "bg-emerald-100 text-emerald-800 ring-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-300 dark:ring-emerald-800/50",
    description:
      "First-person text by the speaker, published under their direction.",
    example: "1909 First Presidency statement",
  },
  B: {
    badge:
      "bg-teal-100 text-teal-800 ring-teal-200 dark:bg-teal-950/50 dark:text-teal-300 dark:ring-teal-800/50",
    description: "Contemporaneous notes by trained scribes, amalgamated.",
    example: "King Follett Discourse scribal accounts",
  },
  C: {
    badge:
      "bg-amber-100 text-amber-800 ring-amber-200 dark:bg-amber-950/50 dark:text-amber-300 dark:ring-amber-800/50",
    description:
      "Contemporaneous secondhand report, including shorthand reports edited for publication.",
    example: "Journal of Discourses via George Watt's shorthand",
  },
  D: {
    badge:
      "bg-orange-100 text-orange-800 ring-orange-200 dark:bg-orange-950/50 dark:text-orange-300 dark:ring-orange-800/50",
    description: "Later recollection, years after the fact.",
    example: "Snow's c. 1901 account of the couplet's 1840 origin",
  },
  E: {
    badge:
      "bg-rose-100 text-rose-800 ring-rose-200 dark:bg-rose-950/50 dark:text-rose-300 dark:ring-rose-800/50",
    description:
      "Attributed via tertiary compilation with no traceable original.",
    example: "Genuinely orphaned attributions; folklore",
  },
};

export const STATUS_META: Record<
  CorrelationStatus,
  { label: string; dot: string }
> = {
  "current-correlated": {
    label: "Current-correlated",
    dot: "bg-[color:var(--accent)]",
  },
  "historical-official": {
    label: "Historical-official",
    dot: "bg-[color:var(--muted)]",
  },
  discontinued: { label: "Discontinued", dot: "bg-amber-500" },
  "never-official": { label: "Never official", dot: "bg-rose-500" },
};

export const REFERENT_META: Record<
  Referent,
  { label: string; short: string; chip: string; definition: string }
> = {
  father: {
    label: "Referent: the Father",
    short: "Father",
    chip: "bg-blue-50 text-blue-900 ring-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:ring-blue-800/50",
    definition:
      "The “God” of the key claim is demonstrably God the Father. These are the doctrinally distinctive claims.",
  },
  son: {
    label: "Referent: the Son",
    short: "Son",
    chip: "bg-emerald-50 text-emerald-900 ring-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:ring-emerald-800/50",
    definition:
      "The claim's own warrant points at Christ — a being who was mortal, is now God, and has a Father above him. Requires no theogony for the Father.",
  },
  ambiguous: {
    label: "Referent: ambiguous",
    short: "Ambiguous",
    chip: "bg-amber-50 text-amber-900 ring-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:ring-amber-800/50",
    definition:
      "The referent cannot be settled from the source itself. Later use often exploits exactly this ambiguity.",
  },
  "n/a": {
    label: "Referent: not applicable",
    short: "n/a",
    chip: "bg-[color:var(--muted-soft)] text-[color:var(--muted)] ring-[color:var(--border)]",
    definition: "The source makes no backward-direction claim about God.",
  },
};

export const SOURCE_TYPE_META: Record<
  SourceType,
  { label: string; chip: string; definition: string }
> = {
  original: {
    label: "Original",
    chip: "bg-[color:var(--accent-soft)] text-[color:var(--accent)] ring-[color:var(--border)]",
    definition: "First attestation of the teaching.",
  },
  citation: {
    label: "Citation",
    chip: "bg-[color:var(--muted-soft)] text-[color:var(--muted)] ring-[color:var(--border)]",
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
