import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, Download } from "lucide-react";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";
import { GraphicAdminControls } from "@/components/admin/graphic-admin-controls";
import { GraphicShareButton } from "@/components/data-explorer/graphic-share-button";
import { Tag } from "@/components/tag";
import { getCurrentUser } from "@/lib/auth";
import { graphicId } from "@/lib/data-explorer";
import { getStudyBySlug } from "@/lib/data";
import { filterPublished, getGraphicPostMap } from "@/lib/graphic-posts";
import { STUDY_GRAPHICS, getStudyGraphics } from "@/lib/study-graphics";

export function generateStaticParams() {
  return STUDY_GRAPHICS.filter((e) => e.graphics.length > 0).map((e) => ({
    slug: e.studySlug,
  }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const entry = getStudyGraphics(slug);
  if (!entry || entry.graphics.length === 0) return {};
  const study = await getStudyBySlug(slug);
  if (!study) return {};
  return {
    title: `${study.title} graphics`,
    description: `Graphics made from the data in ${study.title}, free to download.`,
    alternates: { canonical: `/studies/${slug}/graphics` },
  };
}

export default async function StudyGraphicsPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const entry = getStudyGraphics(slug);
  if (!entry || entry.graphics.length === 0) notFound();
  const study = await getStudyBySlug(slug);
  if (!study) notFound();

  const [auth, postMap] = await Promise.all([getCurrentUser(), getGraphicPostMap()]);
  const isAdmin = auth?.profile?.is_admin === true;
  const currentPath = `/studies/${study.slug}/graphics`;

  const graphics = isAdmin ? entry.graphics : filterPublished(postMap, slug, entry.graphics);
  if (graphics.length === 0) notFound();

  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <Link
        href={`/studies/${study.slug}`}
        className="inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)] hover:underline"
      >
        <ArrowLeft aria-hidden="true" size={13} />
        {study.title}
      </Link>

      <h1 className="serif mt-4 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        <DeseretTitle text="Graphics" />
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
        Charts made from the data in {study.title}. Free to download and share
        — credit appears on each image.
      </p>

      <div className="mt-12 grid gap-8 sm:grid-cols-2">
        {graphics.map((graphic) => {
          const id = graphicId(graphic);
          const graphicHref = `/studies/${study.slug}/graphics/${id}`;
          const status = postMap[`${slug}/${id}`];
          const published = status?.published === true;
          return (
            <figure
              key={id}
              className={`rounded-[var(--radius)] border bg-white p-5 ${
                isAdmin && !published
                  ? "border-dashed border-[color:var(--oxblood)]/40"
                  : "border-[color:var(--border)]"
              }`}
            >
              <Link
                href={graphicHref}
                className="block overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)]"
              >
                <Image
                  src={graphic.imageSrc}
                  alt={graphic.alt}
                  width={graphic.width}
                  height={graphic.height}
                  className="h-auto w-full"
                />
              </Link>
              <figcaption className="mt-4">
                <div className="flex items-center gap-2">
                  <h2 className="serif text-lg font-semibold leading-snug tracking-tight text-[color:var(--foreground)]">
                    <Link href={graphicHref} className="hover:underline">
                      {graphic.title}
                    </Link>
                  </h2>
                  {isAdmin && !published && <Tag ink="oxblood">Unpublished</Tag>}
                </div>
                <p className="mt-1.5 text-sm leading-relaxed text-[color:var(--muted)]">
                  {graphic.description}
                </p>
                <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
                  {graphic.credit && (
                    <span className="text-xs text-[color:var(--muted)]">{graphic.credit}</span>
                  )}
                  <div className="ml-auto flex flex-wrap items-center gap-2">
                    {isAdmin && (
                      <GraphicAdminControls
                        slug={slug}
                        graphicId={id}
                        published={published}
                        posted={status?.posted === true}
                        postedDates={status?.posted_dates ?? ""}
                        currentPath={currentPath}
                      />
                    )}
                    <GraphicShareButton path={graphicHref} title={graphic.title} />
                    <a
                      href={graphic.imageSrc}
                      download
                      className="inline-flex min-h-9 items-center gap-1.5 rounded-[var(--radius)] border border-[color:var(--border)] px-3 text-xs font-medium hover:bg-[color:var(--muted-soft)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
                    >
                      <Download aria-hidden="true" size={13} />
                      Download
                    </a>
                  </div>
                </div>
              </figcaption>
            </figure>
          );
        })}
      </div>

      <div className="dinkus mt-14" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>
    </div>
  );
}
