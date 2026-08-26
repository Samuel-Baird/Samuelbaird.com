/**
 * Types for the "How evangelical are you?" quiz.
 *
 * The shape here is exactly what `scripts/evangelical-quiz/build_data.py`
 * emits into `data.json`. Nothing in the app computes a probability at
 * runtime — the build reads the State of Theology workbook, does the
 * likelihood math once, and ships the result. The client only sums weights
 * the build already decided on.
 */

/** The survey's five-point scale, in the order the explorer publishes it. */
export type Response =
  | "strongly_disagree"
  | "somewhat_disagree"
  | "not_sure"
  | "somewhat_agree"
  | "strongly_agree";

/** The four traditions a reader can be matched to. */
export type Tradition =
  | "Evangelical"
  | "Black Protestant"
  | "Mainline"
  | "Roman Catholic";

export type QuizItem = {
  id: string;
  statement: string;
  /**
   * Survey wave. Not uniform: most items are 2025, but an item dropped from
   * a later instrument keeps the last year it actually ran, and the results
   * screen says so rather than implying one clean vintage.
   */
  year: number | null;
  /**
   * Which response options this item offers. Five normally; three when the
   * source only published collapsed agree/disagree totals, in which case the
   * item genuinely has three options rather than an invented split.
   */
  scale: Response[];
  three_option: boolean;
  /** ln( P(r | Evangelical) / P(r | not Evangelical) ), one per scale slot. */
  w: number[];
  /** Smoothed P(r | tradition), one array per tradition. */
  p: Record<Tradition, number[]>;
  /** Smoothed P(r | All U.S. adults). The reference distribution. */
  p_all: number[];
  p_not_evangelical: number[];
  /**
   * As-entered percentages (whole numbers, sum to 100), one array per group
   * that has data for this item, aligned to `scale`. Unsmoothed — unlike
   * `p` / `p_all`, nothing here is floored for log-safety, so this is what
   * the per-question group breakdown chart should render, not `p`.
   */
  raw_pct: Record<string, number[]>;
};

export type QuizConstants = {
  EVANGELICAL_SHARE: number;
  PROB_FLOOR: number;
  NEG_FLOOR: number;
  SHRINKAGE: number;
  TIE_MARGIN: number;
};

/**
 * The reference groups an empirical percentile can be reported against.
 * Every key except `evangelical_by_belief` is one of this build's own
 * workbook groups (Evangelical/Black Protestant/Mainline/Roman Catholic, by
 * RELTRAD) or their complement/union; `evangelical_by_belief` is the
 * survey's separate belief-based (NAE definition) flag, kept distinct.
 */
export type ReferenceGroupKey =
  | "all"
  | "evangelical"
  | "non_evangelical"
  | "black_protestant"
  | "mainline"
  | "catholic"
  | "other_none"
  | "evangelical_by_belief";

export type ReferenceGroup = {
  label: string;
  /**
   * Unweighted respondent count. Small for e.g. Black Protestants (n=103) —
   * the results screen should caveat percentiles built on a small n.
   */
  n: number;
  /**
   * Scores of this group's real, survey-weighted respondents at evenly
   * spaced percentiles, ascending. Index i is the (100 * i / (n-1))th
   * percentile. Built from respondents who answered every `percentile_items`
   * question (the quiz has no skip path, so every reader's score is
   * comparable to this without adjustment).
   */
  curve: number[];
};

export type Reference = {
  source: string;
  url: string;
  /** Total respondents backing every curve (the "all" group's n). */
  n: number;
  group_order: ReferenceGroupKey[];
  groups: Partial<Record<ReferenceGroupKey, ReferenceGroup>>;
};

export type QuizData = {
  /** Stamps which probability blob produced a result. */
  data_version: string;
  responses: Response[];
  responses_3: Response[];
  traditions: Tradition[];
  baseline_group: string;
  constants: QuizConstants;
  years: number[];
  items: QuizItem[];
  /** How many items the workbook defines, usable or not. */
  expected_items: number;
  /** Items the workbook defines but has no usable data for yet. */
  pending_items: { id: string; reason: string }[];
  /**
   * The item ids counted in the percentile score — every usable item except
   * `arian` (2022-only; the real respondents behind `reference` were never
   * asked it, so it can't contribute to a score compared against them).
   */
  percentile_items: string[];
  /** The real-respondent data the percentile is computed against. */
  reference: Reference | null;
};

/**
 * A reader's answers: item id to the index of the chosen option within that
 * item's `scale`. An item the reader skipped is simply absent.
 */
export type AnswerMap = Record<string, number>;

export type TraditionScore = {
  tradition: Tradition;
  /** sum over answered items of ln P(r | tradition). Always negative. */
  logLikelihood: number;
};

export type Match = {
  top: TraditionScore;
  runnerUp: TraditionScore;
  all: TraditionScore[];
  /**
   * True when the top two are closer than TIE_MARGIN. Subgroup samples are
   * small; a hair's difference between two traditions is noise, and the
   * results screen should say "a tie" rather than pick one.
   */
  tie: boolean;
};

export type BreakdownRow = {
  item: QuizItem;
  response: Response;
  /** The item's weight for the chosen response, before shrinkage. */
  weight: number;
  /** Contribution to the reported score, i.e. weight / SHRINKAGE. */
  contribution: number;
};
