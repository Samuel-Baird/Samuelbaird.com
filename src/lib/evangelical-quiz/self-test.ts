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

import { matchTradition, percentileOf, percentileScore } from "./scoring";
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

  // 2. Every reference group's percentile curve is monotonically
  // non-decreasing.
  const reference = data.reference;
  const nonMonotonic: string[] = [];
  for (const key of reference?.group_order ?? []) {
    const curve = reference?.groups[key]?.curve ?? [];
    for (let i = 1; i < curve.length; i++) {
      if (curve[i] < curve[i - 1]) {
        nonMonotonic.push(key);
        break;
      }
    }
  }
  results.push({
    name: "reference percentile curves monotonic",
    pass: reference !== null && nonMonotonic.length === 0,
    detail:
      reference === null
        ? "no reference data in this blob"
        : nonMonotonic.length === 0
          ? `all ${reference.group_order.length} group curves ascending`
          : `curve decreases somewhere in: ${nonMonotonic.join(", ")}`,
  });

  // 3. percentile_items is every usable item except arian (2022-only — the
  // real respondents behind `reference` were never asked it).
  const percentileItemsOk =
    !data.percentile_items.includes("arian") &&
    data.percentile_items.length === data.items.filter((i) => i.id !== "arian").length;
  results.push({
    name: "percentile_items excludes arian",
    pass: percentileItemsOk,
    detail: `${data.percentile_items.length} percentile items of ${data.items.length} total`,
  });

  // 4. The "all" curve's median is self-consistent: looking its own p50
  // breakpoint back up should return ~50.
  const allCurve = reference?.groups.all?.curve ?? [];
  const median = allCurve[Math.round((allCurve.length - 1) / 2)];
  const medianPercentile = median !== undefined ? percentileOf(data, median) : NaN;
  results.push({
    name: "median is self-consistent",
    pass: Math.abs(medianPercentile - 50) <= 2,
    detail: `percentileOf(median score ${median?.toFixed(3)}) = ${medianPercentile.toFixed(1)} (expect ~50)`,
  });

  // 5. RELTRAD-based group counts sum to the "all" group's count — the five
  // traditions should partition every respondent exactly once.
  const reltradKeys = ["evangelical", "black_protestant", "mainline", "catholic", "other_none"] as const;
  const reltradSum = reltradKeys.reduce((sum, k) => sum + (reference?.groups[k]?.n ?? 0), 0);
  const allN = reference?.groups.all?.n ?? -1;
  results.push({
    name: "RELTRAD group counts sum to all-Americans count",
    pass: reltradSum === allN && allN > 0,
    detail: `${reltradKeys.map((k) => `${k}=${reference?.groups[k]?.n ?? 0}`).join(" + ")} = ${reltradSum} (all=${allN})`,
  });

  // 6. Answering the modal Evangelical response to every question scores
  // high (top decile) against the empirical all-Americans curve.
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
  const modalScore = percentileScore(data, modalAnswers);
  const modalPercentile = percentileOf(data, modalScore);
  results.push({
    name: "modal-evangelical answers score high",
    pass: modalPercentile >= 90,
    detail: `modal-Evangelical answers -> score ${modalScore.toFixed(
      3,
    )}, percentile ${modalPercentile.toFixed(1)} (expect >= 90)`,
  });

  // 7. The same modal-evangelical answers should land in the top half of
  // the Evangelical group's own curve — a consistency check between the
  // per-item weights (which come from the Evangelical vs. not-Evangelical
  // contrast) and the empirical Evangelical percentile curve.
  const evangelicalPercentile = percentileOf(data, modalScore, "evangelical");
  results.push({
    name: "modal-evangelical answers rank high among evangelicals too",
    pass: evangelicalPercentile >= 75,
    detail: `percentile among evangelicals: ${evangelicalPercentile.toFixed(1)} (expect >= 75)`,
  });

  // 8. Tradition match on the same modal-evangelical answers actually names
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
