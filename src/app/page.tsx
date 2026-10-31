import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import {
  getChannelsWithLatest,
  getRecentlyAdded,
  getRisersAndFallers,
  getSiteStats,
  getStudies,
  getStudiesBySlugs,
  getStudiesCarouselMix,
} from "@/lib/data";
import {
  DATASETS,
  getAllGraphics,
  graphicId,
  type GalleryGraphic,
} from "@/lib/data-explorer";
import { getGraphicPostMap, isPublished } from "@/lib/graphic-posts";
import { getAllStudyGraphics, getStudyFolderSlugs } from "@/lib/study-graphics";
import { BeehiveMark } from "@/components/beehive-mark";
import { StudiesCarousel } from "@/components/studies-carousel";
import {
  TopStatsCarousel,
  type TopStatSlide,
} from "@/components/top-stats-carousel";
import { DeseretTitle } from "@/components/deseret-title";
import { HomeFeatureGrid, type HomeFeature } from "@/components/home-feature-grid";
import { HomeGraphicsStrip, type HomeGraphic } from "@/components/home-graphics-strip";
import { HomeMovers } from "@/components/home-movers";
import { Tag } from "@/components/tag";
import { inkForType } from "@/lib/channel-types";
import { fmtCompact, fmtNumber } from "@/lib/format";
import type { ChannelWithStats } from "@/lib/types";

export const metadata: Metadata = {
  alternates: { canonical: "/" },
};

const GRAPHICS_ON_HOME = 4;

// One graphic per dataset, so the strip shows range rather than several charts
// from one survey. The client component shuffles this pool on every visit.
function graphicPool(all: GalleryGraphic[]): HomeGraphic[] {
  const seen = new Set<string>();
  const pool: HomeGraphic[] = [];
  for (const g of all) {
    if (seen.has(g.datasetSlug)) continue;
    seen.add(g.datasetSlug);
    const id = graphicId(g);
    pool.push({
      key: `${g.datasetSlug}/${id}`,
      href: g.href ?? `/data-explorer/${g.datasetSlug}/graphics/${id}`,
      imageSrc: g.imageSrc,
      width: g.width,
      height: g.height,
      alt: g.alt,
      title: g.title,
      datasetName: g.datasetName,
    });
  }
  return pool;
}

export default async function Home() {
  const includeCritical = true;
  const studySlugs = getStudyFolderSlugs();
  const [stats, channels, randomStudies, recent, allStudies, movers, postMap, graphicStudies] =
    await Promise.all([
      getSiteStats(),
      getChannelsWithLatest({ includeCritical }),
      getStudiesCarouselMix(20),
      getRecentlyAdded(30, 3, { studies: false, includeCritical }),
      getStudies(),
      getRisersAndFallers(30, 3),
      getGraphicPostMap(),
      getStudiesBySlugs(studySlugs),
    ]);
  const topStatSlides = buildTopStatSlides(channels);

  // Public visitors only ever see published graphics (same rule as the gallery).
  const publishedGraphics = [
    ...getAllGraphics(),
    ...getAllStudyGraphics(graphicStudies),
  ].filter((g) => isPublished(postMap, g.datasetSlug, graphicId(g)));
  const graphicsPool = graphicPool(publishedGraphics);

  const topRiser = movers.risers[0];
  const features: HomeFeature[] = [
    {
      href: "/channels",
      title: "Channels",
      description:
        "Latter-day Saint YouTube creators, with subscriber, view and video counts refreshed regularly.",
      figure: stats ? `${fmtNumber(stats.total_channels)} creators tracked` : "Browse creators",
      icon: "channels",
    },
    {
      href: "/studies",
      title: "Studies",
      description:
        "Academic studies and research on the Latter-day Saint community, searchable by topic.",
      figure: `${fmtNumber(allStudies.length)} studies`,
      icon: "studies",
    },
    {
      href: "/data-explorer",
      title: "Data Explorer",
      description:
        "Public survey and statistical datasets, with quizzes, charts and write-ups for each.",
      figure: `${fmtNumber(DATASETS.length)} datasets · ${fmtNumber(publishedGraphics.length)} graphics`,
      icon: "data",
    },
    {
      href: "/data-explorer/tools/map-explorer",
      title: "Map Explorer",
      description:
        "A world map of membership, congregations, stakes, missions and temples by country.",
      figure: "Membership by country",
      icon: "map",
    },
    {
      href: "/compare",
      title: "Compare",
      description:
        "Risers and fallers, and side-by-side growth for up to four channels.",
      figure: topRiser
        ? `Top riser: ${topRiser.name}`
        : "Channel growth, side by side",
      icon: "compare",
    },
    {
      href: "/connect",
      title: "Use with AI",
      description:
        "Connect the data to Claude or ChatGPT and ask questions in plain language. Free, no account.",
      figure: "Claude · ChatGPT",
      icon: "ai",
    },
  ];

  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      {/* Hero */}
      <section className="max-w-3xl">
        <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
          Latter-day Stats
        </p>
        <h1 className="serif mt-4 text-4xl font-semibold leading-[1.05] tracking-tight sm:text-5xl md:text-6xl">
          <DeseretTitle text="Statistics, research, and creator data on the Latter-day Saint community." />
        </h1>
        <p className="mt-6 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
          A public hub tracking LDS YouTube creators, academic studies, survey
          datasets, and community trends — sourced from public data and
          refreshed regularly.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href="/channels"
            className="inline-flex h-11 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-5 text-sm font-medium text-white transition-colors hover:opacity-90"
          >
            Browse channels
          </Link>
          <Link
            href="/studies"
            className="inline-flex h-11 items-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-5 text-sm font-medium text-[color:var(--foreground)] transition-colors hover:bg-[color:var(--muted-soft)]"
          >
            Read studies
          </Link>
          <Link
            href="/data-explorer"
            className="inline-flex h-11 items-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-5 text-sm font-medium text-[color:var(--foreground)] transition-colors hover:bg-[color:var(--muted-soft)]"
          >
            Explore data
          </Link>
        </div>
      </section>

      {/* Site-wide numbers */}
      <section
        aria-label="The site at a glance"
        className="mt-16 grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-4"
      >
        {stats && (
          <>
            <MetricTile label="Channels tracked" value={fmtNumber(stats.total_channels)} />
            <MetricTile label="Combined subscribers" value={fmtCompact(stats.total_subscribers)} />
          </>
        )}
        <MetricTile label="Studies" value={fmtNumber(allStudies.length)} />
        <MetricTile label="Graphics" value={fmtNumber(publishedGraphics.length)} />
      </section>

      <HomeFeatureGrid features={features} />

      <TopStatsCarousel slides={topStatSlides} />

      <HomeGraphicsStrip pool={graphicsPool} count={GRAPHICS_ON_HOME} />

      <div className="dinkus mt-20" aria-hidden="true">
        <BeehiveMark className="h-3.5 w-3.5" />
      </div>

      <div className="mt-16 grid gap-12 lg:grid-cols-2">
        <HomeMovers risers={movers.risers} fallers={movers.fallers} />

        {recent.channels.length > 0 && (
          <section aria-labelledby="home-new">
            <div className="flex items-baseline justify-between gap-3">
              <h2
                id="home-new"
                className="serif text-2xl font-semibold tracking-tight sm:text-3xl"
              >
                New this month
              </h2>
              <Link
                href="/channels"
                className="inline-flex items-center gap-1 text-sm font-medium text-[color:var(--accent)] hover:underline"
              >
                All channels
                <ArrowRight aria-hidden="true" size={14} />
              </Link>
            </div>
            <p className="mt-1 text-sm text-[color:var(--muted)]">
              Added in the last 30 days.
            </p>
            <ul className="mt-6 space-y-3">
              {recent.channels.map((c) => {
                const tags = channelTagsOf(c);
                return (
                  <li key={c.id}>
                    <Link
                      href={`/channels/${c.slug}`}
                      className="group flex items-center gap-4 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-4 transition-colors hover:border-[color:var(--accent)]"
                    >
                      {c.thumbnail_url ? (
                        <Image
                          src={c.thumbnail_url}
                          alt=""
                          width={56}
                          height={56}
                          className="h-14 w-14 shrink-0 rounded-full object-cover"
                        />
                      ) : (
                        <div className="h-14 w-14 shrink-0 rounded-full bg-[color:var(--muted-soft)]" />
                      )}
                      <div className="min-w-0 flex-1">
                        <h3 className="truncate text-sm font-semibold group-hover:text-[color:var(--accent)]">
                          {c.name}
                        </h3>
                        <div className="mt-1 flex flex-wrap items-center gap-1.5 text-xs text-[color:var(--muted)]">
                          {tags.map((tag) => (
                            <Tag key={tag} ink={inkForType(tag)}>
                              {tag}
                            </Tag>
                          ))}
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
      </div>

      <StudiesCarousel studies={randomStudies} />
    </div>
  );
}

function MetricTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5">
      <div className="small-caps text-[11px] font-medium text-[color:var(--muted)]">
        {label}
      </div>
      <div className="serif mt-2 text-3xl font-semibold tabular-nums sm:text-4xl">
        {value}
      </div>
    </div>
  );
}

function channelTagsOf(c: ChannelWithStats): string[] {
  return c.channel_types?.length ? c.channel_types : c.channel_type ? [c.channel_type] : [];
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
      sublabel: channelTagsOf(channel)[0]
        ? `${channelTagsOf(channel)[0]} - ${sublabel}`
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
    channels: channels.filter((channel) =>
      channelTagsOf(channel).some(
        (tag) => tag.toLowerCase() === category.toLowerCase(),
      ),
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
