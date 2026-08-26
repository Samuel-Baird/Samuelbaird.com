/**
 * The Data Explorer: a home for public survey/statistical datasets and
 * whatever's been done with them here — quizzes, graphics, write-ups.
 * Adding a dataset or an analysis is a data change to this file, not a new
 * route or component, the same reasoning as the quiz's own tradition
 * lookup table (see scripts/evangelical-quiz/README.md).
 */

import { fiveColumnPct, groupBreakdownRows, QUIZ_DATA } from "@/lib/evangelical-quiz";
import switchingRatesData from "../../docs/datasets/pew-rls-2023-24/switching-rates.json";
import switchingGeneralizedData from "../../docs/datasets/pew-rls-2023-24/switching-generalized.json";
import birthDecadeData from "../../docs/datasets/pew-rls-2023-24/birth-decade-distribution.json";
import childhoodFormationData from "../../docs/datasets/pew-rls-2023-24/childhood-formation.json";
import familyHouseholdData from "../../docs/datasets/pew-rls-2023-24/family-household.json";
import practiceData from "../../docs/datasets/pew-rls-2023-24/practice.json";
import pidOverTimeData from "../../docs/datasets/ryan-burge/pid-over-time.json";

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

/** Sort/label order for the switching-rates graphic's alt text. */
const SWITCHING_GROUP_ORDER = [
  "Catholic",
  "Jehovah's Witness",
  "Latter-day Saint",
  "Protestant",
  "Other Christian",
  "Orthodox Christian",
];

/** Group order shared by the three "switching, generalized" + birth-decade
 * graphics below, and by their render scripts
 * (scripts/pew-rls/render_switching_generalized_chart.py,
 * scripts/pew-rls/render_birth_decade_chart.py) - keep all three in sync. */
const GENERALIZED_GROUP_ORDER = [
  "Latter-day Saint",
  "Catholic",
  "Protestant",
  "Orthodox Christian",
  "Jehovah's Witness",
  "Other Christian",
  "Christian average",
];

/** Group order for children_with_kids_at_home, matching CHILDREN_ORDER in
 * scripts/pew-rls/render_family_household_charts.py. */
const CHILDREN_GROUP_ORDER = [
  "Latter-day Saint", "Catholic", "Protestant", "Orthodox Christian",
  "Jehovah's Witness", "Other Christian", "Christian average",
];

/** Group order for pray_or_read_scripture_with_kids, matching
 * KIDACT_ORDER in scripts/pew-rls/render_family_household_charts.py - a
 * wider population than every other chart on this page, per the backlog
 * item's own note. */
const KIDACT_GROUP_ORDER = [
  "Latter-day Saint", "Catholic", "Protestant", "Orthodox Christian",
  "Jehovah's Witness", "Other Christian", "Other religions",
  "Religiously affiliated average",
];

/** Group order for the six "Practice" items whose population is every
 * religiously affiliated tradition individually (not lumped), matching
 * ALL_RELIGIOUS_ORDER in scripts/pew-rls/render_practice_charts.py. */
const ALL_RELIGIOUS_GROUP_ORDER = [
  "Latter-day Saint", "Catholic", "Protestant", "Jehovah's Witness",
  "Muslim", "Hindu", "Orthodox Christian", "Other Christian", "Buddhist",
  "Jewish", "Other world religions", "Other faiths", "All religious average",
];

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
    graphics: [
      pewSwitchingRatesGraphic(),
      pewSwitchingCurrentCompositionGraphic(),
      pewSwitchingRaisedCohortGraphic(),
      pewBirthDecadeGraphic(),
      pewChildhoodAttendanceGraphic(),
      pewChildhoodImportanceGraphic(),
      pewChildhoodEducationGraphic(),
      pewChildrenAtHomeGraphic(),
      pewKidactPrayerGraphic(),
      pewRelimpGraphic(),
      pewBibimpGraphic(),
      pewAttendDistributionGraphic(),
      pewAttendMonthlyPlusGraphic(),
      pewMembGraphic(),
      pewPrayDistributionGraphic(),
      pewPracbGraphic(),
      pewPraccGraphic(),
      pewGraceGraphic(),
      pewPracaGraphic(),
    ],
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
    graphics: [cesPidOverTimeGraphic()],
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
 * Net-change-since-childhood graphic for the Pew RLS entry. Built from
 * switching-rates.json (produced by scripts/pew-rls/switching_rates.py and
 * rendered to PNG by scripts/pew-rls/render_switching_chart.py) rather than
 * hand-typed, so the alt text can't drift from the numbers the chart
 * itself shows - same reasoning as stateOfTheologyGraphics() below.
 */
function pewSwitchingRatesGraphic(): Graphic {
  const { switching, protestant_current_composition: protestant } = switchingRatesData;
  const fmt = (n: number) => `${n >= 0 ? "+" : ""}${n.toFixed(0)}%`;
  const netChangeAlt = SWITCHING_GROUP_ORDER.map((group) => {
    const g = switching[group as keyof typeof switching];
    return `${group} ${fmt(g.net_change_pct)} (raised ${g.raised_pct.toFixed(1)}%, ` +
      `now ${g.current_pct.toFixed(1)}%)`;
  }).join(", ");
  const protestantAlt = Object.entries(protestant)
    .map(([group, g]) => `${group} ${g.current_pct.toFixed(1)}%`)
    .join(", ");

  return {
    title: "Net change since childhood, by tradition",
    description:
      "Each tradition's share of U.S. adults today, compared with the share raised in it.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/switching-rates.png",
    width: 1080,
    height: 1350,
    alt:
      `Diverging bar chart: net change from the share of U.S. adults raised in each ` +
      `tradition to the share currently in it. ${netChangeAlt}. Faded bars (Other ` +
      `Christian, Orthodox Christian) have a 95% confidence interval that includes zero. ` +
      `Below it, current Protestant tradition composition: ${protestantAlt}.`,
  };
}

/**
 * "Of today's members, raised in it or converted in?" - one half of
 * GRAPHICS_TODO.md's "Switching, generalized" item. Built from
 * switching-generalized.json (scripts/pew-rls/switching_generalized.py),
 * rendered by scripts/pew-rls/render_switching_generalized_chart.py.
 */
function pewSwitchingCurrentCompositionGraphic(): Graphic {
  const { switching_generalized: switching } = switchingGeneralizedData;
  const alt = GENERALIZED_GROUP_ORDER.map((group) => {
    const g = switching[group as keyof typeof switching];
    return `${group} raised in it ${g.retained_in_pct.toFixed(0)}%, converted in ${g.converted_in_pct.toFixed(0)}%`;
  }).join(", ");

  return {
    title: "Of today's members: raised in it, or converted in?",
    description:
      "Each tradition's current membership, split by whether they were raised in it or " +
      "joined from elsewhere.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/switching-current-composition.png",
    width: 1080,
    height: 1350,
    alt: `100%-stacked bar chart, share of each tradition's current membership: ${alt}.`,
  };
}

/**
 * "Of those raised in it, stayed or left?" - the other half of the same
 * backlog item; see pewSwitchingCurrentCompositionGraphic above for why
 * this is a separate figure rather than one merged bar (different
 * denominators - current members there, the raised cohort here).
 */
function pewSwitchingRaisedCohortGraphic(): Graphic {
  const { switching_generalized: switching } = switchingGeneralizedData;
  const alt = GENERALIZED_GROUP_ORDER.map((group) => {
    const g = switching[group as keyof typeof switching];
    return `${group} stayed ${g.stayed_pct.toFixed(0)}%, left ${g.left_pct.toFixed(0)}%`;
  }).join(", ");

  return {
    title: "Of those raised in it: still in it, or left?",
    description: "People raised in each tradition, split by whether they're still in it today.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/switching-raised-cohort.png",
    width: 1080,
    height: 1350,
    alt: `100%-stacked bar chart, share of each tradition's raised-in-it cohort: ${alt}.`,
  };
}

/**
 * Birth-decade makeup by tradition. Built from birth-decade-distribution.json
 * (scripts/pew-rls/birth_decade_distribution.py), rendered by
 * scripts/pew-rls/render_birth_decade_chart.py.
 */
function pewBirthDecadeGraphic(): Graphic {
  const { distribution, decade_order: decadeOrder } = birthDecadeData;
  const alt = GENERALIZED_GROUP_ORDER.map((group) => {
    const g = distribution[group as keyof typeof distribution];
    const shares = decadeOrder
      .map((d) => `${d} ${g.shares_pct[d as keyof typeof g.shares_pct].toFixed(0)}%`)
      .join(", ");
    return `${group}: ${shares}`;
  }).join("; ");

  return {
    title: "Birth-decade makeup, by tradition",
    description:
      "Share of each tradition's current members born in each decade — the finest age " +
      "measure the public-use file offers.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/birth-decade-distribution.png",
    width: 1080,
    height: 1350,
    alt: `100%-stacked bar chart, birth-decade share of each tradition's current members. ${alt}.`,
  };
}

/**
 * Grew up attending church monthly or more, by tradition raised in. Built
 * from childhood-formation.json (scripts/pew-rls/childhood_formation.py),
 * rendered by scripts/pew-rls/render_childhood_formation_charts.py.
 */
function pewChildhoodAttendanceGraphic(): Graphic {
  const results = childhoodFormationData.chattend_monthly_plus;
  const alt = GENERALIZED_GROUP_ORDER.map((group) => {
    const g = results[group as keyof typeof results];
    return `${group} ${g.pct.toFixed(0)}%`;
  }).join(", ");

  return {
    title: "Grew up attending church monthly or more",
    description:
      "Share of each Christian tradition's raised-in-it population, by childhood " +
      "attendance frequency.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/childhood-attendance.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share raised in each tradition who attended church monthly+ as a child: ${alt}.`,
  };
}

/**
 * Religion was very important to their family growing up, by tradition
 * raised in. Same data source and render script as the attendance graphic
 * above.
 */
function pewChildhoodImportanceGraphic(): Graphic {
  const results = childhoodFormationData.chimprel_very_important;
  const alt = GENERALIZED_GROUP_ORDER.map((group) => {
    const g = results[group as keyof typeof results];
    return `${group} ${g.pct.toFixed(0)}%`;
  }).join(", ");

  return {
    title: "Religion was very important to their family growing up",
    description:
      "Share of each Christian tradition's raised-in-it population who say religion was " +
      "\"very important\" to their family.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/childhood-importance.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share raised in each tradition who say religion was very important to their family: ${alt}.`,
  };
}

/**
 * Religious education received growing up (4-category distribution), by
 * tradition raised in. Same data source and render script as the two
 * childhood-formation graphics above.
 */
function pewChildhoodEducationGraphic(): Graphic {
  const { chedu2_distribution: results, chedu2_order: order } = childhoodFormationData;
  const alt = GENERALIZED_GROUP_ORDER.map((group) => {
    const g = results[group as keyof typeof results];
    const shares = order
      .map((label) => `${label} ${g.shares_pct[label as keyof typeof g.shares_pct].toFixed(0)}%`)
      .join(", ");
    return `${group}: ${shares}`;
  }).join("; ");

  return {
    title: "Religious education received growing up",
    description:
      "Years of Sunday School, CCD, or similar religious education, by tradition raised in.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/childhood-education.png",
    width: 1080,
    height: 1350,
    alt: `100%-stacked bar chart, years of religious education received by tradition raised in. ${alt}.`,
  };
}

/**
 * Share with children under 18 at home, by current tradition. Built from
 * family-household.json (scripts/pew-rls/family_household.py), rendered by
 * scripts/pew-rls/render_family_household_charts.py.
 */
function pewChildrenAtHomeGraphic(): Graphic {
  const results = familyHouseholdData.children_with_kids_at_home;
  const alt = CHILDREN_GROUP_ORDER.map((group) => {
    const g = results[group as keyof typeof results];
    return `${group} ${g.pct.toFixed(0)}%`;
  }).join(", ");

  return {
    title: "Share with children under 18 at home",
    description:
      "Of each current tradition's members, share who are a parent or guardian of a child " +
      "under 18 living with them.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/family-children-at-home.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share of each current tradition's members with children under 18 at home: ${alt}.`,
  };
}

/**
 * Of parents, share who pray or read scripture with their kids, by current
 * tradition (+ "Other religions" and a religiously-affiliated average).
 * Same data source and render script as the graphic above.
 */
function pewKidactPrayerGraphic(): Graphic {
  const results = familyHouseholdData.pray_or_read_scripture_with_kids;
  const alt = KIDACT_GROUP_ORDER.map((group) => {
    const g = results[group as keyof typeof results];
    return `${group} ${g.pct.toFixed(0)}%`;
  }).join(", ");

  return {
    title: "Of parents, who pray or read scripture with their kids",
    description: "Share of each tradition's parents who pray or read scripture with their children.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/family-kidact-prayer.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share of each tradition's parents who pray or read scripture with their children: ${alt}.`,
  };
}

/** Formats a group-order list of {pct} results into "Group NN%, Group NN%,
 * ..." for a magnitude-bar graphic's alt text - shared by every "Practice"
 * single-percentage item below. */
function pctAlt(
  order: readonly string[],
  results: Record<string, { pct: number }>,
): string {
  return order.map((group) => `${group} ${results[group]!.pct.toFixed(0)}%`).join(", ");
}

/**
 * Religion is important in their life (very+somewhat, top-two-box), by
 * current tradition. Built from practice.json (scripts/pew-rls/practice.py),
 * rendered by scripts/pew-rls/render_practice_charts.py.
 */
function pewRelimpGraphic(): Graphic {
  const alt = pctAlt(KIDACT_GROUP_ORDER, practiceData.relimp_important);
  return {
    title: "Religion is important in their life",
    description: "Share who say religion is very or somewhat important in their life.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/practice-relimp.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who say religion is very or somewhat important in their life: ${alt}.`,
  };
}

/**
 * The Bible is important in their life (extremely+very), Christian only.
 * Same data source and render script as the graphic above.
 */
function pewBibimpGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, practiceData.bibimp_important);
  return {
    title: "The Bible is important in their life",
    description: "Share who say the Bible is extremely or very important in their life.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/practice-bibimp.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who say the Bible is extremely or very important in their life: ${alt}.`,
  };
}

/**
 * Attendance frequency, full 6-category distribution, every religiously
 * affiliated tradition individually. Same data source and render script
 * as the graphic above.
 */
function pewAttendDistributionGraphic(): Graphic {
  const { attend_distribution: results, attend_order: order } = practiceData;
  const alt = ALL_RELIGIOUS_GROUP_ORDER.map((group) => {
    const g = results[group as keyof typeof results];
    const shares = order
      .map((label) => `${label} ${g.shares_pct[label as keyof typeof g.shares_pct].toFixed(0)}%`)
      .join(", ");
    return `${group}: ${shares}`;
  }).join("; ");

  return {
    title: "Attendance frequency, full distribution",
    description: "How often each tradition's members attend religious services in person.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/practice-attend-distribution.png",
    width: 1080,
    height: 1350,
    alt: `100%-stacked bar chart, religious attendance frequency by tradition. ${alt}.`,
  };
}

/**
 * Attend in-person and/or online, monthly or more (a derived flag: monthly+
 * on either item). Same data source and render script as the graphic above.
 */
function pewAttendMonthlyPlusGraphic(): Graphic {
  const alt = pctAlt(ALL_RELIGIOUS_GROUP_ORDER, practiceData.attend_monthly_plus_either);
  return {
    title: "Attend in-person and/or online, monthly or more",
    description:
      "Share attending religious services monthly or more, either in person or online/on TV.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/practice-attend-monthly-plus.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share attending religious services monthly+ in person and/or online: ${alt}.`,
  };
}

/**
 * Member of a house of worship, every religiously affiliated tradition
 * individually. Same data source and render script as the graphic above.
 */
function pewMembGraphic(): Graphic {
  const alt = pctAlt(ALL_RELIGIOUS_GROUP_ORDER, practiceData.memb_member);
  return {
    title: "Member of a house of worship",
    description:
      "Share who are personally a member of a church, synagogue, mosque, temple, or other " +
      "house of worship.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/practice-memb.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who are a member of a house of worship, by tradition: ${alt}.`,
  };
}

/**
 * Prayer frequency, collapsed to 4 buckets (see practice.py's
 * design_decisions), every religiously affiliated tradition individually.
 * Same data source and render script as the graphic above.
 */
function pewPrayDistributionGraphic(): Graphic {
  const { pray_distribution: results, pray_order: order } = practiceData;
  const alt = ALL_RELIGIOUS_GROUP_ORDER.map((group) => {
    const g = results[group as keyof typeof results];
    const shares = order
      .map((label) => `${label} ${g.shares_pct[label as keyof typeof g.shares_pct].toFixed(0)}%`)
      .join(", ");
    return `${group}: ${shares}`;
  }).join("; ");

  return {
    title: "Prayer frequency",
    description: "How often each tradition's members pray, outside of attending religious services.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/practice-pray-distribution.png",
    width: 1080,
    height: 1350,
    alt: `100%-stacked bar chart, prayer frequency by tradition. ${alt}.`,
  };
}

/**
 * Read scripture outside of services, weekly+, every religiously affiliated
 * tradition individually. Same data source and render script as the
 * graphic above.
 */
function pewPracbGraphic(): Graphic {
  const alt = pctAlt(ALL_RELIGIOUS_GROUP_ORDER, practiceData.pracb_weekly_plus);
  return {
    title: "Read scripture outside of services, weekly+",
    description: "Share reading scripture at least once a week, outside of religious services.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/practice-pracb.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share reading scripture weekly+ outside of services, by tradition: ${alt}.`,
  };
}

/**
 * Read other holy texts or devotions, weekly+, Christian only. Same data
 * source and render script as the graphic above.
 */
function pewPraccGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, practiceData.pracc_weekly_plus);
  return {
    title: "Read other holy texts or devotions, weekly+",
    description:
      "Share reading other holy texts, devotions, or inspirational literature at least " +
      "once a week.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/practice-pracc.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share reading other holy texts/devotions weekly+, by Christian tradition: ${alt}.`,
  };
}

/**
 * Always say grace before meals (top box), Christian only. Same data
 * source and render script as the graphic above.
 */
function pewGraceGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, practiceData.grace_always);
  return {
    title: "Always say grace before meals",
    description: "Share who always pray or say grace before meals.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/practice-grace.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who always say grace before meals, by Christian tradition: ${alt}.`,
  };
}

/**
 * Prayer or scripture study groups, weekly+, Christian only. Same data
 * source and render script as the graphic above.
 */
function pewPracaGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, practiceData.praca_weekly_plus);
  return {
    title: "Prayer or scripture study groups, weekly+",
    description:
      "Share participating in prayer groups, scripture study, or religious education " +
      "programs at least once a week.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/practice-praca.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share in weekly+ prayer/scripture-study/religious-ed groups, by Christian tradition: ${alt}.`,
  };
}

/**
 * Party ID (pid7) over time, by tradition - the CES Stacked entry's own
 * graphic. Built from pid-over-time.json (scripts/ryan-burge/pid_over_time.py),
 * rendered by scripts/ryan-burge/render_pid_over_time_chart.py.
 */
function cesPidOverTimeGraphic(): Graphic {
  const { waves, series } = pidOverTimeData;
  const alt = Object.entries(series)
    .map(([group, s]) => {
      const points = waves
        .map((yr, i) => (s.values[i] == null ? null : `${yr} ${s.values[i]!.toFixed(2)}`))
        .filter((p): p is string => p != null)
        .join(", ");
      return `${group}: ${points}`;
    })
    .join("; ");

  return {
    title: "Party ID over time, by tradition",
    description:
      "Mean 7-point party ID (-3 = strong Democrat, +3 = strong Republican) across seven " +
      "federal election cycles.",
    imageSrc: "/data-explorer/ces-stacked-2006-2018/pid-over-time.png",
    width: 1080,
    height: 1350,
    credit: "via Ryan Burge",
    alt: `Line chart, mean 7-point party ID by tradition and survey wave. ${alt}.`,
  };
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
