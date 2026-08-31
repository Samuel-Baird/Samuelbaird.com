import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, Download } from "lucide-react";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";
import { GraphicAdminOverlay } from "@/components/admin/graphic-admin-overlay";
import { GraphicShareButton } from "@/components/data-explorer/graphic-share-button";
import { Tag } from "@/components/tag";
import { getCurrentUser } from "@/lib/auth";
import { DATASETS, getDataset, graphicId } from "@/lib/data-explorer";
import { filterPublished, getGraphicPostMap } from "@/lib/graphic-posts";

export function generateStaticParams() {
  return DATASETS.map((d) => ({ slug: d.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const dataset = getDataset(slug);
  if (!dataset) return {};
  return {
    title: `${dataset.name} graphics`,
    description: `Graphics made from the ${dataset.name} dataset, free to download.`,
    alternates: { canonical: `/data-explorer/${dataset.slug}/graphics` },
  };
}

export default async function DatasetGraphicsPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const dataset = getDataset(slug);
  if (!dataset) notFound();

  const [auth, postMap] = await Promise.all([getCurrentUser(), getGraphicPostMap()]);
  const isAdmin = auth?.profile?.is_admin === true;
  const currentPath = `/data-explorer/${dataset.slug}/graphics`;

  const graphics = isAdmin ? dataset.graphics : filterPublished(postMap, slug, dataset.graphics);
  if (graphics.length === 0) notFound();

  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <Link
        href={`/data-explorer/${dataset.slug}`}
        className="inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)] hover:underline"
      >
        <ArrowLeft aria-hidden="true" size={13} />
        {dataset.name}
      </Link>

      <h1 className="serif mt-4 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        <DeseretTitle text="Graphics" />
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
        Charts made from the {dataset.name} dataset. Free to download and share — credit
        appears on each image.
      </p>

      <div className="mt-12 grid gap-8 sm:grid-cols-2">
        {graphics.map((graphic) => {
          const id = graphicId(graphic);
          const graphicHref = `/data-explorer/${dataset.slug}/graphics/${id}`;
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
              <div className="relative">
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
                {isAdmin && (
                  <GraphicAdminOverlay
                    slug={slug}
                    graphicId={id}
                    published={published}
                    posted={status?.posted === true}
                    postedDates={status?.posted_dates ?? ""}
                    currentPath={currentPath}
                  />
                )}
              </div>
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
                <div className="mt-3 flex items-center justify-between gap-3">
                  {graphic.credit && (
                    <span className="text-xs text-[color:var(--muted)]">{graphic.credit}</span>
                  )}
                  <div className="ml-auto flex items-center gap-2">
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
