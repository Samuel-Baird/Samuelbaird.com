import { fmtCompact, fmtDate } from "@/lib/format";

type Point = { captured_at: string; subscribers: number };

type Props = {
  data: Point[];
  height?: number;
  label?: string;
};

export function GrowthChart({ data, height = 200, label = "Subscribers" }: Props) {
  if (!data || data.length < 2) {
    return (
      <div className="rounded-2xl border border-dashed border-[color:var(--border)] bg-white p-6 text-center text-sm text-[color:var(--muted)]">
        Subscriber history will appear here once at least two snapshots have
        been collected.
      </div>
    );
  }

  const points = data
    .map((d) => ({
      iso: d.captured_at,
      t: new Date(d.captured_at).getTime(),
      v: d.subscribers,
    }))
    .filter((p) => Number.isFinite(p.t) && Number.isFinite(p.v));

  const tMin = points[0].t;
  const tMax = points[points.length - 1].t;
  const vMin = Math.min(...points.map((p) => p.v));
  const vMax = Math.max(...points.map((p) => p.v));
  const vSpan = Math.max(1, vMax - vMin);
  const tSpan = Math.max(1, tMax - tMin);

  const W = 800;
  const H = height;
  const padL = 8;
  const padR = 8;
  const padT = 8;
  const padB = 24;
  const innerW = W - padL - padR;
  const innerH = H - padT - padB;

  const x = (t: number) => padL + ((t - tMin) / tSpan) * innerW;
  const y = (v: number) => padT + innerH - ((v - vMin) / vSpan) * innerH;

  const path = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${x(p.t).toFixed(1)} ${y(p.v).toFixed(1)}`)
    .join(" ");

  const area =
    `M ${x(points[0].t).toFixed(1)} ${(padT + innerH).toFixed(1)} ` +
    points.map((p) => `L ${x(p.t).toFixed(1)} ${y(p.v).toFixed(1)}`).join(" ") +
    ` L ${x(points[points.length - 1].t).toFixed(1)} ${(padT + innerH).toFixed(1)} Z`;

  const first = points[0];
  const last = points[points.length - 1];
  const delta = last.v - first.v;
  const pct = first.v > 0 ? (delta / first.v) * 100 : 0;
  const up = delta >= 0;

  return (
    <div className="rounded-2xl border border-[color:var(--border)] bg-white p-5">
      <div className="flex items-end justify-between gap-3">
        <div>
          <div className="text-[11px] font-medium uppercase tracking-wider text-[color:var(--muted)]">
            {label} over time
          </div>
          <div className="mt-1 text-xs text-[color:var(--muted)]">
            {fmtDate(first.iso)} → {fmtDate(last.iso)}
          </div>
        </div>
        <div className="text-right">
          <div className="serif text-2xl font-semibold tabular-nums">
            {fmtCompact(last.v)}
          </div>
          <div
            className={
              "text-xs tabular-nums " +
              (up ? "text-emerald-700" : "text-red-700")
            }
          >
            {up ? "+" : ""}
            {fmtCompact(delta)} ({up ? "+" : ""}
            {pct.toFixed(1)}%)
          </div>
        </div>
      </div>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        preserveAspectRatio="none"
        role="img"
        aria-label={`${label} from ${fmtDate(first.iso)} to ${fmtDate(last.iso)}`}
        className="mt-4 h-44 w-full sm:h-52"
      >
        <path
          d={area}
          fill="var(--accent)"
          fillOpacity={0.08}
        />
        <path
          d={path}
          fill="none"
          stroke="var(--accent)"
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
          vectorEffect="non-scaling-stroke"
        />
        <circle cx={x(last.t)} cy={y(last.v)} r={3.5} fill="var(--accent)" />
      </svg>
    </div>
  );
}
