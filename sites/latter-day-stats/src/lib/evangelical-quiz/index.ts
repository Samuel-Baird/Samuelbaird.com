import rawData from "./data.json";
import type { QuizData } from "./types";

export type {
  AnswerMap,
  BreakdownRow,
  Match,
  QuizConstants,
  QuizData,
  QuizItem,
  Reference,
  ReferenceGroup,
  ReferenceGroupKey,
  Response,
  Tradition,
  TraditionScore,
} from "./types";

export {
  answeredCount,
  breakdown,
  displayOptions,
  fiveColumnPct,
  groupBreakdownRows,
  groupPercentiles,
  itemById,
  itemWavePercentile,
  matchTradition,
  percentileOf,
  percentileScore,
  responseLabel,
  scoreAnswers,
  TRADITION_LABEL,
} from "./scoring";
export type { GroupBreakdownRow, GroupPercentile } from "./scoring";

export { runSelfTest, printSelfTest } from "./self-test";
export type { SelfTestResult } from "./self-test";

/**
 * The probability blob, produced by
 * `python scripts/evangelical-quiz/build_data.py --xlsx <workbook> --out
 * src/lib/evangelical-quiz/data.json` from the State of Theology workbook.
 * Regenerate it — never hand-edit data.json — whenever the workbook changes.
 * See scripts/evangelical-quiz/README.md.
 */
export const QUIZ_DATA = rawData as QuizData;

/** How many of the workbook's items currently carry usable data. */
export const QUIZ_QUESTION_COUNT = QUIZ_DATA.items.length;

/** True once every item the workbook defines has usable data. */
export const QUIZ_IS_COMPLETE = QUIZ_DATA.pending_items.length === 0;
