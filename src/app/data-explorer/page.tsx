import type { Metadata } from "next";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";
import { CategoryCard, DatasetCard } from "@/components/dataset-card";
import { DATASETS, categorySlug, type Dataset } from "@/lib/data-explorer";

export const metadata: Metadata = {
  title: "Data Explorer",
  description:
    "Public survey and statistical datasets, and what Latter-day Stats has done with them — quizzes, graphics, and write-ups.",
  alternates: { canonical: "/data-explorer" },
};

/**
 * Groups DATASETS by consecutive runs of the same `category` (see that
 * field's own doc comment in src/lib/data-explorer.ts). Each category run
 * collapses into a single CategoryCard "box" in the main grid rather than
 * expanding inline - clicking it goes to its own /data-explorer/category
 * page. Everything else renders as its own normal DatasetCard, in the
 * same flat grid.
 */
function groupByCategory(datasets: Dataset[]): { category: string | null; items: Dataset[] }[] {
  const groups: { category: string | null; items: Dataset[] }[] = [];
  for (const dataset of datasets) {
    const category = dataset.category ?? null;
    const current = groups[groups.length - 1];
    if (current && current.category === category) {
      current.items.push(dataset);
    } else {
      groups.push({ category, items: [dataset] });
    }
  }
  return groups;
}

export default function DataExplorerPage() {
  const groups = groupByCategory(DATASETS);

  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <h1 className="serif text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        <DeseretTitle text="Data Explorer" />
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
        Public survey and statistical datasets, and what we&apos;ve done with each one —
        quizzes you can take, graphics, and write-ups.
      </p>

      <div className="mt-12 grid gap-5 sm:grid-cols-2">
        {groups.map((group) =>
          group.category ? (
            <CategoryCard
              key={group.category}
              category={group.category}
              slug={categorySlug(group.category)}
              items={group.items}
            />
          ) : (
            group.items.map((dataset) => <DatasetCard key={dataset.slug} dataset={dataset} />)
          ),
        )}
      </div>

      <div className="dinkus mt-14" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>
    </div>
  );
}
