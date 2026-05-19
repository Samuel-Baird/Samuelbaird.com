"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

export type TopStatSlide = {
  label: string;
  title: string;
  href: string;
  metricLabel: string;
  metricValue: string;
  eyebrow: string;
  items: {
    id: string;
    name: string;
    href: string;
    value: string;
    sublabel?: string;
  }[];
};

type TopStatsCarouselProps = {
  slides: TopStatSlide[];
};

export function TopStatsCarousel({ slides }: TopStatsCarouselProps) {
  const [index, setIndex] = useState(0);
  const active = slides[index];

  const canRotate = slides.length > 1;
  const dots = useMemo(() => slides.map((slide) => slide.label), [slides]);

  useEffect(() => {
    if (!canRotate) return;
    const timer = window.setInterval(() => {
      setIndex((current) => (current + 1) % slides.length);
    }, 6500);
    return () => window.clearInterval(timer);
  }, [canRotate, slides.length]);

  if (!active) return null;

  function move(delta: number) {
    setIndex((current) => (current + delta + slides.length) % slides.length);
  }

  return (
    <section className="mt-16">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
            Top statistics
          </p>
          <h2 className="serif mt-2 text-2xl font-semibold tracking-tight sm:text-3xl">
            Leaders across the tracker
          </h2>
        </div>
        {canRotate ? (
          <div className="flex gap-2">
            <button
              type="button"
              aria-label="Previous statistic"
              onClick={() => move(-1)}
              className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-[color:var(--border)] bg-white hover:bg-[color:var(--muted-soft)]"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              type="button"
              aria-label="Next statistic"
              onClick={() => move(1)}
              className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-[color:var(--border)] bg-white hover:bg-[color:var(--muted-soft)]"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        ) : null}
      </div>

      <div className="mt-6 overflow-hidden rounded-2xl border border-[color:var(--border)] bg-white">
        <div className="grid gap-0 md:grid-cols-[0.95fr_1.35fr]">
          <Link
            href={active.href}
            className="flex min-h-72 flex-col justify-between bg-[color:var(--accent-soft)] p-6 transition-colors hover:bg-[color:var(--muted-soft)] sm:p-8"
          >
            <div>
              <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
                {active.eyebrow}
              </p>
              <h3 className="serif mt-3 text-3xl font-semibold leading-tight tracking-tight sm:text-4xl">
                {active.title}
              </h3>
            </div>
            <div className="mt-10">
              <p className="text-xs font-medium uppercase tracking-wider text-[color:var(--muted)]">
                {active.metricLabel}
              </p>
              <p className="serif mt-2 text-5xl font-semibold tabular-nums tracking-tight">
                {active.metricValue}
              </p>
            </div>
          </Link>

          <ol className="divide-y divide-[color:var(--border)]">
            {active.items.map((item, itemIndex) => (
              <li key={item.id}>
                <Link
                  href={item.href}
                  className="grid min-h-16 grid-cols-[2rem_minmax(0,1fr)_auto] items-center gap-3 px-5 py-3.5 hover:bg-[color:var(--muted-soft)] sm:px-6"
                >
                  <span className="text-right text-sm tabular-nums text-[color:var(--muted)]">
                    {itemIndex + 1}
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-semibold text-[color:var(--foreground)]">
                      {item.name}
                    </span>
                    {item.sublabel ? (
                      <span className="mt-0.5 block truncate text-xs text-[color:var(--muted)]">
                        {item.sublabel}
                      </span>
                    ) : null}
                  </span>
                  <span className="text-sm font-medium tabular-nums text-[color:var(--muted)]">
                    {item.value}
                  </span>
                </Link>
              </li>
            ))}
          </ol>
        </div>
      </div>

      {canRotate ? (
        <div className="mt-4 flex flex-wrap gap-2">
          {dots.map((label, dotIndex) => (
            <button
              key={label}
              type="button"
              aria-label={`Show ${label}`}
              aria-current={dotIndex === index}
              onClick={() => setIndex(dotIndex)}
              className={
                "h-2.5 rounded-full transition-all " +
                (dotIndex === index
                  ? "w-8 bg-[color:var(--accent)]"
                  : "w-2.5 bg-[color:var(--border)] hover:bg-[color:var(--muted)]")
              }
            />
          ))}
        </div>
      ) : null}
    </section>
  );
}
