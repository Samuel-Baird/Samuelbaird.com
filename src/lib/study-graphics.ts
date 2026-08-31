import {
  type Graphic,
  graphicId,
  sortGraphicsAlphabetically,
} from "@/lib/data-explorer";
import churchNewsStateGrowthData from "../../docs/study-data/church-news-us-membership-growth-by-state-2000-2025/data.json";
import pewMormonsInAmericaData from "../../docs/study-data/pew-mormons-in-america-2012/data.json";
import religionPerfectionismData from "../../docs/study-data/byu-studies-63-4-religion-and-perfectionism/data.json";

/**
 * Per-study downloadable graphics — the studies-section counterpart of the
 * Data Explorer's per-dataset graphics, sharing the same PNG pipeline
 * (scripts/chart_style.py canvas/fonts/palette), the same `Graphic` shape,
 * and the same alphabetical gallery order. See
 * scripts/study-graphics/STYLE.md for the pipeline contract: every number
 * lives once, in docs/study-data/<study-slug>/data.json (with a `sources`
 * array citing the exact table/page each series was transcribed from), and
 * both the render script and this registry read that one file, so a
 * transcription fix propagates to the PNG and its alt text together.
 *
 * The join key to the database is the study's `slug` in `public.studies` —
 * a renamed slug fails soft (the study page simply shows no graphics), so
 * keep entries here in sync when renaming a study.
 */
export type StudyGraphicsEntry = {
  studySlug: string;
  /** Sorted alphabetically at export, like the Data Explorer's DATASETS. */
  graphics: Graphic[];
  /**
   * Cross-link for a study that duplicates an existing Data Explorer
   * dataset (e.g. the Ligonier State of Theology studies): the study page
   * renders a callout linking to /data-explorer/<slug>/graphics instead of
   * (or in addition to) study-specific PNGs, so the same chart is never
   * committed twice.
   */
  dataExplorerSlug?: string;
  /** Human name for the linked dataset, shown in the callout. */
  dataExplorerName?: string;
};

function churchNewsPctGrowthGraphic(): Graphic {
  const { rows } = churchNewsStateGrowthData.charts["pct-growth-by-state"];
  const alt = rows.map((r) => `${r.label} +${r.pct}%`).join(", ");
  return {
    title: "Membership growth by percent, 2000–2025",
    description:
      "Percent change in reported Latter-day Saint membership over 25 years, in the fastest-growing states and D.C., against the U.S. overall.",
    imageSrc:
      "/study-graphics/church-news-us-membership-growth-by-state-2000-2025/pct-growth-by-state.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart: percent change in reported Latter-day Saint membership by state, 2000–2025. ${alt}.`,
  };
}

function churchNewsGainsGraphic(): Graphic {
  const { rows } = churchNewsStateGrowthData.charts["gains-by-state"];
  const alt = rows.map((r) => `${r.label} +${r.added.toLocaleString()}`).join(", ");
  return {
    title: "Membership growth by headcount, 2000–2025",
    description:
      "States adding the most reported Latter-day Saint members over 25 years, in absolute numbers.",
    imageSrc:
      "/study-graphics/church-news-us-membership-growth-by-state-2000-2025/gains-by-state.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart: reported Latter-day Saint members added by state, 2000–2025. ${alt}.`,
  };
}

function pewReligiousPracticeGraphic(): Graphic {
  const { rows } = pewMormonsInAmericaData.charts["religious-practice"];
  const alt = rows.map((r) => `${r.label} ${r.pct}%`).join(", ");
  return {
    title: "Religious practice among U.S. Mormons",
    description:
      "Share of self-identified Mormon adults who pray daily, call religion very important, attend weekly — and all three at once, 2011.",
    imageSrc: "/study-graphics/pew-mormons-in-america-2012/religious-practice.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart: religious practice among self-identified U.S. Mormon adults, 2011. ${alt}.`,
  };
}

function pewMormonsVsPublicGraphic(): Graphic {
  const { rows } = pewMormonsInAmericaData.charts["mormons-vs-public"];
  const alt = rows
    .map((r) => `${r.label}: Mormons ${r.mormon}%, general public ${r.public}%`)
    .join("; ");
  return {
    title: "Mormons and the general public, side by side",
    description:
      "Where self-identified Mormons and the U.S. general public diverged on family, politics, and moral views, 2011.",
    imageSrc: "/study-graphics/pew-mormons-in-america-2012/mormons-vs-public.png",
    width: 1080,
    height: 1350,
    alt: `Paired bar chart comparing self-identified U.S. Mormons with the general public, 2011. ${alt}.`,
  };
}

function pewMissionServiceGraphic(): Graphic {
  const { rows } = pewMormonsInAmericaData.charts["mission-service"];
  const alt = rows.map((r) => `${r.label} ${r.pct}%`).join(", ");
  return {
    title: "Who has served a full-time mission",
    description:
      "Share of self-identified U.S. Mormons who have served a full-time mission, by gender, 2011.",
    imageSrc: "/study-graphics/pew-mormons-in-america-2012/mission-service.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart: share of self-identified U.S. Mormons who have served a full-time mission, 2011. ${alt}.`,
  };
}

function pewPerceivedDiscriminationGraphic(): Graphic {
  const { rows } = pewMormonsInAmericaData.charts["perceived-discrimination"];
  const alt = rows.map((r) => `${r.label} ${r.pct}%`).join(", ");
  return {
    title: "Perceptions of discrimination, as Mormons see it",
    description:
      "Share of self-identified U.S. Mormons saying each group faces a lot of discrimination in America, 2011.",
    imageSrc:
      "/study-graphics/pew-mormons-in-america-2012/perceived-discrimination.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart: share of U.S. Mormons saying each group faces a lot of discrimination, 2011. ${alt}.`,
  };
}

function perfectionismByGroupGraphic(): Graphic {
  const { rows } = religionPerfectionismData.charts["high-perfectionism-by-group"];
  const alt = rows.map((r) => `${r.label} ${r.pct}%`).join(", ");
  return {
    title: "High toxic perfectionism, by religious group",
    description:
      "Share of youth in the high-toxic-perfectionism category by religious affiliation, from the Foundations longitudinal panel (Utah, Arizona, California).",
    imageSrc:
      "/study-graphics/byu-studies-63-4-religion-and-perfectionism/high-perfectionism-by-group.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart: share of youth in the high-toxic-perfectionism category, by religious group. ${alt}.`,
  };
}

function introjectedMotivationGraphic(): Graphic {
  const { rows } = religionPerfectionismData.charts["introjected-motivation"];
  const alt = rows.map((r) => `${r.label} ${r.pct}%`).join(", ");
  return {
    title: "Guilt-driven religion and perfectionism",
    description:
      "Share of high- vs. low-perfectionism youth in the high-introjected-motivation (guilt/shame-driven religiosity) group.",
    imageSrc:
      "/study-graphics/byu-studies-63-4-religion-and-perfectionism/introjected-motivation.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart: share of youth high in introjected (guilt/shame-driven) religious motivation. ${alt}.`,
  };
}

const RAW_STUDY_GRAPHICS: StudyGraphicsEntry[] = [
  {
    studySlug: "church-news-us-membership-growth-by-state-2000-2025",
    graphics: [churchNewsPctGrowthGraphic(), churchNewsGainsGraphic()],
    // The article's underlying U.S.-total series is already charted, year by
    // year, in this dataset — link rather than re-render it here.
    dataExplorerSlug: "us-membership-growth-2000-2025",
    dataExplorerName: "U.S. Membership Growth 2000–2025",
  },
  {
    studySlug: "pew-mormons-in-america-2012",
    graphics: [
      pewReligiousPracticeGraphic(),
      pewMormonsVsPublicGraphic(),
      pewMissionServiceGraphic(),
      pewPerceivedDiscriminationGraphic(),
    ],
  },
  {
    studySlug: "byu-studies-63-4-religion-and-perfectionism",
    graphics: [perfectionismByGroupGraphic(), introjectedMotivationGraphic()],
  },
  // Link-only entries: these studies duplicate an existing Data Explorer
  // dataset, so their pages point at its graphics instead of committing the
  // same PNGs twice.
  ...[
    "ligonier-theological-awareness-2014",
    "ligonier-state-of-theology-2016",
    "ligonier-state-of-theology-2018",
    "ligonier-state-of-theology-2020",
    "ligonier-state-of-theology-2022",
    "ligonier-state-of-theology-2025",
  ].map((studySlug) => ({
    studySlug,
    graphics: [],
    dataExplorerSlug: "state-of-theology",
    dataExplorerName: "State of Theology",
  })),
  ...[
    "pew-religious-landscape-study-2024",
    "pew-2025-religious-identity",
    "pew-2025-decline-christianity-lds-racial",
    "sltrib-2025-pew-lds-religious-practice",
  ].map((studySlug) => ({
    studySlug,
    graphics: [],
    dataExplorerSlug: "pew-religious-landscape-study",
    dataExplorerName: "Pew Religious Landscape Study 2023–24",
  })),
];

export const STUDY_GRAPHICS: StudyGraphicsEntry[] = RAW_STUDY_GRAPHICS.map(
  (e) => ({ ...e, graphics: sortGraphicsAlphabetically(e.graphics) }),
);

// Build-time guards, mirroring data-explorer.ts's: graphic ids are URL
// segments, so they must be unique within a study, and a study slug must
// appear only once. Throws at module load so `next build` fails loudly.
{
  const seenSlugs = new Set<string>();
  for (const e of STUDY_GRAPHICS) {
    if (seenSlugs.has(e.studySlug)) {
      throw new Error(`Duplicate study-graphics entry for "${e.studySlug}"`);
    }
    seenSlugs.add(e.studySlug);
    const seenIds = new Set<string>();
    for (const g of e.graphics) {
      const id = graphicId(g);
      if (seenIds.has(id)) {
        throw new Error(`Duplicate graphic id "${id}" for study "${e.studySlug}"`);
      }
      seenIds.add(id);
    }
  }
}

export function getStudyGraphics(studySlug: string): StudyGraphicsEntry | undefined {
  return STUDY_GRAPHICS.find((e) => e.studySlug === studySlug);
}

export function getStudyGraphic(studySlug: string, id: string): Graphic | undefined {
  return getStudyGraphics(studySlug)?.graphics.find((g) => graphicId(g) === id);
}
