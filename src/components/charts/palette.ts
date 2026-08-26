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
 * chart, and the opacity it's drawn at. */
export const CONTEXT_GRAY = "var(--muted)";
export const CONTEXT_OPACITY = 0.45;

/** Which text color reads correctly on top of a given segment fill.
 * A literal map, not runtime luminance math — see docs/CHARTS.md. Every
 * paint value a stacked-bar or dot-plot label chart uses must have an
 * entry here; missing entries fall back to `var(--foreground)`, which is
 * only safe on the lightest fills. */
export const LABEL_ON: Record<string, string> = {
  "var(--accent)": "var(--surface)",
  "var(--honey)": "var(--surface)",
  "var(--oxblood)": "var(--surface)",
  "var(--foreground)": "var(--surface)",
  "var(--muted)": "var(--surface)",
  "var(--muted-soft)": "var(--foreground)",
  "var(--accent-soft)": "var(--foreground)",
  "var(--honey-soft)": "var(--foreground)",
  "var(--oxblood-soft)": "var(--foreground)",
  // The ordinal ramp's own tokens (see globals.css): steps 1-3 are the
  // faint end in both themes (a dark near-background navy in dark mode,
  // a pale tint in light mode) and read correctly with --foreground;
  // steps 5-7 are the intense end and read correctly with --surface, by
  // the same per-theme-authored-token logic. Step 4 sits at the light
  // theme's crossover, so it takes --foreground there and is close
  // enough in dark mode not to fail contrast noticeably.
  "var(--chart-ordinal-1)": "var(--foreground)",
  "var(--chart-ordinal-2)": "var(--foreground)",
  "var(--chart-ordinal-3)": "var(--foreground)",
  "var(--chart-ordinal-4)": "var(--foreground)",
  "var(--chart-ordinal-5)": "var(--surface)",
  "var(--chart-ordinal-6)": "var(--surface)",
  "var(--chart-ordinal-7)": "var(--surface)",
};

export function labelInkFor(paint: string): string {
  return LABEL_ON[paint] ?? "var(--foreground)";
}

/** Single-hue ordinal ramp (e.g. birth-decade shares within one tradition) —
 * a "which decade" scale rather than a second identity color. Its own
 * tokens (`--chart-ordinal-1..7` in globals.css), not a color-mix() built
 * from --accent: every semantic token in this palette flips which end
 * reads as "light" between themes, so mixing toward a token like
 * --foreground or --accent-soft as a fixed anchor produces a ramp that's
 * monotonic in light mode and inverted in dark mode. Faintest first. */
export const ACCENT_ORDINAL_RAMP = [
  "var(--chart-ordinal-1)",
  "var(--chart-ordinal-2)",
  "var(--chart-ordinal-3)",
  "var(--chart-ordinal-4)",
  "var(--chart-ordinal-5)",
  "var(--chart-ordinal-6)",
  "var(--chart-ordinal-7)",
] as const;
