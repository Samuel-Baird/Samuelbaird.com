import Link from "next/link";
import { BookmarkButton } from "@/components/bookmark-button";
import { Tag } from "@/components/tag";
import { requireUser } from "@/lib/auth";
import {
  getBookmarkedChannelsForUser,
  getBookmarkedStudiesForUser,
} from "@/lib/data";
import {
  fmtAvgViews,
  fmtCompact,
  fmtNumber,
  fmtYearsSince,
} from "@/lib/format";

export const dynamic = "force-dynamic";

type SearchParams = { tab?: string };

export default async function BookmarksPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const [{ user }, params] = await Promise.all([requireUser(), searchParams]);
  const [channels, studies] = await Promise.all([
    getBookmarkedChannelsForUser(user.id),
    getBookmarkedStudiesForUser(user.id),
  ]);
  const tab = params.tab === "studies" ? "studies" : "channels";

  return (
    <div>
      <h1 className="serif text-4xl font-semibold tracking-tight">
        Your bookmarks
      </h1>

      <div className="mt-8 flex gap-6 border-b border-[color:var(--border)] text-sm">
        <TabLink href="/me/bookmarks?tab=channels" active={tab === "channels"}>
          Channels ({channels.length})
        </TabLink>
        <TabLink href="/me/bookmarks?tab=studies" active={tab === "studies"}>
          Studies ({studies.length})
        </TabLink>
      </div>

      {tab === "channels" && channels.length >= 2 && (
        <div className="mt-6">
          <Link
            href={`/beta?slugs=${channels
              .slice(0, 4)
              .map((c) => encodeURIComponent(c.slug))
              .join(",")}`}
            className="inline-flex h-10 items-center rounded-[var(--radius)] border border-[color:var(--honey)]/40 bg-[color:var(--honey-soft)] px-4 text-sm font-medium text-[color:var(--honey)] hover:bg-[color:var(--honey)]/15"
          >
            Compare {Math.min(channels.length, 4)} bookmarked →
          </Link>
        </div>
      )}

      {tab === "channels" ? (
        channels.length ? (
          <ul className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {channels.map((c) => (
              <li
                key={c.id}
                className="relative rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5 pr-14"
              >
                <div className="absolute right-3 top-3">
                  <BookmarkButton
                    targetType="channel"
                    targetId={c.id}
                    initial
                    signedIn
                    size="sm"
                  />
                </div>
                <Link href={`/channels/${c.slug}`} className="block">
                  {(c.channel_types?.length
                    ? c.channel_types
                    : c.channel_type
                      ? [c.channel_type]
                      : []
                  ).length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {(c.channel_types?.length
                        ? c.channel_types
                        : c.channel_type
                          ? [c.channel_type]
                          : []
                      ).map((t) => (
                        <Tag key={t} ink="muted">
                          {t}
                        </Tag>
                      ))}
                    </div>
                  )}
                  <h2 className="serif mt-4 text-xl font-semibold leading-snug hover:text-[color:var(--accent)]">
                    {c.name}
                  </h2>
                  <dl className="mt-4 grid grid-cols-3 gap-2 text-xs text-[color:var(--muted)]">
                    <Metric label="Subs" value={fmtCompact(c.latest?.subscribers)} />
                    <Metric label="Views" value={fmtCompact(c.latest?.total_views)} />
                    <Metric label="Videos" value={fmtNumber(c.latest?.video_count)} />
                    <Metric
                      label="Avg/video"
                      value={fmtAvgViews(c.latest?.total_views, c.latest?.video_count)}
                    />
                    <Metric label="Age" value={fmtYearsSince(c.created_at_youtube)} />
                  </dl>
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <Empty label="channels" href="/channels" />
        )
      ) : studies.length ? (
        <ul className="mt-6 grid gap-5 sm:grid-cols-2">
          {studies.map((s) => (
            <li key={s.id} className="relative">
              <div className="absolute right-3 top-3 z-10">
                <BookmarkButton
                  targetType="study"
                  targetId={s.id}
                  initial
                  signedIn
                  size="sm"
                />
              </div>
              <Link
                href={`/studies/${s.slug}`}
                className="group block h-full rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6 pr-16 transition-colors hover:border-[color:var(--accent)]"
              >
                <div className="flex flex-wrap items-center gap-2 text-xs text-[color:var(--muted)]">
                  {s.year && (
                    <Tag ink="muted" className="serif-onum">
                      {s.year}
                    </Tag>
                  )}
                  {s.tags.slice(0, 3).map((t) => (
                    <Tag key={t} ink="accent">
                      {t}
                    </Tag>
                  ))}
                </div>
                <h2 className="serif mt-4 text-xl font-semibold leading-snug tracking-tight group-hover:text-[color:var(--accent)]">
                  {s.title}
                </h2>
                {s.authors.length > 0 && (
                  <p className="mt-2 text-sm text-[color:var(--muted)]">
                    {s.authors.join(", ")}
                  </p>
                )}
                {s.abstract && (
                  <p className="mt-4 line-clamp-4 text-sm leading-relaxed">
                    {s.abstract}
                  </p>
                )}
              </Link>
            </li>
          ))}
        </ul>
      ) : (
        <Empty label="studies" href="/studies" />
      )}
    </div>
  );
}

function TabLink({
  href,
  active,
  children,
}: {
  href: string;
  active: boolean;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className={
        "px-1 pb-3 " +
        (active
          ? "border-b-2 border-[color:var(--accent)] font-medium text-[color:var(--foreground)]"
          : "text-[color:var(--muted)] hover:text-[color:var(--foreground)]")
      }
    >
      {children}
    </Link>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="small-caps text-[10px]">{label}</dt>
      <dd className="tabular-nums text-[color:var(--foreground)]">{value}</dd>
    </div>
  );
}

function Empty({ label, href }: { label: string; href: string }) {
  return (
    <div className="mt-8 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-8 text-center">
      <p className="text-sm text-[color:var(--muted)]">No saved {label} yet</p>
      <Link
        href={href}
        className="mt-4 inline-flex h-10 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-4 text-sm font-medium text-white hover:opacity-90"
      >
        Browse {label}
      </Link>
    </div>
  );
}
