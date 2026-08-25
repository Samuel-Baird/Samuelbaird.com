/**
 * Console-runnable sanity checks on the shipped data blob, per the build
 * spec: weights finite, percentiles monotonic, and the modal-evangelical
 * answer set scores high. These are assertions about data.json, not unit
 * tests of the scoring functions in isolation — run them any time the
 * workbook changes and you want a fast "did the build produce something
 * sane" check without re-deriving the math by hand.
 *
 * Run in the browser console on the quiz page:
 *   import("/_next/static/chunks/...").then(...)  // not practical directly
 * Easier: paste into the console from the Node REPL, or call
 * `runEvangelicalQuizSelfTest()` — it's attached to `window` in dev builds
 * by the quiz page itself.
 */

import { matchTradition, percentileOf, scoreAnswers } from "./scoring";
import type { AnswerMap, QuizData } from "./types";

export type SelfTestResult = {
  name: string;
  pass: boolean;
  detail: string;
};

export function runSelfTest(data: QuizData): SelfTestResult[] {
  const results: SelfTestResult[] = [];

  // 1. Every weight is finite.
  const nonFinite: string[] = [];
  for (const item of data.items) {
    for (const w of item.w) {
      if (!Number.isFinite(w)) nonFinite.push(item.id);
    }
  }
  results.push({
    name: "weights finite",
    pass: nonFinite.length === 0,
    detail:
      nonFinite.length === 0
        ? `all ${data.items.length} items have finite weights`
        : `non-finite weight in: ${nonFinite.join(", ")}`,
  });

  // 2. Percentile breakpoints are monotonically non-decreasing.
  const bp = data.percentile_breakpoints;
  let monotonic = true;
  for (let i = 1; i < bp.length; i++) {
    if (bp[i] < bp[i - 1]) {
      monotonic = false;
      break;
    }
  }
  results.push({
    name: "percentile breakpoints monotonic",
    pass: monotonic,
    detail: monotonic
      ? `${bp.length} breakpoints, ascending from ${bp[0]?.toFixed(3)} to ${bp[
          bp.length - 1
        ]?.toFixed(3)}`
      : "breakpoints decrease somewhere — simulation or sort is broken",
  });

  // 3. Answering the modal Evangelical response to every question scores
  // high (top decile) on the synthetic curve.
  const modalAnswers: AnswerMap = {};
  for (const item of data.items) {
    const pe = item.p.Evangelical;
    let bestIdx = 0;
    let bestP = -Infinity;
    pe.forEach((p, i) => {
      if (p > bestP) {
        bestP = p;
        bestIdx = i;
      }
    });
    modalAnswers[item.id] = bestIdx;
  }
  const modalScore = scoreAnswers(data, modalAnswers);
  const modalPercentile = percentileOf(data, modalScore);
  results.push({
    name: "modal-evangelical answers score high",
    pass: modalPercentile >= 90,
    detail: `modal-Evangelical answers -> score ${modalScore.toFixed(
      3,
    )}, percentile ${modalPercentile.toFixed(1)} (expect >= 90)`,
  });

  // 4. Tradition match on the same modal-evangelical answers actually names
  // Evangelical as top or runner-up — a basic sanity check that the two
  // scoring paths agree with each other.
  const match = matchTradition(data, modalAnswers);
  const evangelicalRanked =
    match !== null &&
    (match.top.tradition === "Evangelical" || match.runnerUp.tradition === "Evangelical");
  results.push({
    name: "modal-evangelical answers match Evangelical tradition",
    pass: evangelicalRanked,
    detail: match
      ? `ranked: ${match.all.map((s) => `${s.tradition}=${s.logLikelihood.toFixed(2)}`).join(", ")}`
      : "matchTradition returned null (no items with data)",
  });

  return results;
}

/** Formats results for a console.table / console.log call. */
export function printSelfTest(results: SelfTestResult[]): void {
  const allPass = results.every((r) => r.pass);
  console.log(
    `%cHow-evangelical-are-you self-test: ${allPass ? "PASS" : "FAIL"}`,
    `color: ${allPass ? "green" : "red"}; font-weight: bold`,
  );
  for (const r of results) {
    console.log(`${r.pass ? "✓" : "✗"} ${r.name} — ${r.detail}`);
  }
}
