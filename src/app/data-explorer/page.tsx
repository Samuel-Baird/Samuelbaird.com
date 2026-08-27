import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";
import { DATASETS, type Dataset } from "@/lib/data-explorer";

export const metadata: Metadata = {
  title: "Data Explorer",
  description:
    "Public survey and statistical datasets, and what Latter-day Stats has done with them — quizzes, graphics, and write-ups.",
  alternates: { canonical: "/data-explorer" },
};

function DatasetCard({ dataset }: { dataset: Dataset }) {
  const count = (dataset.quiz ? 1 : 0) + dataset.graphics.length;
  return (
    <Link
      href={`/data-explorer/${dataset.slug}`}
      className="group flex flex-col justify-between rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6 no-underline transition-colors hover:border-[color:var(--accent)]"
    >
      <div>
        <h3 className="serif text-xl font-semibold tracking-tight text-[color:var(--foreground)] group-hover:text-[color:var(--accent)]">
          {dataset.name}
        </h3>
        <p className="mt-2 text-sm leading-relaxed text-[color:var(--muted)]">
          {dataset.shortDescription}
        </p>
        <p className="small-caps mt-3 text-[11px] text-[color:var(--muted)]">
          {dataset.sponsor} · {dataset.fielder}
        </p>
      </div>
      <span className="mt-5 inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)]">
        {/* A dataset earns a card as soon as the site uses it — the
            analyses can come later, so don't advertise "0 analyses". */}
        {count === 0
          ? "About this dataset"
          : `${count} ${count === 1 ? "analysis" : "analyses"}`}
        <ArrowRight
          aria-hidden="true"
          size={13}
          className="transition-transform group-hover:translate-x-0.5"
        />
      </span>
    </Link>
  );
}

/**
 * Groups DATASETS by consecutive runs of the same `category` (see that
 * field's own doc comment in src/lib/data-explorer.ts) - a category
 * becomes its own labeled section; everything else falls into one
 * unlabeled default section, same flat grid the page always had.
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

      {groups.map((group, i) => (
        <section key={group.category ?? `_ungrouped_${i}`} className="mt-12">
          {group.category && (
            <h2 className="serif mb-5 text-2xl font-semibold tracking-tight">{group.category}</h2>
          )}
          <div className="grid gap-5 sm:grid-cols-2">
            {group.items.map((dataset) => (
              <DatasetCard key={dataset.slug} dataset={dataset} />
            ))}
          </div>
        </section>
      ))}

      <div className="dinkus mt-14" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>
    </div>
  );
}
