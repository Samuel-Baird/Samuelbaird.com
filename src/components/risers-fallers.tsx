import Link from "next/link";
import type { ChannelMover } from "@/lib/data";
import { fmtCompact, fmtDate } from "@/lib/format";

type Tone = "up" | "down";

function Sparkline({
  data,
  tone,
}: {
  data: { captured_at: string; subscribers: number }[];
  tone: Tone;
}) {
  if (!data || data.length < 2) {
    return <div className="h-8 w-20" aria-hidden="true" />;
  }
  const W = 80;
  const H = 32;
  const xs = data.map((p) => new Date(p.captured_at).getTime());
  const ys = data.map((p) => p.subscribers);
  const tMin = xs[0];
  const tMax = xs[xs.length - 1];
  const vMin = Math.min(...ys);
  const vMax = Math.max(...ys);
  const tSpan = Math.max(1, tMax - tMin);
  const vSpan = Math.max(1, vMax - vMin);
  const x = (t: number) => ((t - tMin) / tSpan) * W;
  const y = (v: number) => H - ((v - vMin) / vSpan) * H;
  const path = data
    .map(
      (p, i) =>
        `${i === 0 ? "M" : "L"} ${x(xs[i]).toFixed(1)} ${y(p.subscribers).toFixed(1)}`,
    )
    .join(" ");
  const stroke = tone === "up" ? "rgb(4 120 87)" : "rgb(185 28 28)";
  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      preserveAspectRatio="none"
      className="h-8 w-20 shrink-0"
      aria-hidden="true"
    >
      <path
        d={path}
        fill="none"
        stroke={stroke}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
}

function MoverList({
  title,
  tone,
  channels,
  emptyMsg,
}: {
  title: string;
  tone: Tone;
  channels: ChannelMover[];
  emptyMsg: string;
}) {
  const up = tone === "up";
  const toneText = up ? "text-emerald-700" : "text-red-700";
  const arrow = up ? "▲" : "▼";
  return (
    <div className="overflow-hidden rounded-2xl border border-[color:var(--border)] bg-white">
      <div className="flex items-center justify-between border-b border-[color:var(--border)] px-5 py-3">
        <span className="text-sm font-semibold">{title}</span>
        <span className={"text-xs " + toneText}>{arrow} 30d</span>
      </div>
      {channels.length === 0 ? (
        <p className="px-5 py-6 text-sm text-[color:var(--muted)]">{emptyMsg}</p>
      ) : (
        <ol>
          {channels.map((c, i) => (
            <li
              key={c.id}
              className={
                "flex items-center gap-3 px-4 py-3 sm:px-5 " +
                (i > 0 ? "border-t border-[color:var(--border)]" : "")
              }
            >
              <span className="w-4 shrink-0 text-right text-xs text-[color:var(--muted)] tabular-nums">
                {i + 1}
              </span>
              {c.thumbnail_url ? (
                /* eslint-disable-next-line @next/next/no-img-element */
                <img
                  src={c.thumbnail_url}
                  alt=""
                  className="h-8 w-8 shrink-0 rounded-full object-cover"
                />
              ) : (
                <div className="h-8 w-8 shrink-0 rounded-full bg-[color:var(--muted-soft)]" />
              )}
              <Link
                href={`/channels/${c.slug}`}
                className="min-w-0 flex-1 truncate text-sm font-medium hover:text-[color:var(--accent)]"
              >
                {c.name}
              </Link>
              <Sparkline data={c.history} tone={tone} />
              <div className="w-16 shrink-0 text-right">
                <div className={"text-sm tabular-nums " + toneText}>
                  {up ? "+" : ""}
                  {c.delta_pct.toFixed(1)}%
                </div>
                <div className="text-[10px] tabular-nums text-[color:var(--muted)]">
                  {up ? "+" : ""}
                  {fmtCompact(c.delta_subscribers)}
                </div>
              </div>
            </li>
          ))}
        </ol>
      )}
      {channels.length > 0 && (
        <div className="border-t border-[color:var(--border)] bg-[color:var(--muted-soft)]/40 px-5 py-2 text-[11px] text-[color:var(--muted)]">
          Since {fmtDate(channels[0].baseline_captured_at)}
        </div>
      )}
    </div>
  );
}

export function RisersFallers({
  risers,
  fallers,
}: {
  risers: ChannelMover[];
  fallers: ChannelMover[];
}) {
  const hasMovers = risers.length > 0 || fallers.length > 0;
  if (!hasMovers) return null;
  return (
    <section className="mt-20">
      <div className="flex items-end justify-between gap-3">
        <div>
          <h2 className="serif text-2xl font-semibold tracking-tight sm:text-3xl">
            Risers & Fallers
          </h2>
          <p className="mt-1 text-sm text-[color:var(--muted)]">
            Biggest subscriber moves over the last 30 days.
          </p>
        </div>
      </div>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <MoverList
          title="Risers"
          tone="up"
          channels={risers}
          emptyMsg="No risers in this window yet."
        />
        <MoverList
          title="Fallers"
          tone="down"
          channels={fallers}
          emptyMsg="No fallers in this window yet."
        />
      </div>
    </section>
  );
}
