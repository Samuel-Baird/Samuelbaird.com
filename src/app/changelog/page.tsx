import type { Metadata } from "next";
import Link from "next/link";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import type { ChangelogDocument } from "@/lib/types";

export const metadata: Metadata = {
  title: "Changelog",
  description:
    "Track how Latter-day Saint documents — handbooks, manuals, and guides — change across editions over time.",
};

type DocumentRow = ChangelogDocument & {
  changelog_versions: { count: number }[];
};

export default async function ChangelogPage() {
  const supabase = await createSupabaseServerClient();
  const { data, error } = await supabase
    .from("changelog_documents")
    .select("*, changelog_versions(count)")
    .order("title", { ascending: true });
  if (error) throw error;

  const documents = (data ?? []) as DocumentRow[];

  return (
    <div className="mx-auto max-w-4xl px-5 py-14 sm:px-8 sm:py-20">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        Changelog
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
        How Latter-day Saint documents change
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
        A neutral, source-based archive of major Church documents across
        editions — handbooks, manuals, and guides. Browse a document&rsquo;s
        version history; side-by-side comparison and change summaries are on the
        way.
      </p>

      {documents.length === 0 ? (
        <div className="mt-12 rounded-2xl border border-[color:var(--border)] bg-white p-8 text-center">
          <p className="serif text-lg font-semibold tracking-tight">
            No documents tracked yet
          </p>
          <p className="mt-2 text-sm text-[color:var(--muted)]">
            Documents and their editions will appear here as they&rsquo;re added.
          </p>
        </div>
      ) : (
        <ul className="mt-10 grid gap-3 sm:grid-cols-2">
          {documents.map((doc) => {
            const versionCount = doc.changelog_versions?.[0]?.count ?? 0;
            return (
              <li key={doc.id}>
                <Link
                  href={`/changelog/${doc.slug}`}
                  className="group block h-full rounded-2xl border border-[color:var(--border)] bg-white p-5 transition-colors hover:border-[color:var(--accent)]"
                >
                  {doc.category && (
                    <span className="inline-block rounded-full bg-[color:var(--accent-soft)] px-2.5 py-1 text-[10px] font-medium uppercase tracking-wider text-[color:var(--accent)]">
                      {doc.category}
                    </span>
                  )}
                  <p className="serif mt-3 text-xl font-semibold leading-snug tracking-tight group-hover:text-[color:var(--accent)]">
                    {doc.title}
                  </p>
                  {doc.summary && (
                    <p className="mt-2 line-clamp-3 text-sm leading-relaxed text-[color:var(--muted)]">
                      {doc.summary}
                    </p>
                  )}
                  <p className="mt-3 text-xs tabular-nums text-[color:var(--muted)]">
                    {versionCount} {versionCount === 1 ? "edition" : "editions"}
                  </p>
                </Link>
              </li>
            );
          })}
        </ul>
      )}

      <aside className="mt-14 rounded-2xl border border-[color:var(--border)] bg-[color:var(--accent-soft)]/40 p-6 text-sm text-[color:var(--foreground)] sm:p-8">
        <p className="serif text-lg font-semibold tracking-tight">
          About this archive
        </p>
        <p className="mt-2 leading-relaxed text-[color:var(--muted)]">
          LDS Changelog is an independent research and archival tool for studying
          how official and semi-official documents develop over time. It is not
          affiliated with The Church of Jesus Christ of Latter-day Saints. The
          aim is to make changes visible and easy to study — not to tell you what
          to think about them.
        </p>
      </aside>
    </div>
  );
}
