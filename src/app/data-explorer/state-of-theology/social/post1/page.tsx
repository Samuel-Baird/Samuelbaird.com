import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { ArrowLeft, Download } from "lucide-react";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";

export const metadata: Metadata = {
  title: "Evangelicals vs. the country, 2016–2025",
  description:
    "An Instagram carousel tracking evangelicals against all U.S. adults across five " +
    "State of Theology survey waves.",
  alternates: { canonical: "/data-explorer/state-of-theology/social/post1" },
};

const SLIDES = [
  { file: "hook_c_combined.png", title: "Hook — 92% believe in the Trinity" },
  { file: "hook_a_created.png", title: "Hook — 61% say Jesus was created" },
  { file: "hook_b_not_god.png", title: "Hook — 44% say Jesus was not God" },
  {
    file: "1_nicaea_won.png",
    title:
      "“There is one true God in three persons: God the Father, God the Son, and God the Holy Spirit.”",
  },
  { file: "2_nicaea_lost.png", title: "“Jesus is the first and greatest being created by God.”" },
  {
    file: "3_one_god_two_persons.png",
    title: "“The Holy Spirit is a force but is not a personal being.”",
  },
  {
    file: "4_many_roads.png",
    title:
      "“God accepts the worship of all religions, including Christianity, Judaism, and Islam.”",
  },
  {
    file: "5_pelagius_undefeated.png",
    title: "“Everyone sins a little, but most people are good by nature.”",
  },
  { file: "6_abortion.png", title: "“Abortion is a sin.”" },
  { file: "7_sex_outside_marriage.png", title: "“Sex outside of traditional marriage is a sin.”" },
  {
    file: "8_condemnation.png",
    title: "“The Bible's condemnation of homosexual behavior doesn't apply today.”",
  },
  { file: "jesus_not_god.png", title: "“Jesus was a great teacher, but he was not God.”" },
  { file: "9_scorecard.png", title: "Firmer, but not firm" },
  { file: "10_thesis.png", title: "Words without weight" },
];

const BASE = "/social-graphics/state-of-theology/post1";

export default function Post1SocialPage() {
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
        <DeseretTitle text="Evangelicals vs. the country" />
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
        An Instagram carousel (@ithinkisam) tracking evangelicals against all U.S. adults
        across five State of Theology survey waves, 2016–2025, plus a 2022 scorecard of
        where evangelical belief is firmest and a closing text card.
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
