import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";
import { FolderExplorer } from "@/components/folder-explorer";
import { getStudiesBySlugs } from "@/lib/data";
import { DATASETS } from "@/lib/data-explorer";
import { buildDatasetFolders, buildStudyFolders } from "@/lib/explorer-folders";
import { getStudyFolderSlugs, STUDY_GRAPHICS } from "@/lib/study-graphics";

export const metadata: Metadata = {
  title: "Data Explorer",
  description:
    "Public survey and statistical datasets, and what Latter-day Stats has done with them — quizzes, graphics, and write-ups.",
  alternates: { canonical: "/data-explorer" },
};

export default async function DataExplorerPage() {
  const datasetFolders = buildDatasetFolders(DATASETS);

  const studySlugs = getStudyFolderSlugs();
  const studies = await getStudiesBySlugs(studySlugs);
  const graphicsBySlug = new Map(STUDY_GRAPHICS.map((e) => [e.studySlug, e.graphics]));
  const studyFolders = buildStudyFolders(studies, graphicsBySlug);

  const folders = [...datasetFolders, ...studyFolders];

  return (
    <div className="w-full px-5 py-14 sm:px-8 sm:py-20">
      <h1 className="serif text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        <DeseretTitle text="Data Explorer" />
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
        Public survey and statistical datasets, and what we&apos;ve done with each one —
        quizzes you can take, graphics, and write-ups — plus every study with its own
        downloadable charts.
      </p>
      <Link
        href="/data-explorer/gallery"
        className="group mt-5 inline-flex items-center gap-1.5 text-sm font-medium text-[color:var(--accent)] hover:underline"
      >
        Browse every graphic in one gallery
        <ArrowRight
          aria-hidden="true"
          size={13}
          className="transition-transform group-hover:translate-x-0.5"
        />
      </Link>

      <div className="mt-10">
        <FolderExplorer folders={folders} />
      </div>

      <div className="dinkus mt-14" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>
    </div>
  );
}
