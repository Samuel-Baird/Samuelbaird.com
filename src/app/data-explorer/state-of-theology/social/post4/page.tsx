import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { ArrowLeft, Download } from "lucide-react";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";

export const metadata: Metadata = {
  title: "Comparing four traditions, widescreen",
  description:
    "Post2's four-tradition comparison, reformatted 16:9 for platforms that want landscape " +
    "images instead of an Instagram-portrait carousel.",
  alternates: { canonical: "/data-explorer/state-of-theology/social/post4" },
};

const SLIDES = [
  { file: "0_intro.png", title: "Evangelicals won" },
  {
    file: "1_trinity.png",
    title:
      "“There is one true God in three persons: God the Father, God the Son, and God the Holy Spirit.”",
  },
  { file: "2_arian.png", title: "“Jesus is the first and greatest being created by God.”" },
  { file: "3_teacher.png", title: "“Jesus was a great teacher, but he was not God.”" },
  { file: "4_spirit.png", title: "“The Holy Spirit is a force but is not a personal being.”" },
  {
    file: "5_relig.png",
    title:
      "“God accepts the worship of all religions, including Christianity, Judaism, and Islam.”",
  },
  { file: "6_nature.png", title: "“Everyone sins a little, but most people are good by nature.”" },
  { file: "7_abortion.png", title: "“Abortion is a sin.”" },
  { file: "8_sex.png", title: "“Sex outside of traditional marriage is a sin.”" },
  {
    file: "9_homo.png",
    title: "“The Bible's condemnation of homosexual behavior doesn't apply today.”",
  },
  {
    file: "10_gender.png",
    title: "“People should be able to choose their gender regardless of their biological sex.”",
  },
  { file: "11_closing.png", title: "Still the beam" },
];

const BASE = "/social-graphics/state-of-theology/post4";

export default function Post4SocialPage() {
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
        <DeseretTitle text="Comparing four traditions, widescreen" />
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
        The same carousel as{" "}
        <Link href="/data-explorer/state-of-theology/social/post2" className="underline">
          post2
        </Link>{" "}
        — Evangelical, Black Protestant, Mainline, and Roman Catholic respondents across nine
        State of Theology survey statements, 2025 wave unless noted — reformatted 16:9 for
        platforms that want a landscape image instead of an Instagram-portrait carousel.
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
