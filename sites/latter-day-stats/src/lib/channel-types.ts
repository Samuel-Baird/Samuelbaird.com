/**
 * Visual styling for channel type tags.
 *
 * The Archive direction uses one small ink family (ink, accent blue,
 * oxblood, honey) rather than a distinct pastel per type — 19 different
 * hues is what reads as "vibe-coded." Types are grouped by what they mean,
 * not given individual colors, so the palette stays legible and the
 * grouping itself carries meaning:
 *   - accent (blue): faith-affiliated / institutional
 *   - honey: culture, lifestyle, media
 *   - oxblood: critical / outside perspectives
 *   - ink: everything else (education, ancestry, neutral)
 * Unknown types fall back to muted so new types added later still render
 * cleanly without code changes.
 */

import type { TagInk } from "@/components/tag";

const NEUTRAL: TagInk = "muted";

export const TYPE_INK: Record<string, TagInk> = {
  // Faith-affiliated / institutional
  Religious: "accent",
  Church: "accent",
  BYU: "accent",
  "Gen. Conf. Video Reposts": "accent",
  "General Religious": "accent",
  Apologetics: "accent",

  // Critical / outside
  Critical: "oxblood",
  Investigator: "oxblood",
  Politics: "oxblood",
  "Not LDS": "oxblood",

  // Lifestyle / culture / media
  Music: "honey",
  Children: "honey",
  Youth: "honey",
  News: "honey",
  TV: "honey",

  // Neutral / reference
  Education: "ink",
  "Church History": "ink",
  Ancestry: "ink",
  Business: "ink",
};

export function inkForType(type: string | null | undefined): TagInk {
  if (!type) return NEUTRAL;
  return TYPE_INK[type] ?? NEUTRAL;
}
