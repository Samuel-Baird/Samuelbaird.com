"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Tag, type TagInk } from "@/components/tag";
import type { Study } from "@/lib/types";

function previewUrl(path: string | null): string | null {
  if (!path) return null;
  const base = process.env.NEXT_PUBLIC_SUPABASE_URL;
  if (!base) return null;
  return `${base}/storage/v1/object/public/studies/${path}`;
}

const SOURCE_TYPE_LABELS: Record<string, { label: string; ink: TagInk }> = {
  primary_dataset: {
    label: "Primary Dataset",
    ink: "accent",
  },
  study: {
    label: "Study",
    ink: "ink",
  },
  secondary_analysis: {
    label: "Secondary Analysis",
    ink: "muted",
  },
  blog_analysis: {
    label: "Blog Analysis",
    ink: "honey",
  },
};

const PAGE_SIZE = 4;
const ROTATE_MS = 6000;

export function StudiesCarousel({ studies }: { studies: Study[] }) {
  const pageCount = Math.max(1, Math.ceil(studies.length / PAGE_SIZE));
  const [page, setPage] = useState(0);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    if (paused || pageCount <= 1) return;
    const id = setInterval(() => {
      setPage((p) => (p + 1) % pageCount);
    }, ROTATE_MS);
    return () => clearInterval(id);
  }, [paused, pageCount]);

  if (studies.length === 0) return null;

  const start = page * PAGE_SIZE;
  const visible = studies.slice(start, start + PAGE_SIZE);

  return (
    <section
      className="mt-20"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      <div className="flex items-end justify-between gap-3">
        <h2 className="serif text-2xl font-semibold tracking-tight sm:text-3xl">
          From the research library
        </h2>
        <Link
          href="/studies"
          className="text-sm text-[color:var(--accent)] hover:underline"
        >
          View all →
        </Link>
      </div>
      <ul className="mt-6 grid gap-5 sm:grid-cols-2">
        {visible.map((s) => (
          <StudyCard key={s.id} study={s} />
        ))}
      </ul>
      {pageCount > 1 && (
        <div className="mt-5 flex items-center justify-center gap-2">
          {Array.from({ length: pageCount }).map((_, i) => (
            <button
              key={i}
              type="button"
              aria-label={`Show studies page ${i + 1}`}
              onClick={() => setPage(i)}
              className={
                "h-1.5 rounded-full transition-all " +
                (i === page
                  ? "w-6 bg-[color:var(--accent)]"
                  : "w-1.5 bg-[color:var(--border)] hover:bg-[color:var(--muted)]")
              }
            />
          ))}
        </div>
      )}
    </section>
  );
}

function StudyCard({ study: s }: { study: Study }) {
  const sourceType = s.source_type ? SOURCE_TYPE_LABELS[s.source_type] : null;
  const imgUrl = previewUrl(s.preview_image_path);
  return (
    <li className="relative">
      <Link
        href={`/studies/${s.slug}`}
        className={
          "group block h-full overflow-hidden rounded-[var(--radius)] border bg-white transition-colors " +
          (s.flagged_problematic
            ? "border-[color:var(--border)] hover:border-red-500"
            : "border-[color:var(--border)] hover:border-[color:var(--accent)]")
        }
      >
        {imgUrl && (
          <div className="relative aspect-[16/9] w-full overflow-hidden bg-[color:var(--muted-soft)]">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={imgUrl}
              alt={s.preview_image_caption ?? ""}
              loading="lazy"
              className="h-full w-full object-cover"
            />
            {s.preview_image_is_ai && (
              <span className="absolute bottom-2 left-2 rounded-[var(--radius)] bg-black/70 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-white">
                AI · not from study
              </span>
            )}
          </div>
        )}
        <div className="p-6">
          <div className="flex flex-wrap items-center gap-2 text-xs text-[color:var(--muted)]">
            {sourceType && <Tag ink={sourceType.ink}>{sourceType.label}</Tag>}
            {s.year && <Tag>{s.year}</Tag>}
            {s.tags.slice(0, 2).map((t) => (
              <Tag key={t} ink="accent">
                {t}
              </Tag>
            ))}
          </div>
          <h3 className="serif mt-4 text-xl font-semibold leading-snug tracking-tight text-[color:var(--foreground)] group-hover:text-[color:var(--accent)]">
            {s.title}
          </h3>
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
          <p className="mt-5 text-xs text-[color:var(--accent)]">Read study →</p>
        </div>
      </Link>
    </li>
  );
}
