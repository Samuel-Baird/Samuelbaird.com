/**
 * Pure scoring functions for the "How evangelical are you?" quiz.
 *
 * Every function here mirrors a function in
 * `scripts/evangelical-quiz/build_data.py` of the same purpose: the build
 * computes per-item weights and the synthetic percentile curve once, and
 * ships them in data.json; the client only sums weights and looks values up
 * in that curve. Nothing here calls a probability formula on raw survey
 * percentages — that math already ran at build time.
 */

import type {
  AnswerMap,
  BreakdownRow,
  Match,
  QuizData,
  QuizItem,
  Response,
  Tradition,
  TraditionScore,
} from "./types";

/** Number of items the reader has answered. */
export function answeredCount(answers: AnswerMap): number {
  return Object.keys(answers).length;
}

/**
 * Sum of per-answer log-likelihood weights, divided by SHRINKAGE.
 * Unanswered items are skipped, not penalized.
 */
export function scoreAnswers(data: QuizData, answers: AnswerMap): number {
  let total = 0;
  for (const item of data.items) {
    const r = answers[item.id];
    if (r === undefined) continue;
    const w = item.w[r];
    if (w === undefined) continue;
    total += w;
  }
  return total / data.constants.SHRINKAGE;
}

/**
 * Percent of the synthetic national population scoring below `score`.
 * Binary search over the ascending breakpoints the build computed.
 */
export function percentileOf(data: QuizData, score: number): number {
  const bp = data.percentile_breakpoints;
  if (bp.length < 2) return 50;
  let lo = 0;
  let hi = bp.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (bp[mid] < score) lo = mid + 1;
    else hi = mid;
  }
  // lo can reach bp.length when score exceeds every breakpoint (a real
  // score more extreme than all 20k simulated respondents) - clamp so the
  // result never reads as more than "100% of Americans."
  return (100 * Math.min(lo, bp.length - 1)) / (bp.length - 1);
}

/**
 * Tradition match: for each tradition, sum ln P(r | tradition) over answered
 * items. Highest wins the headline; the runner-up is shown too, and a close
 * top two is reported as a tie rather than a false-precision winner.
 */
export function matchTradition(data: QuizData, answers: AnswerMap): Match | null {
  const scores: TraditionScore[] = data.traditions.map((tradition) => {
    let logLikelihood = 0;
    for (const item of data.items) {
      const r = answers[item.id];
      if (r === undefined) continue;
      const p = item.p[tradition]?.[r];
      if (p === undefined) continue;
      logLikelihood += Math.log(p);
    }
    return { tradition, logLikelihood };
  });

  if (scores.every((s) => s.logLikelihood === 0)) return null;

  const ranked = [...scores].sort((a, b) => b.logLikelihood - a.logLikelihood);
  const [top, runnerUp] = ranked;
  const tie = Math.abs(top.logLikelihood - runnerUp.logLikelihood) < data.constants.TIE_MARGIN;

  return { top, runnerUp, all: ranked, tie };
}

/**
 * Every answered item, sorted by |weight| descending — the payoff screen:
 * which answers pushed the reader's score the most, and which direction.
 */
export function breakdown(data: QuizData, answers: AnswerMap): BreakdownRow[] {
  const rows: BreakdownRow[] = [];
  for (const item of data.items) {
    const r = answers[item.id];
    if (r === undefined) continue;
    const weight = item.w[r];
    if (weight === undefined) continue;
    rows.push({
      item,
      response: item.scale[r],
      weight,
      contribution: weight / data.constants.SHRINKAGE,
    });
  }
  return rows.sort((a, b) => Math.abs(b.weight) - Math.abs(a.weight));
}

/** Convenience lookup used by the runner and the results screen alike. */
export function itemById(data: QuizData, id: string): QuizItem | undefined {
  return data.items.find((i) => i.id === id);
}

/** Human label for a response, e.g. "somewhat_agree" -> "Somewhat agree". */
export function responseLabel(response: string): string {
  const words = response.split("_");
  return words[0][0].toUpperCase() + words[0].slice(1) + " " + words.slice(1).join(" ");
}

/**
 * The order buttons are shown in on the question screen: agree options
 * first (top of thumb reach on mobile), then disagree, "not sure" last.
 * Independent of `scale`'s storage order (which matches the survey
 * explorer's disagree -> not-sure -> agree layout, for easy data entry).
 */
const DISPLAY_ORDER = [
  "strongly_agree",
  "somewhat_agree",
  "somewhat_disagree",
  "strongly_disagree",
  "not_sure",
] as const;

/** This item's options as {response, index}, in on-screen display order. */
export function displayOptions(item: QuizItem): { response: string; index: number }[] {
  return DISPLAY_ORDER.filter((r) => item.scale.includes(r as never)).map((r) => ({
    response: r,
    index: item.scale.indexOf(r as never),
  }));
}

/** Display order for the per-question group breakdown chart. */
const GROUP_DISPLAY_ORDER = [
  "Evangelical",
  "Black Protestant",
  "Mainline",
  "Roman Catholic",
  "All U.S. adults",
];

export type GroupBreakdownRow = {
  group: string;
  /** Percentages aligned to item.scale, summing to 100. */
  pcts: number[];
};

/**
 * This item's raw group percentages, in a fixed display order, limited to
 * groups the workbook actually has data for (currently that's often all of
 * them or none — an item only ships once every required group is filled —
 * but the chart stays correct either way).
 */
export function groupBreakdownRows(item: QuizItem): GroupBreakdownRow[] {
  return GROUP_DISPLAY_ORDER.filter((g) => item.raw_pct[g] !== undefined).map(
    (g) => ({ group: g, pcts: item.raw_pct[g] }),
  );
}

/**
 * `item.raw_pct[group]` back into the workbook's fixed 5-column order
 * (strongly_disagree, somewhat_disagree, not_sure, somewhat_agree,
 * strongly_agree), for export. A 3-option item's two collapsed columns come
 * back as 0 — the same convention the workbook itself uses for a collapsed
 * item, not a claim that 0% chose "somewhat."
 */
export function fiveColumnPct(item: QuizItem, group: string): number[] | null {
  const pcts = item.raw_pct[group];
  if (!pcts) return null;
  const byResponse = Object.fromEntries(
    item.scale.map((r, i) => [r, pcts[i]]),
  ) as Partial<Record<Response, number>>;
  return [
    "strongly_disagree",
    "somewhat_disagree",
    "not_sure",
    "somewhat_agree",
    "strongly_agree",
  ].map((r) => byResponse[r as Response] ?? 0);
}

export const TRADITION_LABEL: Record<Tradition, string> = {
  Evangelical: "an Evangelical Protestant",
  "Black Protestant": "a Black Protestant",
  Mainline: "a Mainline Protestant",
  "Roman Catholic": "a Roman Catholic",
};
