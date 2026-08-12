import eternalIncreaseSources from "@/app/eternal-increase-timeline/sources.json";

/**
 * The published timeline index. Adding a timeline here is what makes it
 * publicly listed — see docs/timelines/CONSTRUCTING.md §5. A timeline can
 * exist as a route without appearing in this list, which is how a working
 * draft stays unlisted until it is ready to be found.
 */
export type TimelineSummary = {
  href: string;
  title: string;
  /** The question the timeline is measuring, in one sentence. */
  question: string;
  /**
   * Period covered, derived from the data rather than hand-maintained. Absent
   * on a timeline whose sources have not been gathered yet.
   */
  span?: string;
  /** Absent rather than 0 while a timeline is still in preparation. */
  sourceCount?: number;
  /** Shown as a caveat chip when the dataset is still being verified. */
  status?: string;
  /**
   * Scoped but unsourced: the question and axes are settled and its quiz runs,
   * but there is nothing on it yet to read as evidence.
   */
  planned?: boolean;
};

function spanOf(sources: { date: string }[]): string | undefined {
  if (sources.length === 0) return undefined;
  const years = sources.map((s) => Number(s.date.slice(0, 4)));
  return `${Math.min(...years)}–${Math.max(...years)}`;
}

export const TIMELINES: TimelineSummary[] = [
  {
    href: "/eternal-increase-timeline",
    title: "Eternal regress & eternal increase",
    question:
      "Whether God the Father had a Father, whether exalted humans become parents of spirits, how spirit birth was described, and how those teachings were reframed in correlated materials.",
    span: spanOf(eternalIncreaseSources),
    sourceCount: eternalIncreaseSources.length,
    status: "Working draft",
  },
  {
    href: "/family-proclamation-timeline",
    title: "The Family: A Proclamation to the World",
    question:
      "What has been taught about gender as an eternal characteristic, about the family forms exaltation requires, and about what kind of document the 1995 Proclamation is.",
    status: "In preparation",
    planned: true,
  },
  {
    href: "/baptism-timeline",
    title: "Baptism",
    question:
      "Whether baptism works the remission of sins and the new birth or witnesses to a change already worked, who may receive it, and whose baptism counts.",
    status: "In preparation",
    planned: true,
  },
  {
    href: "/sacrament-timeline",
    title: "The sacrament",
    question:
      "What the emblems have been said to be, from memorial through the forms of real presence, what partaking is said to do, and how plainly or ceremonially the rite has been kept.",
    status: "In preparation",
    planned: true,
  },
];
