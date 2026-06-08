import type { ChangelogSection } from "@/lib/types";

export type Pair = {
  left: ChangelogSection | null;
  right: ChangelogSection | null;
  manual?: boolean;
};

export type ManualLink = { leftId: string; rightId: string };

function normalizeHeading(h: string | null | undefined): string {
  if (!h) return "";
  return h
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * Run LCS-based heading alignment on a slice of each list, returning pairs.
 * Sections without headings are paired positionally within unmatched gaps.
 */
function alignSlice(left: ChangelogSection[], right: ChangelogSection[]): Pair[] {
  const lh = left.map((s) => normalizeHeading(s.heading));
  const rh = right.map((s) => normalizeHeading(s.heading));

  const lAnchors = lh.map((h, i) => (h ? i : -1)).filter((i) => i >= 0);
  const rAnchors = rh.map((h, i) => (h ? i : -1)).filter((i) => i >= 0);
  const lAnchorHeadings = lAnchors.map((i) => lh[i]);
  const rAnchorHeadings = rAnchors.map((i) => rh[i]);

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

  const matchedL: number[] = [];
  const matchedR: number[] = [];
  let i = n, j = m;
  while (i > 0 && j > 0) {
    if (lAnchorHeadings[i - 1] === rAnchorHeadings[j - 1]) {
      matchedL.unshift(lAnchors[i - 1]);
      matchedR.unshift(rAnchors[j - 1]);
      i--; j--;
    } else if (dp[i - 1][j] >= dp[i][j - 1]) {
      i--;
    } else {
      j--;
    }
  }

  const matchedLSet = new Set(matchedL);
  const matchedRSet = new Set(matchedR);
  const pairs: Pair[] = [];
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

/**
 * Align two section lists. Manual links are treated as forced anchors —
 * they are resolved first (in left-ordinal order), then LCS alignment runs
 * independently on each gap between consecutive anchors.
 */
export function alignSections(
  left: ChangelogSection[],
  right: ChangelogSection[],
  manualLinks: ManualLink[] = [],
): Pair[] {
  if (manualLinks.length === 0) return alignSlice(left, right);

  const leftById = new Map(left.map((s, i) => [s.id, i]));
  const rightById = new Map(right.map((s, i) => [s.id, i]));

  // Resolve manual links to index pairs, discard any whose IDs aren't found
  const forcedRaw = manualLinks
    .map((link) => ({
      li: leftById.get(link.leftId) ?? -1,
      ri: rightById.get(link.rightId) ?? -1,
    }))
    .filter(({ li, ri }) => li >= 0 && ri >= 0);

  // Sort by left index and remove any that would violate order on either side
  forcedRaw.sort((a, b) => a.li - b.li);
  const forced: { li: number; ri: number }[] = [];
  let maxRi = -1;
  for (const anchor of forcedRaw) {
    if (anchor.ri > maxRi) {
      forced.push(anchor);
      maxRi = anchor.ri;
    }
  }

  const pairs: Pair[] = [];
  const forcedLSet = new Set(forced.map((f) => f.li));
  const forcedRSet = new Set(forced.map((f) => f.ri));

  // Walk through gaps between forced anchors
  const segments = [
    ...forced.map((f, k) => ({ li: f.li, ri: f.ri })),
    { li: left.length, ri: right.length },
  ];
  let prevLi = 0;
  let prevRi = 0;

  for (let k = 0; k < segments.length; k++) {
    const { li, ri } = segments[k];
    const isForced = k < forced.length;

    // Slice of each side that falls between previous and current anchor,
    // excluding any sections that are themselves forced anchors in between
    const leftSlice = left
      .slice(prevLi, li)
      .filter((_, idx) => !forcedLSet.has(prevLi + idx));
    const rightSlice = right
      .slice(prevRi, ri)
      .filter((_, idx) => !forcedRSet.has(prevRi + idx));

    pairs.push(...alignSlice(leftSlice, rightSlice));

    if (isForced) {
      pairs.push({ left: left[li], right: right[ri], manual: true });
      prevLi = li + 1;
      prevRi = ri + 1;
    }
  }

  return pairs;
}
