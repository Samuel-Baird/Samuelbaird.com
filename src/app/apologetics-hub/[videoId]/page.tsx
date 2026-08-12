import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Tag } from "@/components/tag";
import { VideoPanel } from "@/components/hub/video-panel";
import { StatusControls } from "@/components/hub/status-controls";
import { fmtCompact, fmtDate } from "@/lib/format";
import { requireApologist } from "@/lib/permissions";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import type {
  HubClaim,
  HubVideo,
  HubVideoStatusValue,
  HubVideoStatusWithUser,
} from "@/lib/types";

export const dynamic = "force-dynamic";

const YOUTUBE_ID_PATTERN = /^[A-Za-z0-9_-]{8,20}$/;

type PageProps = {
  params: Promise<{ videoId: string }>;
};

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { videoId } = await params;
  return {
    title: YOUTUBE_ID_PATTERN.test(videoId) ? "Apologetics Hub" : "Not found",
    robots: { index: false, follow: false },
  };
}

export default async function HubVideoPage({ params }: PageProps) {
  const auth = await requireApologist();
  const { videoId } = await params;

  if (!YOUTUBE_ID_PATTERN.test(videoId)) {
    notFound();
  }

  const supabase = createSupabaseServiceClient();

  const { data: video, error: videoError } = await supabase
    .from("hub_videos")
    .select(
      "id, channel_id, youtube_video_id, title, published_at, duration_seconds, thumbnail_url, summary, view_count, view_count_updated_at, expected_views, debunkability, priority_score, video_status, analyzed_at, created_at, updated_at",
    )
    .eq("youtube_video_id", videoId)
    .maybeSingle();
  if (videoError) throw videoError;
  if (!video) notFound();

  const typedVideo = video as HubVideo;

  const [
    { data: channel, error: channelError },
    { data: claimRows, error: claimsError },
    { data: statusRows, error: statusesError },
  ] = await Promise.all([
    supabase
      .from("channel_full")
      .select("name, slug")
      .eq("id", typedVideo.channel_id)
      .maybeSingle(),
    supabase
      .from("hub_claims")
      .select(
        "id, video_id, position, timestamp_seconds, excerpt, claim_summary, response, sources, created_at, updated_at",
      )
      .eq("video_id", typedVideo.id)
      .order("position", { ascending: true }),
    supabase
      .from("hub_video_statuses")
      .select("user_id, video_id, status, response_url, created_at, updated_at")
      .eq("video_id", typedVideo.id),
  ]);
  if (channelError) throw channelError;
  if (claimsError) throw claimsError;
  if (statusesError) throw statusesError;

  const claims = (claimRows ?? []) as HubClaim[];

  const statusRowsTyped = (statusRows ?? []) as {
    user_id: string;
    video_id: string;
    status: HubVideoStatusValue;
    response_url: string | null;
    created_at: string;
    updated_at: string;
  }[];

  const userIds = [...new Set(statusRowsTyped.map((s) => s.user_id))];
  const { data: profileRows, error: profilesError } = userIds.length
    ? await supabase
        .from("profiles")
        .select("id, full_name, email")
        .in("id", userIds)
    : { data: [], error: null };
  if (profilesError) throw profilesError;

  const profileById = new Map(
    ((profileRows ?? []) as {
      id: string;
      full_name: string | null;
      email: string | null;
    }[]).map((p) => [p.id, p]),
  );

  const allStatuses: HubVideoStatusWithUser[] = statusRowsTyped.map((s) => ({
    ...s,
    full_name: profileById.get(s.user_id)?.full_name ?? null,
    email: profileById.get(s.user_id)?.email ?? null,
  }));

  const ownStatus =
    allStatuses.find((s) => s.user_id === auth.user.id) ?? null;

  const ratio =
    typedVideo.expected_views && typedVideo.expected_views > 0
      ? typedVideo.view_count / typedVideo.expected_views
      : null;

  const currentPath = `/apologetics-hub/${typedVideo.youtube_video_id}`;

  return (
    <div>
      <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
        {channel?.name ?? "Unknown channel"} · {fmtDate(typedVideo.published_at)}
      </p>
      <h1 className="serif mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
        {typedVideo.title}
      </h1>
      {typedVideo.video_status !== "active" && (
        <div className="mt-3">
          <Tag ink="muted">
            {typedVideo.video_status === "removed"
              ? "Removed from YouTube — embed may not work"
              : "Now private — embed may not work"}
          </Tag>
        </div>
      )}
      {typedVideo.summary && (
        <p className="mt-4 max-w-3xl text-base leading-relaxed text-[color:var(--muted)]">
          {typedVideo.summary}
        </p>
      )}

      <div className="mt-8 grid gap-8 lg:grid-cols-[1fr_320px]">
        <div>
          <VideoPanel
            youtubeVideoId={typedVideo.youtube_video_id}
            claims={claims}
          />
        </div>

        <aside className="space-y-6">
          <div className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5">
            <h2 className="serif text-lg font-semibold tracking-tight">
              Ranking
            </h2>
            <dl className="mt-3 space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-[color:var(--muted)]">Views</dt>
                <dd className="tabular-nums">
                  {fmtCompact(typedVideo.view_count)}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-[color:var(--muted)]">Expected views</dt>
                <dd className="tabular-nums">
                  {fmtCompact(typedVideo.expected_views)}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-[color:var(--muted)]">Attention</dt>
                <dd className="tabular-nums">
                  {ratio != null ? `${ratio.toFixed(1)}×` : "—"}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-[color:var(--muted)]">Debunkability</dt>
                <dd className="tabular-nums">
                  {typedVideo.debunkability ?? "—"}/10
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-[color:var(--muted)]">Priority</dt>
                <dd className="tabular-nums">
                  {typedVideo.priority_score != null
                    ? typedVideo.priority_score.toFixed(2)
                    : "—"}
                </dd>
              </div>
            </dl>
          </div>

          <StatusControls
            videoId={typedVideo.id}
            currentPath={currentPath}
            ownStatus={ownStatus}
            allStatuses={allStatuses}
            currentUserId={auth.user.id}
          />
        </aside>
      </div>
    </div>
  );
}
