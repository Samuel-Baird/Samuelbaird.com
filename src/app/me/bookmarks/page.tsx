import Link from "next/link";
import { BookmarkButton } from "@/components/bookmark-button";
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

      {tab === "channels" ? (
        channels.length ? (
          <ul className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {channels.map((c) => (
              <li
                key={c.id}
                className="relative rounded-2xl border border-[color:var(--border)] bg-white p-5 pr-14"
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
                  {c.channel_type && (
                    <span className="rounded-full bg-[color:var(--muted-soft)] px-2.5 py-1 text-[10px] uppercase tracking-wider text-[color:var(--muted)]">
                      {c.channel_type}
                    </span>
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
                className="group block h-full rounded-2xl border border-[color:var(--border)] bg-white p-6 pr-16 transition-colors hover:border-[color:var(--accent)]"
              >
                <div className="flex flex-wrap items-center gap-2 text-xs text-[color:var(--muted)]">
                  {s.year && (
                    <span className="rounded-full bg-[color:var(--muted-soft)] px-2.5 py-1 tabular-nums">
                      {s.year}
                    </span>
                  )}
                  {s.tags.slice(0, 3).map((t) => (
                    <span
                      key={t}
                      className="rounded-full bg-[color:var(--accent-soft)] px-2.5 py-1 text-[color:var(--accent)]"
                    >
                      {t}
                    </span>
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
      <dt className="text-[10px] uppercase tracking-wider">{label}</dt>
      <dd className="tabular-nums text-[color:var(--foreground)]">{value}</dd>
    </div>
  );
}

function Empty({ label, href }: { label: string; href: string }) {
  return (
    <div className="mt-8 rounded-2xl border border-[color:var(--border)] bg-white p-8 text-center">
      <p className="text-sm text-[color:var(--muted)]">No saved {label} yet</p>
      <Link
        href={href}
        className="mt-4 inline-flex h-10 items-center rounded-full bg-[color:var(--accent)] px-4 text-sm font-medium text-white hover:opacity-90"
      >
        Browse {label}
      </Link>
    </div>
  );
}
