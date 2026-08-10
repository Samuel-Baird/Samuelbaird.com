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
  /** Period covered, derived from the data rather than hand-maintained. */
  span: string;
  sourceCount: number;
  /** Shown as a caveat chip when the dataset is still being verified. */
  status?: string;
};

function spanOf(sources: { date: string }[]): string {
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
];
