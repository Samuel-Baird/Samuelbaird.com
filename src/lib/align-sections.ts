import type { ChangelogSection } from "@/lib/types";

type Pair = { left: ChangelogSection | null; right: ChangelogSection | null };

function normalizeHeading(h: string | null | undefined): string {
  if (!h) return "";
  return h
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * Align two section lists using LCS on normalized headings, then insert
 * unmatched sections as single-sided pairs in their original positions.
 *
 * Sections without headings are treated as anonymous and paired positionally
 * within the groups of unmatched sections between each LCS anchor.
 */
export function alignSections(
  left: ChangelogSection[],
  right: ChangelogSection[],
): Pair[] {
  const lh = left.map((s) => normalizeHeading(s.heading));
  const rh = right.map((s) => normalizeHeading(s.heading));

  // Only anchor on non-empty headings
  const lAnchors = lh.map((h, i) => (h ? i : -1)).filter((i) => i >= 0);
  const rAnchors = rh.map((h, i) => (h ? i : -1)).filter((i) => i >= 0);

  const lAnchorHeadings = lAnchors.map((i) => lh[i]);
  const rAnchorHeadings = rAnchors.map((i) => rh[i]);

  // LCS on heading strings at anchor positions
  const n = lAnchorHeadings.length;
  const m = rAnchorHeadings.length;
  const dp: number[][] = Array.from({ length: n + 1 }, () =>
    new Array(m + 1).fill(0),
  );
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      dp[i][j] =
        lAnchorHeadings[i - 1] === rAnchorHeadings[j - 1]
          ? dp[i - 1][j - 1] + 1
          : Math.max(dp[i - 1][j], dp[i][j - 1]);
    }
  }

  // Backtrack to get matched anchor index pairs
  const matchedL: number[] = [];
  const matchedR: number[] = [];
  let i = n,
    j = m;
  while (i > 0 && j > 0) {
    if (lAnchorHeadings[i - 1] === rAnchorHeadings[j - 1]) {
      matchedL.unshift(lAnchors[i - 1]);
      matchedR.unshift(rAnchors[j - 1]);
      i--;
      j--;
    } else if (dp[i - 1][j] >= dp[i][j - 1]) {
      i--;
    } else {
      j--;
    }
  }

  const matchedLSet = new Set(matchedL);
  const matchedRSet = new Set(matchedR);

  const pairs: Pair[] = [];
  // Sentinel anchor at the end
  const anchors = [
    ...matchedL.map((li, k) => ({ li, ri: matchedR[k] })),
    { li: left.length, ri: right.length },
  ];

  let prevLi = 0;
  let prevRi = 0;

  for (const { li, ri } of anchors) {
    const unmatchedL = left
      .slice(prevLi, li)
      .filter((_, idx) => !matchedLSet.has(prevLi + idx));
    const unmatchedR = right
      .slice(prevRi, ri)
      .filter((_, idx) => !matchedRSet.has(prevRi + idx));

    const gapLen = Math.max(unmatchedL.length, unmatchedR.length);
    for (let g = 0; g < gapLen; g++) {
      pairs.push({ left: unmatchedL[g] ?? null, right: unmatchedR[g] ?? null });
    }

    if (li < left.length && ri < right.length) {
      pairs.push({ left: left[li], right: right[ri] });
      prevLi = li + 1;
      prevRi = ri + 1;
    }
  }

  return pairs;
}
