/**
 * Direct labels in place of a legend — Burge's "label the line, not the
 * legend" convention. HTML overlays, percent-positioned, per the house
 * text rule (see axis.tsx's file comment for why).
 */

export function EndOfLineLabel({
  xPct,
  yPct,
  color,
  children,
}: {
  xPct: number;
  yPct: number;
  color: string;
  children: React.ReactNode;
}) {
  return (
    <span
      className="tabular-nums absolute -translate-y-1/2 whitespace-nowrap pl-2 text-xs font-medium"
      style={{ left: `${xPct}%`, top: `${yPct}%`, color }}
    >
      {children}
    </span>
  );
}

/** An in-segment percent label for a stacked bar. Suppressed by the caller
 * when the segment is too narrow to hold it (see stacked-bars.tsx). */
export function SegmentLabel({
  xPct,
  yPct,
  ink,
  children,
}: {
  xPct: number;
  yPct: number;
  ink: string;
  children: React.ReactNode;
}) {
  return (
    <span
      className="tabular-nums absolute -translate-x-1/2 -translate-y-1/2 text-[11px] font-medium"
      style={{ left: `${xPct}%`, top: `${yPct}%`, color: ink }}
    >
      {children}
    </span>
  );
}
