import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";
import { GraphicsGallery } from "@/components/graphics-gallery";
import { getStudiesBySlugs } from "@/lib/data";
import { getAllGraphics } from "@/lib/data-explorer";
import { getAllStudyGraphics, getStudyFolderSlugs } from "@/lib/study-graphics";

export const metadata: Metadata = {
  title: "Graphics Gallery",
  description:
    "Every chart made from every Data Explorer dataset and study, in one searchable gallery — filter by source, fielded period, or religious tradition.",
  alternates: { canonical: "/data-explorer/gallery" },
};

export default async function GraphicsGalleryPage() {
  const studies = await getStudiesBySlugs(getStudyFolderSlugs());
  const graphics = [...getAllGraphics(), ...getAllStudyGraphics(studies)];

  return (
    <div className="w-full px-5 py-14 sm:px-8 sm:py-20">
      <Link
        href="/data-explorer"
        className="inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)] hover:underline"
      >
        <ArrowLeft aria-hidden="true" size={13} />
        Data Explorer
      </Link>

      <h1 className="serif mt-4 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        <DeseretTitle text="Graphics Gallery" />
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
        Every chart across every dataset and study, in one place. Search by keyword, or
        filter by source, fielded period, or religious tradition.
      </p>

      <div className="mt-10">
        <GraphicsGallery graphics={graphics} />
      </div>

      <div className="dinkus mt-14" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>
    </div>
  );
}
