import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, ArrowRight, BarChart3, ClipboardList } from "lucide-react";
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
    title: dataset.name,
    description: dataset.shortDescription,
    alternates: { canonical: `/data-explorer/${dataset.slug}` },
  };
}

export default async function DatasetPage({
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
        href="/data-explorer"
        className="inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)] hover:underline"
      >
        <ArrowLeft aria-hidden="true" size={13} />
        Data Explorer
      </Link>

      <h1 className="serif mt-4 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        <DeseretTitle text={dataset.name} />
      </h1>
      <p className="small-caps mt-3 text-[11px] text-[color:var(--muted)]">
        {dataset.sponsor} · {dataset.fielder}
      </p>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
        {dataset.description}
      </p>

      <div className="mt-12 space-y-8">
        {dataset.analyses.map((analysis) =>
          analysis.type === "quiz" ? (
            <Link
              key={analysis.title}
              href={analysis.href}
              className="group block rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6 no-underline transition-colors hover:border-[color:var(--accent)] sm:p-7"
            >
              <span className="small-caps inline-flex items-center gap-1.5 text-[11px] font-medium text-[color:var(--accent)]">
                <ClipboardList aria-hidden="true" size={13} />
                Quiz
              </span>
              <h2 className="serif mt-2 text-2xl font-semibold tracking-tight text-[color:var(--foreground)] group-hover:text-[color:var(--accent)]">
                {analysis.title}
              </h2>
              <p className="mt-2 max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
                {analysis.description}
              </p>
              <span className="mt-4 inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)]">
                Take the quiz
                <ArrowRight
                  aria-hidden="true"
                  size={13}
                  className="transition-transform group-hover:translate-x-0.5"
                />
              </span>
            </Link>
          ) : (
            <figure
              key={analysis.title}
              className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6 sm:p-7"
            >
              <span className="small-caps inline-flex items-center gap-1.5 text-[11px] font-medium text-[color:var(--honey)]">
                <BarChart3 aria-hidden="true" size={13} />
                Graphic
              </span>
              <h2 className="serif mt-2 text-2xl font-semibold tracking-tight text-[color:var(--foreground)]">
                {analysis.title}
              </h2>
              <p className="mt-2 max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
                {analysis.description}
              </p>
              <div className="mt-5 max-w-sm overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)]">
                <Image
                  src={analysis.imageSrc}
                  alt={analysis.alt}
                  width={analysis.width}
                  height={analysis.height}
                  className="h-auto w-full"
                />
              </div>
              {analysis.credit && (
                <figcaption className="mt-2 text-xs text-[color:var(--muted)]">
                  {analysis.credit}
                </figcaption>
              )}
            </figure>
          ),
        )}
      </div>

      <div className="dinkus mt-14" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>
    </div>
  );
}
