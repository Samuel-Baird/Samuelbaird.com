import type {
  CategoryId,
  CorrelationStatus,
  HearsayGrade,
  SourceEntry,
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
      "Explicitly states God the Father had a Father / a God above Him.",
  },
  "BACKWARD-MORTALITY": {
    label: "Backward: mortality",
    pill: "bg-sky-50 text-sky-900 ring-sky-200 dark:bg-sky-950/40 dark:text-sky-300 dark:ring-sky-800/50",
    definition:
      "God underwent mortality (“was once as we are”) — implies but does not state a Father above Him.",
  },
  "BACKWARD-AGNOSTIC": {
    label: "Backward: agnostic",
    pill: "bg-indigo-50 text-indigo-900 ring-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 dark:ring-indigo-800/50",
    definition:
      "Acknowledges the question but declines or discourages inquiry.",
  },
  "FORWARD-EXPLICIT": {
    label: "Forward: explicit",
    pill: "bg-emerald-50 text-emerald-900 ring-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:ring-emerald-800/50",
    definition:
      "Exalted humans will procreate spirit children / people worlds.",
  },
  "FORWARD-EUPHEMISM": {
    label: "Forward: euphemism",
    pill: "bg-teal-50 text-teal-900 ring-teal-200 dark:bg-teal-950/40 dark:text-teal-300 dark:ring-teal-800/50",
    definition:
      "“Eternal increase,” “continuation of the seeds,” “eternal families” without stating the mechanism.",
  },
  "SPIRIT-BIRTH-VIVIPAROUS": {
    label: "Spirit birth: viviparous",
    pill: "bg-purple-50 text-purple-900 ring-purple-200 dark:bg-purple-950/40 dark:text-purple-300 dark:ring-purple-800/50",
    definition:
      "Spirit birth described in physiological or literal terms (Heavenly Parents beget spirits).",
  },
  "SPIRIT-BIRTH-TRIPARTITE": {
    label: "Spirit birth: tripartite",
    pill: "bg-violet-50 text-violet-900 ring-violet-200 dark:bg-violet-950/40 dark:text-violet-300 dark:ring-violet-800/50",
    definition:
      "Intelligence → spirit → body framework (organization of pre-existing intelligence).",
  },
  "SPIRIT-BIRTH-ADOPTION": {
    label: "Spirit birth: adoption/organization",
    pill: "bg-fuchsia-50 text-fuchsia-900 ring-fuchsia-200 dark:bg-fuchsia-950/40 dark:text-fuchsia-300 dark:ring-fuchsia-800/50",
    definition:
      "Spirits organized rather than begotten (King Follett reading; Ostler's view).",
  },
  "HEAVENLY-MOTHER": {
    label: "Heavenly Mother",
    pill: "bg-amber-50 text-amber-900 ring-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:ring-amber-800/50",
    definition:
      "Mother in Heaven as necessary participant in spirit generation.",
  },
  "INFINITE-CHAIN": {
    label: "Infinite chain",
    pill: "bg-slate-100 text-slate-800 ring-slate-200 dark:bg-slate-800/50 dark:text-slate-300 dark:ring-slate-700/60",
    definition:
      "Explicit chain language: worlds without end, endless succession of Gods.",
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
      "Contemporaneous secondhand report (journal entry of what someone heard).",
    example: "Wilford Woodruff journal reporting a Joseph Smith sermon",
  },
  D: {
    badge:
      "bg-orange-100 text-orange-800 ring-orange-200 dark:bg-orange-950/50 dark:text-orange-300 dark:ring-orange-800/50",
    description: "Later recollection, years after the fact.",
    example: "1890s reminiscences of Nauvoo teachings",
  },
  E: {
    badge:
      "bg-rose-100 text-rose-800 ring-rose-200 dark:bg-rose-950/50 dark:text-rose-300 dark:ring-rose-800/50",
    description:
      "Attributed via tertiary compilation without traceable original.",
    example: "Some Journal of Discourses attributions; folklore",
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
  discontinued: {
    label: "Discontinued",
    dot: "bg-amber-500",
  },
  "never-official": {
    label: "Never official",
    dot: "bg-rose-500",
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
  return ERAS.find((e) => year >= e.startYear && year <= e.endYear) ?? ERAS[ERAS.length - 1];
}
