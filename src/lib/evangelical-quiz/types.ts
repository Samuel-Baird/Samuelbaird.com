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
};

export type QuizConstants = {
  EVANGELICAL_SHARE: number;
  PROB_FLOOR: number;
  NEG_FLOOR: number;
  SHRINKAGE: number;
  SIM_N: number;
  SIM_SEED: number;
  TIE_MARGIN: number;
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
   * Scores of the synthetic national population at evenly spaced
   * percentiles, ascending. Index i is the (100 * i / (n-1))th percentile.
   */
  percentile_breakpoints: number[];
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
