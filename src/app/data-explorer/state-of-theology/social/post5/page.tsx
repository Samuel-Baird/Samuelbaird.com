import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { ArrowLeft, Download } from "lucide-react";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";

export const metadata: Metadata = {
  title: "Raw numbers, widescreen",
  description:
    "Post3's headcount-not-percentage set, reformatted 16:9 for platforms that want " +
    "landscape images instead of an Instagram-portrait carousel.",
  alternates: { canonical: "/data-explorer/state-of-theology/social/post5" },
};

const SLIDES = [
  { file: "m1_how_it_works.png", title: "How the raw numbers are estimated" },
  { file: "m2_worked_example.png", title: "The same math, four traditions" },
  {
    file: "1_trinity_headcount.png",
    title:
      "“There is one true God in three persons: God the Father, God the Son, and God the Holy Spirit.” — who agree",
  },
  {
    file: "1b_trinity_disagree_headcount.png",
    title:
      "“There is one true God in three persons: God the Father, God the Son, and God the Holy Spirit.” — who disagree",
  },
  { file: "2_arian_headcount.png", title: "“Jesus is the first and greatest being created by God.”" },
  { file: "3_teacher_headcount.png", title: "“Jesus was a great teacher, but he was not God.”" },
  {
    file: "4_spirit_headcount.png",
    title: "“The Holy Spirit is a force but is not a personal being.”",
  },
  {
    file: "5_relig_headcount.png",
    title:
      "“God accepts the worship of all religions, including Christianity, Judaism, and Islam.”",
  },
  {
    file: "6_nature_headcount.png",
    title: "“Everyone sins a little, but most people are good by nature.” — who agree",
  },
  {
    file: "6b_nature_disagree_headcount.png",
    title: "“Everyone sins a little, but most people are good by nature.” — who disagree",
  },
  { file: "7_abortion_headcount.png", title: "“Abortion is a sin.” — who agree" },
  { file: "7b_abortion_disagree_headcount.png", title: "“Abortion is a sin.” — who disagree" },
  {
    file: "8_sex_headcount.png",
    title: "“Sex outside of traditional marriage is a sin.” — who agree",
  },
  {
    file: "8b_sex_disagree_headcount.png",
    title: "“Sex outside of traditional marriage is a sin.” — who disagree",
  },
  {
    file: "9_homo_headcount.png",
    title: "“The Bible's condemnation of homosexual behavior doesn't apply today.” — who disagree",
  },
  {
    file: "9b_homo_agree_headcount.png",
    title: "“The Bible's condemnation of homosexual behavior doesn't apply today.” — who agree",
  },
  {
    file: "10_gender_headcount.png",
    title:
      "“People should be able to choose their gender regardless of their biological sex.” — who disagree",
  },
  {
    file: "10b_gender_agree_headcount.png",
    title:
      "“People should be able to choose their gender regardless of their biological sex.” — who agree",
  },
];

const BASE = "/social-graphics/state-of-theology/post5";

export default function Post5SocialPage() {
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
        <DeseretTitle text="Raw numbers, widescreen" />
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
        The same set as{" "}
        <Link href="/data-explorer/state-of-theology/social/post3" className="underline">
          post3
        </Link>{" "}
        — each State of Theology percentage converted into an estimated headcount and
        contrasted against the Church of Jesus Christ of Latter-day Saints&apos; own
        published U.S. membership — reformatted 16:9 for platforms that want a landscape
        image instead of an Instagram-portrait carousel.
      </p>

      <div className="mt-12 grid gap-8 sm:grid-cols-2">
        {SLIDES.map((slide) => {
          const src = `${BASE}/${slide.file}`;
          return (
            <figure
              key={slide.file}
              className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5"
            >
              <div className="overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)]">
                <Image src={src} alt={slide.title} width={1920} height={1080} className="h-auto w-full" />
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
