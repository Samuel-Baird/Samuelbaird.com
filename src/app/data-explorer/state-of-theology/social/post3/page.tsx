import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { ArrowLeft, Download } from "lucide-react";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";

export const metadata: Metadata = {
  title: "Raw numbers, not percentages, 2025",
  description:
    "How many actual Americans agree with each State of Theology statement, once survey " +
    "percentages are converted to estimated headcounts using Pew RLS tradition shares and " +
    "the 2025 Census population.",
  alternates: { canonical: "/data-explorer/state-of-theology/social/post3" },
};

const SLIDES = [
  { file: "1_teacher_headcount.png", title: "Great teacher, not God — by the numbers" },
];

const BASE = "/social-graphics/state-of-theology/post3";

export default function Post3SocialPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <Link
        href="/data-explorer/state-of-theology"
        className="inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)] hover:underline"
      >
        <ArrowLeft aria-hidden="true" size={13} />
        State of Theology Survey
      </Link>

      <h1 className="serif mt-4 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        <DeseretTitle text="Raw numbers, not percentages" />
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
        Post1 and post2 chart survey <em>percentages</em>. This set converts each
        percentage into an estimated headcount — a tradition&apos;s State of Theology
        agreement rate applied to that tradition&apos;s own share of the U.S. population
        (Pew Religious Landscape Study, 2023-24) and the 2025 Census population estimate —
        then contrasts the total against the Church of Jesus Christ of Latter-day
        Saints&apos; own published U.S. membership, on the same scale.
      </p>

      <div className="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
        {SLIDES.map((slide) => {
          const src = `${BASE}/${slide.file}`;
          return (
            <figure
              key={slide.file}
              className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5"
            >
              <div className="overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)]">
                <Image src={src} alt={slide.title} width={1080} height={1350} className="h-auto w-full" />
              </div>
              <figcaption className="mt-4">
                <h2 className="serif text-base font-semibold leading-snug tracking-tight text-[color:var(--foreground)]">
                  {slide.title}
                </h2>
                <div className="mt-3 flex justify-end">
                  <a
                    href={src}
                    download
                    className="inline-flex min-h-9 items-center gap-1.5 rounded-[var(--radius)] border border-[color:var(--border)] px-3 text-xs font-medium hover:bg-[color:var(--muted-soft)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
                  >
                    <Download aria-hidden="true" size={13} />
                    Download
                  </a>
                </div>
              </figcaption>
            </figure>
          );
        })}
      </div>

      <div className="dinkus mt-14" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>
    </div>
  );
}
