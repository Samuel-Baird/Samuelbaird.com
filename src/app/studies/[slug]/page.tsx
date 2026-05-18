import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { BookmarkButton } from "@/components/bookmark-button";
import { getCurrentUser } from "@/lib/auth";
import { getBookmarkSetForUser, getStudyBySlug, pdfPublicUrl } from "@/lib/data";

export const revalidate = 600;

type RouteParams = { slug: string };

export async function generateMetadata({
  params,
}: {
  params: Promise<RouteParams>;
}): Promise<Metadata> {
  const { slug } = await params;
  const s = await getStudyBySlug(slug);
  if (!s) return { title: "Study not found" };
  return {
    title: s.title,
    description: s.abstract?.slice(0, 200) ?? undefined,
  };
}

export default async function StudyDetailPage({
  params,
}: {
  params: Promise<RouteParams>;
}) {
  const { slug } = await params;
  const [study, auth] = await Promise.all([
    getStudyBySlug(slug),
    getCurrentUser(),
  ]);
  if (!study) notFound();
  const bookmarks = auth ? await getBookmarkSetForUser(auth.user.id) : null;

  const pdfUrl = pdfPublicUrl(study.pdf_path);

  return (
    <div className="mx-auto max-w-3xl px-5 py-14 sm:px-8 sm:py-20">
      <Link
        href="/studies"
        className="text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
      >
        ← All studies
      </Link>

      <div className="mt-6 flex flex-wrap items-center gap-2 text-xs text-[color:var(--muted)]">
        {study.year && (
          <span className="rounded-full bg-[color:var(--muted-soft)] px-2.5 py-1 tabular-nums">
            {study.year}
          </span>
        )}
        {study.tags.map((t) => (
          <span
            key={t}
            className="rounded-full bg-[color:var(--accent-soft)] px-2.5 py-1 text-[color:var(--accent)]"
          >
            {t}
          </span>
        ))}
      </div>

      <div className="mt-4 flex flex-wrap items-start justify-between gap-4">
        <h1 className="serif text-3xl font-semibold leading-tight tracking-tight sm:text-4xl">
          {study.title}
        </h1>
        <BookmarkButton
          targetType="study"
          targetId={study.id}
          initial={bookmarks?.studies.has(study.id) ?? false}
          signedIn={Boolean(auth)}
          label="inline"
        />
      </div>
      {(study.authors.length > 0 || study.source) && (
        <p className="mt-3 text-sm text-[color:var(--muted)]">
          {study.authors.length > 0 ? study.authors.join(", ") : null}
          {study.authors.length > 0 && study.source ? " · " : ""}
          {study.source ?? ""}
        </p>
      )}

      {!pdfUrl && study.external_url && (
        <div className="mt-6">
          <a
            href={study.external_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex h-11 items-center rounded-full bg-[color:var(--accent)] px-5 text-sm font-medium text-white transition-colors hover:opacity-90"
          >
            Read on external site ↗
          </a>
        </div>
      )}

      {study.abstract && (
        <section className="mt-10">
          <h2 className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
            Abstract
          </h2>
          <p className="mt-3 text-base leading-relaxed text-[color:var(--foreground)] sm:text-lg">
            {study.abstract}
          </p>
        </section>
      )}

      {pdfUrl && (
        <section className="mt-12">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
              Full text
            </h2>
            <div className="flex flex-wrap gap-2">
              <a
                href={pdfUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex h-10 items-center rounded-full border border-[color:var(--border)] bg-white px-4 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
              >
                Open in new tab ↗
              </a>
              <a
                href={pdfUrl}
                download
                className="inline-flex h-10 items-center rounded-full bg-[color:var(--accent)] px-4 text-xs font-medium text-white hover:opacity-90"
              >
                Download PDF
              </a>
            </div>
          </div>
          <div className="mt-4 overflow-hidden rounded-2xl border border-[color:var(--border)] bg-[color:var(--muted-soft)]/40">
            <object
              data={pdfUrl}
              type="application/pdf"
              className="block h-[80vh] w-full"
              aria-label={study.title}
            >
              <div className="p-6 text-sm text-[color:var(--muted)]">
                Your browser can&apos;t display this PDF inline.{" "}
                <a
                  href={pdfUrl}
                  className="text-[color:var(--accent)] underline"
                >
                  Open it in a new tab
                </a>
                .
              </div>
            </object>
          </div>
        </section>
      )}

      {study.external_url && (
        <p className="mt-8 text-sm text-[color:var(--muted)]">
          Source:{" "}
          <a
            href={study.external_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[color:var(--accent)] underline"
          >
            {study.external_url}
          </a>
        </p>
      )}
    </div>
  );
}
