import Link from "next/link";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { fmtDate, fmtNumber } from "@/lib/format";

export const dynamic = "force-dynamic";

type CountRow = { target_id: string; count: number };

async function aggregateCounts(
  rows: { target_id: string }[] | null,
): Promise<CountRow[]> {
  const map = new Map<string, number>();
  for (const r of rows ?? []) {
    map.set(r.target_id, (map.get(r.target_id) ?? 0) + 1);
  }
  return [...map.entries()]
    .map(([target_id, count]) => ({ target_id, count }))
    .sort((a, b) => b.count - a.count);
}

function daysAgoIso(days: number) {
  return new Date(Date.now() - days * 86_400_000).toISOString();
}

export default async function AdminAnalyticsPage() {
  const sb = createSupabaseServiceClient();
  const since30 = daysAgoIso(30);
  const since7 = daysAgoIso(7);

  const [
    bookmarksRows,
    upvotesRows,
    progressRows,
    progressRead,
    recentSignups,
    messageVolume,
    staleChannels,
    allChannels,
    allStudies,
  ] = await Promise.all([
    sb.from("bookmarks").select("target_type, target_id"),
    sb.from("upvotes").select("target_type, target_id"),
    sb.from("study_progress").select("study_id, status, user_id"),
    sb
      .from("study_progress")
      .select("study_id, user_id")
      .eq("status", "read"),
    sb
      .from("profiles")
      .select("created_at")
      .gte("created_at", since30)
      .order("created_at", { ascending: true }),
    sb
      .from("messages")
      .select("created_at, category")
      .gte("created_at", since30)
      .order("created_at", { ascending: false }),
    sb
      .from("channel_stats_latest")
      .select("channel_id, captured_at")
      .lt("captured_at", since7),
    sb.from("channels").select("id, name, slug, is_active"),
    sb.from("studies").select("id, title, slug"),
  ]);

  const bookmarks = bookmarksRows.data ?? [];
  const upvotes = upvotesRows.data ?? [];
  const progress = progressRows.data ?? [];
  const reads = progressRead.data ?? [];
  const signups = recentSignups.data ?? [];
  const messages = messageVolume.data ?? [];
  const channels = allChannels.data ?? [];
  const studies = allStudies.data ?? [];

  const channelById = new Map(channels.map((c) => [c.id as string, c]));
  const studyById = new Map(studies.map((s) => [s.id as string, s]));

  const channelBookmarks = await aggregateCounts(
    bookmarks.filter((b) => b.target_type === "channel"),
  );
  const studyBookmarks = await aggregateCounts(
    bookmarks.filter((b) => b.target_type === "study"),
  );
  const channelUpvotes = await aggregateCounts(
    upvotes.filter((u) => u.target_type === "channel"),
  );
  const studyUpvotes = await aggregateCounts(
    upvotes.filter((u) => u.target_type === "study"),
  );
  const studyReads = await aggregateCounts(
    reads.map((r) => ({ target_id: r.study_id as string })),
  );

  const distinctReaders = new Set(reads.map((r) => r.user_id as string)).size;
  const totalNotes = progress.filter((p) => p.status === "read").length;
  const totalNotesWithText = progress.length;

  // Signups by day (30d)
  const signupsByDay = new Map<string, number>();
  for (let i = 29; i >= 0; i--) {
    const d = new Date(Date.now() - i * 86_400_000);
    const key = d.toISOString().slice(0, 10);
    signupsByDay.set(key, 0);
  }
  for (const row of signups) {
    const key = (row.created_at as string).slice(0, 10);
    if (signupsByDay.has(key)) {
      signupsByDay.set(key, (signupsByDay.get(key) ?? 0) + 1);
    }
  }
  const signupSeries = [...signupsByDay.entries()];
  const signupMax = Math.max(1, ...signupSeries.map(([, v]) => v));

  // Messages by category
  const messagesByCategory = new Map<string, number>();
  for (const m of messages) {
    const key = (m.category as string) ?? "other";
    messagesByCategory.set(key, (messagesByCategory.get(key) ?? 0) + 1);
  }

  return (
    <div>
      <h1 className="serif text-4xl font-semibold tracking-tight">Analytics</h1>
      <p className="mt-2 text-sm text-[color:var(--muted)]">
        Engagement and data-quality snapshot, computed live from Supabase.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Tile
          label="Bookmarks"
          value={fmtNumber(bookmarks.length)}
          detail={`${channelBookmarks.length} channels · ${studyBookmarks.length} studies`}
        />
        <Tile
          label="Upvotes"
          value={fmtNumber(upvotes.length)}
          detail={`${channelUpvotes.length} channels · ${studyUpvotes.length} studies`}
        />
        <Tile
          label="Studies read"
          value={fmtNumber(reads.length)}
          detail={`by ${distinctReaders} ${distinctReaders === 1 ? "reader" : "readers"}`}
        />
        <Tile
          label="Private notes"
          value={fmtNumber(totalNotesWithText)}
          detail={`${totalNotes} also marked read`}
        />
      </div>

      <section className="mt-10">
        <h2 className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
          Sign-ups · last 30 days
        </h2>
        <div className="mt-4 rounded-2xl border border-[color:var(--border)] bg-white p-5">
          <p className="text-sm text-[color:var(--muted)]">
            {signups.length} sign-up{signups.length === 1 ? "" : "s"} in window
          </p>
          <div className="mt-4 flex h-32 items-end gap-1">
            {signupSeries.map(([day, count]) => (
              <div
                key={day}
                title={`${day}: ${count}`}
                className="flex-1 rounded-t bg-[color:var(--accent)]"
                style={{
                  height: `${(count / signupMax) * 100}%`,
                  minHeight: count > 0 ? 2 : 0,
                  opacity: count > 0 ? 1 : 0.15,
                }}
              />
            ))}
          </div>
          <div className="mt-2 flex justify-between text-[10px] uppercase tracking-wider text-[color:var(--muted)]">
            <span>{signupSeries[0]?.[0]}</span>
            <span>{signupSeries[signupSeries.length - 1]?.[0]}</span>
          </div>
        </div>
      </section>

      <div className="mt-10 grid gap-6 md:grid-cols-2">
        <Leaderboard
          title="Top channels by bookmarks"
          empty="No bookmarks yet."
          rows={channelBookmarks.slice(0, 8).map((r) => {
            const c = channelById.get(r.target_id);
            return {
              key: r.target_id,
              label: c?.name ?? "(unknown channel)",
              href: c ? `/channels/${c.slug}` : null,
              value: r.count,
            };
          })}
        />
        <Leaderboard
          title="Top studies by upvotes"
          empty="No upvotes yet."
          rows={studyUpvotes.slice(0, 8).map((r) => {
            const s = studyById.get(r.target_id);
            return {
              key: r.target_id,
              label: s?.title ?? "(unknown study)",
              href: s ? `/studies/${s.slug}` : null,
              value: r.count,
            };
          })}
        />
        <Leaderboard
          title="Top studies by reads"
          empty="No studies marked read yet."
          rows={studyReads.slice(0, 8).map((r) => {
            const s = studyById.get(r.target_id);
            return {
              key: r.target_id,
              label: s?.title ?? "(unknown study)",
              href: s ? `/studies/${s.slug}` : null,
              value: r.count,
            };
          })}
        />
        <Leaderboard
          title="Top channels by upvotes"
          empty="No upvotes yet."
          rows={channelUpvotes.slice(0, 8).map((r) => {
            const c = channelById.get(r.target_id);
            return {
              key: r.target_id,
              label: c?.name ?? "(unknown channel)",
              href: c ? `/channels/${c.slug}` : null,
              value: r.count,
            };
          })}
        />
      </div>

      <section className="mt-10">
        <h2 className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
          Contact messages · last 30 days
        </h2>
        <div className="mt-4 overflow-hidden rounded-2xl border border-[color:var(--border)] bg-white">
          {messages.length === 0 ? (
            <p className="px-5 py-6 text-sm text-[color:var(--muted)]">
              No messages in the window.
            </p>
          ) : (
            <ul>
              {[...messagesByCategory.entries()]
                .sort((a, b) => b[1] - a[1])
                .map(([category, count], i) => (
                  <li
                    key={category}
                    className={
                      "flex items-center justify-between px-5 py-3 text-sm " +
                      (i > 0 ? "border-t border-[color:var(--border)]" : "")
                    }
                  >
                    <span className="font-medium capitalize">{category}</span>
                    <span className="tabular-nums text-[color:var(--muted)]">
                      {count}
                    </span>
                  </li>
                ))}
            </ul>
          )}
        </div>
      </section>

      <section className="mt-10">
        <h2 className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
          Data quality
        </h2>
        <p className="mt-2 text-sm text-[color:var(--muted)]">
          Active channels whose latest snapshot is older than 7 days. Run the{" "}
          <Link
            href="/admin/refresh"
            className="text-[color:var(--accent)] underline"
          >
            refresh
          </Link>{" "}
          if this grows.
        </p>
        <div className="mt-4 overflow-hidden rounded-2xl border border-[color:var(--border)] bg-white">
          {(() => {
            const activeIds = new Set(
              channels.filter((c) => c.is_active).map((c) => c.id as string),
            );
            const stale = (staleChannels.data ?? []).filter((s) =>
              activeIds.has(s.channel_id as string),
            );
            if (stale.length === 0) {
              return (
                <p className="px-5 py-6 text-sm text-[color:var(--muted)]">
                  All active channels refreshed within the last 7 days.
                </p>
              );
            }
            return (
              <ul>
                {stale.slice(0, 20).map((row, i) => {
                  const c = channelById.get(row.channel_id as string);
                  return (
                    <li
                      key={row.channel_id as string}
                      className={
                        "flex items-center justify-between gap-3 px-5 py-3 text-sm " +
                        (i > 0 ? "border-t border-[color:var(--border)]" : "")
                      }
                    >
                      {c ? (
                        <Link
                          href={`/channels/${c.slug}`}
                          className="font-medium hover:text-[color:var(--accent)]"
                        >
                          {c.name}
                        </Link>
                      ) : (
                        <span className="font-medium">(unknown)</span>
                      )}
                      <span className="text-xs text-[color:var(--muted)]">
                        {fmtDate(row.captured_at as string)}
                      </span>
                    </li>
                  );
                })}
                {stale.length > 20 && (
                  <li className="border-t border-[color:var(--border)] px-5 py-2 text-xs text-[color:var(--muted)]">
                    +{stale.length - 20} more
                  </li>
                )}
              </ul>
            );
          })()}
        </div>
      </section>
    </div>
  );
}

function Tile({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="rounded-2xl border border-[color:var(--border)] bg-white p-5">
      <div className="text-[11px] font-medium uppercase tracking-wider text-[color:var(--muted)]">
        {label}
      </div>
      <div className="serif mt-2 text-3xl font-semibold tabular-nums">
        {value}
      </div>
      <p className="mt-2 text-xs text-[color:var(--muted)]">{detail}</p>
    </div>
  );
}

function Leaderboard({
  title,
  rows,
  empty,
}: {
  title: string;
  empty: string;
  rows: { key: string; label: string; href: string | null; value: number }[];
}) {
  return (
    <div>
      <h2 className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        {title}
      </h2>
      <div className="mt-4 overflow-hidden rounded-2xl border border-[color:var(--border)] bg-white">
        {rows.length === 0 ? (
          <p className="px-5 py-6 text-sm text-[color:var(--muted)]">{empty}</p>
        ) : (
          <ol>
            {rows.map((r, i) => (
              <li
                key={r.key}
                className={
                  "flex items-center gap-3 px-5 py-3 " +
                  (i > 0 ? "border-t border-[color:var(--border)]" : "")
                }
              >
                <span className="w-5 text-right text-xs text-[color:var(--muted)] tabular-nums">
                  {i + 1}
                </span>
                {r.href ? (
                  <Link
                    href={r.href}
                    className="min-w-0 flex-1 truncate text-sm font-medium hover:text-[color:var(--accent)]"
                  >
                    {r.label}
                  </Link>
                ) : (
                  <span className="min-w-0 flex-1 truncate text-sm font-medium">
                    {r.label}
                  </span>
                )}
                <span className="text-sm tabular-nums text-[color:var(--muted)]">
                  {r.value}
                </span>
              </li>
            ))}
          </ol>
        )}
      </div>
    </div>
  );
}
