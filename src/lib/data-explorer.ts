/**
 * The Data Explorer: a home for public survey/statistical datasets and
 * whatever's been done with them here — quizzes, graphics, write-ups.
 * Adding a dataset or an analysis is a data change to this file, not a new
 * route or component, the same reasoning as the quiz's own tradition
 * lookup table (see scripts/evangelical-quiz/README.md).
 */

export type Quiz = {
  title: string;
  description: string;
  href: string;
};

export type Graphic = {
  /** Neutral - the survey statement itself. See the graphics style guide's
   * "Titles: neutral, not editorial" for why this is never an editorial
   * claim on the website, unlike @ithinkisam's social posts. */
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

/** A direct quotation of how the dataset's own source describes itself. */
export type SelfDescription = {
  quote: string;
  sourceLabel: string;
  sourceUrl: string;
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
  selfDescription?: SelfDescription;
  /** Verbatim methodology lines, in order, from the source's own writeup. */
  methodology?: string[];
  methodologySourceUrl?: string;
  quiz?: Quiz;
  graphics: Graphic[];
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
    selfDescription: {
      quote:
        "The State of Theology is a nationwide survey revealing how people today view key " +
        "doctrines of the Christian faith.\n\n" +
        "R.C. Sproul said that everyone is a theologian. The question is whether you're a " +
        "good theologian or a poor one.\n\n" +
        "Do your beliefs align with what God has revealed? Are your values and priorities " +
        "based in the truth? Or do you embrace confused ideas that can lead your whole life " +
        "astray?\n\n" +
        "Every few years, this survey takes America's theological temperature, revealing " +
        "what people actually believe — both outside and inside the church. Our goal is to " +
        "diagnose prominent errors and to prescribe the cure: the clear teaching of sound " +
        "doctrine. We hope these findings equip Christians with insights for discipleship.",
      sourceLabel: "thestateoftheology.com",
      sourceUrl: "https://thestateoftheology.com/",
    },
    methodology: [
      "A demographically balanced online panel was used for interviewing American adults.",
      "3,001 surveys were completed January 6–15, 2025.",
      "The sample provides 95% confidence that the sampling error from the online panel " +
        "does not exceed ±1.9%.",
      "Margins of error are higher in sub-groups.",
      "Slight weights were used to balance gender, age, ethnicity, income, region, and " +
        "religion.",
    ],
    methodologySourceUrl: "https://thestateoftheology.com/",
    quiz: {
      title: "How evangelical are you?",
      description:
        "Answer belief statements from the survey and see which tradition you answer most " +
        "like, and how evangelical your answers are relative to the rest of the country.",
      href: "/how-evangelical",
    },
    graphics: [
      {
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
