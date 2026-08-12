import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { Tag, type TagInk } from "@/components/tag";
import { fmtCompact, fmtDate } from "@/lib/format";
import { requireApologist } from "@/lib/permissions";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import type { HubVideo, HubVideoStatusValue } from "@/lib/types";

export const metadata: Metadata = {
  title: "Apologetics Hub",
  robots: { index: false, follow: false },
};

export const dynamic = "force-dynamic";

type SearchParams = { sort?: string };

type FeedVideo = HubVideo & {
  channel_name: string;
  channel_slug: string;
  working_on_it_count: number;
  responded_count: number;
};

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
  await requireApologist();
  const params = await searchParams;
  const sort = params.sort === "newest" ? "newest" : "priority";

  const supabase = createSupabaseServiceClient();

  const videosQuery = supabase
    .from("hub_videos")
    .select(
      "id, channel_id, youtube_video_id, title, published_at, duration_seconds, thumbnail_url, summary, view_count, view_count_updated_at, expected_views, debunkability, priority_score, video_status, analyzed_at, created_at, updated_at",
    );
  const { data: videoRows, error: videosError } =
    sort === "newest"
      ? await videosQuery.order("published_at", { ascending: false })
      : await videosQuery.order("priority_score", {
          ascending: false,
          nullsFirst: false,
        });
  if (videosError) throw videosError;

  const videos = (videoRows ?? []) as HubVideo[];

  const channelIds = [...new Set(videos.map((v) => v.channel_id))];
  const videoIds = videos.map((v) => v.id);

  const [{ data: channelRows, error: channelsError }, { data: statusRows, error: statusesError }] =
    await Promise.all([
      channelIds.length
        ? supabase.from("channel_full").select("id, name, slug").in("id", channelIds)
        : Promise.resolve({ data: [], error: null }),
      videoIds.length
        ? supabase
            .from("hub_video_statuses")
            .select("video_id, status")
            .in("video_id", videoIds)
        : Promise.resolve({ data: [], error: null }),
    ]);
  if (channelsError) throw channelsError;
  if (statusesError) throw statusesError;

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

  const feed: FeedVideo[] = videos.map((v) => {
    const channel = channelById.get(v.channel_id);
    const counts = statusCounts.get(v.id) ?? { working_on_it: 0, responded: 0 };
    return {
      ...v,
      channel_name: channel?.name ?? "Unknown channel",
      channel_slug: channel?.slug ?? "",
      working_on_it_count: counts.working_on_it,
      responded_count: counts.responded,
    };
  });

  return (
    <div>
      <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
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

      <div className="mt-8 flex items-center gap-2 text-sm">
        <span className="text-[color:var(--muted)]">Sort:</span>
        <Link
          href="/apologetics-hub?sort=priority"
          className={
            sort === "priority"
              ? "font-medium text-[color:var(--accent)]"
              : "text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
          }
        >
          Priority
        </Link>
        <span className="text-[color:var(--border)]">·</span>
        <Link
          href="/apologetics-hub?sort=newest"
          className={
            sort === "newest"
              ? "font-medium text-[color:var(--accent)]"
              : "text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
          }
        >
          Newest
        </Link>
      </div>

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
