import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { Tag, type TagInk } from "@/components/tag";
import { fmtCompact, fmtDate } from "@/lib/format";
import { requireApologist } from "@/lib/permissions";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import {
  HUB_INGEST_STAGE_LABEL,
  hubIngestStage,
  type HubIngestStage,
  type HubVideo,
  type HubVideoStatusValue,
} from "@/lib/types";

export const metadata: Metadata = {
  title: "Apologetics Hub",
  robots: { index: false, follow: false },
};

export const dynamic = "force-dynamic";

type SearchParams = { sort?: string; stage?: string; hide?: string };

const SORT_OPTIONS = ["priority", "newest", "views", "expected"] as const;
type SortOption = (typeof SORT_OPTIONS)[number];

const SORT_LABEL: Record<SortOption, string> = {
  priority: "Priority",
  newest: "Newest",
  views: "Most viewed",
  expected: "Most expected views",
};

const HIDE_OPTIONS: HubVideoStatusValue[] = ["working_on_it", "responded"];

const HIDE_LABEL: Record<HubVideoStatusValue, string> = {
  working_on_it: "Hide: someone's working on it",
  responded: "Hide: already responded",
};

type FeedVideo = HubVideo & {
  channel_name: string;
  channel_slug: string;
  working_on_it_count: number;
  responded_count: number;
  ingest_stage: HubIngestStage;
};

const STAGE_INK: Record<HubIngestStage, TagInk> = {
  metadata_only: "muted",
  transcript_fetched: "honey",
  ai_analyzed: "accent",
};

const STAGE_OPTIONS: HubIngestStage[] = [
  "metadata_only",
  "transcript_fetched",
  "ai_analyzed",
];

// Hard cap on rows fetched per request. Without this, every downstream
// .in(id, [...]) call (channels, statuses, transcripts) grows with the
// total row count, and once that count reaches the thousands the resulting
// query URL exceeds PostgREST's limit and every request 400s — this is not
// a hypothetical, it happened in production once hub_videos passed ~6,000
// rows. 60 is generous for a "what to work on" feed; nobody needs more than
// that in view at once.
const FEED_LIMIT = 60;

function debunkabilityInk(score: number | null): TagInk {
  if (score == null) return "muted";
  if (score >= 8) return "oxblood";
  if (score >= 5) return "honey";
  return "muted";
}

function attentionRatio(video: HubVideo): number | null {
  if (!video.expected_views || video.expected_views <= 0) return null;
  return video.view_count / video.expected_views;
}

export default async function ApologeticsHubPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const auth = await requireApologist();
  const isAdmin = auth.profile?.is_admin === true;
  const params = await searchParams;
  const sort: SortOption = SORT_OPTIONS.includes(params.sort as SortOption)
    ? (params.sort as SortOption)
    : "priority";
  const stageFilter = STAGE_OPTIONS.includes(params.stage as HubIngestStage)
    ? (params.stage as HubIngestStage)
    : null;
  const hideStatuses = new Set(
    (params.hide ?? "")
      .split(",")
      .map((s) => s.trim())
      .filter((s): s is HubVideoStatusValue => HIDE_OPTIONS.includes(s as HubVideoStatusValue)),
  );

  const supabase = createSupabaseServiceClient();

  // Resolve "hide responded/working-on-it" to a bounded set of video ids to
  // exclude, before the row cap applies — same reasoning as the stage
  // pushdown below: filtering after the LIMIT would silently under-fill the
  // feed once a channel has a lot of claimed videos.
  let excludeIds: string[] = [];
  if (hideStatuses.size > 0) {
    const { data: hideRows, error: hideError } = await supabase
      .from("hub_video_statuses")
      .select("video_id")
      .in("status", [...hideStatuses]);
    if (hideError) throw hideError;
    excludeIds = [
      ...new Set((hideRows ?? []).map((r) => r.video_id as string)),
    ];
  }

  let videosQuery = supabase
    .from("hub_videos")
    .select(
      "id, channel_id, youtube_video_id, title, published_at, duration_seconds, thumbnail_url, summary, view_count, view_count_updated_at, expected_views, debunkability, priority_score, video_status, analyzed_at, lds_relevant, created_at, updated_at",
    )
    // Videos determined during analysis to not be about Latter-day
    // Saints/Mormonism are hidden here; not-yet-analyzed rows (null) stay
    // visible until a real determination is made.
    .or("lds_relevant.is.null,lds_relevant.eq.true");
  if (excludeIds.length > 0) {
    videosQuery = videosQuery.not("id", "in", `(${excludeIds.join(",")})`);
  }
  // Push the coarse half of the stage filter (analyzed vs. not) down to the
  // database before the row cap applies — otherwise, with thousands of
  // metadata-only rows outscored by every analyzed one on both sort orders,
  // "show me what still needs a transcript" would always return empty. The
  // finer metadata-only/transcript-fetched split happens after fetching,
  // against this already-bounded set.
  videosQuery =
    stageFilter === "ai_analyzed"
      ? videosQuery.not("debunkability", "is", null)
      : stageFilter
        ? videosQuery.is("debunkability", null)
        : videosQuery;
  const sortedQuery =
    sort === "newest"
      ? videosQuery.order("published_at", { ascending: false })
      : sort === "views"
        ? videosQuery.order("view_count", { ascending: false })
        : sort === "expected"
          ? videosQuery.order("expected_views", {
              ascending: false,
              nullsFirst: false,
            })
          : videosQuery.order("priority_score", {
              ascending: false,
              nullsFirst: false,
            });
  const { data: videoRows, error: videosError } = await sortedQuery.limit(
    FEED_LIMIT,
  );
  if (videosError) throw videosError;

  const videos = (videoRows ?? []) as HubVideo[];

  const channelIds = [...new Set(videos.map((v) => v.channel_id))];
  const videoIds = videos.map((v) => v.id);

  const [
    { data: channelRows, error: channelsError },
    { data: statusRows, error: statusesError },
    { data: transcriptRows, error: transcriptsError },
  ] = await Promise.all([
    channelIds.length
      ? supabase.from("channel_full").select("id, name, slug").in("id", channelIds)
      : Promise.resolve({ data: [], error: null }),
    videoIds.length
      ? supabase
          .from("hub_video_statuses")
          .select("video_id, status")
          .in("video_id", videoIds)
      : Promise.resolve({ data: [], error: null }),
    videoIds.length
      ? supabase.from("hub_transcripts").select("video_id").in("video_id", videoIds)
      : Promise.resolve({ data: [], error: null }),
  ]);
  if (channelsError) throw channelsError;
  if (statusesError) throw statusesError;
  if (transcriptsError) throw transcriptsError;

  const videoIdsWithTranscript = new Set(
    ((transcriptRows ?? []) as { video_id: string }[]).map((r) => r.video_id),
  );

  const channelById = new Map(
    ((channelRows ?? []) as { id: string; name: string; slug: string }[]).map(
      (c) => [c.id, c],
    ),
  );

  const statusCounts = new Map<string, { working_on_it: number; responded: number }>();
  for (const row of (statusRows ?? []) as {
    video_id: string;
    status: HubVideoStatusValue;
  }[]) {
    const counts = statusCounts.get(row.video_id) ?? {
      working_on_it: 0,
      responded: 0,
    };
    counts[row.status]++;
    statusCounts.set(row.video_id, counts);
  }

  const feedAll: FeedVideo[] = videos.map((v) => {
    const channel = channelById.get(v.channel_id);
    const counts = statusCounts.get(v.id) ?? { working_on_it: 0, responded: 0 };
    return {
      ...v,
      channel_name: channel?.name ?? "Unknown channel",
      channel_slug: channel?.slug ?? "",
      working_on_it_count: counts.working_on_it,
      responded_count: counts.responded,
      ingest_stage: hubIngestStage(v, videoIdsWithTranscript.has(v.id)),
    };
  });

  const feed = stageFilter
    ? feedAll.filter((v) => v.ingest_stage === stageFilter)
    : feedAll;

  function hrefFor(overrides: {
    sort?: SortOption;
    stage?: HubIngestStage | null;
    hide?: Set<HubVideoStatusValue>;
  }) {
    const qs = new URLSearchParams();
    qs.set("sort", overrides.sort ?? sort);
    const stage = overrides.stage !== undefined ? overrides.stage : stageFilter;
    if (stage) qs.set("stage", stage);
    const hide = overrides.hide ?? hideStatuses;
    if (hide.size > 0) qs.set("hide", [...hide].join(","));
    return `/apologetics-hub?${qs.toString()}`;
  }

  function toggledHide(status: HubVideoStatusValue): Set<HubVideoStatusValue> {
    const next = new Set(hideStatuses);
    if (next.has(status)) next.delete(status);
    else next.add(status);
    return next;
  }

  return (
    <div>
      <section className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6 sm:p-8">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-start">
          <div className="order-2 sm:order-1">
            <p className="small-caps text-xs font-medium text-[color:var(--honey)]">
              In Memory
            </p>
            <h2 className="serif mt-2 text-2xl font-semibold tracking-tight">
              Chandler David Hendry
            </h2>
            <p className="mt-4 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
              This resource is dedicated to the memory of Chandler David
              Hendry, who devoted his time to sharing and defending the
              restored gospel of Jesus Christ, engaging sincerely with those
              of other faiths, and helping Latter-day Saints better
              understand and articulate what they believe.
            </p>
            <blockquote className="mt-5 max-w-2xl border-l-2 border-[color:var(--honey)] pl-4 text-base italic leading-relaxed text-[color:var(--foreground)]">
              &ldquo;I think everyone should first understand what the
              Church&rsquo;s main truth claims are, and how to articulate
              them correctly, and how to defend them. And once you have that
              basic understanding, just start having good-faith
              discussions.&rdquo;
              <footer className="small-caps mt-2 text-xs font-medium not-italic text-[color:var(--muted)]">
                —{" "}
                <a
                  href="https://www.youtube.com/live/AwrFGqxSuO8?si=vCl3OZHzI9W_-t_b&t=3557"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[color:var(--accent)] hover:underline"
                >
                  Chandler David Hendry
                </a>
              </footer>
            </blockquote>
          </div>
          <Image
            src="/apologetics-hub/chandler-hendry.jpg"
            alt="Chandler David Hendry"
            width={331}
            height={335}
            className="order-1 w-full shrink-0 rounded-[var(--radius)] object-cover sm:order-2 sm:w-56"
          />
        </div>
      </section>

      <section className="mt-8 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6 sm:p-8">
        <h2 className="serif text-3xl font-semibold tracking-tight sm:text-4xl">
          About This Tool
        </h2>
        <p className="mt-4 max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
          The Apologetics Hub exists to help apologists find the content
          most worth responding to and give them good material to respond
          with — a feed of critical-channel videos, ranked by attention and
          debunkability, each paired with claim-level rebuttals and sources.
          It&apos;s meant to save the work of tracking every channel
          yourself and to keep real sourcing at the center of every
          response.
        </p>
        <p className="mt-3 max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
          We all work better when we work together. Collaborate, help each
          other, and mark what you&apos;re working on or have already
          responded to so effort isn&apos;t duplicated. If you have feedback
          on how to make this resource more useful, reach out to{" "}
          <a
            href="mailto:ithinksamofficial@gmail.com"
            className="text-[color:var(--accent)] hover:underline"
          >
            ithinksamofficial@gmail.com
          </a>
          .
        </p>
      </section>

      <p className="small-caps mt-12 text-xs font-medium text-[color:var(--accent)]">
        Apologetics Hub
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
        Videos to respond to
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
        Critical-channel videos with claim-level rebuttals and sources,
        ranked by how much attention they&apos;re getting and how
        debunkable they are. Visible only to accounts granted apologist
        access.
      </p>

      <div className="mt-8 flex flex-wrap items-center gap-2 text-sm">
        <span className="text-[color:var(--muted)]">Sort:</span>
        {SORT_OPTIONS.map((option, i) => (
          <span key={option} className="contents">
            {i > 0 && <span className="text-[color:var(--border)]">·</span>}
            <Link
              href={hrefFor({ sort: option })}
              className={
                sort === option
                  ? "font-medium text-[color:var(--accent)]"
                  : "text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
              }
            >
              {SORT_LABEL[option]}
            </Link>
          </span>
        ))}
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2 text-sm">
        {HIDE_OPTIONS.map((status, i) => {
          const active = hideStatuses.has(status);
          return (
            <span key={status} className="contents">
              {i > 0 && <span className="text-[color:var(--border)]">·</span>}
              <Link
                href={hrefFor({ hide: toggledHide(status) })}
                className={
                  active
                    ? "font-medium text-[color:var(--accent)]"
                    : "text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
                }
              >
                {active ? "✓ " : ""}
                {HIDE_LABEL[status]}
              </Link>
            </span>
          );
        })}
      </div>

      {isAdmin && (
        <div className="mt-3 flex flex-wrap items-center gap-2 text-sm">
          <span className="text-[color:var(--muted)]">
            Ingest stage (admin):
          </span>
          <Link
            href={hrefFor({ stage: null })}
            className={
              !stageFilter
                ? "font-medium text-[color:var(--accent)]"
                : "text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
            }
          >
            All
          </Link>
          {STAGE_OPTIONS.map((stage) => (
            <span key={stage} className="contents">
              <span className="text-[color:var(--border)]">·</span>
              <Link
                href={hrefFor({ stage })}
                className={
                  stageFilter === stage
                    ? "font-medium text-[color:var(--accent)]"
                    : "text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
                }
              >
                {HUB_INGEST_STAGE_LABEL[stage]}
              </Link>
            </span>
          ))}
        </div>
      )}

      {feed.length === 0 ? (
        <div className="mt-8 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-8 text-center text-sm text-[color:var(--muted)]">
          No videos yet. Run the ingest process documented in{" "}
          <code className="text-xs">APOLOGETICS_HUB_INGEST.md</code> to add
          the first ones.
        </div>
      ) : (
        <ul className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {feed.map((video) => {
            const ratio = attentionRatio(video);
            const thumb =
              video.thumbnail_url ??
              `https://i.ytimg.com/vi/${video.youtube_video_id}/hqdefault.jpg`;
            return (
              <li key={video.id}>
                <Link
                  href={`/apologetics-hub/${video.youtube_video_id}`}
                  className="group block h-full overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)] bg-white transition-colors hover:border-[color:var(--accent)]"
                >
                  <div className="relative aspect-[16/9] w-full overflow-hidden bg-[color:var(--muted-soft)]">
                    <Image
                      src={thumb}
                      alt=""
                      fill
                      sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
                      className="object-cover"
                    />
                    {video.video_status !== "active" && (
                      <span className="absolute bottom-2 left-2">
                        <Tag ink="muted">{video.video_status}</Tag>
                      </span>
                    )}
                  </div>
                  <div className="p-5">
                    <p className="small-caps text-xs text-[color:var(--muted)]">
                      {video.channel_name} · {fmtDate(video.published_at)}
                    </p>
                    <h2 className="serif mt-1.5 line-clamp-2 text-lg font-semibold tracking-tight group-hover:text-[color:var(--accent)]">
                      {video.title}
                    </h2>

                    <div className="mt-3 flex flex-wrap items-center gap-1.5">
                      <Tag ink={STAGE_INK[video.ingest_stage]}>
                        {HUB_INGEST_STAGE_LABEL[video.ingest_stage]}
                      </Tag>
                      <Tag ink={debunkabilityInk(video.debunkability)}>
                        Debunkability {video.debunkability ?? "—"}/10
                      </Tag>
                      {video.working_on_it_count > 0 && (
                        <Tag ink="accent">
                          {video.working_on_it_count} working on it
                        </Tag>
                      )}
                      {video.responded_count > 0 && (
                        <Tag ink="ink">
                          {video.responded_count} responded
                        </Tag>
                      )}
                    </div>

                    <dl className="mt-3 grid grid-cols-3 gap-2 text-xs text-[color:var(--muted)]">
                      <div>
                        <dt className="small-caps">Views</dt>
                        <dd className="tabular-nums text-[color:var(--foreground)]">
                          {fmtCompact(video.view_count)}
                        </dd>
                      </div>
                      <div>
                        <dt className="small-caps">Expected</dt>
                        <dd className="tabular-nums text-[color:var(--foreground)]">
                          {fmtCompact(video.expected_views)}
                        </dd>
                      </div>
                      <div>
                        <dt className="small-caps">Attention</dt>
                        <dd className="tabular-nums text-[color:var(--foreground)]">
                          {ratio != null ? `${ratio.toFixed(1)}×` : "—"}
                        </dd>
                      </div>
                    </dl>
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
