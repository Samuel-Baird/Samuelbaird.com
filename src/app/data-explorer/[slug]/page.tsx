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

  const previewGraphic = dataset.graphics[0];

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

      <div className="mt-12 lg:grid lg:grid-cols-[minmax(0,1fr)_20rem] lg:gap-14">
        <div className="max-w-2xl space-y-8">
          {dataset.howWeUseIt && (
            <section className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6 sm:p-7">
              <h2 className="small-caps text-[11px] font-medium text-[color:var(--accent)]">
                How we use it
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-[color:var(--muted)]">
                {dataset.howWeUseIt}
              </p>
            </section>
          )}

          {dataset.quiz && (
            <Link
              href={dataset.quiz.href}
              className="group block rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6 no-underline transition-colors hover:border-[color:var(--accent)] sm:p-7"
            >
              <span className="small-caps inline-flex items-center gap-1.5 text-[11px] font-medium text-[color:var(--accent)]">
                <ClipboardList aria-hidden="true" size={13} />
                Quiz
              </span>
              <h2 className="serif mt-2 text-2xl font-semibold tracking-tight text-[color:var(--foreground)] group-hover:text-[color:var(--accent)]">
                {dataset.quiz.title}
              </h2>
              <p className="mt-2 max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
                {dataset.quiz.description}
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
          )}

          {previewGraphic && (
            <Link
              href={`/data-explorer/${dataset.slug}/graphics`}
              className="group block rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6 no-underline transition-colors hover:border-[color:var(--accent)] sm:p-7"
            >
              <span className="small-caps inline-flex items-center gap-1.5 text-[11px] font-medium text-[color:var(--honey)]">
                <BarChart3 aria-hidden="true" size={13} />
                Graphics
              </span>
              <h2 className="serif mt-2 text-2xl font-semibold tracking-tight text-[color:var(--foreground)] group-hover:text-[color:var(--accent)]">
                {dataset.graphics.length}{" "}
                {dataset.graphics.length === 1 ? "graphic" : "graphics"}
              </h2>
              <div className="mt-4 w-40 overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)]">
                <Image
                  src={previewGraphic.imageSrc}
                  alt={previewGraphic.alt}
                  width={previewGraphic.width}
                  height={previewGraphic.height}
                  className="h-auto w-full"
                />
              </div>
              <span className="mt-4 inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)]">
                View all graphics
                <ArrowRight
                  aria-hidden="true"
                  size={13}
                  className="transition-transform group-hover:translate-x-0.5"
                />
              </span>
            </Link>
          )}
        </div>

        <aside className="mt-10 space-y-8 lg:mt-0 lg:border-l lg:border-[color:var(--border)] lg:pl-10">
          {dataset.citation && (
            <section>
              <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
                Cite it as
              </h2>
              <p className="mt-3 text-sm leading-relaxed text-[color:var(--muted)]">
                {dataset.citation}
              </p>
              <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1">
                {dataset.doi && (
                  <a
                    href={`https://doi.org/${dataset.doi}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs font-medium text-[color:var(--accent)] hover:underline"
                  >
                    doi.org/{dataset.doi}
                  </a>
                )}
                {dataset.sourceUrl && (
                  <a
                    href={dataset.sourceUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs font-medium text-[color:var(--accent)] hover:underline"
                  >
                    Download the dataset
                  </a>
                )}
              </div>
            </section>
          )}

          {dataset.selfDescription && (
            <section>
              <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
                How {dataset.sponsor} describes it
              </h2>
              <blockquote className="mt-3 space-y-3 border-l-2 border-[color:var(--border)] pl-4 text-sm leading-relaxed text-[color:var(--muted)]">
                {dataset.selfDescription.quote.split("\n\n").map((para, i) => (
                  <p key={i}>{para}</p>
                ))}
              </blockquote>
              <a
                href={dataset.selfDescription.sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-2 inline-block text-xs font-medium text-[color:var(--accent)] hover:underline"
              >
                {dataset.selfDescription.sourceLabel}
              </a>
            </section>
          )}

          {dataset.methodology && (
            <section>
              <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
                Methodology
              </h2>
              <ul className="mt-3 space-y-2 text-sm leading-relaxed text-[color:var(--muted)]">
                {dataset.methodology.map((line, i) => (
                  <li key={i}>{line}</li>
                ))}
              </ul>
              {dataset.methodologySourceUrl && (
                <a
                  href={dataset.methodologySourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-2 inline-block text-xs font-medium text-[color:var(--accent)] hover:underline"
                >
                  {dataset.methodologySourceUrl.replace(/^https?:\/\//, "")}
                </a>
              )}
            </section>
          )}
        </aside>
      </div>

      <div className="dinkus mt-14" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>
    </div>
  );
}
