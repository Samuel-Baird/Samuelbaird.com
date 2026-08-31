import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { ArrowLeft, Download } from "lucide-react";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";

export const metadata: Metadata = {
  title: "Comparing four traditions, 2025",
  description:
    "An Instagram carousel comparing Evangelical, Black Protestant, Mainline, and Roman " +
    "Catholic respondents across nine State of Theology survey statements.",
  alternates: { canonical: "/data-explorer/state-of-theology/social/post2" },
};

const SLIDES = [
  { file: "0_intro.png", title: "Evangelicals won" },
  { file: "1_trinity.png", title: "Nearly everyone confesses it" },
  { file: "2_arian.png", title: "A majority also deny the Trinity" },
  { file: "3_teacher.png", title: "In most traditions, half say he isn't God" },
  { file: "4_spirit.png", title: "Surprisingly binitarian" },
  { file: "5_relig.png", title: "Most say God accepts every religion" },
  { file: "6_nature.png", title: "Pelagius, still at large" },
  { file: "7_abortion.png", title: "Abortion is a sin" },
  { file: "8_sex.png", title: "Sex outside traditional marriage" },
  { file: "9_homo.png", title: "Biblical authority on sexuality" },
  { file: "10_gender.png", title: "Most reject choosing one's gender" },
  { file: "11_closing.png", title: "Still the beam" },
];

const BASE = "/social-graphics/state-of-theology/post2";

export default function Post2SocialPage() {
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
        <DeseretTitle text="Comparing four traditions" />
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
        An Instagram carousel (@ithinkisam) comparing Evangelical, Black Protestant,
        Mainline, and Roman Catholic respondents across nine State of Theology survey
        statements, 2025 wave unless noted.
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
