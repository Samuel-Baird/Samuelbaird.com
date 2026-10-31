import Image from "next/image";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import type { ChannelMover } from "@/lib/data";
import { fmtCompact } from "@/lib/format";

function Row({ c, up }: { c: ChannelMover; up: boolean }) {
  const tone = up ? "text-[color:var(--accent)]" : "text-[color:var(--oxblood)]";
  return (
    <li className="flex items-center gap-3 border-t border-[color:var(--border)] px-4 py-2.5 first:border-t-0">
      {c.thumbnail_url ? (
        <Image
          src={c.thumbnail_url}
          alt=""
          width={28}
          height={28}
          className="h-7 w-7 shrink-0 rounded-[var(--radius)] object-cover"
        />
      ) : (
        <div className="h-7 w-7 shrink-0 rounded-[var(--radius)] bg-[color:var(--muted-soft)]" />
      )}
      <Link
        href={`/channels/${c.slug}`}
        className="min-w-0 flex-1 truncate text-sm font-medium hover:text-[color:var(--accent)]"
      >
        {c.name}
      </Link>
      <div className={`shrink-0 text-right text-sm tabular-nums ${tone}`}>
        {up ? "▲ +" : "▼ "}
        {c.delta_pct.toFixed(1)}%
        <span className="ml-2 text-[11px] text-[color:var(--muted)]">
          {up ? "+" : ""}
          {fmtCompact(c.delta_subscribers)}
        </span>
      </div>
    </li>
  );
}

// Compact half-width take on /compare's risers & fallers: the top few of each.
export function HomeMovers({
  risers,
  fallers,
}: {
  risers: ChannelMover[];
  fallers: ChannelMover[];
}) {
  if (risers.length === 0 && fallers.length === 0) return null;
  return (
    <section aria-labelledby="home-movers">
      <div className="flex items-baseline justify-between gap-3">
        <h2
          id="home-movers"
          className="serif text-2xl font-semibold tracking-tight sm:text-3xl"
        >
          Movers this month
        </h2>
        <Link
          href="/compare"
          className="inline-flex items-center gap-1 text-sm font-medium text-[color:var(--accent)] hover:underline"
        >
          Compare
          <ArrowRight aria-hidden="true" size={14} />
        </Link>
      </div>
      <p className="mt-1 text-sm text-[color:var(--muted)]">
        Biggest subscriber changes over the last 30 days.
      </p>
      <div className="mt-6 overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)] bg-white">
        <ul>
          {risers.map((c) => (
            <Row key={c.id} c={c} up />
          ))}
        </ul>
        {risers.length > 0 && fallers.length > 0 && (
          <div className="border-t border-[color:var(--border)]" />
        )}
        <ul>
          {fallers.map((c) => (
            <Row key={c.id} c={c} up={false} />
          ))}
        </ul>
      </div>
    </section>
  );
}
