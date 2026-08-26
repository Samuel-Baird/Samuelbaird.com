/**
 * The Data Explorer: a home for public survey/statistical datasets and
 * whatever's been done with them here — quizzes, graphics, write-ups.
 * Adding a dataset or an analysis is a data change to this file, not a new
 * route or component, the same reasoning as the quiz's own tradition
 * lookup table (see scripts/evangelical-quiz/README.md).
 */

import { fiveColumnPct, groupBreakdownRows, QUIZ_DATA } from "@/lib/evangelical-quiz";

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
  /** The source's own recommended citation, verbatim. */
  citation?: string;
  /** Bare DOI, e.g. "10.58094/3kwb-bf52" - linked via doi.org. */
  doi?: string;
  /** Where the dataset itself can be downloaded. */
  sourceUrl?: string;
  /**
   * What this site does with the dataset beyond the quizzes and graphics
   * below - the reason it's listed even before there's an analysis of it.
   */
  howWeUseIt?: string;
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
    graphics: stateOfTheologyGraphics(),
  },
  {
    slug: "pew-religious-landscape-study",
    name: "Religious Landscape Study",
    shortDescription:
      "Pew's 36,908-respondent map of American religion — who belongs to what, and what they believe.",
    sponsor: "Pew Research Center",
    fielder: "NORC at the University of Chicago",
    description:
      "Pew Research Center's third Religious Landscape Study, after 2007 and 2014. " +
      "36,908 U.S. adults answered " +
      "between July 2023 and March 2024 — enough for reliable state-level estimates, and enough " +
      "to say something about small groups that national polls of 1,000 people can only round " +
      "off. Latter-day Saints are one of those groups. The study's other contribution is its " +
      "taxonomy: a branching set of questions about religious identity, back-coded into 298 " +
      "denominations, which collapse into families of denominations, which collapse into 16 " +
      "religious traditions.",
    citation:
      "Pew Research Center. 2025. “2023-24 Religious Landscape Study (RLS) Dataset.” " +
      "doi: 10.58094/3kwb-bf52.",
    doi: "10.58094/3kwb-bf52",
    sourceUrl: "https://www.pewresearch.org/religious-landscape-study/",
    howWeUseIt:
      "The optional demographic questions in this site's quizzes are Pew's, taken from this " +
      "study's questionnaire and worded the same way — religion, birth cohort, gender, race, " +
      "Hispanic origin, education, marital status, and state. The religion list is Pew's own " +
      "taxonomy in full, down to the denominational family, including the Protestant, " +
      "non-Christian, and religiously unaffiliated subcategories. Answers given here can " +
      "therefore be read against a national sample without a recoding step in between.",
    methodology: [
      "36,908 U.S. adults, interviewed July 17, 2023 – March 4, 2024, in English and Spanish.",
      "A geographically stratified address-based sample; 205,100 addresses were invited.",
      "Respondents chose their mode: 25,250 answered online, 10,733 by mail, 925 by phone.",
      "The AAPOR RR3 response rate was 20%.",
      "Weights are raked to American Community Survey and CPS benchmarks.",
      "National margin of sampling error: ±0.8 percentage points at 95% confidence, after " +
        "accounting for the sample design and the loss of precision from weighting. Subgroups " +
        "are wider — ±1.7 points for historically Black Protestants, ±8.7 for Hindus.",
      "The public-use file withholds sensitive variables, geography among them; a restricted-use " +
        "file is to reach ICPSR under a data use agreement.",
      "Not directly comparable with the 2007 and 2014 waves without care: those were " +
        "random-digit-dial telephone surveys, this one is mostly online and paper. Pew ran a " +
        "1,519-respondent telephone bridge study to measure the mode difference — read " +
        "Appendix A of the accompanying report before comparing across waves.",
    ],
    methodologySourceUrl: "https://www.pewresearch.org/religious-landscape-study/",
    graphics: [],
  },
  {
    slug: "cces-2016",
    name: "CCES 2016",
    shortDescription:
      "A 64,600-respondent national election survey, with 870 Latter-day Saints in it.",
    sponsor: "Cooperative Election Studies (multi-university consortium)",
    fielder: "YouGov",
    description:
      "The Cooperative Congressional Election Study is a large annual national survey on " +
      "politics and public opinion, run online by YouGov. This entry is a 33-variable teaching " +
      "extract of the 2016 wave — issue positions on guns, abortion, immigration, and gay " +
      "marriage, plus party ID, ideology, vote choice, and religion — redistributed by Ryan " +
      "Burge (github.com/ryanburge). It carries 870 Latter-day Saint respondents, enough to " +
      "compare LDS answers against every other religious tradition and the religiously " +
      "unaffiliated side by side, not just against the sample as a whole.",
    sourceUrl: "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/GDF6Z0",
    graphics: [],
  },
  {
    slug: "ces-stacked-2006-2018",
    name: "CES Stacked, 2006–2018",
    shortDescription:
      "Party ID, race, and gender by religious tradition, across seven federal election cycles.",
    sponsor: "Cooperative Election Studies (multi-university consortium)",
    fielder: "YouGov",
    description:
      "Ryan Burge's own tabulation stacking eight waves of the CCES/CES common content " +
      "(2006–2018) down to five variables — religious tradition, 7-point party ID, race, " +
      "gender, and year — for tracking a group's partisanship over time rather than in a " +
      "single snapshot. It carries 5,955 Latter-day Saint respondents across the eight waves, " +
      "enough to break that group out by year and by gender and still have a usable sample in " +
      "most cells.",
    sourceUrl: "https://github.com/ryanburge/pets",
    graphics: [],
  },
  {
    slug: "voter-survey-panel",
    name: "VOTER Survey Panel",
    shortDescription:
      "A longitudinal panel of the same 8,000 voters, re-interviewed from 2011 through 2020.",
    sponsor: "Democracy Fund Voter Study Group",
    fielder: "YouGov",
    description:
      "The VOTER (Views of the Electorate Research) Survey re-interviews the same panel of " +
      "voters across multiple waves — 2011, 2012, 2016, 2017, 2018, 2019, and 2020 — which " +
      "makes it possible to track how the same people's views moved, not just how the " +
      "population's views compare year to year. This 867-variable file, redistributed by Ryan " +
      "Burge (github.com/ryanburge), includes feeling thermometers toward other religious and " +
      "political groups, issue-importance ratings, and a religion battery with 141–149 " +
      "Latter-day Saint respondents at baseline (84 in the 2017 wave specifically).",
    sourceUrl: "https://www.voterstudygroup.org/",
    graphics: [],
  },
];

export function getDataset(slug: string): Dataset | undefined {
  return DATASETS.find((d) => d.slug === slug);
}

/**
 * One graphic per quiz item, generated from the quiz's own data so the
 * gallery can never drift from what the quiz itself shows. Images are
 * rendered by scripts/state-of-theology-graphics/render_chart.py
 * (`--all`) to `/public/data-explorer/state-of-theology/<item_id>.png` —
 * rerun that after regenerating data.json to keep these in sync.
 */
function stateOfTheologyGraphics(): Graphic[] {
  return QUIZ_DATA.items.map((item) => {
    const rows = groupBreakdownRows(item).map((row) => {
      const pcts = fiveColumnPct(item, row.group)!;
      const agree = pcts[3] + pcts[4]; // somewhat_agree + strongly_agree
      return { group: row.group, agree };
    });
    return {
      title: `"${item.statement}"`,
      description: `Agreement by religious tradition, ${item.year} wave.`,
      imageSrc: `/data-explorer/state-of-theology/${item.id}.png`,
      width: 1080,
      height: 1350,
      alt:
        `Bar chart: share who agree "${item.statement}," by religious tradition. ` +
        rows.map((r) => `${r.group} ${r.agree}%`).join(", ") +
        ".",
      credit: "@ithinkisam",
    };
  });
}
