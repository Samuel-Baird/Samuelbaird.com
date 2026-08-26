/**
 * The Data Explorer: a home for public survey/statistical datasets and
 * whatever's been done with them here — quizzes, graphics, write-ups.
 * Adding a dataset or an analysis is a data change to this file, not a new
 * route or component, the same reasoning as the quiz's own tradition
 * lookup table (see scripts/evangelical-quiz/README.md).
 */

export type Analysis =
  | {
      type: "quiz";
      title: string;
      description: string;
      href: string;
    }
  | {
      type: "graphic";
      title: string;
      description: string;
      imageSrc: string;
      /** Image width/height in px, for next/image and to avoid layout shift. */
      width: number;
      height: number;
      alt: string;
      /** Where the graphic itself credits its source, e.g. an @handle. */
      credit?: string;
    };

export type Dataset = {
  slug: string;
  name: string;
  /** One line, for the index card. */
  shortDescription: string;
  sponsor: string;
  fielder: string;
  /** A paragraph or two, for the dataset's own page. */
  description: string;
  analyses: Analysis[];
};

export const DATASETS: Dataset[] = [
  {
    slug: "state-of-theology",
    name: "State of Theology Survey",
    shortDescription:
      "A national survey of American theological belief, run every two years since 2014.",
    sponsor: "Ligonier Ministries",
    fielder: "Lifeway Research",
    description:
      "Ligonier Ministries and Lifeway Research have surveyed American adults on their " +
      "theological beliefs every two years since 2014 — around 3,000 respondents per wave, " +
      "broken out by religious tradition (Evangelical, Black Protestant, Mainline Protestant, " +
      "Roman Catholic) alongside the general population. Some statements have run in every " +
      "wave; others have been added, retired, or reworded over time.",
    analyses: [
      {
        type: "quiz",
        title: "How evangelical are you?",
        description:
          "Answer belief statements from the survey and see which tradition you answer most " +
          "like, and how evangelical your answers are relative to the rest of the country.",
        href: "/how-evangelical",
      },
      {
        type: "graphic",
        title: '"Jesus is the first and greatest being created by God."',
        description: "Agreement by religious tradition, 2022 wave.",
        imageSrc: "/data-explorer/state-of-theology/nicaea-lost.png",
        width: 1080,
        height: 1350,
        alt:
          'Bar chart: share who agree "Jesus is the first and greatest being created by God," ' +
          "by religious tradition. Evangelical 61%, Black Protestant 78%, Mainline 61%, Roman " +
          "Catholic 71%, All U.S. adults 55%.",
        credit: "@ithinkisam",
      },
    ],
  },
];

export function getDataset(slug: string): Dataset | undefined {
  return DATASETS.find((d) => d.slug === slug);
}
