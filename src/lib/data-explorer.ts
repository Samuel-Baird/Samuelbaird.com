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
import beliefsData from "../../docs/datasets/pew-rls-2023-24/beliefs.json";
import spiritualExperienceData from "../../docs/datasets/pew-rls-2023-24/spiritual-experience.json";
import publicLifeData from "../../docs/datasets/pew-rls-2023-24/public-life.json";
import cces2016Data from "../../docs/datasets/ryan-burge/cces2016-by-religion.json";
import pidByGenderData from "../../docs/datasets/ryan-burge/pid-by-gender.json";
import voterStrangerData from "../../docs/datasets/ryan-burge/voter-stranger.json";
import voterFtRacialData from "../../docs/datasets/ryan-burge/voter-ft-racial-religious.json";
import voterFtPoliticalData from "../../docs/datasets/ryan-burge/voter-ft-political-social.json";
import voterIssueImportanceData from "../../docs/datasets/ryan-burge/voter-issue-importance.json";
import voterIdeasBarsData from "../../docs/datasets/ryan-burge/voter-ideas-bars.json";
import voterIdeasLongitudinalData from "../../docs/datasets/ryan-burge/voter-ideas-longitudinal.json";
import voterIdeasSexismData from "../../docs/datasets/ryan-burge/voter-ideas-sexism.json";
import voterIdeasMuslimData from "../../docs/datasets/ryan-burge/voter-ideas-muslim-distrust.json";
import voterIdeasImmigrationData from "../../docs/datasets/ryan-burge/voter-ideas-immigration.json";
import voterIdeasTradeData from "../../docs/datasets/ryan-burge/voter-ideas-trade.json";
import voterIdeasPromisesData from "../../docs/datasets/ryan-burge/voter-ideas-promises.json";
import voterIdeasMediaData from "../../docs/datasets/ryan-burge/voter-ideas-media.json";
import voterIdeasOrgsData from "../../docs/datasets/ryan-burge/voter-ideas-orgs.json";
import voterIdeasVolunteeringData from "../../docs/datasets/ryan-burge/voter-ideas-volunteering.json";
import voterIdeasPrideData from "../../docs/datasets/ryan-burge/voter-ideas-pride.json";
import pidOverTimeData from "../../docs/datasets/ryan-burge/pid-over-time.json";
import mormonOrdinationData from "../../docs/datasets/pew-mormon-survey-2011/ordination-by-activity.json";
import mormonismChristianData from "../../docs/datasets/pew-mormon-survey-2011/mormonism-christian.json";
import essentialToBeingMormonData from "../../docs/datasets/pew-mormon-survey-2011/essential-to-being-mormon.json";
import tithingByActivityData from "../../docs/datasets/pew-mormon-survey-2011/tithing-by-activity.json";
import mormonFoundingKnowledgeData from "../../docs/datasets/pew-religious-knowledge-2010/mormon-founding-knowledge.json";
import josephSmithKnowledgeData from "../../docs/datasets/pew-religious-knowledge-2010/joseph-smith-knowledge.json";
import bookOfMormonKnowledgeData from "../../docs/datasets/pew-religious-knowledge-2010/book-of-mormon-knowledge.json";
import evolutionBeliefData from "../../docs/datasets/pew-rls-2007/evolution-belief.json";
import certaintyOfGodData from "../../docs/datasets/pew-rls-2007/certainty-of-god.json";
import dailyPrayerData from "../../docs/datasets/pew-rls-2007/daily-prayer.json";
import samesexMarriage2014Data from "../../docs/datasets/pew-rls-2014/samesex-marriage.json";
import weeklyAttendance2014Data from "../../docs/datasets/pew-rls-2014/weekly-attendance.json";
import certaintyOfGod2014Data from "../../docs/datasets/pew-rls-2014/certainty-of-god.json";
import marriageSharedBeliefsData from "../../docs/datasets/pew-rls-2014-recontact/marriage-shared-beliefs.json";
import raisedInterfaithData from "../../docs/datasets/pew-rls-2014-recontact/raised-interfaith.json";
import spouseReligionMatteredData from "../../docs/datasets/pew-rls-2014-recontact/spouse-religion-mattered.json";
import mormonsAsChristianData from "../../docs/datasets/pew-latin-america-2014/mormons-as-christian.json";
import reasonsJoinedLdsData from "../../docs/datasets/pew-faith-in-flux-2008/reasons-joined-lds.json";
import onlineWorshipCovidData from "../../docs/datasets/pew-atp-w70-2020/online-worship-covid.json";
import usMembershipGrowthData from "../../docs/datasets/us-membership-growth-2000-2025/membership-by-year.json";
import usMembershipProjectionData from "../../docs/datasets/us-membership-growth-2000-2025/membership-projection-2050.json";
import worldwideMembershipHistoryData from "../../docs/datasets/worldwide-membership-history/membership-by-year.json";

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

/** Group order for the "Beliefs" section, matching GROUP_ORDER in
 * scripts/pew-rls/render_beliefs_charts.py - all religious traditions
 * individually + an average + the unaffiliated as their own row, per that
 * section's own open-population resolution (see beliefs.py's docstring). */
const BELIEFS_GROUP_ORDER = [
  "Latter-day Saint", "Catholic", "Protestant", "Jehovah's Witness",
  "Muslim", "Hindu", "Orthodox Christian", "Other Christian", "Buddhist",
  "Jewish", "Other world religions", "Other faiths",
  "All religious average", "Religiously unaffiliated",
];

/** Group order for the CCES 2016 "by religion" graphics, matching
 * GROUP_ORDER in scripts/ryan-burge/render_cces2016_by_religion_charts.py -
 * all 12 religpew categories individually, per that backlog item's own
 * "not just LDS vs. everyone else" population note. */
const CCES2016_GROUP_ORDER = [
  "Mormon", "Protestant", "Catholic", "Orthodox", "Jewish", "Muslim",
  "Buddhist", "Hindu", "Atheist", "Agnostic", "Nothing in particular",
  "Something else",
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
  /**
   * Optional section label for the Data Explorer index (e.g. "Mixed
   * Datasets" for a compiled cross-source timeline, as opposed to one
   * survey's own microdata). Datasets sharing a category must sit
   * consecutively in this array - the index page groups by *runs* of the
   * same category, not by a global sort, so a category split across two
   * places in this list would render as two separate sections.
   */
  category?: string;
};

export const DATASETS: Dataset[] = [
  {
    slug: "us-membership-growth-2000-2025",
    name: "U.S. Church Membership Growth, 2000-2025",
    shortDescription:
      "A compiled year-by-year timeline of reported U.S. Church membership — not one survey, several sources stitched together.",
    sponsor: "The Church of Jesus Christ of Latter-day Saints",
    fielder: "Compiled by this site from multiple public sources",
    description:
      "This site's first \"mixed data\" entry: no single source publishes a complete " +
      "year-by-year U.S.-only membership series, so this stitches one together from the " +
      "2000 and 2010 U.S. Religion Census, the Deseret News Church Almanac, and the " +
      "Church's own newsroom country page. Five years (2001, 2003, 2005, 2007, 2011) have " +
      "no findable U.S.-only total in any source checked and are linearly interpolated " +
      "between their nearest real neighbors — shown as a dashed line, never presented as " +
      "if reported. See docs/datasets/us-membership-growth-2000-2025/README.md for every " +
      "year's exact citation.",
    citation:
      "Compiled from the U.S. Religion Census (2000, 2010), the Deseret News Church " +
      "Almanac (2002-2009), and the Church's newsroom country page (2012-2025).",
    sourceUrl:
      "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/united-states",
    category: "Mixed Datasets",
    graphics: [usMembershipGrowthGraphic(), usMembershipProjectionGraphic()],
  },
  {
    slug: "worldwide-membership-history",
    name: "Worldwide Church Membership History, 1830-2025",
    shortDescription:
      "The full worldwide membership count, year by year, from six founding members to nearly 18 million.",
    sponsor: "The Church of Jesus Christ of Latter-day Saints",
    fielder: "Compiled by this site from multiple public sources",
    description:
      "Unlike the U.S.-only timeline above, this one has no gaps: worldwide membership is " +
      "documented for every single year since the Church's 1830 founding in one coherent " +
      "source lineage — the 2013 Church Almanac for 1830-2011, and the Church's own annual " +
      "statistical reports for 2012-2025. 2025's figure (17,887,212) was independently " +
      "cross-checked against the Church's current newsroom statistics page and matches " +
      "exactly. See docs/datasets/worldwide-membership-history/README.md for the full source.",
    citation:
      "Wikipedia, \"Membership history of the Church of Jesus Christ of Latter-day " +
      "Saints,\" sourced to the 2013 Church Almanac (1830-2011) and the Church's annual " +
      "statistical reports (2012-2025).",
    sourceUrl:
      "https://en.wikipedia.org/wiki/Membership_history_of_the_Church_of_Jesus_Christ_of_Latter-day_Saints",
    category: "Mixed Datasets",
    graphics: [worldwideMembershipHistoryGraphic(), worldwideMembershipDirectionGraphic()],
  },
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
      pewSoulBeliefGraphic(),
      pewHeavenBeliefGraphic(),
      pewHellBeliefGraphic(),
      pewHeavenVsHellGraphic(),
      pewEvolutionGuidedGraphic(),
      pewSpiritualMeaningGraphic(),
      pewSpiritualPeaceGraphic(),
      pewSpiritualPresenceGraphic(),
      pewOpenidenGraphic(),
      pewChngAGraphic(),
      pewDivracpopGraphic(),
      pewDivrelpopGraphic(),
      pewHumntrGraphic(),
      pewRelimpactGraphic(),
      pewRelinstFGraphic(),
      pewRelinstGGraphic(),
      pewRelinstEGraphic(),
      pewScimpactGraphic(),
      pewVol12Graphic(),
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
    graphics: [
      cces2016PathwayGraphic(),
      cces2016BorderGraphic(),
      cces2016DreamerGraphic(),
      cces2016DeportGraphic(),
      cces2016ProchoiceGraphic(),
      cces2016ProlifeGraphic(),
      cces2016GaymGraphic(),
      cces2016AttendGraphic(),
    ],
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
    graphics: [cesPidOverTimeGraphic(), cesPidByGenderGraphic()],
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
    graphics: [
      voterStrangerGraphic(),
      voterFtRacialGraphic(),
      voterFtPoliticalGraphic(),
      voterIssueImportanceGraphic(),
      voterRetentionGraphic(),
      voterReligimpTrendGraphic(),
      voterPrayerTrendGraphic(),
      voterTrustGovtTrendGraphic(),
      voterVote2012vs2016Graphic(),
      voterGaymarShiftGraphic(),
      voterWishedVotedGraphic(),
      voterVoteRegretsGraphic(),
      voterSelfRelianceGraphic(),
      voterRaceSlaveGraphic(),
      voterReverseDiscriminationGraphic(),
      voterTrustPeopleGraphic(),
      voterRiggedElitesGraphic(),
      voterMilitaryGraphic(),
      voterSexismGraphic(),
      voterMuslimDistrustGraphic(),
      voterImmigrationIdeaGraphic(),
      voterTradeGraphic(),
      voterPromisesGraphic(),
      voterMediaGraphic(),
      voterOrgsGraphic(),
      voterVolunteeringGraphic(),
      voterPrideGraphic(),
    ],
  },
  {
    slug: "pew-mormon-survey-2011",
    name: "2011 National Survey of Mormons",
    shortDescription:
      "Pew's survey of Mormons themselves — belief, practice, and place in American life.",
    sponsor: "Pew Research Center",
    fielder: "Social Science Research Solutions (SSRS)",
    description:
      "Rather than surveying the general public about Mormons, this 2011 study surveyed " +
      "1,019 self-identified Mormon adults directly — what they believe, how they practice, " +
      "and how accepted they feel in American society. Interviews were conducted Oct. 25–Nov. " +
      "16, 2011 by telephone (landline and cell) in English and Spanish, oversampling counties " +
      "with the largest Mormon populations and recontacting self-identified Mormons from " +
      "earlier Pew and SSRS surveys. The resulting report, \"Mormons in America,\" was released " +
      "in January 2012.",
    citation:
      "Pew Research Center. 2012. \"2011 National Survey of Mormons.\"",
    sourceUrl:
      "https://www.pewresearch.org/religion/2012/01/12/mormons-in-america-executive-summary/",
    graphics: [
      mormonismChristianGraphic(),
      mormonOrdinationGraphic(),
      essentialToBeingMormonGraphic(),
      tithingByActivityGraphic(),
    ],
  },
  {
    slug: "pew-religious-knowledge-2010",
    name: "2010 U.S. Religious Knowledge Survey",
    shortDescription:
      "What Americans of every faith (and none) actually know about religion.",
    sponsor: "Pew Research Center",
    fielder: "Princeton Survey Research Associates International (PSRAI)",
    description:
      "A 32-question quiz on the Bible, world religions, and church-state law, fielded " +
      "May 19–June 6, 2010 among 3,412 U.S. adults by landline and cell phone. The survey " +
      "oversampled Jewish, Mormon, and atheist/agnostic respondents by recontacting people " +
      "previous surveys had identified as belonging to those groups, which makes it one of " +
      "the few Pew datasets from this era with a usable standalone Mormon subsample on a " +
      "knowledge (rather than belief/practice) battery.",
    citation: "Pew Research Center. 2010. \"U.S. Religious Knowledge Survey.\"",
    sourceUrl:
      "https://www.pewresearch.org/religion/2010/09/28/u-s-religious-knowledge-survey/",
    graphics: [
      mormonFoundingKnowledgeGraphic(),
      josephSmithKnowledgeGraphic(),
      bookOfMormonKnowledgeGraphic(),
    ],
  },
  {
    slug: "pew-rls-2007",
    name: "2007 U.S. Religious Landscape Survey",
    shortDescription:
      "The original Religious Landscape Survey — the baseline the 2014 and 2023-24 waves track against.",
    sponsor: "Pew Research Center",
    fielder: "Princeton Survey Research Associates International (PSRAI)",
    description:
      "The first Religious Landscape Survey: 35,556 adults in the continental U.S., " +
      "interviewed by telephone in summer 2007, plus a supplemental spring 2008 sample of " +
      "200 Alaska and 201 Hawaii adults (reported separately; the two files don't share a " +
      "combining weight). This is the survey that first measured the scale of religious " +
      "switching in America and established the RELTRAD religious-tradition classification " +
      "later waves (2014, 2023-24) still use.",
    sourceUrl: "https://www.pewresearch.org/religious-landscape-study/2007/",
    graphics: [evolutionBeliefGraphic(), certaintyOfGodGraphic(), dailyPrayerGraphic()],
  },
  {
    slug: "pew-rls-2014",
    name: "2014 Religious Landscape Study",
    shortDescription:
      "The middle wave of Pew's Religious Landscape Study, between the 2007 original and 2023-24.",
    sponsor: "Pew Research Center",
    fielder: "Princeton Survey Research Associates International (PSRAI)",
    description:
      "35,071 U.S. adults interviewed by telephone (60% cell, 40% landline) June 4–Sept. 30, " +
      "2014, in English and Spanish, with a minimum of 300 interviews in every state and the " +
      "District of Columbia. This wave is the source of the widely cited \"America's Changing " +
      "Religious Landscape\" report and, alongside the 2007 and 2023-24 waves, forms the " +
      "three-point trendline this site's Religious Landscape Study material draws on.",
    citation:
      "Pew Research Center. 2015. \"2014 Religious Landscape Study.\"",
    sourceUrl: "https://www.pewresearch.org/religious-landscape-study/2014/",
    graphics: [
      samesexMarriage2014Graphic(),
      weeklyAttendance2014Graphic(),
      certaintyOfGod2014Graphic(),
    ],
  },
  {
    slug: "pew-rls-2014-recontact",
    name: "2014 Religious Landscape Study — Recontact Survey",
    shortDescription:
      "A 2015 follow-up to 5,000 RLS 2014 respondents, focused on interfaith upbringing and marriage.",
    sponsor: "Pew Research Center",
    fielder: "Princeton Survey Research Associates International (PSRAI)",
    description:
      "Between March 17 and May 6, 2015, Pew recontacted 5,000 respondents from the main " +
      "2014 Religious Landscape Study, sorted into 15 strata by religious and demographic " +
      "characteristics (oversampling groups like the religiously intermarried) and reweighted " +
      "afterward to restore proper proportions. It shares respondent IDs and key variables " +
      "(RELTRAD, CHRELTRAD, region) with the main 2014 file, so the two can be merged. It " +
      "underlies the report \"One-in-Five U.S. Adults Were Raised in Interfaith Homes.\"",
    sourceUrl:
      "https://www.pewresearch.org/religion/2016/10/26/one-in-five-u-s-adults-were-raised-in-interfaith-homes/",
    graphics: [
      marriageSharedBeliefsGraphic(),
      raisedInterfaithGraphic(),
      spouseReligionMatteredGraphic(),
    ],
  },
  {
    slug: "pew-latin-america-2014",
    name: "Religion in Latin America",
    shortDescription:
      "Pew's face-to-face survey of religious belief and practice across 19 Latin American countries and territories.",
    sponsor: "Pew Research Center (Pew-Templeton Global Religious Futures project)",
    fielder: "Princeton Survey Research Associates International (PSRAI) and Ipsos Public Affairs",
    description:
      "Between October 2013 and February 2014, Pew conducted over 30,000 face-to-face " +
      "interviews with non-institutionalized adults across 18 Latin American and Caribbean " +
      "countries plus Puerto Rico, covering religious affiliation, belief, practice, and " +
      "social and political views. Latter-day Saints are a small share of most national " +
      "samples here, but the dataset is large enough to compare the region's Catholic-to-" +
      "Protestant shift against how much smaller traditions like LDS appear by comparison.",
    citation:
      "Pew Research Center. 2014. \"Religion in Latin America: Widespread Change in a " +
      "Historically Catholic Region.\"",
    sourceUrl:
      "https://www.pewresearch.org/religion/2014/11/13/religion-in-latin-america/",
    graphics: [mormonsAsChristianGraphic()],
  },
  {
    slug: "pew-faith-in-flux-2008",
    name: "Faith in Flux (2008 Conversion Recontact Survey)",
    shortDescription:
      "Follow-up interviews with 2007 Religious Landscape Survey respondents, focused on why people change religion.",
    sponsor: "Pew Research Center",
    fielder: "Princeton Survey Research Associates International (PSRAI)",
    description:
      "A follow-up to the 2007 U.S. Religious Landscape Survey, which found that 28% of " +
      "American adults had changed religious tradition since childhood (44% including moves " +
      "within a tradition). This 2008 recontact survey re-interviewed 2,867 of those " +
      "respondents by phone between Oct. 3 and Nov. 7, 2008, asking specifically why they " +
      "left, why they joined, and how they feel about the change — the reasons behind " +
      "religious switching, not just its incidence.",
    citation:
      "Pew Research Center. 2009. \"Faith in Flux: Changes in Religious Affiliation in the " +
      "U.S.\"",
    sourceUrl:
      "https://www.pewresearch.org/religion/2009/04/27/faith-in-flux/",
    graphics: [reasonsJoinedLdsGraphic()],
  },
  {
    slug: "pew-atp-w70-2020",
    name: "American Trends Panel, Wave 70 (July 2020)",
    shortDescription:
      "A general Pew American Trends Panel wave, fielded July 2020, carrying a religious-tradition variable.",
    sponsor: "Pew Research Center",
    fielder: "Pew Research Center (American Trends Panel)",
    description:
      "Wave 70 of Pew's American Trends Panel: 10,211 U.S. adults surveyed online (a small " +
      "non-internet subsample by mail) July 13–19, 2020, in English and Spanish. Like other " +
      "ATP waves, it carries a F_RELTRAD frame variable classifying each respondent's " +
      "religious tradition (Latter-day Saints coded 20000), which is what makes an otherwise " +
      "general-topic wave usable for breaking its questions out by religion.",
    sourceUrl: "https://www.pewresearch.org/our-methods/u-s-surveys/american-trends-panel/",
    graphics: [onlineWorshipCovidGraphic()],
  },
];

// --- Flagship graphics for the eight raw-Pew-dataset registrations above.
// Each dataset gets exactly one chart (found via scripts/<slug>/*.py, an
// analysis script that reads the raw .sav microdata and writes a JSON
// aggregate to docs/datasets/<slug>/, rendered by
// scripts/<slug>/render_*.py using the shared shape in
// scripts/flagship-charts/common.py) rather than the many-chart buildout
// pew-rls-2023-24 or the ryan-burge sources have - see each dataset's own
// docs/datasets/<slug>/README.md for the regeneration commands.

function worldwideMembershipHistoryGraphic(): Graphic {
  const { year_order: years, series } = worldwideMembershipHistoryData;
  const milestones = [years[0], 1900, 1947, 2000, years[years.length - 1]];
  const alt = milestones
    .map((y) => `${y}: ${series[String(y) as keyof typeof series].members.toLocaleString()}`)
    .join(", ");
  return {
    title: "Worldwide Church membership, 1830-2025",
    description: "From six founding members to nearly 18 million, year by year, with no gaps.",
    imageSrc: "/data-explorer/worldwide-membership-history/membership-by-year.png",
    width: 1080, height: 1350,
    alt: `Line chart: worldwide Church membership by year, 1830 to 2025, complete with no gaps. Selected milestones - ${alt}.`,
  };
}

function worldwideMembershipDirectionGraphic(): Graphic {
  const { year_order: years, series } = worldwideMembershipHistoryData;
  const decreaseYears = years.filter((y, i) => {
    if (i === 0) return false;
    const prev = years[i - 1];
    return series[String(y) as keyof typeof series].members < series[String(prev) as keyof typeof series].members;
  });
  const decreaseAlt = decreaseYears
    .map((y) => `${y}: ${series[String(y) as keyof typeof series].members.toLocaleString()}`)
    .join(", ");
  const milestoneYears = years.filter((y, i) => i === 0 || i === years.length - 1 || (y - years[0]) % 25 === 0);
  const milestoneAlt = milestoneYears
    .map((y) => `${y}: ${series[String(y) as keyof typeof series].members.toLocaleString()}`)
    .join(", ");
  return {
    title: "Worldwide Church membership, 1830-2025",
    description: "The same series, colored by whether membership grew or shrank from the year before, with the total every 25 years.",
    imageSrc: "/data-explorer/worldwide-membership-history/membership-by-direction.png",
    width: 1080, height: 1350,
    alt: `Line chart: worldwide Church membership, 1830 to 2025, colored blue for growth and red for decrease from the prior year, labeled every 25 years - ${milestoneAlt}. Years with a decrease: ${decreaseAlt}. Every other year grew.`,
  };
}

function usMembershipProjectionGraphic(): Graphic {
  const { range_year_order: years, range_series, trend_fit_years: fit, anchor_year } =
    usMembershipProjectionData;
  const milestones = years.filter((y) => y === anchor_year || y % 5 === 0);
  const alt = milestones
    .map((y) => {
      const r = range_series[String(y) as keyof typeof range_series];
      return y === anchor_year ? `${y}: ${r.high.toLocaleString()}` : `${y}: ${r.low.toLocaleString()}-${r.high.toLocaleString()}`;
    })
    .join(", ");
  return {
    title: "U.S. membership, projected to 2050",
    description: `Reported through ${anchor_year}, then a range between two scenarios built from the ${fit[0]}-${fit[1]} reported trend, rather than a single guess.`,
    imageSrc: "/data-explorer/us-membership-growth-2000-2025/membership-projection-2050.png",
    width: 1080, height: 1350,
    alt: `Line and range chart: U.S. Church membership, reported through ${anchor_year}, then a projected range through 2050 between a "trend continues" high estimate and a "deceleration continues" low estimate. ${alt}. Neither bound is a forecast.`,
  };
}

function usMembershipGrowthGraphic(): Graphic {
  const { year_order: years, series } = usMembershipGrowthData;
  const alt = years
    .map((y) => {
      const r = series[String(y) as keyof typeof series];
      return `${y}: ${r.members.toLocaleString()}${r.status === "interpolated" ? " (interpolated)" : r.status === "rounded" ? " (rounded)" : ""}`;
    })
    .join(", ");
  return {
    title: "U.S. Church membership, 2000-2025",
    description: "Reported U.S. membership year by year; interpolated years are marked and shown dashed.",
    imageSrc: "/data-explorer/us-membership-growth-2000-2025/membership-by-year.png",
    width: 1080, height: 1350,
    alt: `Line chart: U.S. Church membership by year, 2000 to 2025. ${alt}.`,
  };
}

function mormonismChristianGraphic(): Graphic {
  const { row_order: rows, segment_order: segs, results } = mormonismChristianData;
  const alt = rows
    .map((r) => {
      const v = results[r as keyof typeof results];
      return `${r}: ` + segs.map((s) => `${s} ${v[s as keyof typeof v]}%`).join(", ");
    })
    .join("; ");
  return {
    title: "Is Mormonism a Christian religion?",
    description: "Mormons themselves vs. the U.S. general public.",
    imageSrc: "/data-explorer/pew-mormon-survey-2011/mormonism-christian.png",
    width: 1080, height: 1350,
    alt: `Stacked bar chart, is Mormonism a Christian religion, Mormons vs. U.S. general public. ${alt}.`,
  };
}

function mormonOrdinationGraphic(): Graphic {
  const { activity_order: order, ordain_women_yes: results } = mormonOrdinationData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Should women be ordained to the priesthood?",
    description: "Share of Mormons who believe dedicated women members should be ordained, by activity level.",
    imageSrc: "/data-explorer/pew-mormon-survey-2011/ordination-by-activity.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of Mormons believing women should be ordained to the priesthood, by activity level in the Church. ${alt}.`,
  };
}

function essentialToBeingMormonGraphic(): Graphic {
  const { item_order: order, essential_pct: results } = essentialToBeingMormonData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "What's essential to being a good Mormon?",
    description: "Share of Mormons calling each belief or practice essential for being a good Mormon.",
    imageSrc: "/data-explorer/pew-mormon-survey-2011/essential-to-being-mormon.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of Mormons calling each belief or practice essential for being a good Mormon. ${alt}.`,
  };
}

function tithingByActivityGraphic(): Graphic {
  const { activity_order: order, pay_tithing_yes: results } = tithingByActivityData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Do Mormons pay a full tithe?",
    description: "Share of Mormons who pay tithing, at least 10% of income, by activity level.",
    imageSrc: "/data-explorer/pew-mormon-survey-2011/tithing-by-activity.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of Mormons paying a full tithe, by activity level in the Church. ${alt}.`,
  };
}

function mormonFoundingKnowledgeGraphic(): Graphic {
  const { group_order: order, correct_pct: results } = mormonFoundingKnowledgeData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Who knows when Mormonism was founded?",
    description: "Share correctly saying the Mormon religion was founded after 1800, by the respondent's own religion.",
    imageSrc: "/data-explorer/pew-religious-knowledge-2010/mormon-founding-knowledge.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share correctly identifying Mormonism as founded sometime after 1800, by respondent's own religion. ${alt}.`,
  };
}

function josephSmithKnowledgeGraphic(): Graphic {
  const { group_order: order, correct_pct: results } = josephSmithKnowledgeData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Who knows Joseph Smith was a Mormon?",
    description: "Share correctly identifying Joseph Smith's religion, by the respondent's own religion.",
    imageSrc: "/data-explorer/pew-religious-knowledge-2010/joseph-smith-knowledge.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share correctly identifying Joseph Smith as Mormon, by respondent's own religion. ${alt}.`,
  };
}

function bookOfMormonKnowledgeGraphic(): Graphic {
  const { group_order: order, correct_pct: results } = bookOfMormonKnowledgeData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Where does the Book of Mormon say Jesus appeared?",
    description: "Share correctly saying the Americas, by the respondent's own religion.",
    imageSrc: "/data-explorer/pew-religious-knowledge-2010/book-of-mormon-knowledge.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share correctly saying the Book of Mormon places Jesus's appearance in the Americas, by respondent's own religion. ${alt}.`,
  };
}

function evolutionBeliefGraphic(): Graphic {
  const { group_order: order, evolution_agree: results } = evolutionBeliefData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Is evolution the best explanation?",
    description: "Share who agree evolution is the best explanation for human life on Earth, by religious tradition (2007).",
    imageSrc: "/data-explorer/pew-rls-2007/evolution-belief.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share agreeing evolution is the best explanation for human life on Earth, by religious tradition, 2007. ${alt}.`,
  };
}

function certaintyOfGodGraphic(): Graphic {
  const { group_order: order, absolutely_certain: results } = certaintyOfGodData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "How certain are people that God exists?",
    description: "Share of believers absolutely certain God or a universal spirit exists, by religious tradition (2007).",
    imageSrc: "/data-explorer/pew-rls-2007/certainty-of-god.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of believers absolutely certain God or a universal spirit exists, by religious tradition, 2007. ${alt}.`,
  };
}

function dailyPrayerGraphic(): Graphic {
  const { group_order: order, pray_daily: results } = dailyPrayerData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Who prays daily?",
    description: "Share who pray at least once a day outside of religious services, by religious tradition (2007).",
    imageSrc: "/data-explorer/pew-rls-2007/daily-prayer.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share praying at least once a day outside of religious services, by religious tradition, 2007. ${alt}.`,
  };
}

function samesexMarriage2014Graphic(): Graphic {
  const { group_order: order, favor_samesex_marriage: results } = samesexMarriage2014Data;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Support for same-sex marriage, 2014",
    description: "Share who favor allowing gays and lesbians to marry legally, by religious tradition.",
    imageSrc: "/data-explorer/pew-rls-2014/samesex-marriage.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share favoring same-sex marriage, by religious tradition, 2014. ${alt}.`,
  };
}

function weeklyAttendance2014Graphic(): Graphic {
  const { group_order: order, attend_weekly: results } = weeklyAttendance2014Data;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Who attends religious services weekly?",
    description: "Share attending religious services once a week or more, by religious tradition, 2014.",
    imageSrc: "/data-explorer/pew-rls-2014/weekly-attendance.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share attending religious services weekly or more, by religious tradition, 2014. ${alt}.`,
  };
}

function certaintyOfGod2014Graphic(): Graphic {
  const { group_order: order, absolutely_certain: results } = certaintyOfGod2014Data;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "How certain are people that God exists?",
    description: "Share of believers absolutely certain God exists, by religious tradition, 2014.",
    imageSrc: "/data-explorer/pew-rls-2014/certainty-of-god.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of believers absolutely certain God exists, by religious tradition, 2014. ${alt}.`,
  };
}

function marriageSharedBeliefsGraphic(): Graphic {
  const { group_order: order, shared_beliefs_very_important: results } = marriageSharedBeliefsData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Sharing faith with a spouse",
    description: "Share who say shared religious beliefs are very important for a successful marriage, by tradition (2015).",
    imageSrc: "/data-explorer/pew-rls-2014-recontact/marriage-shared-beliefs.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share saying shared religious beliefs are very important for a successful marriage, by religious tradition. ${alt}.`,
  };
}

function raisedInterfaithGraphic(): Graphic {
  const { group_order: order, raised_interfaith: results } = raisedInterfaithData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Raised in more than one religion?",
    description: "Share who think of themselves as having been raised in more than one religion, by current tradition.",
    imageSrc: "/data-explorer/pew-rls-2014-recontact/raised-interfaith.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share raised in more than one religion, by current religious tradition. ${alt}.`,
  };
}

function spouseReligionMatteredGraphic(): Graphic {
  const { group_order: order, spouse_religion_very_important: results } = spouseReligionMatteredData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Did your spouse's religion matter?",
    description: "Share of the ever-married saying their spouse's religion was very important in deciding to marry them, by tradition.",
    imageSrc: "/data-explorer/pew-rls-2014-recontact/spouse-religion-mattered.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of the ever-married saying their spouse's religion was very important in deciding to marry them, by religious tradition. ${alt}.`,
  };
}

function mormonsAsChristianGraphic(): Graphic {
  const { group_order: order, consider_mormons_christian: results } = mormonsAsChristianData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Are Mormons seen as Christian?",
    description: "Share across Latin America who consider Mormons to be followers of the Christian faith, by their own religion.",
    imageSrc: "/data-explorer/pew-latin-america-2014/mormons-as-christian.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share considering Mormons to be followers of the Christian faith, by respondent's own religion, across Latin America. ${alt}.`,
  };
}

function reasonsJoinedLdsGraphic(): Graphic {
  const { reason_order: order, important_reason_pct: results, lds_converts_unweighted_n: n } = reasonsJoinedLdsData;
  const alt = order
    .map((r) => `${r} ${results[r as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Why converts say they joined the LDS Church",
    description: `Share of LDS converts (n=${n}) calling each factor an important reason they became Mormon.`,
    imageSrc: "/data-explorer/pew-faith-in-flux-2008/reasons-joined-lds.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of LDS converts calling each factor an important reason for joining. ${alt}.`,
  };
}

function onlineWorshipCovidGraphic(): Graphic {
  const { group_order: order, watched_online_worship: results } = onlineWorshipCovidData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Worship online during COVID lockdowns",
    description: "Share who watched religious services online or on TV in the past month, by religious tradition, July 2020.",
    imageSrc: "/data-explorer/pew-atp-w70-2020/online-worship-covid.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share watching religious services online or on TV in the past month, by religious tradition, July 2020. ${alt}.`,
  };
}

export function getDataset(slug: string): Dataset | undefined {
  return DATASETS.find((d) => d.slug === slug);
}

/** Kebab-cases a category label (e.g. "Mixed Datasets" -> "mixed-datasets")
 * for its /data-explorer/category/<slug> route. */
export function categorySlug(category: string): string {
  return category
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function getDatasetsByCategory(slug: string): Dataset[] {
  return DATASETS.filter((d) => d.category && categorySlug(d.category) === slug);
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
 * Belief in a soul or spirit, by current tradition (all religiously
 * affiliated traditions individually + the unaffiliated, per this
 * section's open-population resolution - see beliefs.py's docstring).
 * Built from beliefs.json (scripts/pew-rls/beliefs.py), rendered by
 * scripts/pew-rls/render_beliefs_charts.py.
 */
function pewSoulBeliefGraphic(): Graphic {
  const alt = pctAlt(BELIEFS_GROUP_ORDER, beliefsData.soul_belief);
  return {
    title: "Believe people have a soul or spirit",
    description:
      "Share who believe people have a soul or spirit in addition to their physical body.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/beliefs-soul.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who believe in a soul or spirit, by tradition: ${alt}.`,
  };
}

/**
 * Belief in heaven, by current tradition. Same data source and render
 * script as the graphic above.
 */
function pewHeavenBeliefGraphic(): Graphic {
  const alt = pctAlt(BELIEFS_GROUP_ORDER, beliefsData.heaven_belief);
  return {
    title: "Believe in heaven",
    description:
      "Share who believe there is a heaven where people who led good lives are eternally " +
      "rewarded.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/beliefs-heaven.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who believe in heaven, by tradition: ${alt}.`,
  };
}

/**
 * Belief in hell, by current tradition. Same data source and render
 * script as the graphic above.
 */
function pewHellBeliefGraphic(): Graphic {
  const alt = pctAlt(BELIEFS_GROUP_ORDER, beliefsData.hell_belief);
  return {
    title: "Believe in hell",
    description:
      "Share who believe there is a hell where people who led bad lives are eternally " +
      "punished.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/beliefs-hell.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who believe in hell, by tradition: ${alt}.`,
  };
}

/**
 * Heaven vs. hell belief, paired per tradition - the fifth Beliefs item,
 * built once both individual belief graphics above exist. Same data
 * source and render script as the graphics above.
 */
function pewHeavenVsHellGraphic(): Graphic {
  const alt = BELIEFS_GROUP_ORDER.map((group) => {
    const h = beliefsData.heaven_belief[group as keyof typeof beliefsData.heaven_belief];
    const l = beliefsData.hell_belief[group as keyof typeof beliefsData.hell_belief];
    return `${group} heaven ${h.pct.toFixed(0)}%, hell ${l.pct.toFixed(0)}%`;
  }).join(", ");

  return {
    title: "Belief in heaven vs. hell",
    description: "The same two questions, compared side by side per tradition.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/beliefs-heaven-vs-hell.png",
    width: 1080,
    height: 1350,
    alt: `Paired bar chart, belief in heaven vs. hell by tradition: ${alt}.`,
  };
}

/**
 * Evolution guided by God, by current tradition. Same data source and
 * render script as the graphics above.
 */
function pewEvolutionGuidedGraphic(): Graphic {
  const alt = pctAlt(BELIEFS_GROUP_ORDER, beliefsData.evolution_guided_by_god);
  return {
    title: "Evolution guided by God",
    description:
      "Share who say humans evolved over time due to processes guided or allowed by God.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/beliefs-evolution.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who say evolution was guided by God, by tradition: ${alt}.`,
  };
}

/**
 * Think about life's meaning and purpose, weekly+, Christian only. Built
 * from spiritual-experience.json (scripts/pew-rls/spiritual_experience.py),
 * rendered by scripts/pew-rls/render_spiritual_experience_charts.py.
 */
function pewSpiritualMeaningGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, spiritualExperienceData.meaning_purpose_weekly_plus);
  return {
    title: "Think about life's meaning and purpose, weekly+",
    description: "Share who think about the meaning and purpose of life at least once a week.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/spiritual-meaning.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who think about life's meaning/purpose weekly+, by Christian tradition: ${alt}.`,
  };
}

/**
 * Feel spiritual peace and well-being, weekly+, Christian only. Same data
 * source and render script as the graphic above.
 */
function pewSpiritualPeaceGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, spiritualExperienceData.spiritual_peace_weekly_plus);
  return {
    title: "Feel spiritual peace and well-being, weekly+",
    description:
      "Share who feel a deep sense of spiritual peace and well-being at least once a week.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/spiritual-peace.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who feel spiritual peace weekly+, by Christian tradition: ${alt}.`,
  };
}

/**
 * Feel a presence beyond this world, weekly+, Christian only. Same data
 * source and render script as the graphic above.
 */
function pewSpiritualPresenceGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, spiritualExperienceData.presence_beyond_weekly_plus);
  return {
    title: "Feel a presence beyond this world, weekly+",
    description:
      "Share who feel the presence of something from beyond this world at least once a week.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/spiritual-presence.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who feel a presence beyond this world weekly+, by Christian tradition: ${alt}.`,
  };
}

/**
 * America's openness to the world is essential, Christian only. Built from
 * public-life.json (scripts/pew-rls/public_life.py), rendered by
 * scripts/pew-rls/render_public_life_charts.py.
 */
function pewOpenidenGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, publicLifeData.openiden_openness_essential);
  return {
    title: "America's openness to the world is essential",
    description:
      "Share who say America's openness to people from all over the world is essential to " +
      "who we are as a nation.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/public-openiden.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who say America's openness to the world is essential, by Christian tradition: ${alt}.`,
  };
}

/**
 * Immigration is a change for the better, Christian only. Same data
 * source and render script as the graphic above.
 */
function pewChngAGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, publicLifeData.chng_a_immigration_better);
  return {
    title: "Immigration is a change for the better",
    description: "Share who say a growing population of immigrants is a change for the better.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/public-chng-a.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who say immigration is a change for the better, by Christian tradition: ${alt}.`,
  };
}

/**
 * Racial/ethnic diversity strengthens society, Christian only. Same data
 * source and render script as the graphic above.
 */
function pewDivracpopGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, publicLifeData.divracpop_strengthens);
  return {
    title: "Racial/ethnic diversity strengthens society",
    description:
      "Share who say people of many different races/ethnicities strengthens American society.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/public-divracpop.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who say racial/ethnic diversity strengthens society, by Christian tradition: ${alt}.`,
  };
}

/**
 * Religious diversity strengthens society, Christian only. Same data
 * source and render script as the graphic above.
 */
function pewDivrelpopGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, publicLifeData.divrelpop_strengthens);
  return {
    title: "Religious diversity strengthens society",
    description:
      "Share who say people of many different religions (and no religion) strengthens " +
      "American society.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/public-divrelpop.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who say religious diversity strengthens society, by Christian tradition: ${alt}.`,
  };
}

/**
 * God gave humans a duty to protect the Earth (top box, God-believers
 * only), Christian + other religions. Same data source and render script
 * as the graphic above.
 */
function pewHumntrGraphic(): Graphic {
  const alt = pctAlt(KIDACT_GROUP_ORDER, publicLifeData.humntr_b_completely);
  return {
    title: "God gave humans a duty to protect the Earth",
    description: "Of God-believers, share who say this completely describes their view.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/public-humntr.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share of God-believers who say humans have a duty to protect the Earth, by tradition: ${alt}.`,
  };
}

/**
 * Religion does more good than harm, the widest population in this
 * section (all religiously affiliated traditions + the unaffiliated).
 * Same data source and render script as the graphic above.
 */
function pewRelimpactGraphic(): Graphic {
  const alt = pctAlt(BELIEFS_GROUP_ORDER, publicLifeData.relimpact_more_good);
  return {
    title: "Religion does more good than harm",
    description:
      "Share who say religion's overall impact on American society is more good than harm.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/public-relimpact.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who say religion does more good than harm, by tradition: ${alt}.`,
  };
}

/**
 * Religious orgs bring people together, Christian only. Same data source
 * and render script as the graphic above.
 */
function pewRelinstFGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, publicLifeData.relinst_f_bring_together);
  return {
    title: "Religious orgs bring people together",
    description:
      "Share who agree churches and other religious organizations strengthen community bonds.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/public-relinst-f.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who agree religious orgs bring people together, by Christian tradition: ${alt}.`,
  };
}

/**
 * Religious orgs help the poor and needy, Christian only. Same data
 * source and render script as the graphic above.
 */
function pewRelinstGGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, publicLifeData.relinst_g_help_poor);
  return {
    title: "Religious orgs help the poor and needy",
    description:
      "Share who agree churches and other religious organizations play an important role " +
      "helping the poor.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/public-relinst-g.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who agree religious orgs help the poor and needy, by Christian tradition: ${alt}.`,
  };
}

/**
 * Religious orgs protect and strengthen morality, Christian only. Same
 * data source and render script as the graphic above.
 */
function pewRelinstEGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, publicLifeData.relinst_e_strengthen_morality);
  return {
    title: "Religious orgs protect and strengthen morality",
    description:
      "Share who agree churches and other religious organizations protect and strengthen " +
      "morality in society.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/public-relinst-e.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who agree religious orgs protect/strengthen morality, by Christian tradition: ${alt}.`,
  };
}

/**
 * Science does more harm than good, Christian only. Same data source and
 * render script as the graphic above.
 */
function pewScimpactGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, publicLifeData.scimpact_more_harm);
  return {
    title: "Science does more harm than good",
    description:
      "Share who say science's overall impact on American society is more harm than good.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/public-scimpact.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who say science does more harm than good, by Christian tradition: ${alt}.`,
  };
}

/**
 * Volunteered in the past 12 months, the widest population in this
 * section. Same data source and render script as the graphic above.
 */
function pewVol12Graphic(): Graphic {
  const alt = pctAlt(BELIEFS_GROUP_ORDER, publicLifeData.vol12_volunteered);
  return {
    title: "Volunteered in the past 12 months",
    description: "Share who spent any time volunteering in the past 12 months.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/public-vol12.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who volunteered in the past 12 months, by tradition: ${alt}.`,
  };
}

/** Formats a CCES2016_GROUP_ORDER-keyed {pct} result set into alt text,
 * shared by the seven single-percentage CCES 2016 graphics below. */
function cces2016PctAlt(results: Record<string, { pct: number | null }>): string {
  return CCES2016_GROUP_ORDER
    .map((group) => `${group} ${results[group]!.pct?.toFixed(0) ?? "n/a"}%`)
    .join(", ");
}

/**
 * Grant legal status (3+ years worked, no felonies) - a select-all
 * immigration item, by the CCES 2016 extract's full 12-category religion
 * variable. Built from cces2016-by-religion.json
 * (scripts/ryan-burge/cces2016_by_religion.py), rendered by
 * scripts/ryan-burge/render_cces2016_by_religion_charts.py.
 */
function cces2016PathwayGraphic(): Graphic {
  const alt = cces2016PctAlt(cces2016Data.pathway_selected);
  return {
    title: "Grant legal status: 3+ years worked, no felonies",
    description: "Share who selected this option in a multi-select immigration-policy battery.",
    imageSrc: "/data-explorer/cces-2016/pathway.png",
    width: 1080,
    height: 1350,
    credit: "via Ryan Burge",
    alt: `Bar chart, share selecting legal-status-for-workers in a multi-select battery, by religion: ${alt}.`,
  };
}

/**
 * Increase border patrols - same select-all battery, population, data
 * source, and render script as the graphic above.
 */
function cces2016BorderGraphic(): Graphic {
  const alt = cces2016PctAlt(cces2016Data.border_selected);
  return {
    title: "Increase border patrols",
    description: "Share who selected this option in a multi-select immigration-policy battery.",
    imageSrc: "/data-explorer/cces-2016/border.png",
    width: 1080,
    height: 1350,
    credit: "via Ryan Burge",
    alt: `Bar chart, share selecting increased border patrols in a multi-select battery, by religion: ${alt}.`,
  };
}

/**
 * Grant legal status to Dreamers - same select-all battery, population,
 * data source, and render script as the graphic above.
 */
function cces2016DreamerGraphic(): Graphic {
  const alt = cces2016PctAlt(cces2016Data.dreamer_selected);
  return {
    title: "Grant legal status to Dreamers",
    description: "Share who selected this option in a multi-select immigration-policy battery.",
    imageSrc: "/data-explorer/cces-2016/dreamer.png",
    width: 1080,
    height: 1350,
    credit: "via Ryan Burge",
    alt: `Bar chart, share selecting legal status for Dreamers in a multi-select battery, by religion: ${alt}.`,
  };
}

/**
 * Identify and deport illegal immigrants - same select-all battery,
 * population, data source, and render script as the graphic above.
 */
function cces2016DeportGraphic(): Graphic {
  const alt = cces2016PctAlt(cces2016Data.deport_selected);
  return {
    title: "Identify and deport illegal immigrants",
    description: "Share who selected this option in a multi-select immigration-policy battery.",
    imageSrc: "/data-explorer/cces-2016/deport.png",
    width: 1080,
    height: 1350,
    credit: "via Ryan Burge",
    alt: `Bar chart, share selecting identify-and-deport in a multi-select battery, by religion: ${alt}.`,
  };
}

/**
 * Always allow abortion as a matter of choice (support), by the CCES
 * 2016 extract's full religion variable. Same data source and render
 * script as the graphics above.
 */
function cces2016ProchoiceGraphic(): Graphic {
  const alt = cces2016PctAlt(cces2016Data.prochoice_support);
  return {
    title: "Always allow abortion as a matter of choice",
    description:
      "Share who support always allowing a woman to obtain an abortion as a matter of choice.",
    imageSrc: "/data-explorer/cces-2016/prochoice.png",
    width: 1080,
    height: 1350,
    credit: "via Ryan Burge",
    alt: `Bar chart, share supporting unrestricted abortion access, by religion: ${alt}.`,
  };
}

/**
 * Make abortion illegal in all circumstances (support), by the CCES 2016
 * extract's full religion variable. Same data source and render script
 * as the graphics above.
 */
function cces2016ProlifeGraphic(): Graphic {
  const alt = cces2016PctAlt(cces2016Data.prolife_support);
  return {
    title: "Make abortion illegal in all circumstances",
    description: "Share who support making abortion illegal in all circumstances.",
    imageSrc: "/data-explorer/cces-2016/prolife.png",
    width: 1080,
    height: 1350,
    credit: "via Ryan Burge",
    alt: `Bar chart, share supporting a total abortion ban, by religion: ${alt}.`,
  };
}

/**
 * Favor same-sex marriage, by the CCES 2016 extract's full religion
 * variable. Same data source and render script as the graphics above.
 */
function cces2016GaymGraphic(): Graphic {
  const alt = cces2016PctAlt(cces2016Data.gaym_favor);
  return {
    title: "Favor same-sex marriage",
    description: "Share who favor allowing gays and lesbians to marry legally.",
    imageSrc: "/data-explorer/cces-2016/gaym.png",
    width: 1080,
    height: 1350,
    credit: "via Ryan Burge",
    alt: `Bar chart, share favoring same-sex marriage, by religion: ${alt}.`,
  };
}

/**
 * Religious attendance, full 6-category distribution, by the CCES 2016
 * extract's full religion variable. Same data source and render script
 * as the graphics above.
 */
function cces2016AttendGraphic(): Graphic {
  const { attend_distribution: results, attend_order: order } = cces2016Data;
  const alt = CCES2016_GROUP_ORDER.map((group) => {
    const g = results[group as keyof typeof results];
    const shares = order
      .map((label) => `${label} ${g.shares_pct[label as keyof typeof g.shares_pct]?.toFixed(0) ?? "n/a"}%`)
      .join(", ");
    return `${group}: ${shares}`;
  }).join("; ");

  return {
    title: "Religious attendance, full distribution",
    description: "How often each religion group attends religious services.",
    imageSrc: "/data-explorer/cces-2016/attend-distribution.png",
    width: 1080,
    height: 1350,
    credit: "via Ryan Burge",
    alt: `100%-stacked bar chart, religious attendance frequency by religion: ${alt}.`,
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
 * Party ID (pid7), LDS men vs. LDS women, over time - the CES Stacked
 * entry's second graphic. Built from pid-by-gender.json
 * (scripts/ryan-burge/pid_by_gender.py), rendered by
 * scripts/ryan-burge/render_pid_by_gender_chart.py.
 */
function cesPidByGenderGraphic(): Graphic {
  const { by_year_gender: results, category_order: categories, waves } = pidByGenderData;
  const alt = waves
    .map((year) => {
      const parts = (["Male", "Female"] as const).map((gender) => {
        const r = results[`${year}_${gender}` as keyof typeof results];
        const shares = categories
          .map((cat) => `${cat} ${r.shares_pct[cat as keyof typeof r.shares_pct]?.toFixed(0) ?? "n/a"}%`)
          .join(", ");
        return `${gender === "Male" ? "Men" : "Women"}: ${shares}`;
      });
      return `${year} — ${parts.join("; ")}`;
    })
    .join(". ");

  return {
    title: "Party ID, LDS men vs. LDS women, over time",
    description:
      "3-category party ID (Democrat/Independent/Republican, leaners folded in) among " +
      "Latter-day Saints, by gender and wave.",
    imageSrc: "/data-explorer/ces-stacked-2006-2018/pid-by-gender.png",
    width: 1080,
    height: 1350,
    credit: "via Ryan Burge",
    alt: `100%-stacked bar chart, LDS party ID by gender and survey wave. ${alt}.`,
  };
}

/**
 * "These days I feel like a stranger in my own country," by religion
 * (2017 wave) - the VOTER Survey Panel entry's first graphic. Built from
 * voter-stranger.json (scripts/ryan-burge/voter_stranger.py), rendered by
 * scripts/ryan-burge/render_voter_stranger_chart.py.
 */
function voterStrangerGraphic(): Graphic {
  const { results, group_order: order, stranger_order: segments } = voterStrangerData;
  const alt = order
    .map((group) => {
      const g = results[group as keyof typeof results];
      const shares = segments
        .map((label) => `${label} ${g.shares_pct[label as keyof typeof g.shares_pct]?.toFixed(0) ?? "n/a"}%`)
        .join(", ");
      return `${group}: ${shares}`;
    })
    .join("; ");

  return {
    title: "“These days I feel like a stranger in my own country”",
    description: "Agreement with this statement, by religion (2017 wave).",
    imageSrc: "/data-explorer/voter-survey-panel/stranger-2017.png",
    width: 1080,
    height: 1350,
    credit: "via Ryan Burge",
    alt: `100%-stacked bar chart, agreement with "these days I feel like a stranger in my own country," by religion. ${alt}.`,
  };
}

/** Formats a religion x target matrix into "Target: Group NN, Group NN, ...;
 * ..." alt text, shared by the three VOTER "matrix" heatmap graphics
 * below. `unit` is appended to each value ("" for a 0-100 thermometer
 * mean, "%" for a top-two-box share). */
function voterMatrixAlt(
  matrix: Record<string, Record<string, number | null>>,
  targetOrder: readonly string[],
  groupOrder: readonly string[],
  unit: string,
): string {
  return targetOrder
    .map((target) => {
      const cells = groupOrder
        .map((group) => `${group} ${matrix[group]![target]?.toFixed(0) ?? "n/a"}${unit}`)
        .join(", ");
      return `${target}: ${cells}`;
    })
    .join("; ");
}

/**
 * Feeling thermometers toward racial and religious groups, by religion
 * (2017 wave) - a heatmap/small-multiples matrix (7 targets x 9 religion
 * groups). Built from voter-ft-racial-religious.json
 * (scripts/ryan-burge/voter_matrices.py), rendered by
 * scripts/ryan-burge/render_voter_matrices.py.
 */
function voterFtRacialGraphic(): Graphic {
  const { matrix, target_order: targets, group_order: groups } = voterFtRacialData;
  const alt = voterMatrixAlt(matrix, targets, groups, "");
  return {
    title: "Feeling thermometers: racial and religious groups, by religion",
    description: "0 = coldest/most unfavorable, 100 = warmest/most favorable. Weighted means.",
    imageSrc: "/data-explorer/voter-survey-panel/ft-racial-religious.png",
    width: 1080,
    height: 1350,
    credit: "via Ryan Burge",
    alt: `Heatmap, feeling-thermometer mean (0-100) toward racial/religious groups by religion. ${alt}.`,
  };
}

/**
 * Feeling thermometers toward political and social groups, by religion
 * (2017 wave) - a heatmap/small-multiples matrix (9 targets x 9 religion
 * groups). Same data source and render script as the graphic above.
 */
function voterFtPoliticalGraphic(): Graphic {
  const { matrix, target_order: targets, group_order: groups } = voterFtPoliticalData;
  const alt = voterMatrixAlt(matrix, targets, groups, "");
  return {
    title: "Feeling thermometers: political and social groups, by religion",
    description: "0 = coldest/most unfavorable, 100 = warmest/most favorable. Weighted means.",
    imageSrc: "/data-explorer/voter-survey-panel/ft-political-social.png",
    width: 1080,
    height: 1350,
    credit: "via Ryan Burge",
    alt: `Heatmap, feeling-thermometer mean (0-100) toward political/social groups by religion. ${alt}.`,
  };
}

/**
 * Issue importance (top-two-box: very or somewhat important), by religion
 * (2017 wave) - a heatmap/small-multiples matrix (23 issues x 9 religion
 * groups). Same data source and render script as the graphics above.
 */
function voterIssueImportanceGraphic(): Graphic {
  const { matrix, target_order: targets, group_order: groups } = voterIssueImportanceData;
  const alt = voterMatrixAlt(matrix, targets, groups, "%");
  return {
    title: "Issue importance, by religion",
    description: "Share saying very or somewhat important (top-two-box).",
    imageSrc: "/data-explorer/voter-survey-panel/issue-importance.png",
    width: 1080,
    height: 1350,
    credit: "via Ryan Burge",
    alt: `Heatmap, share saying each issue is very/somewhat important, by religion. ${alt}.`,
  };
}

/**
 * The twenty VOTER Panel "idea" graphics below build out
 * docs/datasets/ryan-burge/VOTER_PANEL_IDEAS.md - a brainstorm list, not a
 * formal backlog, but the user asked for all twenty built. Six lean on the
 * panel's own longitudinal structure (a fixed religpew_baseline cohort
 * tracked forward through 2016/2017, per each JSON's own method note);
 * fourteen are single-wave cross-sections reusing this file's established
 * magnitude-bar and heatmap-matrix shapes.
 */

/** Formats a wave-series result set (idea's own {values: [n,n,n]} shape)
 * into alt text for the four VOTER longitudinal line-chart graphics. */
function voterSeriesAlt(
  series: Record<string, { values: (number | null)[] }>,
  groupOrder: readonly string[],
  waveYears: readonly number[],
): string {
  return groupOrder
    .map((group) => {
      const points = waveYears
        .map((yr, i) => `${yr} ${series[group]!.values[i]?.toFixed(0) ?? "n/a"}%`)
        .join(", ");
      return `${group}: ${points}`;
    })
    .join("; ");
}

function voterRetentionGraphic(): Graphic {
  const { retention, group_order: groups, wave_years: waves } = voterIdeasLongitudinalData;
  const alt = voterSeriesAlt(retention, groups, waves);
  return {
    title: "Religious retention, by tradition",
    description: "Of each tradition's baseline (~2011) members, share who still identify with it at each later wave.",
    imageSrc: "/data-explorer/voter-survey-panel/idea-retention.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Line chart, religious retention from baseline through 2017 by tradition. ${alt}.`,
  };
}

function voterReligimpTrendGraphic(): Graphic {
  const { religimp_very_important: series, group_order: groups, wave_years: waves } = voterIdeasLongitudinalData;
  const alt = voterSeriesAlt(series, groups, waves);
  return {
    title: "Religion \"very important,\" by tradition",
    description: "Of each tradition's baseline cohort, share who say religion is very important in their life.",
    imageSrc: "/data-explorer/voter-survey-panel/idea-religimp-trend.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Line chart, share saying religion is very important, baseline cohort tracked to 2017. ${alt}.`,
  };
}

function voterPrayerTrendGraphic(): Graphic {
  const { prayer_daily: series, group_order: groups, wave_years: waves } = voterIdeasLongitudinalData;
  const alt = voterSeriesAlt(series, groups, waves);
  return {
    title: "Pray daily, by tradition",
    description: "Of each tradition's baseline cohort, share who pray at least once a day.",
    imageSrc: "/data-explorer/voter-survey-panel/idea-prayer-trend.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Line chart, share praying daily, baseline cohort tracked to 2017. ${alt}.`,
  };
}

function voterTrustGovtTrendGraphic(): Graphic {
  const { trustgovt_top_two: series, group_order: groups, wave_years: waves } = voterIdeasLongitudinalData;
  const alt = voterSeriesAlt(series, groups, waves);
  return {
    title: "Trust the government, by tradition",
    description: "Of each tradition's baseline cohort, share who trust the government to do right most of the time or always.",
    imageSrc: "/data-explorer/voter-survey-panel/idea-trustgovt-trend.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Line chart, share trusting government, baseline cohort tracked to 2017. ${alt}.`,
  };
}

function voterVote2012vs2016Graphic(): Graphic {
  const { vote_r_share_2012_2016: results, group_order: groups } = voterIdeasLongitudinalData;
  const alt = groups
    .map((g) => {
      const r = results[g as keyof typeof results];
      return `${g} 2012=${r["2012"]?.toFixed(0) ?? "n/a"}%, 2016=${r["2016"]?.toFixed(0) ?? "n/a"}%`;
    })
    .join(", ");
  return {
    title: "Republican presidential vote share, 2012 vs. 2016",
    description: "Of each tradition's baseline cohort, share who voted for the Republican candidate.",
    imageSrc: "/data-explorer/voter-survey-panel/idea-vote-2012-2016.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Paired bar chart, Republican vote share 2012 vs 2016 by tradition. ${alt}.`,
  };
}

function voterGaymarShiftGraphic(): Graphic {
  const { gaymar_favor_baseline_2016: results, group_order: groups } = voterIdeasLongitudinalData;
  const alt = groups
    .map((g) => {
      const r = results[g as keyof typeof results];
      return `${g} baseline=${r.baseline?.toFixed(0) ?? "n/a"}%, 2016=${r["2016"]?.toFixed(0) ?? "n/a"}%`;
    })
    .join(", ");
  return {
    title: "Favor gay marriage, baseline vs. 2016",
    description: "Of each tradition's baseline cohort, share who favor allowing gays and lesbians to marry legally.",
    imageSrc: "/data-explorer/voter-survey-panel/idea-gaymar-shift.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Paired bar chart, favor gay marriage baseline vs 2016 by tradition. ${alt}.`,
  };
}

/** Formats a {pct} result set into alt text, shared by the eight
 * single-value VOTER idea magnitude-bar graphics below. */
function voterIdeaPctAlt(results: Record<string, { pct: number | null }>, groupOrder: readonly string[]): string {
  return groupOrder.map((g) => `${g} ${results[g]!.pct?.toFixed(0) ?? "n/a"}%`).join(", ");
}

function voterWishedVotedGraphic(): Graphic {
  const alt = voterIdeaPctAlt(voterIdeasBarsData.wished_voted, voterIdeasBarsData.group_order);
  return {
    title: "Wished they had voted in 2016",
    description: "Of those who didn't vote, share who wish they had.",
    imageSrc: "/data-explorer/voter-survey-panel/idea-wished-voted.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Bar chart, share who wished they'd voted in 2016, by religion: ${alt}.`,
  };
}

function voterVoteRegretsGraphic(): Graphic {
  const alt = voterIdeaPctAlt(voterIdeasBarsData.vote_regrets, voterIdeasBarsData.group_order);
  return {
    title: "Regret their 2016 presidential vote",
    description: "Share who regret who they voted for president in 2016.",
    imageSrc: "/data-explorer/voter-survey-panel/idea-vote-regrets.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Bar chart, share regretting their 2016 presidential vote, by religion: ${alt}.`,
  };
}

function voterSelfRelianceGraphic(): Graphic {
  const alt = voterIdeaPctAlt(voterIdeasBarsData.self_reliance, voterIdeasBarsData.group_order);
  return {
    title: "Value self-reliance over obedience in children",
    description: "Forced choice: which quality matters more for a child to have - obedience, or self-reliance.",
    imageSrc: "/data-explorer/voter-survey-panel/idea-self-reliance.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Bar chart, share valuing self-reliance over obedience in children, by religion: ${alt}.`,
  };
}

function voterRaceSlaveGraphic(): Graphic {
  const alt = voterIdeaPctAlt(voterIdeasBarsData.race_slave_agree, voterIdeasBarsData.group_order);
  return {
    title: "Slavery's legacy still disadvantages Black Americans",
    description: "Share who agree generations of slavery and discrimination have made it hard for Black people to succeed.",
    imageSrc: "/data-explorer/voter-survey-panel/idea-race-slave.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Bar chart, share agreeing slavery's legacy disadvantages Black Americans, by religion: ${alt}.`,
  };
}

function voterReverseDiscriminationGraphic(): Graphic {
  const alt = voterIdeaPctAlt(voterIdeasBarsData.reverse_discrimination_agree, voterIdeasBarsData.group_order);
  return {
    title: "Discrimination against whites is a serious problem",
    description: "Share who agree discrimination against white people is as big a problem as discrimination against minorities.",
    imageSrc: "/data-explorer/voter-survey-panel/idea-reverse-discrimination.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Bar chart, share agreeing reverse discrimination is a serious problem, by religion: ${alt}.`,
  };
}

function voterTrustPeopleGraphic(): Graphic {
  const alt = voterIdeaPctAlt(voterIdeasBarsData.trust_people, voterIdeasBarsData.group_order);
  return {
    title: "Most people can be trusted",
    description: "Generalized social trust - can't be too careful vs. most people can be trusted.",
    imageSrc: "/data-explorer/voter-survey-panel/idea-trust-people.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Bar chart, share saying most people can be trusted, by religion: ${alt}.`,
  };
}

function voterRiggedElitesGraphic(): Graphic {
  const alt = voterIdeaPctAlt(voterIdeasBarsData.rigged_elites_agree, voterIdeasBarsData.group_order);
  return {
    title: "Elites don't understand people like me",
    description: "Share who agree elites in this country don't understand the problems they're facing.",
    imageSrc: "/data-explorer/voter-survey-panel/idea-rigged-elites.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Bar chart, share agreeing elites don't understand people like them, by religion: ${alt}.`,
  };
}

function voterMilitaryGraphic(): Graphic {
  const alt = voterIdeaPctAlt(voterIdeasBarsData.military_household, voterIdeasBarsData.group_order);
  return {
    title: "Military household connection",
    description: "Share who or whose family currently serve or previously served in the military.",
    imageSrc: "/data-explorer/voter-survey-panel/idea-military.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Bar chart, share with a military household connection, by religion: ${alt}.`,
  };
}

/** Formats a religion x target matrix (the nine VOTER idea heatmaps'
 * shared JSON shape) into alt text. */
function voterIdeaMatrixAlt(
  matrix: Record<string, Record<string, number | null>>,
  targetOrder: readonly string[],
  groupOrder: readonly string[],
): string {
  return targetOrder
    .map((target) => {
      const cells = groupOrder.map((group) => `${group} ${matrix[group]![target]?.toFixed(0) ?? "n/a"}%`).join(", ");
      return `${target}: ${cells}`;
    })
    .join("; ");
}

function voterSexismGraphic(): Graphic {
  const { matrix, target_order: targets, group_order: groups } = voterIdeasSexismData;
  const alt = voterIdeaMatrixAlt(matrix, targets, groups);
  return {
    title: "Gender-role attitudes, by religion",
    description: "Share who strongly or somewhat agree with each statement (2016 wave).",
    imageSrc: "/data-explorer/voter-survey-panel/idea-sexism.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Heatmap, agreement with gender-role statements by religion. ${alt}.`,
  };
}

function voterMuslimDistrustGraphic(): Graphic {
  const { matrix, target_order: targets, group_order: groups } = voterIdeasMuslimData;
  const alt = voterIdeaMatrixAlt(matrix, targets, groups);
  return {
    title: "Muslim surveillance proposals, by religion",
    description: "Share who strongly or somewhat agree with each proposal (2017 wave).",
    imageSrc: "/data-explorer/voter-survey-panel/idea-muslim-distrust.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Heatmap, agreement with Muslim surveillance proposals by religion. ${alt}.`,
  };
}

function voterImmigrationIdeaGraphic(): Graphic {
  const { matrix, target_order: targets, group_order: groups } = voterIdeasImmigrationData;
  const alt = voterIdeaMatrixAlt(matrix, targets, groups);
  return {
    title: "Views of immigrants, by religion",
    description: "Share holding the pro-immigrant view on each measure (2017 wave).",
    imageSrc: "/data-explorer/voter-survey-panel/idea-immigration.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Heatmap, pro-immigrant sentiment by religion. ${alt}.`,
  };
}

function voterTradeGraphic(): Graphic {
  const { matrix, target_order: targets, group_order: groups } = voterIdeasTradeData;
  const alt = voterIdeaMatrixAlt(matrix, targets, groups);
  return {
    title: "Free trade attitudes, by religion",
    description: "Share holding the positive-for-consumers view on each effect (2016 wave).",
    imageSrc: "/data-explorer/voter-survey-panel/idea-trade.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Heatmap, positive view of free trade's effects by religion. ${alt}.`,
  };
}

function voterPromisesGraphic(): Graphic {
  const { matrix, target_order: targets, group_order: groups } = voterIdeasPromisesData;
  const alt = voterIdeaMatrixAlt(matrix, targets, groups);
  return {
    title: "Support for Trump's specific promises, by religion",
    description: "Share who support each promise (2017 wave).",
    imageSrc: "/data-explorer/voter-survey-panel/idea-promises.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Heatmap, support for Trump campaign promises by religion. ${alt}.`,
  };
}

function voterMediaGraphic(): Graphic {
  const { matrix, target_order: targets, group_order: groups } = voterIdeasMediaData;
  const alt = voterIdeaMatrixAlt(matrix, targets, groups);
  return {
    title: "Evening news viewership, by religion",
    description: "Share who watch each program (baseline wave, ~2011).",
    imageSrc: "/data-explorer/voter-survey-panel/idea-media.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Heatmap, evening news program viewership by religion. ${alt}.`,
  };
}

function voterOrgsGraphic(): Graphic {
  const { matrix, target_order: targets, group_order: groups } = voterIdeasOrgsData;
  const alt = voterIdeaMatrixAlt(matrix, targets, groups);
  return {
    title: "Organization membership, by religion",
    description: "Share who are a member of each organization (baseline wave, ~2011).",
    imageSrc: "/data-explorer/voter-survey-panel/idea-orgs.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Heatmap, civic-organization membership by religion. ${alt}.`,
  };
}

function voterVolunteeringGraphic(): Graphic {
  const { matrix, target_order: targets, group_order: groups } = voterIdeasVolunteeringData;
  const alt = voterIdeaMatrixAlt(matrix, targets, groups);
  return {
    title: "Volunteering by cause, by religion",
    description: "Share who volunteered for each type of cause in the past 12 months (baseline wave).",
    imageSrc: "/data-explorer/voter-survey-panel/idea-volunteering.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Heatmap, volunteering by cause type and religion. ${alt}.`,
  };
}

function voterPrideGraphic(): Graphic {
  const { matrix, target_order: targets, group_order: groups } = voterIdeasPrideData;
  const alt = voterIdeaMatrixAlt(matrix, targets, groups);
  return {
    title: "National pride, by religion",
    description: "Share very or somewhat proud of America on each dimension (2016 wave).",
    imageSrc: "/data-explorer/voter-survey-panel/idea-pride.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Heatmap, national pride by dimension and religion. ${alt}.`,
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
