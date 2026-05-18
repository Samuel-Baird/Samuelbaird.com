import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { BookmarkButton } from "@/components/bookmark-button";
import { getCurrentUser } from "@/lib/auth";
import { colorsForType } from "@/lib/channel-types";
import { getBookmarkSetForUser, getChannelBySlug } from "@/lib/data";
import { effectiveCountry, effectiveLanguage } from "@/lib/types";
import {
  fmtCompact,
  fmtNumber,
  fmtYearsSince,
  fmtAvgViews,
  fmtDate,
} from "@/lib/format";

export const revalidate = 600;

type RouteParams = { slug: string };

function isHttpUrl(value: string) {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}

function socialHref(value: string) {
  return isHttpUrl(value) ? value : `https://${value}`;
}

export async function generateMetadata({
  params,
}: {
  params: Promise<RouteParams>;
}): Promise<Metadata> {
  const { slug } = await params;
  const c = await getChannelBySlug(slug);
  if (!c) return { title: "Channel not found" };
  return {
    title: c.name,
    description: `Subscriber, view, and upload stats for the LDS YouTube channel ${c.name}.`,
  };
}

export default async function ChannelDetailPage({
  params,
}: {
  params: Promise<RouteParams>;
}) {
  const { slug } = await params;
  const [channel, auth] = await Promise.all([
    getChannelBySlug(slug),
    getCurrentUser(),
  ]);
  if (!channel) notFound();
  const bookmarks = auth ? await getBookmarkSetForUser(auth.user.id) : null;

  const yt = channel.latest;
  const ytLink = `https://www.youtube.com/channel/${channel.youtube_channel_id}`;
  const country = effectiveCountry(channel);
  const language = effectiveLanguage(channel);
  const location = [channel.city, channel.state, country]
    .filter(Boolean)
    .join(", ");
  const socialProfiles = [
    { label: "Facebook", url: channel.facebook_url },
    { label: "Instagram", url: channel.instagram_url },
    { label: "TikTok", url: channel.tiktok_url },
    { label: "X", url: channel.x_url },
  ].filter((profile): profile is { label: string; url: string } =>
    Boolean(profile.url),
  );

  const stats = [
    { label: "Subscribers", value: fmtCompact(yt?.subscribers) },
    { label: "Total views", value: fmtCompact(yt?.total_views) },
    { label: "Videos", value: fmtNumber(yt?.video_count) },
    {
      label: "Avg / video",
      value: fmtAvgViews(yt?.total_views, yt?.video_count),
    },
    { label: "Channel age", value: fmtYearsSince(channel.created_at_youtube) },
    { label: "Created", value: fmtDate(channel.created_at_youtube) },
  ];

  return (
    <div className="mx-auto max-w-4xl px-5 py-14 sm:px-8 sm:py-20">
      <Link
        href="/channels"
        className="text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
      >
        ← All channels
      </Link>

      {channel.channel_type && (() => {
        const { bg, text } = colorsForType(channel.channel_type);
        return (
          <div className="mt-6 flex flex-wrap items-center gap-2">
            <span
              className={`rounded-full ${bg} ${text} px-2.5 py-1 text-[10px] font-medium uppercase tracking-wider`}
            >
              {channel.channel_type}
            </span>
          </div>
        );
      })()}

      <div className="mt-6 flex items-center gap-5">
        {channel.thumbnail_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={channel.thumbnail_url}
            alt=""
            className="h-20 w-20 shrink-0 rounded-full object-cover sm:h-24 sm:w-24"
          />
        ) : (
          <div className="h-20 w-20 shrink-0 rounded-full bg-[color:var(--muted-soft)] sm:h-24 sm:w-24" />
        )}
        <h1 className="serif text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          {channel.name}
        </h1>
      </div>
      {(location || channel.owned_by || language) && (
        <dl className="mt-5 grid gap-3 text-sm text-[color:var(--muted)] sm:grid-cols-3">
          {location && (
            <div>
              <dt className="text-[10px] uppercase tracking-wider">Location</dt>
              <dd className="mt-1 text-[color:var(--foreground)]">{location}</dd>
            </div>
          )}
          {channel.owned_by && (
            <div>
              <dt className="text-[10px] uppercase tracking-wider">Owned by</dt>
              <dd className="mt-1 text-[color:var(--foreground)]">
                {channel.owned_by}
              </dd>
            </div>
          )}
          {language && (
            <div>
              <dt className="text-[10px] uppercase tracking-wider">Language</dt>
              <dd className="mt-1 text-[color:var(--foreground)]">
                {language}
              </dd>
            </div>
          )}
        </dl>
      )}
      <p className="mt-3 text-sm text-[color:var(--muted)]">
        YouTube ID:{" "}
        <code className="rounded bg-[color:var(--muted-soft)] px-1.5 py-0.5 text-xs">
          {channel.youtube_channel_id}
        </code>
      </p>
      <p className="mt-2 text-sm text-[color:var(--muted)]">
        LDS affiliation source:{" "}
        {channel.lds_affiliation_source &&
        isHttpUrl(channel.lds_affiliation_source) ? (
          <a
            href={channel.lds_affiliation_source}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
          >
            {channel.lds_affiliation_source}
          </a>
        ) : channel.lds_affiliation_source ? (
          <span className="text-[color:var(--foreground)]">
            {channel.lds_affiliation_source}
          </span>
        ) : ["Religious", "Critical", "Apologetics"].includes(
            channel.channel_type ?? "",
          ) ? (
          <span className="text-[color:var(--foreground)]">channel content</span>
        ) : (
          <span className="font-medium text-red-700">missing</span>
        )}
      </p>

      <div className="mt-6 flex flex-wrap gap-3">
        <a
          href={ytLink}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex h-11 items-center rounded-full bg-[color:var(--accent)] px-5 text-sm font-medium text-white transition-colors hover:opacity-90"
        >
          Open on YouTube ↗
        </a>
        <BookmarkButton
          targetType="channel"
          targetId={channel.id}
          initial={bookmarks?.channels.has(channel.id) ?? false}
          signedIn={Boolean(auth)}
          label="inline"
        />
        {auth?.profile?.is_admin && (
          <Link
            href={`/admin/channels/${channel.slug}/edit`}
            className="inline-flex h-11 items-center rounded-full border border-[color:var(--border)] px-5 text-sm font-medium text-[color:var(--foreground)] hover:bg-[color:var(--muted-soft)]"
          >
            Edit (admin)
          </Link>
        )}
      </div>

      {socialProfiles.length > 0 && (
        <div className="mt-5 flex flex-wrap items-center gap-2 text-sm">
          <span className="mr-1 text-[color:var(--muted)]">
            Other profiles:
          </span>
          {socialProfiles.map((profile) => (
            <a
              key={profile.label}
              href={socialHref(profile.url)}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex h-9 items-center rounded-full border border-[color:var(--border)] bg-white px-3 text-xs font-medium text-[color:var(--foreground)] hover:bg-[color:var(--muted-soft)]"
            >
              {profile.label}
            </a>
          ))}
        </div>
      )}

      <dl className="mt-10 grid grid-cols-2 gap-3 sm:grid-cols-3">
        {stats.map((s) => (
          <div
            key={s.label}
            className="rounded-2xl border border-[color:var(--border)] bg-white p-5"
          >
            <dt className="text-[11px] font-medium uppercase tracking-wider text-[color:var(--muted)]">
              {s.label}
            </dt>
            <dd className="serif mt-2 text-2xl font-semibold tabular-nums">
              {s.value}
            </dd>
          </div>
        ))}
      </dl>

      <p className="mt-10 text-xs text-[color:var(--muted)]">
        Last refreshed:{" "}
        {fmtDate(yt?.captured_at) ?? "—"}. Subscriber growth chart will appear
        once more snapshots have been collected.
      </p>
    </div>
  );
}
