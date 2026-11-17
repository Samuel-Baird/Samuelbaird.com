"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight } from "lucide-react";

export type HomeGraphic = {
  key: string;
  href: string;
  imageSrc: string;
  width: number;
  height: number;
  alt: string;
  title: string;
  datasetName: string;
};

function shuffled<T>(items: T[]): T[] {
  const out = [...items];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

// The homepage is cached on the server, so the "random every visit" pick has
// to happen in the browser. The server render shows the first few of the pool
// (so no-JS visitors and crawlers still get charts), then each visit reshuffles.
export function HomeGraphicsStrip({
  pool,
  count,
}: {
  pool: HomeGraphic[];
  count: number;
}) {
  const [picks, setPicks] = useState(() => pool.slice(0, count));

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- must run after hydration to avoid a server/client mismatch
    setPicks(shuffled(pool).slice(0, count));
  }, [pool, count]);

  if (picks.length === 0) return null;
  return (
    <section aria-labelledby="home-graphics" className="mt-20">
      <div className="flex flex-col gap-1 sm:flex-row sm:items-baseline sm:justify-between sm:gap-3">
        <h2
          id="home-graphics"
          className="serif text-2xl font-semibold tracking-tight sm:text-3xl"
        >
          From the graphics gallery
        </h2>
        <Link
          href="/data-explorer/gallery"
          className="inline-flex items-center gap-1 text-sm font-medium text-[color:var(--accent)] hover:underline"
        >
          Browse the gallery
          <ArrowRight aria-hidden="true" size={14} />
        </Link>
      </div>
      <ul className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        {picks.map((g) => (
          <li key={g.key}>
            <Link
              href={g.href}
              className="group flex h-full flex-col overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)] bg-white transition-colors hover:border-[color:var(--accent)]"
            >
              <Image
                src={g.imageSrc}
                alt={g.alt}
                width={g.width}
                height={g.height}
                sizes="(min-width: 1024px) 280px, 50vw"
                className="aspect-[4/3] w-full border-b border-[color:var(--border)] object-cover object-top"
              />
              <div className="p-3">
                <h3 className="line-clamp-2 text-sm font-medium group-hover:text-[color:var(--accent)]">
                  {g.title}
                </h3>
                <p className="small-caps mt-1 truncate text-[11px] text-[color:var(--muted)]">
                  {g.datasetName}
                </p>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
