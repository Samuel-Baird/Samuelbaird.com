import type { Metadata } from "next";
import Link from "next/link";
import { BookmarkButton } from "@/components/bookmark-button";
import { getCurrentUser } from "@/lib/auth";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";
import { getBookmarkSetForUser, getStudies } from "@/lib/data";

export const metadata: Metadata = {
  title: "Studies",
  description:
    "Academic studies and research relating to the Latter-day Saint community.",
};

export const revalidate = 600;

export default async function StudiesPage() {
  const [studies, auth] = await Promise.all([getStudies(), getCurrentUser()]);
  const bookmarks = auth
    ? await getBookmarkSetForUser(auth.user.id)
    : { channels: new Set<string>(), studies: new Set<string>() };

  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        Studies
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
        Research library
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
        Curated academic studies relating to the Latter-day Saint community.
        New entries added as they&apos;re reviewed.
      </p>

      <ul className="mt-12 grid gap-5 sm:grid-cols-2">
        {studies.map((s) => (
          <li key={s.id} className="relative">
            <div className="absolute right-3 top-3 z-10">
              <BookmarkButton
                targetType="study"
                targetId={s.id}
                initial={bookmarks.studies.has(s.id)}
                signedIn={Boolean(auth)}
                size="sm"
              />
            </div>
            <Link
              href={`/studies/${s.slug}`}
              className={
                "group block h-full rounded-2xl border bg-white p-6 pr-16 transition-colors " +
                (s.flagged_problematic
                  ? "border-red-200 hover:border-red-500"
                  : "border-[color:var(--border)] hover:border-[color:var(--accent)]")
              }
              title={
                s.flagged_problematic
                  ? "Flagged for methodological concerns"
                  : undefined
              }
            >
              {s.flagged_problematic && (
                <span
                  aria-label="Flagged for methodological concerns"
                  className="absolute left-3 top-3 z-10 inline-flex h-5 w-5 items-center justify-center rounded-full bg-red-600 text-xs font-bold text-white"
                >
                  !
                </span>
              )}
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
              <h2 className="serif mt-4 text-xl font-semibold leading-snug tracking-tight text-[color:var(--foreground)] group-hover:text-[color:var(--accent)]">
                {s.title}
              </h2>
              {s.authors.length > 0 && (
                <p className="mt-2 text-sm text-[color:var(--muted)]">
                  {s.authors.join(", ")}
                </p>
              )}
              {s.abstract && (
                <p className="mt-4 line-clamp-4 text-sm leading-relaxed text-[color:var(--foreground)]">
                  {s.abstract}
                </p>
              )}
              <p className="mt-5 text-xs text-[color:var(--accent)]">
                Read study →
              </p>
            </Link>
          </li>
        ))}
      </ul>

      <aside className="mt-12 rounded-2xl border border-[color:var(--border)] bg-[color:var(--accent-soft)]/40 p-6 text-sm text-[color:var(--foreground)] sm:p-8">
        <p className="serif text-lg font-semibold tracking-tight">
          Know a study we should add?
        </p>
        <p className="mt-2 leading-relaxed text-[color:var(--muted)]">
          Email{" "}
          <a
            href={mailto("Add a study")}
            className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
          >
            {CONTACT_EMAIL}
          </a>{" "}
          with a link or PDF — peer-reviewed work and reputable independent
          research are both welcome.
        </p>
      </aside>
    </div>
  );
}
