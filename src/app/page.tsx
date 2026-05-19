import Link from "next/link";
import {
  getChannelsWithLatest,
  getFeaturedChannelsMix,
  getFeaturedStudies,
  getRisersAndFallers,
  getSiteStats,
} from "@/lib/data";
import { RisersFallers } from "@/components/risers-fallers";
import { colorsForType } from "@/lib/channel-types";
import { fmtCompact, fmtNumber } from "@/lib/format";

export const revalidate = 600;

export default async function Home() {
  const [stats, channels, featuredMix, studies, movers] = await Promise.all([
    getSiteStats(),
    getChannelsWithLatest(),
    getFeaturedChannelsMix(6),
    getFeaturedStudies(2),
    getRisersAndFallers(30, 5),
  ]);
  const top = channels
    .filter((c) => c.latest)
    .sort((a, b) => (b.latest!.subscribers ?? 0) - (a.latest!.subscribers ?? 0))
    .slice(0, 10);

  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      {/* Hero */}
      <section className="max-w-3xl">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
          Latter-day Stats
        </p>
        <h1 className="serif mt-4 text-4xl font-semibold leading-[1.05] tracking-tight sm:text-5xl md:text-6xl">
          Statistics, research, and creator data on the Latter-day Saint community.
        </h1>
        <p className="mt-6 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
          A public hub tracking LDS YouTube creators, academic studies, and
          community trends — sourced from public data and refreshed regularly.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href="/channels"
            className="inline-flex h-11 items-center rounded-full bg-[color:var(--accent)] px-5 text-sm font-medium text-white transition-colors hover:opacity-90"
          >
            Browse channels
          </Link>
          <Link
            href="/studies"
            className="inline-flex h-11 items-center rounded-full border border-[color:var(--border)] bg-white px-5 text-sm font-medium text-[color:var(--foreground)] transition-colors hover:bg-[color:var(--muted-soft)]"
          >
            Read studies
          </Link>
        </div>
      </section>

      {/* Core metric tiles */}
      {stats && (
        <section className="mt-16 grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-4">
          <MetricTile
            label="Channels tracked"
            value={fmtNumber(stats.total_channels)}
          />
          <MetricTile
            label="Combined subscribers"
            value={fmtCompact(stats.total_subscribers)}
          />
          <MetricTile
            label="Combined views"
            value={fmtCompact(stats.total_views)}
          />
          <MetricTile
            label="Total videos"
            value={fmtCompact(stats.total_videos)}
          />
        </section>
      )}

      {/* Featured channels */}
      {featuredMix.length > 0 && (
        <section className="mt-20">
          <div className="flex items-end justify-between gap-3">
            <h2 className="serif text-2xl font-semibold tracking-tight sm:text-3xl">
              Featured channels
            </h2>
            <Link
              href="/channels"
              className="text-sm text-[color:var(--accent)] hover:underline"
            >
              View all →
            </Link>
          </div>
          <ul className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {featuredMix.map((c) => {
              const { bg, text } = colorsForType(c.channel_type);
              return (
                <li key={c.id}>
                  <Link
                    href={`/channels/${c.slug}`}
                    className="group flex h-full items-center gap-4 rounded-2xl border border-[color:var(--border)] bg-white p-4 transition-colors hover:border-[color:var(--accent)]"
                  >
                    {c.thumbnail_url ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={c.thumbnail_url}
                        alt=""
                        className="h-14 w-14 shrink-0 rounded-full object-cover"
                      />
                    ) : (
                      <div className="h-14 w-14 shrink-0 rounded-full bg-[color:var(--muted-soft)]" />
                    )}
                    <div className="min-w-0 flex-1">
                      <h3 className="truncate text-sm font-semibold group-hover:text-[color:var(--accent)]">
                        {c.name}
                      </h3>
                      <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-[color:var(--muted)]">
                        {c.channel_type && (
                          <span
                            className={`rounded-full ${bg} ${text} px-2 py-0.5 text-[10px] uppercase tracking-wider`}
                          >
                            {c.channel_type}
                          </span>
                        )}
                        <span className="tabular-nums">
                          {fmtCompact(c.latest?.subscribers)} subs
                        </span>
                      </div>
                    </div>
                  </Link>
                </li>
              );
            })}
          </ul>
        </section>
      )}

      {/* Top channels */}
      <section className="mt-20">
        <div className="flex items-end justify-between gap-3">
          <h2 className="serif text-2xl font-semibold tracking-tight sm:text-3xl">
            Top channels by subscribers
          </h2>
          <Link
            href="/channels"
            className="text-sm text-[color:var(--accent)] hover:underline"
          >
            View all →
          </Link>
        </div>
        <ol className="mt-6 overflow-hidden rounded-2xl border border-[color:var(--border)] bg-white">
          {top.map((c, i) => (
            <li
              key={c.id}
              className={
                "flex items-center gap-4 px-5 py-3.5 " +
                (i > 0 ? "border-t border-[color:var(--border)]" : "")
              }
            >
              <span className="w-6 text-right text-sm text-[color:var(--muted)] tabular-nums">
                {i + 1}
              </span>
              <Link
                href={`/channels/${c.slug}`}
                className="flex min-w-0 flex-1 items-center gap-2 text-sm font-medium hover:text-[color:var(--accent)]"
              >
                <span className="truncate">{c.name}</span>
                {c.channel_type && (
                  <span className="shrink-0 rounded-full bg-[color:var(--muted-soft)] px-2.5 py-1 text-[10px] uppercase tracking-wider text-[color:var(--muted)]">
                    {c.channel_type}
                  </span>
                )}
              </Link>
              <span className="text-sm tabular-nums text-[color:var(--muted)]">
                {fmtCompact(c.latest?.subscribers)}
              </span>
            </li>
          ))}
        </ol>
      </section>

      <RisersFallers risers={movers.risers} fallers={movers.fallers} />

      {/* Featured studies */}
      {studies.length > 0 && (
        <section className="mt-20">
          <div className="flex items-end justify-between gap-3">
            <h2 className="serif text-2xl font-semibold tracking-tight sm:text-3xl">
              Featured studies
            </h2>
            <Link
              href="/studies"
              className="text-sm text-[color:var(--accent)] hover:underline"
            >
              View all →
            </Link>
          </div>
          <ul className="mt-6 grid gap-5 sm:grid-cols-2">
            {studies.map((s) => (
              <li key={s.id}>
                <Link
                  href={`/studies/${s.slug}`}
                  className="group block h-full rounded-2xl border border-[color:var(--border)] bg-white p-6 transition-colors hover:border-[color:var(--accent)]"
                >
                  <div className="flex flex-wrap items-center gap-2 text-xs text-[color:var(--muted)]">
                    {s.year && (
                      <span className="rounded-full bg-[color:var(--muted-soft)] px-2.5 py-1 tabular-nums">
                        {s.year}
                      </span>
                    )}
                    {s.tags.slice(0, 2).map((t) => (
                      <span
                        key={t}
                        className="rounded-full bg-[color:var(--accent-soft)] px-2.5 py-1 text-[color:var(--accent)]"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                  <h3 className="serif mt-4 text-lg font-semibold leading-snug tracking-tight group-hover:text-[color:var(--accent)]">
                    {s.title}
                  </h3>
                  {s.authors.length > 0 && (
                    <p className="mt-2 text-sm text-[color:var(--muted)]">
                      {s.authors.join(", ")}
                    </p>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

function MetricTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-[color:var(--border)] bg-white p-5">
      <div className="text-[11px] font-medium uppercase tracking-wider text-[color:var(--muted)]">
        {label}
      </div>
      <div className="serif mt-2 text-3xl font-semibold tabular-nums sm:text-4xl">
        {value}
      </div>
    </div>
  );
}
