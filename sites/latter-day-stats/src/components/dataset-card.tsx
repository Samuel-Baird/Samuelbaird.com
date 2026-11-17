import Link from "next/link";
import { ArrowRight, BarChart3, Folder } from "lucide-react";
import { type Dataset } from "@/lib/data-explorer";
import type { Study } from "@/lib/types";

/** One dataset's card on the Data Explorer index or a category page. */
export function DatasetCard({ dataset }: { dataset: Dataset }) {
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
 * A folder-style card representing an entire dataset category (e.g.
 * "Mixed Datasets") on the Data Explorer index. Clicking it goes to
 * /data-explorer/category/<slug>, which lists that category's own
 * datasets as DatasetCards - the category itself never expands inline.
 */
export function CategoryCard({ category, slug, items }: { category: string; slug: string; items: Dataset[] }) {
  return (
    <Link
      href={`/data-explorer/category/${slug}`}
      className="group flex flex-col justify-between rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6 no-underline transition-colors hover:border-[color:var(--accent)]"
    >
      <div>
        <span className="small-caps inline-flex items-center gap-1.5 text-[11px] font-medium text-[color:var(--accent)]">
          <Folder aria-hidden="true" size={13} />
          Collection
        </span>
        <h3 className="serif mt-2 text-xl font-semibold tracking-tight text-[color:var(--foreground)] group-hover:text-[color:var(--accent)]">
          {category}
        </h3>
        <p className="mt-2 text-sm leading-relaxed text-[color:var(--muted)]">
          {items.length} {items.length === 1 ? "dataset" : "datasets"}: {items.map((d) => d.name).join(", ")}
        </p>
      </div>
      <span className="mt-5 inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)]">
        View collection
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
 * A study's card on the Data Explorer index, alongside DatasetCard and
 * CategoryCard - the studies-section counterpart, for a study that has its
 * own downloadable graphics (see study-graphics.ts's getStudyFolderSlugs).
 * Links to the study's own page, which is where its graphics teaser lives
 * (mirroring how DatasetCard links to the dataset's own page rather than
 * straight to /graphics).
 */
export function StudyCard({
  study,
  graphicsCount,
}: {
  study: Pick<Study, "slug" | "title" | "authors" | "year">;
  graphicsCount: number;
}) {
  return (
    <Link
      href={`/studies/${study.slug}`}
      className="group flex flex-col justify-between rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6 no-underline transition-colors hover:border-[color:var(--accent)]"
    >
      <div>
        <span className="small-caps inline-flex items-center gap-1.5 text-[11px] font-medium text-[color:var(--honey)]">
          <BarChart3 aria-hidden="true" size={13} />
          Study
        </span>
        <h3 className="serif mt-2 text-xl font-semibold tracking-tight text-[color:var(--foreground)] group-hover:text-[color:var(--accent)]">
          {study.title}
        </h3>
        <p className="small-caps mt-3 text-[11px] text-[color:var(--muted)]">
          {study.authors.length > 0 ? study.authors.join(", ") : "Studies"}
          {study.year ? ` · ${study.year}` : ""}
        </p>
      </div>
      <span className="mt-5 inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)]">
        {graphicsCount} {graphicsCount === 1 ? "graphic" : "graphics"}
        <ArrowRight
          aria-hidden="true"
          size={13}
          className="transition-transform group-hover:translate-x-0.5"
        />
      </span>
    </Link>
  );
}
