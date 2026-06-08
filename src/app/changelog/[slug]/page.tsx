import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getCurrentUser } from "@/lib/auth";
import { fmtDate } from "@/lib/format";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import type { ChangelogDocument, ChangelogVersion } from "@/lib/types";

const CONFIDENCE_LABELS: Record<string, { label: string; className: string }> = {
  "official-digital": { label: "Official digital", className: "bg-emerald-100 text-emerald-800" },
  "official-pdf": { label: "Official PDF", className: "bg-blue-100 text-blue-800" },
  archived: { label: "Archived official", className: "bg-[color:var(--muted-soft)] text-[color:var(--muted)]" },
  "printed-scan": { label: "Printed scan", className: "bg-amber-100 text-amber-800" },
  "ocr-derived": { label: "OCR-derived", className: "bg-amber-100 text-amber-800" },
  "user-uploaded": { label: "User-uploaded", className: "bg-[color:var(--muted-soft)] text-[color:var(--muted)]" },
  unverified: { label: "Unverified", className: "bg-red-100 text-red-800" },
};

type RouteParams = { slug: string };

type VersionRow = ChangelogVersion & {
  changelog_sections: { count: number }[];
};

export async function generateMetadata({
  params,
}: {
  params: Promise<RouteParams>;
}): Promise<Metadata> {
  const { slug } = await params;
  const supabase = await createSupabaseServerClient();
  const { data } = await supabase
    .from("changelog_documents")
    .select("title, summary")
    .eq("slug", slug)
    .maybeSingle();
  if (!data) return { title: "Document not found" };
  return {
    title: data.title,
    description: data.summary?.slice(0, 200) ?? undefined,
  };
}

export default async function ChangelogDocumentPage({
  params,
}: {
  params: Promise<RouteParams>;
}) {
  const { slug } = await params;
  const supabase = await createSupabaseServerClient();
  const [{ data: docData, error: docError }, auth] = await Promise.all([
    supabase
      .from("changelog_documents")
      .select("*")
      .eq("slug", slug)
      .maybeSingle(),
    getCurrentUser(),
  ]);
  if (docError) throw docError;
  if (!docData) notFound();
  const doc = docData as ChangelogDocument;

  const { data: versionData, error: versionError } = await supabase
    .from("changelog_versions")
    .select("*, changelog_sections(count)")
    .eq("document_id", doc.id)
    .order("ordinal", { ascending: true })
    .order("published_on", { ascending: true });
  if (versionError) throw versionError;
  const versions = (versionData ?? []) as VersionRow[];

  return (
    <div className="mx-auto max-w-3xl px-5 py-14 sm:px-8 sm:py-20">
      <Link
        href="/changelog"
        className="text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
      >
        ← All documents
      </Link>

      <div className="mt-6 flex flex-wrap items-center gap-2">
        {doc.category && (
          <span className="rounded-full bg-[color:var(--accent-soft)] px-2.5 py-1 text-[10px] font-medium uppercase tracking-wider text-[color:var(--accent)]">
            {doc.category}
          </span>
        )}
      </div>

      <h1 className="serif mt-3 text-3xl font-semibold leading-tight tracking-tight sm:text-4xl">
        {doc.title}
      </h1>
      {doc.summary && (
        <p className="mt-4 text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
          {doc.summary}
        </p>
      )}

      {auth?.profile?.is_admin && (
        <div className="mt-4">
          <Link
            href={`/admin/changelog/${doc.slug}/edit`}
            className="inline-flex h-9 items-center rounded-full border border-[color:var(--border)] px-4 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
          >
            Edit (admin)
          </Link>
        </div>
      )}

      <section className="mt-12">
        <h2 className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
          Version history
        </h2>

        {versions.length === 0 ? (
          <p className="mt-4 rounded-2xl border border-[color:var(--border)] bg-white p-6 text-sm text-[color:var(--muted)]">
            No editions recorded yet.
          </p>
        ) : (
          <ol className="mt-6 space-y-4">
            {versions.map((version) => {
              const sectionCount =
                version.changelog_sections?.[0]?.count ?? 0;
              const confidence = version.confidence
                ? CONFIDENCE_LABELS[version.confidence]
                : null;
              return (
                <li
                  key={version.id}
                  className="rounded-2xl border border-[color:var(--border)] bg-white p-5"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="serif text-lg font-semibold tracking-tight">
                        {version.label}
                      </p>
                      {version.published_on && (
                        <p className="mt-1 text-xs tabular-nums text-[color:var(--muted)]">
                          Published {fmtDate(`${version.published_on}T12:00:00`)}
                        </p>
                      )}
                    </div>
                    {confidence && (
                      <span
                        className={`rounded-full px-2.5 py-1 text-[10px] font-medium uppercase tracking-wide ${confidence.className}`}
                      >
                        {confidence.label}
                      </span>
                    )}
                  </div>
                  <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-[color:var(--muted)]">
                    <span className="tabular-nums">
                      {sectionCount}{" "}
                      {sectionCount === 1 ? "section" : "sections"}
                    </span>
                    {version.source_url && (
                      <a
                        href={version.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
                      >
                        Source ↗
                      </a>
                    )}
                  </div>
                </li>
              );
            })}
          </ol>
        )}

        <p className="mt-6 text-xs text-[color:var(--muted)]">
          Side-by-side comparison and AI-assisted change summaries between
          editions are coming in a later phase.
        </p>
      </section>
    </div>
  );
}
