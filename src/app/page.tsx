import Link from "next/link";
import {
  getChannelsWithLatest,
  getFeaturedChannelsMix,
  getFeaturedStudies,
  getRisersAndFallers,
  getSiteStats,
  getStudyStats,
} from "@/lib/data";
import { RisersFallers } from "@/components/risers-fallers";
import {
  TopStatsCarousel,
  type TopStatSlide,
} from "@/components/top-stats-carousel";
import { colorsForType } from "@/lib/channel-types";
import { fmtCompact, fmtNumber } from "@/lib/format";
import type { ChannelWithStats } from "@/lib/types";

export const revalidate = 600;

export default async function Home() {
  const [stats, channels, featuredMix, studies, movers, studyStats] =
    await Promise.all([
      getSiteStats(),
      getChannelsWithLatest(),
      getFeaturedChannelsMix(6),
      getFeaturedStudies(2),
      getRisersAndFallers(30, 5),
      getStudyStats(),
    ]);
  const topStatSlides = buildTopStatSlides(channels);

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

      {studyStats.total > 0 && (
        <section className="mt-5">
          <div className="mb-3 flex items-center justify-between gap-3">
            <h2 className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
              Research library
            </h2>
            <Link
              href="/studies"
              className="text-xs font-medium text-[color:var(--accent)] hover:underline"
            >
              Browse studies →
            </Link>
          </div>
          <div className="grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-4">
            <MetricTile
              label="Studies tracked"
              value={fmtNumber(studyStats.total)}
            />
            <MetricTile
              label="Findings catalogued"
              value={fmtNumber(studyStats.findings)}
            />
            <MetricTile
              label="Topics covered"
              value={fmtNumber(studyStats.topics)}
            />
            <MetricTile
              label="Years spanned"
              value={formatYearSpan(studyStats.yearMin, studyStats.yearMax)}
            />
          </div>
        </section>
      )}

      <TopStatsCarousel slides={topStatSlides} />

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

function formatYearSpan(yearMin: number | null, yearMax: number | null) {
  if (!yearMin || !yearMax) return "—";
  if (yearMin === yearMax) return String(yearMin);
  return `${yearMin}–${yearMax}`;
}

function buildTopStatSlides(channels: ChannelWithStats[]): TopStatSlide[] {
  const withStats = channels.filter((channel) => channel.latest);
  const slides = [
    topChannelsSlide({
      channels: withStats,
      label: "Subscribers",
      title: "Top channels by subscribers",
      metricLabel: "Largest audience",
      eyebrow: "Subscribers",
      href: "/channels?sort=subscribers",
      value: (channel) => channel.latest?.subscribers ?? 0,
      format: fmtCompact,
      sublabel: "subscribers",
    }),
    topChannelsSlide({
      channels: withStats,
      label: "Views",
      title: "Most watched channels",
      metricLabel: "Top channel views",
      eyebrow: "Total views",
      href: "/channels?sort=total_views",
      value: (channel) => channel.latest?.total_views ?? 0,
      format: fmtCompact,
      sublabel: "views",
    }),
    topChannelsSlide({
      channels: withStats,
      label: "Videos",
      title: "Largest video libraries",
      metricLabel: "Top video count",
      eyebrow: "Videos published",
      href: "/channels?sort=video_count",
      value: (channel) => channel.latest?.video_count ?? 0,
      format: fmtCompact,
      sublabel: "videos",
    }),
    topChannelsSlide({
      channels: withStats.filter((channel) => {
        const videos = channel.latest?.video_count ?? 0;
        return videos >= 10;
      }),
      label: "Avg views",
      title: "Highest average views per video",
      metricLabel: "Best average",
      eyebrow: "Views per video",
      href: "/channels?sort=avg_views",
      value: averageViews,
      format: fmtCompact,
      sublabel: "avg views/video",
    }),
    categorySlide(withStats, "Apologetics", "subscribers"),
    categorySlide(withStats, "Music", "total_views"),
    categorySlide(withStats, "Church", "video_count"),
    categorySlide(withStats, "Education", "avg_views"),
  ];

  return slides.filter((slide): slide is TopStatSlide => Boolean(slide));
}

function topChannelsSlide({
  channels,
  label,
  title,
  metricLabel,
  eyebrow,
  href,
  value,
  format,
  sublabel,
}: {
  channels: ChannelWithStats[];
  label: string;
  title: string;
  metricLabel: string;
  eyebrow: string;
  href: string;
  value: (channel: ChannelWithStats) => number;
  format: (value: number | null | undefined) => string;
  sublabel: string;
}): TopStatSlide | null {
  const items = [...channels]
    .filter((channel) => value(channel) > 0)
    .sort((a, b) => value(b) - value(a))
    .slice(0, 5);

  const leader = items[0];
  if (!leader) return null;

  return {
    label,
    title,
    href,
    metricLabel,
    metricValue: format(value(leader)),
    eyebrow,
    items: items.map((channel) => ({
      id: channel.id,
      name: channel.name,
      href: `/channels/${channel.slug}`,
      value: format(value(channel)),
      sublabel: channel.channel_type
        ? `${channel.channel_type} - ${sublabel}`
        : sublabel,
    })),
  };
}

function categorySlide(
  channels: ChannelWithStats[],
  category: string,
  sort: "subscribers" | "total_views" | "video_count" | "avg_views",
): TopStatSlide | null {
  const metricMeta = {
    subscribers: {
      label: "Subscribers",
      metricLabel: "Category leader",
      sublabel: "subscribers",
      value: (channel: ChannelWithStats) => channel.latest?.subscribers ?? 0,
      format: fmtCompact,
    },
    total_views: {
      label: "Views",
      metricLabel: "Category leader",
      sublabel: "views",
      value: (channel: ChannelWithStats) => channel.latest?.total_views ?? 0,
      format: fmtCompact,
    },
    video_count: {
      label: "Videos",
      metricLabel: "Largest library",
      sublabel: "videos",
      value: (channel: ChannelWithStats) => channel.latest?.video_count ?? 0,
      format: fmtCompact,
    },
    avg_views: {
      label: "Avg views",
      metricLabel: "Best average",
      sublabel: "avg views/video",
      value: averageViews,
      format: fmtCompact,
    },
  }[sort];

  return topChannelsSlide({
    channels: channels.filter(
      (channel) => channel.channel_type?.toLowerCase() === category.toLowerCase(),
    ),
    label: category,
    title: `Top ${category.toLowerCase()} channels`,
    metricLabel: metricMeta.metricLabel,
    eyebrow: `${category} - ${metricMeta.label}`,
    href: `/channels?type=${encodeURIComponent(category)}`,
    value: metricMeta.value,
    format: metricMeta.format,
    sublabel: metricMeta.sublabel,
  });
}

function averageViews(channel: ChannelWithStats) {
  const views = channel.latest?.total_views ?? 0;
  const videos = channel.latest?.video_count ?? 0;
  return videos > 0 ? Math.round(views / videos) : 0;
}
