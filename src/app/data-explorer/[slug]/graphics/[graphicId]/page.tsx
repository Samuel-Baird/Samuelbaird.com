import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, Download } from "lucide-react";
import { BeehiveMark } from "@/components/beehive-mark";
import { GraphicShareButton } from "@/components/data-explorer/graphic-share-button";
import { DATASETS, getDataset, getGraphic, graphicId as idOf } from "@/lib/data-explorer";

export function generateStaticParams() {
  return DATASETS.flatMap((d) =>
    d.graphics.map((g) => ({ slug: d.slug, graphicId: idOf(g) })),
  );
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string; graphicId: string }>;
}): Promise<Metadata> {
  const { slug, graphicId } = await params;
  const dataset = getDataset(slug);
  const graphic = dataset && getGraphic(slug, graphicId);
  if (!dataset || !graphic) return {};

  return {
    title: graphic.title,
    description: graphic.description,
    alternates: { canonical: `/data-explorer/${slug}/graphics/${graphicId}` },
    // A leaf openGraph block replaces the root opengraph-image.tsx entirely
    // (Next merges metadata shallowly, root -> leaf), so this graphic's own
    // PNG becomes the link preview - no separate opengraph-image route
    // needed here.
    openGraph: {
      title: graphic.title,
      description: graphic.description,
      images: [
        {
          url: graphic.imageSrc,
          width: graphic.width,
          height: graphic.height,
          alt: graphic.alt,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      images: [graphic.imageSrc],
    },
  };
}

export default async function GraphicPage({
  params,
}: {
  params: Promise<{ slug: string; graphicId: string }>;
}) {
  const { slug, graphicId } = await params;
  const dataset = getDataset(slug);
  const graphic = dataset && getGraphic(slug, graphicId);
  if (!dataset || !graphic) notFound();

  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <Link
        href={`/data-explorer/${dataset.slug}/graphics`}
        className="inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)] hover:underline"
      >
        <ArrowLeft aria-hidden="true" size={13} />
        {dataset.name} graphics
      </Link>

      <div className="mt-8 grid gap-8 md:grid-cols-[minmax(0,1fr)_320px]">
        <div className="overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)]">
          <Image
            src={graphic.imageSrc}
            alt={graphic.alt}
            width={graphic.width}
            height={graphic.height}
            priority
            className="h-auto w-full"
          />
        </div>

        <div>
          <h1 className="serif text-2xl font-semibold leading-snug tracking-tight">
            {graphic.title}
          </h1>
          <p className="mt-3 text-sm leading-relaxed text-[color:var(--muted)]">
            {graphic.description}
          </p>
          {graphic.credit && (
            <p className="mt-3 text-xs text-[color:var(--muted)]">{graphic.credit}</p>
          )}

          <div className="mt-6 flex flex-wrap gap-3">
            <GraphicShareButton
              path={`/data-explorer/${dataset.slug}/graphics/${graphicId}`}
              title={graphic.title}
            />
            <a
              href={graphic.imageSrc}
              download
              className="inline-flex min-h-9 items-center gap-1.5 rounded-[var(--radius)] border border-[color:var(--border)] px-3 text-xs font-medium hover:bg-[color:var(--muted-soft)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
            >
              <Download aria-hidden="true" size={13} />
              Download
            </a>
          </div>

          <Link
            href={`/data-explorer/${dataset.slug}`}
            className="mt-6 inline-block text-xs text-[color:var(--accent)] hover:underline"
          >
            About the {dataset.name} dataset
          </Link>
        </div>
      </div>

      <div className="dinkus mt-14" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>
    </div>
  );
}
