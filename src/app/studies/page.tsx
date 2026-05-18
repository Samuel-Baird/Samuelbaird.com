import type { Metadata } from "next";
import Link from "next/link";
import { getStudies } from "@/lib/data";

export const metadata: Metadata = {
  title: "Studies",
  description:
    "Academic studies and research relating to the Latter-day Saint community.",
};

export const revalidate = 600;

export default async function StudiesPage() {
  const studies = await getStudies();

  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        Studies
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
        Research library
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
        Curated academic studies relating to the Latter-day Saint community.
        New entries added as they&apos;re reviewed.
      </p>

      <ul className="mt-12 grid gap-5 sm:grid-cols-2">
        {studies.map((s) => (
          <li key={s.id}>
            <Link
              href={`/studies/${s.slug}`}
              className="group block h-full rounded-2xl border border-[color:var(--border)] bg-white p-6 transition-colors hover:border-[color:var(--accent)]"
            >
              <div className="flex flex-wrap items-center gap-2 text-xs text-[color:var(--muted)]">
                {s.year && (
                  <span className="rounded-full bg-[color:var(--muted-soft)] px-2.5 py-1 tabular-nums">
                    {s.year}
                  </span>
                )}
                {s.tags.slice(0, 3).map((t) => (
                  <span
                    key={t}
                    className="rounded-full bg-[color:var(--accent-soft)] px-2.5 py-1 text-[color:var(--accent)]"
                  >
                    {t}
                  </span>
                ))}
              </div>
              <h2 className="serif mt-4 text-xl font-semibold leading-snug tracking-tight text-[color:var(--foreground)] group-hover:text-[color:var(--accent)]">
                {s.title}
              </h2>
              {s.authors.length > 0 && (
                <p className="mt-2 text-sm text-[color:var(--muted)]">
                  {s.authors.join(", ")}
                </p>
              )}
              {s.abstract && (
                <p className="mt-4 line-clamp-4 text-sm leading-relaxed text-[color:var(--foreground)]">
                  {s.abstract}
                </p>
              )}
              <p className="mt-5 text-xs text-[color:var(--accent)]">
                Read study →
              </p>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
