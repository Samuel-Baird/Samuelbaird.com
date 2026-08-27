import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";
import { DatasetCard } from "@/components/dataset-card";
import { DATASETS, categorySlug, getDatasetsByCategory } from "@/lib/data-explorer";

function allCategorySlugs(): string[] {
  const slugs = new Set<string>();
  for (const d of DATASETS) {
    if (d.category) slugs.add(categorySlug(d.category));
  }
  return [...slugs];
}

export function generateStaticParams() {
  return allCategorySlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const items = getDatasetsByCategory(slug);
  if (items.length === 0) return {};
  const category = items[0].category!;
  return {
    title: category,
    description: `${items.length} dataset${items.length === 1 ? "" : "s"} in the ${category} collection.`,
    alternates: { canonical: `/data-explorer/category/${slug}` },
  };
}

export default async function CategoryPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const items = getDatasetsByCategory(slug);
  if (items.length === 0) notFound();
  const category = items[0].category!;

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
        <DeseretTitle text={category} />
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
        {items.length} {items.length === 1 ? "dataset" : "datasets"} in this collection.
      </p>

      <div className="mt-12 grid gap-5 sm:grid-cols-2">
        {items.map((dataset) => (
          <DatasetCard key={dataset.slug} dataset={dataset} />
        ))}
      </div>

      <div className="dinkus mt-14" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>
    </div>
  );
}
