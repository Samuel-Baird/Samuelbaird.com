/**
 * Apologetics Hub — shared priority_score formula, used by both
 * hub-insert-analysis.ts (fresh analysis) and hub-backfill-priority.ts
 * (recompute existing rows after the formula changes). Keep these two
 * scripts pointed at one implementation so they can't drift.
 *
 * priority = attention (view_count / expected_views) * severity
 *   (debunkability / 10) * recency
 *
 * recency is an exponential decay with a floor, not a hard cutoff: a video
 * published today gets a full ×1 multiplier; one HALF_LIFE_DAYS old gets
 * ×((1+FLOOR)/2); very old videos decay toward ×FLOOR but never below it, so
 * a genuinely still-viral old video (high attention) doesn't get buried
 * under a mediocre-but-fresh one — it's only deprioritized relative to an
 * equally-severe recent claim, which is the actual problem this corrects.
 */

const HALF_LIFE_DAYS = 180;
const FLOOR = 0.3;
const MS_PER_DAY = 86_400_000;

export function recencyMultiplier(publishedAt: string, now: Date = new Date()): number {
  const publishedMs = new Date(publishedAt).getTime();
  if (isNaN(publishedMs)) return FLOOR;
  const days = Math.max(0, (now.getTime() - publishedMs) / MS_PER_DAY);
  return FLOOR + (1 - FLOOR) * Math.pow(0.5, days / HALF_LIFE_DAYS);
}

export function computePriorityScore(params: {
  viewCount: number;
  expectedViews: number | null;
  debunkability: number | null;
  publishedAt: string;
  now?: Date;
}): number | null {
  if (params.debunkability == null) return null;
  const attention = params.viewCount / Math.max(params.expectedViews ?? 1, 1);
  const severity = params.debunkability / 10;
  const recency = recencyMultiplier(params.publishedAt, params.now);
  return Math.round(attention * severity * recency * 1000) / 1000;
}
