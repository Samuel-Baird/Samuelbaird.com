import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, Download } from "lucide-react";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";
import { DATASETS, getDataset } from "@/lib/data-explorer";

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
        {dataset.graphics.map((graphic) => (
          <figure
            key={graphic.imageSrc}
            className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5"
          >
            <div className="overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)]">
              <Image
                src={graphic.imageSrc}
                alt={graphic.alt}
                width={graphic.width}
                height={graphic.height}
                className="h-auto w-full"
              />
            </div>
            <figcaption className="mt-4">
              <h2 className="serif text-lg font-semibold leading-snug tracking-tight text-[color:var(--foreground)]">
                {graphic.title}
              </h2>
              <p className="mt-1.5 text-sm leading-relaxed text-[color:var(--muted)]">
                {graphic.description}
              </p>
              <div className="mt-3 flex items-center justify-between gap-3">
                {graphic.credit && (
                  <span className="text-xs text-[color:var(--muted)]">{graphic.credit}</span>
                )}
                <a
                  href={graphic.imageSrc}
                  download
                  className="ml-auto inline-flex min-h-9 items-center gap-1.5 rounded-[var(--radius)] border border-[color:var(--border)] px-3 text-xs font-medium hover:bg-[color:var(--muted-soft)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
                >
                  <Download aria-hidden="true" size={13} />
                  Download
                </a>
              </div>
            </figcaption>
          </figure>
        ))}
      </div>

      <div className="dinkus mt-14" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>
    </div>
  );
}
