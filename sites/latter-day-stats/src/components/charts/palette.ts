/**
 * Series color and ink assignment for every chart on the site.
 *
 * SVG paint attributes and inline `style` take a CSS variable directly, so
 * unlike Tailwind class strings these can be looked up from a plain object
 * without tripping v4's inability to see constructed class names. Every
 * value here is a literal `var(...)` string for that reason — never build
 * one by concatenation.
 *
 * See docs/CHARTS.md "Color assignment" for the reasoning behind the
 * 4-series cap and the highlight-vs-gray convention.
 */

import type { TagInk } from "@/components/tag";

/** Canonical series order for a multi-series chart with no natural focus
 * (e.g. comparing four arbitrary channels). Matches the four Tag ink
 * families that carry meaning site-wide, so a chart never introduces a
 * color the reader hasn't already learned. */
export const SERIES_PAINT = [
  "var(--accent)",
  "var(--honey)",
  "var(--oxblood)",
  "var(--foreground)",
] as const;

/** Hard cap on distinct chart colors. Context series drawn in CONTEXT_GRAY
 * (below) don't count against this — that's how a highlight-vs-gray chart
 * can carry seven lines and still read cleanly. */
export const MAX_SERIES = 4;

/** Ink-family paint, hoisted from the eternal-increase-timeline figures so
 * any chart can paint a dot/bar in one of the five Tag families. */
export const INK_PAINT: Record<TagInk, string> = {
  ink: "var(--foreground)",
  accent: "var(--accent)",
  oxblood: "var(--oxblood)",
  honey: "var(--honey)",
  muted: "var(--muted)",
};

/** The "everything but the focal series" color for a highlight-vs-gray
 * chart. */
export const CONTEXT_GRAY = "var(--muted)";
