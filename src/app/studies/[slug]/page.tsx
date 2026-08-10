import type { Metadata } from "next";

const SOURCE_TYPE_LABELS: Record<string, { label: string; ink: TagInk }> = {
  primary_dataset: { label: "Primary Dataset", ink: "honey" },
  study: { label: "Study", ink: "accent" },
  secondary_analysis: { label: "Secondary Analysis", ink: "muted" },
  blog_analysis: { label: "Blog Analysis", ink: "oxblood" },
};
import Link from "next/link";
import { notFound } from "next/navigation";
import { BookmarkButton } from "@/components/bookmark-button";
import { CitationCopy } from "@/components/citation-copy";
import { StudyProgressPanel } from "@/components/study-progress-panel";
import { Tag, type TagInk } from "@/components/tag";
import { getCurrentUser } from "@/lib/auth";
import {
  getBookmarkSetForUser,
  getRelatedStudies,
  getStudyBySlug,
  getStudyProgressForUser,
  pdfPublicUrl,
  storagePublicUrl,
} from "@/lib/data";

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
  const [bookmarks, progress, related] = await Promise.all([
    auth ? getBookmarkSetForUser(auth.user.id) : Promise.resolve(null),
    auth ? getStudyProgressForUser(auth.user.id, study.id) : Promise.resolve(null),
    getRelatedStudies(study.id, study.tags ?? [], 4),
  ]);

  const pdfUrl = pdfPublicUrl(study.pdf_path);
  const previewImageUrl = storagePublicUrl(study.preview_image_path);

  return (
    <div className="mx-auto max-w-3xl px-5 py-14 sm:px-8 sm:py-20">
      <Link
        href="/studies"
        className="text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
      >
        ← All studies
      </Link>

      {study.context_note && !study.flagged_problematic && (
        <div className="mt-6 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--accent-soft)]/30 p-4 text-sm text-[color:var(--foreground)]">
          <div className="flex items-start gap-3">
            <span
              aria-hidden
              className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[color:var(--accent)] text-xs font-bold text-white"
            >
              i
            </span>
            <div>
              <p className="font-semibold">Context</p>
              <p className="mt-1 whitespace-pre-line leading-relaxed">
                {study.context_note}
              </p>
            </div>
          </div>
        </div>
      )}

      {study.flagged_problematic && (
        <div className="mt-6 rounded-[var(--radius)] border-2 border-[color:var(--oxblood)]/50 bg-[color:var(--oxblood-soft)] p-4 text-sm text-[color:var(--oxblood)]">
          <div className="flex items-start gap-3">
            <span
              aria-hidden
              className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[color:var(--oxblood)] text-xs font-bold text-white"
            >
              !
            </span>
            <div>
              <p className="font-semibold">
                Flagged for methodological concerns
              </p>
              <p className="mt-1 leading-relaxed">
                {study.flag_reason ??
                  "This study has been flagged for problematic methodology or drawing more from the conclusions than the data find. Read with appropriate caution."}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="mt-6 flex flex-wrap items-center gap-2 text-xs text-[color:var(--muted)]">
        {study.source_type && SOURCE_TYPE_LABELS[study.source_type] && (
          <Tag ink={SOURCE_TYPE_LABELS[study.source_type].ink}>
            {SOURCE_TYPE_LABELS[study.source_type].label}
          </Tag>
        )}
        {study.year && (
          <Tag ink="muted" className="serif-onum">
            {study.year}
          </Tag>
        )}
        {study.tags.map((t) => (
          <Tag key={t} ink="accent">
            {t}
          </Tag>
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

      {auth?.profile?.is_admin && (
        <div className="mt-4">
          <Link
            href={`/admin/studies/${study.slug}/edit`}
            className="inline-flex h-9 items-center rounded-[var(--radius)] border border-[color:var(--border)] px-4 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
          >
            Edit (admin)
          </Link>
        </div>
      )}

      {!pdfUrl && study.external_url && (
        <div className="mt-6">
          <a
            href={study.external_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex h-11 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-5 text-sm font-medium text-white transition-colors hover:opacity-90"
          >
            Read on external site ↗
          </a>
        </div>
      )}

      {previewImageUrl && (
        <figure className="mt-10 overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--muted-soft)]/40">
          <div className="relative">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={previewImageUrl}
              alt={study.preview_image_caption ?? study.title}
              className="block h-auto w-full"
            />
            {study.preview_image_is_ai && (
              <span className="small-caps absolute bottom-2 left-2 rounded-[var(--radius)] bg-black/70 px-2.5 py-1 text-[10px] font-medium text-white">
                AI · not from study
              </span>
            )}
          </div>
          {(study.preview_image_caption || study.preview_image_is_ai) && (
            <figcaption className="border-t border-[color:var(--border)] bg-white px-4 py-3 text-xs leading-relaxed text-[color:var(--muted)]">
              {study.preview_image_is_ai ? (
                <em>
                  This graphic was generated by AI from the study&rsquo;s findings and is not an original figure from the publication.
                  {study.preview_image_caption ? ` ${study.preview_image_caption}` : ""}
                </em>
              ) : (
                study.preview_image_caption
              )}
            </figcaption>
          )}
        </figure>
      )}

      {study.abstract && (
        <section className="mt-10">
          <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
            Abstract
          </h2>
          <p className="mt-3 text-base leading-relaxed text-[color:var(--foreground)] sm:text-lg">
            {study.abstract}
          </p>
        </section>
      )}

      {(study.findings ?? []).length > 0 && (
        <section className="mt-10">
          <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
            {study.category === "Utah" ? "Findings for Utah" : "Findings for Latter-day Saints"}
          </h2>
          <ul className="mt-3 list-disc space-y-2 pl-5 text-base leading-relaxed text-[color:var(--foreground)] sm:text-lg">
            {(study.findings ?? []).map((finding, i) => (
              <li key={i}>{finding}</li>
            ))}
          </ul>
        </section>
      )}

      {pdfUrl && (
        <section className="mt-12">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
              Full text
            </h2>
            <div className="flex flex-wrap gap-2">
              <a
                href={pdfUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex h-10 items-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-4 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
              >
                Open in new tab ↗
              </a>
              <a
                href={pdfUrl}
                download
                className="inline-flex h-10 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-4 text-xs font-medium text-white hover:opacity-90"
              >
                Download PDF
              </a>
            </div>
          </div>
          <div className="mt-4 overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--muted-soft)]/40">
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

      {study.limitations && (
        <section className="mt-12">
          <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
            Limitations in methodology
          </h2>
          <p className="mt-3 whitespace-pre-line text-base leading-relaxed text-[color:var(--foreground)] sm:text-lg">
            {study.limitations}
          </p>
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
      {study.secondary_url && (
        <p className="mt-2 text-sm text-[color:var(--muted)]">
          Data / additional:{" "}
          <a
            href={study.secondary_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[color:var(--accent)] underline"
          >
            {study.secondary_url}
          </a>
        </p>
      )}

      <StudyProgressPanel
        studyId={study.id}
        signedIn={Boolean(auth)}
        initialStatus={progress?.status ?? "unread"}
        initialNotes={progress?.notes ?? ""}
      />

      {related.length > 0 && (
        <section className="mt-12">
          <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
            Related studies
          </h2>
          <ul className="mt-4 grid gap-3 sm:grid-cols-2">
            {related.map((r) => (
              <li key={r.id}>
                <Link
                  href={`/studies/${r.slug}`}
                  className="group block h-full rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-4 transition-colors hover:border-[color:var(--accent)]"
                >
                  <div className="flex flex-wrap items-center gap-2 text-[10px] text-[color:var(--muted)]">
                    {r.year && (
                      <Tag ink="muted" className="serif-onum">
                        {r.year}
                      </Tag>
                    )}
                    {(r.tags ?? []).slice(0, 2).map((t) => (
                      <Tag key={t} ink="accent">
                        {t}
                      </Tag>
                    ))}
                  </div>
                  <p className="serif mt-2 text-base font-semibold leading-snug tracking-tight group-hover:text-[color:var(--accent)]">
                    {r.title}
                  </p>
                  {r.authors.length > 0 && (
                    <p className="mt-1.5 text-xs text-[color:var(--muted)]">
                      {r.authors.slice(0, 2).join(", ")}
                      {r.authors.length > 2 ? " et al." : ""}
                    </p>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      <CitationCopy
        study={{
          title: study.title,
          authors: study.authors,
          year: study.year,
          source: study.source,
          external_url: study.external_url,
        }}
        bibtexKey={study.slug.replace(/-/g, "_")}
      />

      <p className="mt-10 text-xs text-[color:var(--muted)]">
        <Link
          href={`/contact?category=correction&ref=${encodeURIComponent(
            `study:${study.slug}`,
          )}`}
          className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
        >
          Report an error
        </Link>{" "}
        on this study.
      </p>

    </div>
  );
}
