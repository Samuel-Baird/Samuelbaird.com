"use client";

/**
 * The percent-positioned hover tooltip the kit's line charts share. Renders
 * as an HTML overlay, not SVG `<text>` — the charts use
 * `preserveAspectRatio="none"` on their `<svg>`, which stretches SVG text
 * unevenly; an HTML overlay also inherits the site's fonts and theme for
 * free. Edge-flips horizontally near the right edge so it never runs off
 * the card.
 *
 * `anchor="point"` sits just above the hovered point itself (single-series
 * charts like growth-chart, where the tooltip should track the line).
 * `anchor="top"` (default) pins near the top of the chart regardless of
 * `yPct` (multi-series charts like comparison-chart and wave-line-chart,
 * where several values share one x position and stacking them at the
 * point would collide).
 */
export function ChartTooltip({
  xPct,
  yPct = 8,
  anchor = "top",
  align = "auto",
  children,
}: {
  xPct: number;
  yPct?: number;
  anchor?: "point" | "top";
  align?: "auto" | "left" | "right";
  children: React.ReactNode;
}) {
  const flip = align === "right" || (align === "auto" && xPct > 70);
  return (
    <div
      className="pointer-events-none absolute z-10 min-w-[120px] rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-3 py-2 text-xs"
      style={{
        left: `${xPct}%`,
        top: `${yPct}%`,
        transform: `translate(${flip ? "-100%" : "8px"}, ${anchor === "point" ? "-110%" : "0"})`,
      }}
    >
      {children}
    </div>
  );
}
