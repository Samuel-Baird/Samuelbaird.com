/**
 * The Data Explorer: a home for public survey/statistical datasets and
 * whatever's been done with them here — quizzes, graphics, write-ups.
 * Adding a dataset or an analysis is a data change to this file, not a new
 * route or component, the same reasoning as the quiz's own tradition
 * lookup table (see scripts/evangelical-quiz/README.md).
 */

import { fiveColumnPct, groupBreakdownRows, QUIZ_DATA } from "@/lib/evangelical-quiz";
import switchingGeneralizedData from "../../docs/datasets/pew-rls-2023-24/switching-generalized.json";
import birthDecadeData from "../../docs/datasets/pew-rls-2023-24/birth-decade-distribution.json";
import childhoodFormationData from "../../docs/datasets/pew-rls-2023-24/childhood-formation.json";
import familyHouseholdData from "../../docs/datasets/pew-rls-2023-24/family-household.json";
import practiceData from "../../docs/datasets/pew-rls-2023-24/practice.json";
import beliefsData from "../../docs/datasets/pew-rls-2023-24/beliefs.json";
import spiritualExperienceData from "../../docs/datasets/pew-rls-2023-24/spiritual-experience.json";
import publicLifeData from "../../docs/datasets/pew-rls-2023-24/public-life.json";
import holidayBatchData from "../../docs/datasets/pew-rls-2023-24/holiday-batch.json";
import holidayBatch2Data from "../../docs/datasets/pew-rls-2023-24/holiday-batch-2.json";
import stayHomeParentGenderData from "../../docs/datasets/pew-rls-2023-24/stay-home-parent-gender.json";
import polygamyMoralityData from "../../docs/datasets/pew-mormon-survey-2011/polygamy-morality.json";
import foodStorageByActivityData from "../../docs/datasets/pew-mormon-survey-2011/food-storage-by-activity.json";
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
import voterVolunteeringSummaryData from "../../docs/datasets/ryan-burge/voter-volunteering-summary.json";
import voterIdeasPrideData from "../../docs/datasets/ryan-burge/voter-ideas-pride.json";
import pidOverTimeData from "../../docs/datasets/ryan-burge/pid-over-time.json";
import mormonOrdinationData from "../../docs/datasets/pew-mormon-survey-2011/ordination-by-activity.json";
import mormonismChristianData from "../../docs/datasets/pew-mormon-survey-2011/mormonism-christian.json";
import essentialToBeingMormonData from "../../docs/datasets/pew-mormon-survey-2011/essential-to-being-mormon.json";
import tithingByActivityData from "../../docs/datasets/pew-mormon-survey-2011/tithing-by-activity.json";
import missionTitheByConvertData from "../../docs/datasets/pew-mormon-survey-2011/mission-and-tithe-by-convert.json";
import presidentReadinessData from "../../docs/datasets/pew-mormon-survey-2011/president-readiness-by-party.json";
import mormonFoundingKnowledgeData from "../../docs/datasets/pew-religious-knowledge-2010/mormon-founding-knowledge.json";
import josephSmithKnowledgeData from "../../docs/datasets/pew-religious-knowledge-2010/joseph-smith-knowledge.json";
import bookOfMormonKnowledgeData from "../../docs/datasets/pew-religious-knowledge-2010/book-of-mormon-knowledge.json";
import churchStateLawData from "../../docs/datasets/pew-religious-knowledge-2010/church-state-law.json";
import jesusBirthplaceKnowledgeData from "../../docs/datasets/pew-religious-knowledge-2010/jesus-birthplace-knowledge.json";
import overallScoreData from "../../docs/datasets/pew-religious-knowledge-2010/overall-score.json";
import evolutionBeliefData from "../../docs/datasets/pew-rls-2007/evolution-belief.json";
import certaintyOfGodData from "../../docs/datasets/pew-rls-2007/certainty-of-god.json";
import dailyPrayerData from "../../docs/datasets/pew-rls-2007/daily-prayer.json";
import retentionRateData from "../../docs/datasets/pew-rls-2007/retention-rate.json";
import ldsShareByRegionData from "../../docs/datasets/pew-rls-2007/lds-share-by-region.json";
import samesexMarriage2014Data from "../../docs/datasets/pew-rls-2014/samesex-marriage.json";
import weeklyAttendance2014Data from "../../docs/datasets/pew-rls-2014/weekly-attendance.json";
import certaintyOfGod2014Data from "../../docs/datasets/pew-rls-2014/certainty-of-god.json";
import millennialShareData from "../../docs/datasets/pew-rls-2014/millennial-share.json";
import nonesGrowthData from "../../docs/datasets/pew-rls-2014/nones-growth-2007-2014.json";
import marriageSharedBeliefsData from "../../docs/datasets/pew-rls-2014-recontact/marriage-shared-beliefs.json";
import raisedInterfaithData from "../../docs/datasets/pew-rls-2014-recontact/raised-interfaith.json";
import spouseReligionMatteredData from "../../docs/datasets/pew-rls-2014-recontact/spouse-religion-mattered.json";
import attendWithSpouseData from "../../docs/datasets/pew-rls-2014-recontact/attend-with-spouse.json";
import spouseReligiousDisagreementData from "../../docs/datasets/pew-rls-2014-recontact/spouse-religious-disagreement.json";
import mormonsAsChristianData from "../../docs/datasets/pew-latin-america-2014/mormons-as-christian.json";
import transubstantiationData from "../../docs/datasets/pew-latin-america-2014/transubstantiation.json";
import latinAmericaWeeklyAttendanceData from "../../docs/datasets/pew-latin-america-2014/weekly-attendance.json";
import latinAmericaReligionImportanceData from "../../docs/datasets/pew-latin-america-2014/religion-importance.json";
import latinAmericaSamesexMarriageData from "../../docs/datasets/pew-latin-america-2014/samesex-marriage.json";
import witchcraftBeliefData from "../../docs/datasets/pew-latin-america-2014/witchcraft-belief.json";
import reasonsJoinedLdsData from "../../docs/datasets/pew-faith-in-flux-2008/reasons-joined-lds.json";
import reasonsLeftReligionData from "../../docs/datasets/pew-faith-in-flux-2008/reasons-left-religion.json";
import leaveVsJoinData from "../../docs/datasets/pew-faith-in-flux-2008/leave-vs-join.json";
import leavingDecisionMakerData from "../../docs/datasets/pew-faith-in-flux-2008/leaving-decision-maker.json";
import faithStrengthBeforeAfterData from "../../docs/datasets/pew-faith-in-flux-2008/faith-strength-before-after.json";
import onlineWorshipCovidData from "../../docs/datasets/pew-atp-w70-2020/online-worship-covid.json";
import prayerCovidCopingData from "../../docs/datasets/pew-atp-w70-2020/prayer-covid-coping.json";
import inpersonAttendanceCovidData from "../../docs/datasets/pew-atp-w70-2020/inperson-attendance-covid.json";
import financialThreatCovidData from "../../docs/datasets/pew-atp-w70-2020/financial-threat-covid.json";
import blmSermonsData from "../../docs/datasets/pew-atp-w70-2020/blm-sermons.json";
import annulmentCommunionData from "../../docs/datasets/pew-catholic-family-2015/annulment-communion.json";
import householdTypesData from "../../docs/datasets/pew-catholic-family-2015/household-types.json";
import charismaticChristiansData from "../../docs/datasets/pew-subsaharan-africa-2010/charismatic-christians.json";
import womenLeadersData from "../../docs/datasets/pew-black-faith-2021/women-leaders.json";
import religiousNationalIdentityData from "../../docs/datasets/pew-eastern-europe-2015/religious-national-identity.json";
import pewGlobalRestrictionsGriData from "../../docs/datasets/pew-global-restrictions-religion/gri-trend.json";
import christianNeighborAcceptanceData from "../../docs/datasets/pew-india-2021/christian-neighbor-acceptance.json";
import paysChurchTaxData from "../../docs/datasets/pew-church-tax-western-europe/pays-church-tax.json";
import christianShareDeclineData from "../../docs/datasets/pew-religious-composition-2010-2020/christian-share-decline.json";
import globalMigrantCompositionData from "../../docs/datasets/pew-religion-migration/global-migrant-composition.json";
import christianNationData from "../../docs/datasets/pew-atp-w114-2022/christian-nation.json";
import essentJesusData from "../../docs/datasets/pew-atp-w114-2022/essent-jesus.json";
import essentAttendData from "../../docs/datasets/pew-atp-w114-2022/essent-attend.json";
import relfavMormonsData from "../../docs/datasets/pew-atp-w114-2022/relfav-mormons.json";
import inpersonAttendanceW117Data from "../../docs/datasets/pew-atp-w117-2022/inperson-attendance.json";
import nontechPrayerGroupsData from "../../docs/datasets/pew-atp-w117-2022/nontech-prayer-groups.json";
import watchOnlineMonthlyData from "../../docs/datasets/pew-atp-w117-2022/watch-online-monthly.json";
import followsOwnLeadersData from "../../docs/datasets/pew-atp-w117-2022/follows-own-leaders.json";
import beyondThisWorldData from "../../docs/datasets/pew-atp-w132-2023/beyond-this-world.json";
import hasCrossData from "../../docs/datasets/pew-atp-w132-2023/has-cross.json";
import religiousCommunityData from "../../docs/datasets/pew-atp-w132-2023/religious-community.json";
import communionBeliefData from "../../docs/datasets/pew-atp-w44-2018/communion-belief.json";
import w44KnowledgeBatchData from "../../docs/datasets/pew-atp-w44-2018/knowledge-batch.json";
import w44WarmthData from "../../docs/datasets/pew-atp-w44-2018/warmth-toward-mormons.json";
import religiousMinorityData from "../../docs/datasets/pew-atp-w143-2024/religious-minority.json";
import w143HolidayBatchData from "../../docs/datasets/pew-atp-w143-2024/holiday-batch.json";
import w143HolidayBatch2Data from "../../docs/datasets/pew-atp-w143-2024/holiday-batch-2.json";
import w162HolidayBatchData from "../../docs/datasets/pew-atp-w162-2025/holiday-batch.json";
import cathessentData from "../../docs/datasets/pew-atp-w162-2025/cathessent.json";
import confessionFrequencyData from "../../docs/datasets/pew-atp-w162-2025/confession-frequency.json";
import w143HolidayBatch3Data from "../../docs/datasets/pew-atp-w143-2024/holiday-batch-3.json";
import coreBeliefsData from "../../docs/datasets/pew-mormon-survey-2011/core-beliefs.json";
import religiousConflictData from "../../docs/datasets/pew-atp-w162-2025/religious-conflict.json";
import wearReligiousItemsData from "../../docs/datasets/pew-atp-w162-2025/wear-religious-items.json";
import w162AttendanceData from "../../docs/datasets/pew-atp-w162-2025/attendance.json";
import renewalistShareData from "../../docs/datasets/pew-10-country-religion-2007/renewalist-share.json";
import latinoReligiousConvertsData from "../../docs/datasets/pew-hispanics-religion-2007/latino-religious-converts.json";
import usMembershipGrowthData from "../../docs/datasets/us-membership-growth-2000-2025/membership-by-year.json";
import usMembershipProjectionData from "../../docs/datasets/us-membership-growth-2000-2025/membership-projection-2050.json";
import worldwideMembershipHistoryData from "../../docs/datasets/worldwide-membership-history/membership-by-year.json";
import tenLargestChurchesData from "../../docs/datasets/ten-largest-us-churches-2035/denominations.json";

export type Quiz = {
  title: string;
  description: string;
  href: string;
};

/**
 * A set of @ithinkisam's Instagram carousel slides for this dataset - a
 * distinct thing from `graphics` above (those are neutral website charts;
 * these carry an editorial title per-slide, per the social style guide at
 * scripts/social-graphics/STATISTICS_STYLE_GUIDE.md). Just a link out to a
 * static gallery page, not part of the structured Graphic system.
 */
export type SocialSet = {
  title: string;
  description: string;
  href: string;
  count: number;
  previewSrc: string;
  previewWidth: number;
  previewHeight: number;
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
];

/** GENERALIZED_GROUP_ORDER plus the religiously unaffiliated, for the
 * "Christian only" variant graphics whose original wide-population chart
 * already carried an unaffiliated row (the Beliefs section, and
 * relimpact/vol12 in Public Life) - matching NARROW_PLUS_UNAFFILIATED_ORDER
 * in scripts/pew-rls/render_christian_only_variants.py. */
const CHRISTIAN_ONLY_PLUS_UNAFFILIATED_GROUP_ORDER = [
  ...GENERALIZED_GROUP_ORDER,
  "Religiously unaffiliated",
];

/** Group order for children_with_kids_at_home, matching CHILDREN_ORDER in
 * scripts/pew-rls/render_family_household_charts.py. */
const CHILDREN_GROUP_ORDER = [
  "Latter-day Saint", "Catholic", "Protestant", "Orthodox Christian",
  "Jehovah's Witness",
];

/** Group order for pray_or_read_scripture_with_kids, matching
 * KIDACT_ORDER in scripts/pew-rls/render_family_household_charts.py - a
 * wider population than every other chart on this page, per the backlog
 * item's own note. */
const KIDACT_GROUP_ORDER = [
  "Latter-day Saint", "Catholic", "Protestant", "Orthodox Christian",
  "Jehovah's Witness", "Other religions",
  "Religiously affiliated average",
];

/** Group order for the seven holiday-batch graphics, matching
 * holiday-batch.json's own group_order (scripts/pew-rls/holiday_batch.py). */
const HOLIDAY_BATCH_ORDER = holidayBatchData.group_order;

/** Group order for the six "Practice" items whose population is every
 * religiously affiliated tradition individually (not lumped), matching
 * ALL_RELIGIOUS_ORDER in scripts/pew-rls/render_practice_charts.py. */
const ALL_RELIGIOUS_GROUP_ORDER = [
  "Latter-day Saint", "Catholic", "Protestant", "Jehovah's Witness",
  "Muslim", "Hindu", "Orthodox Christian", "Buddhist",
  "Jewish", "Other world religions", "Other faiths", "All religious average",
];

/** Group order for the "Beliefs" section, matching GROUP_ORDER in
 * scripts/pew-rls/render_beliefs_charts.py - all religious traditions
 * individually + an average + the unaffiliated as their own row, per that
 * section's own open-population resolution (see beliefs.py's docstring). */
const BELIEFS_GROUP_ORDER = [
  "Latter-day Saint", "Catholic", "Protestant", "Jehovah's Witness",
  "Muslim", "Hindu", "Orthodox Christian", "Buddhist",
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
  /** The survey's own fielding period, in the source's own words — e.g.
   * "2011", "2023-24", "2000-2025". Free text, used as the gallery's date
   * filter facet; not parsed for chronological sorting. */
  fieldedPeriod: string;
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
  /** @ithinkisam's Instagram carousel sets for this dataset, if any. */
  socialSets?: SocialSet[];
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

/** Raw dataset definitions, in whatever order they were added to this file -
 * NOT the order graphics render in. Each dataset's `graphics` array here can
 * list its entries in any order (grouped by topic, in the order a backlog
 * item was worked, etc.) - `DATASETS` below is what every page actually
 * imports, and it re-sorts each dataset's graphics alphabetically by title
 * before export. See `sortGraphicsAlphabetically`'s docstring for why. */
const RAW_DATASETS: Dataset[] = [
  {
    slug: "us-membership-growth-2000-2025",
    name: "U.S. Church Membership Growth, 2000-2025",
    shortDescription:
      "A compiled year-by-year timeline of reported U.S. Church membership — not one survey, several sources stitched together.",
    sponsor: "The Church of Jesus Christ of Latter-day Saints",
    fielder: "Compiled by this site from multiple public sources",
    fieldedPeriod: "2000-2025",
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
    fieldedPeriod: "1830-2025",
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
    slug: "ten-largest-us-churches-2035",
    name: "Ten Largest U.S.-Rooted Churches, Projected to 2035",
    shortDescription:
      "Ten denominations' own reported membership, each extended by a simple trend line to 2035 — modeled on Ryan Burge's American-religion projections.",
    sponsor: "Multiple denominations (each self-reported; see README for exceptions)",
    fielder: "Compiled by this site from multiple public sources",
    fieldedPeriod: "Historical reporting, projected to 2035",
    description:
      "A third \"mixed data\" entry, comparing ACROSS ten denominations rather than " +
      "tracking one body over time: Catholic Church, United Methodist Church, The " +
      "Church of Jesus Christ of Latter-day Saints, Evangelical Lutheran Church in " +
      "America, Lutheran Church–Missouri Synod, Orthodox Christian churches (combined " +
      "estimate), Episcopal Church, Presbyterian Church (USA), Church of God in " +
      "Christ, and Presbyterian Church in America. For each, an ordinary-least-squares " +
      "line is fit through that body's own reported membership figures and extended to " +
      "2035 — a blunt straight-line extrapolation, not a demographic forecast, modeled " +
      "on Ryan Burge's GSS-based American-religion projections " +
      "(gist.github.com/ryanburge/e785275206cd12584b73eb4ec9b3ad52). Several entries " +
      "carry real data-quality caveats — Catholic figures vary 5-15M by methodology, " +
      "LDS figures are worldwide rather than U.S.-only, and Orthodox/COGIC figures are " +
      "sparse and, for COGIC, diverge roughly 5-6x from independent U.S. Religion " +
      "Census counts. See docs/datasets/ten-largest-us-churches-2035/README.md for " +
      "every figure's exact citation and confidence rating.",
    citation:
      "Compiled from each denomination's own statistical reporting (GCAH/GCFA, ELCA, " +
      "LCMS, PCA Historical Center, etc.), the U.S. Religion Census, and secondary " +
      "research compilations - see README.md for the full per-denomination source list.",
    sourceUrl: "https://gist.github.com/ryanburge/e785275206cd12584b73eb4ec9b3ad52",
    category: "Mixed Datasets",
    graphics: [tenLargestChurchesGraphic()],
  },
  {
    slug: "state-of-theology",
    name: "State of Theology Survey",
    shortDescription:
      "A national survey of American theological belief, run every two years since 2014.",
    sponsor: "Ligonier Ministries",
    fielder: "Lifeway Research",
    fieldedPeriod: "2014-2025",
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
    socialSets: [
      {
        title: "Evangelicals vs. the country, 2016–2025",
        description:
          "An Instagram carousel tracking evangelicals against all U.S. adults across five " +
          "survey waves, plus a 2022 scorecard of where evangelical belief is firmest.",
        href: "/data-explorer/state-of-theology/social/post1",
        count: 14,
        previewSrc: "/social-graphics/state-of-theology/post1/1_nicaea_won.png",
        previewWidth: 1080,
        previewHeight: 1350,
      },
      {
        title: "Comparing four traditions, 2025",
        description:
          "An Instagram carousel comparing Evangelical, Black Protestant, Mainline, and " +
          "Roman Catholic respondents across nine statements from the survey.",
        href: "/data-explorer/state-of-theology/social/post2",
        count: 12,
        previewSrc: "/social-graphics/state-of-theology/post2/1_trinity.png",
        previewWidth: 1080,
        previewHeight: 1350,
      },
    ],
  },
  {
    slug: "pew-religious-landscape-study",
    name: "Religious Landscape Study",
    shortDescription:
      "Pew's 36,908-respondent map of American religion — who belongs to what, and what they believe.",
    sponsor: "Pew Research Center",
    fielder: "NORC at the University of Chicago",
    fieldedPeriod: "2023-24",
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
      pewAttendDistributionChristianGraphic(),
      pewAttendMonthlyPlusGraphic(),
      pewAttendMonthlyPlusChristianGraphic(),
      pewMembGraphic(),
      pewMembChristianGraphic(),
      pewPrayDistributionGraphic(),
      pewPrayDistributionChristianGraphic(),
      pewPracbGraphic(),
      pewPracbChristianGraphic(),
      pewPraccGraphic(),
      pewGraceGraphic(),
      pewPracaGraphic(),
      pewSoulBeliefGraphic(),
      pewSoulBeliefChristianGraphic(),
      pewHeavenBeliefGraphic(),
      pewHeavenBeliefChristianGraphic(),
      pewHellBeliefGraphic(),
      pewHellBeliefChristianGraphic(),
      pewHeavenVsHellGraphic(),
      pewHeavenVsHellChristianGraphic(),
      pewEvolutionGuidedGraphic(),
      pewEvolutionGuidedChristianGraphic(),
      pewSpiritualMeaningGraphic(),
      pewSpiritualPeaceGraphic(),
      pewSpiritualPresenceGraphic(),
      pewOpenidenGraphic(),
      pewChngAGraphic(),
      pewDivracpopGraphic(),
      pewDivrelpopGraphic(),
      pewHumntrGraphic(),
      pewRelimpactGraphic(),
      pewRelimpactChristianGraphic(),
      pewRelinstFGraphic(),
      pewRelinstGGraphic(),
      pewRelinstEGraphic(),
      pewScimpactGraphic(),
      pewVol12Graphic(),
      pewVol12ChristianGraphic(),
      pewWorksForPayGraphic(),
      pewHappinessGraphic(),
      pewHispanicShareGraphic(),
      pewChristianNationGraphic(),
      pewStayHomeParentGraphic(),
      pewReligiousSymbolsGraphic(),
      pewSchoolPrayerGraphic(),
      pewStayHomeParentGenderGraphic(),
      pewSameFaithSpouseGraphic(),
      pewAsianShareGraphic(),
      pewTwoPlusChildrenGraphic(),
    ],
  },
  {
    slug: "cces-2016",
    name: "CCES 2016",
    shortDescription:
      "A 64,600-respondent national election survey, with 870 Latter-day Saints in it.",
    sponsor: "Cooperative Election Studies (multi-university consortium)",
    fielder: "YouGov",
    fieldedPeriod: "2016",
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
      cces2016UnionGraphic(),
    ],
  },
  {
    slug: "ces-stacked-2006-2018",
    name: "CES Stacked, 2006–2018",
    shortDescription:
      "Party ID, race, and gender by religious tradition, across seven federal election cycles.",
    sponsor: "Cooperative Election Studies (multi-university consortium)",
    fielder: "YouGov",
    fieldedPeriod: "2006-2018",
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
    fieldedPeriod: "2011-2020",
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
      voterNonreligiousCausesGraphic(),
      voterReligiousOrgVolunteerGraphic(),
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
    fieldedPeriod: "2011",
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
      missionTitheByConvertGraphic(),
      presidentReadinessGraphic(),
      polygamyMoralityGraphic(),
      foodStorageByActivityGraphic(),
      coreBeliefsGraphic(),
    ],
  },
  {
    slug: "pew-religious-knowledge-2010",
    name: "2010 U.S. Religious Knowledge Survey",
    shortDescription:
      "What Americans of every faith (and none) actually know about religion.",
    sponsor: "Pew Research Center",
    fielder: "Princeton Survey Research Associates International (PSRAI)",
    fieldedPeriod: "2010",
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
      churchStateLawGraphic(),
      jesusBirthplaceKnowledgeGraphic(),
      overallScoreGraphic(),
    ],
  },
  {
    slug: "pew-rls-2007",
    name: "2007 U.S. Religious Landscape Survey",
    shortDescription:
      "The original Religious Landscape Survey — the baseline the 2014 and 2023-24 waves track against.",
    sponsor: "Pew Research Center",
    fielder: "Princeton Survey Research Associates International (PSRAI)",
    fieldedPeriod: "2007-08",
    description:
      "The first Religious Landscape Survey: 35,556 adults in the continental U.S., " +
      "interviewed by telephone in summer 2007, plus a supplemental spring 2008 sample of " +
      "200 Alaska and 201 Hawaii adults (reported separately; the two files don't share a " +
      "combining weight). This is the survey that first measured the scale of religious " +
      "switching in America and established the RELTRAD religious-tradition classification " +
      "later waves (2014, 2023-24) still use.",
    sourceUrl: "https://www.pewresearch.org/religious-landscape-study/2007/",
    graphics: [
      evolutionBeliefGraphic(),
      certaintyOfGodGraphic(),
      dailyPrayerGraphic(),
      retentionRateGraphic(),
      ldsShareByRegionGraphic(),
    ],
  },
  {
    slug: "pew-rls-2014",
    name: "2014 Religious Landscape Study",
    shortDescription:
      "The middle wave of Pew's Religious Landscape Study, between the 2007 original and 2023-24.",
    sponsor: "Pew Research Center",
    fielder: "Princeton Survey Research Associates International (PSRAI)",
    fieldedPeriod: "2014",
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
      millennialShareGraphic(),
      nonesGrowthGraphic(),
    ],
  },
  {
    slug: "pew-rls-2014-recontact",
    name: "2014 Religious Landscape Study — Recontact Survey",
    shortDescription:
      "A 2015 follow-up to 5,000 RLS 2014 respondents, focused on interfaith upbringing and marriage.",
    sponsor: "Pew Research Center",
    fielder: "Princeton Survey Research Associates International (PSRAI)",
    fieldedPeriod: "2015",
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
      attendWithSpouseGraphic(),
      spouseReligiousDisagreementGraphic(),
    ],
  },
  {
    slug: "pew-latin-america-2014",
    name: "Religion in Latin America",
    shortDescription:
      "Pew's face-to-face survey of religious belief and practice across 19 Latin American countries and territories.",
    sponsor: "Pew Research Center (Pew-Templeton Global Religious Futures project)",
    fielder: "Princeton Survey Research Associates International (PSRAI) and Ipsos Public Affairs",
    fieldedPeriod: "2013-14",
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
    graphics: [
      mormonsAsChristianGraphic(),
      transubstantiationGraphic(),
      latinAmericaWeeklyAttendanceGraphic(),
      latinAmericaReligionImportanceGraphic(),
      latinAmericaSamesexMarriageGraphic(),
      witchcraftBeliefGraphic(),
    ],
  },
  {
    slug: "pew-faith-in-flux-2008",
    name: "Faith in Flux (2008 Conversion Recontact Survey)",
    shortDescription:
      "Follow-up interviews with 2007 Religious Landscape Survey respondents, focused on why people change religion.",
    sponsor: "Pew Research Center",
    fielder: "Princeton Survey Research Associates International (PSRAI)",
    fieldedPeriod: "2008",
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
    graphics: [
      reasonsJoinedLdsGraphic(),
      reasonsLeftReligionGraphic(),
      leaveVsJoinGraphic(),
      leavingDecisionMakerGraphic(),
      faithStrengthBeforeAfterGraphic(),
    ],
  },
  {
    slug: "pew-atp-w44-2018",
    name: "American Trends Panel, Wave 44 (February 2019)",
    shortDescription:
      "A Pew American Trends Panel wave on religious knowledge and belief, fielded February 2019.",
    sponsor: "Pew Research Center",
    fielder: "Pew Research Center (American Trends Panel)",
    fieldedPeriod: "February 2019",
    description:
      "Wave 44 of Pew's American Trends Panel: 10,971 U.S. adults surveyed online " +
      "Feb. 4-19, 2019 (full panel plus a KnowledgePanel oversample), in English and " +
      "Spanish. Carries F_RELTRAD, the standard RLS-coded religious-tradition variable " +
      "(Latter-day Saints coded 20000, \"Mormon\"). A wide religious-literacy battery — " +
      "Bible/Torah/Quran/Buddhist-text knowledge questions, feelings toward religious " +
      "groups, Holocaust knowledge, and Catholics' own beliefs about Communion — fed " +
      "Pew's 2019 \"What Americans Know About Religion\" report.",
    sourceUrl: "https://www.pewresearch.org/religion/2019/07/23/what-americans-know-about-religion/",
    graphics: [
      communionBeliefGraphic(),
      w44ConstitutionGraphic(),
      w44EasterGraphic(),
      w44RamadanGraphic(),
      w44RoshHashanaGraphic(),
      w44MeccaGraphic(),
      w44FaithAloneGraphic(),
      w44WarmthGraphic(),
    ],
  },
  {
    slug: "pew-atp-w70-2020",
    name: "American Trends Panel, Wave 70 (July 2020)",
    shortDescription:
      "A general Pew American Trends Panel wave, fielded July 2020, carrying a religious-tradition variable.",
    sponsor: "Pew Research Center",
    fielder: "Pew Research Center (American Trends Panel)",
    fieldedPeriod: "July 2020",
    description:
      "Wave 70 of Pew's American Trends Panel: 10,211 U.S. adults surveyed online (a small " +
      "non-internet subsample by mail) July 13–19, 2020, in English and Spanish. Like other " +
      "ATP waves, it carries a F_RELTRAD frame variable classifying each respondent's " +
      "religious tradition (Latter-day Saints coded 20000), which is what makes an otherwise " +
      "general-topic wave usable for breaking its questions out by religion.",
    sourceUrl: "https://www.pewresearch.org/our-methods/u-s-surveys/american-trends-panel/",
    graphics: [
      onlineWorshipCovidGraphic(),
      prayerCovidCopingGraphic(),
      inpersonAttendanceCovidGraphic(),
      financialThreatCovidGraphic(),
      blmSermonsGraphic(),
    ],
  },
  {
    slug: "pew-catholic-family-2015",
    name: "2015 Survey of U.S. Catholics and Family Life",
    shortDescription:
      "A 2015 Pew survey of U.S. adults (Catholic oversample) on Catholic identity, papal opinion, and family-life teachings.",
    sponsor: "Pew Research Center",
    fielder: "Pew Research Center (telephone, landline + cellphone)",
    fieldedPeriod: "2015",
    description:
      "Pew Research Center's 2015 Survey of U.S. Catholics and Family Life: 5,122 U.S. adults 18+ " +
      "surveyed by telephone (landline and cellphone) May 5–June 7, 2015, in English and Spanish. " +
      "The sample is the general public, not Catholics only, but includes 1,016 respondents who " +
      "are Catholic by religion — enough to analyze Catholic opinion on the pope, confession, " +
      "Communion practice, and Church teachings on marriage and family on its own. It underlies " +
      "Pew's 2015 reports \"Catholics Divided Over Global Warming\" and \"U.S. Catholics Open to " +
      "Non-Traditional Families.\"",
    citation:
      "Pew Research Center. \"U.S. Catholics Open to Non-Traditional Families.\" September 2, 2015. " +
      "2015 Survey of U.S. Catholics and Family Life, fielded May 5-June 7, 2015.",
    sourceUrl: "https://www.pewresearch.org/religion/2015/09/02/u-s-catholics-open-to-non-traditional-families/",
    graphics: [
      annulmentCommunionGraphic(),
      raisedByMarriedParentsGraphic(),
      raisedBySingleParentGraphic(),
      raisedByDivorcedParentsGraphic(),
      raisedByCohabitingParentsGraphic(),
      raisedByGayLesbianCoupleGraphic(),
    ],
  },
  {
    slug: "pew-subsaharan-africa-2010",
    name: "Tolerance and Tension: Islam and Christianity in Sub-Saharan Africa (2010)",
    shortDescription:
      "A 19-country face-to-face survey of sub-Saharan Africa's Christian and Muslim populations, fielded 2008-09.",
    sponsor: "The Pew Charitable Trusts and the John Templeton Foundation",
    fielder: "Pew Research Center's Forum on Religion & Public Life",
    fieldedPeriod: "2008-09",
    description:
      "A face-to-face general-population survey of 25,091 adults across 19 sub-Saharan African " +
      "countries, fielded December 2008–April 2009 in more than 60 languages and dialects. The " +
      "19 countries together hold roughly three-quarters of sub-Saharan Africa's population. It " +
      "covers religious identity, tolerance between faiths, Pentecostal/Charismatic belief and " +
      "practice, traditional/spirit beliefs, and views on national identity and religious law. " +
      "Unlike most datasets in this pipeline it carries no U.S./LDS-specific frame variable — " +
      "Latter-day Saints are not a named category anywhere in the questionnaire.",
    citation:
      "Pew Research Center's Forum on Religion & Public Life. 2010. \"Tolerance and Tension: " +
      "Islam and Christianity in Sub-Saharan Africa.\"",
    sourceUrl: "https://www.pewresearch.org/wp-content/uploads/sites/7/2010/04/sub-saharan-africa-full-report.pdf",
    graphics: [charismaticChristiansGraphic()],
  },
  {
    slug: "pew-black-faith-2021",
    name: "Faith Among Black Americans (2021)",
    shortDescription:
      "A dedicated Pew survey of 8,660 Black American adults on religious belief and practice, fielded 2019-2020.",
    sponsor: "Pew Research Center",
    fielder: "Pew Research Center (combined ATP, ABS, NORC AmeriSpeak, and Ipsos KnowledgePanel samples)",
    fieldedPeriod: "2019-2020",
    description:
      "Pew's dedicated study of Black American religious life: 8,660 Black adults surveyed via a " +
      "combination of four probability-based samples (the Center's American Trends Panel, its own " +
      "ABS survey, NORC's AmeriSpeak panel, and Ipsos's KnowledgePanel), online, by mail, and by " +
      "live telephone, November 19, 2019-June 3, 2020 (most respondents completed the survey between " +
      "January 21 and February 10, 2020). An additional 4,574 non-Black respondents were interviewed " +
      "to support general-population comparisons.",
    citation:
      "Pew Research Center. \"Faith Among Black Americans,\" published Feb. 16, 2021 (survey fielded " +
      "Nov. 19, 2019-June 3, 2020).",
    sourceUrl: "https://www.pewresearch.org/religion/2021/02/16/faith-among-black-americans/",
    graphics: [womenLeadersGraphic()],
  },
  {
    slug: "pew-eastern-europe-2015",
    name: "Central and Eastern Europe (2015-2016)",
    shortDescription:
      "A face-to-face Pew survey across 18 Central and Eastern European countries, fielded 2015-2016, on religion, national identity, and Orthodox-Catholic relations.",
    sponsor: "Pew Research Center",
    fielder: "Pew Research Center",
    fieldedPeriod: "2015-2016",
    description:
      "Pew's face-to-face survey behind the 2017 report \"Religious Belief and National Belonging in " +
      "Central and Eastern Europe\": more than 25,000 adults interviewed June 2015-July 2016 in 17 " +
      "languages across 18 countries (Armenia, Belarus, Bosnia, Bulgaria, Croatia, Czech Republic, " +
      "Estonia, Georgia, Greece, Hungary, Latvia, Lithuania, Moldova, Poland, Romania, Russia, Serbia, " +
      "Ukraine). Covers religious belief and practice, Orthodox-Catholic relations, and how religious " +
      "identity fuses with national identity in a region once dominated by atheist regimes.",
    citation: "Pew Research Center. 2017. \"Religious Belief and National Belonging in Central and Eastern Europe.\"",
    sourceUrl: "https://www.pewresearch.org/religion/2017/05/10/religious-belief-and-national-belonging-in-central-and-eastern-europe/",
    graphics: [religiousNationalIdentityGraphic()],
  },
  {
    slug: "pew-global-restrictions-religion",
    name: "Global Restrictions on Religion (2007-2022)",
    shortDescription:
      "Pew's annual country-level ratings of government restrictions and social hostilities involving religion, worldwide, 2007-2022.",
    sponsor: "Pew Research Center",
    fielder: "Pew Research Center (Pew-Templeton Global Religious Futures project)",
    fieldedPeriod: "2007-2022",
    description:
      "A cumulative country/year-level dataset rating 198 countries and territories each year from 2007 to " +
      "2022 on two 0-10 indexes: the Government Restrictions Index (GRI, 20 measures of how governments " +
      "restrict religious belief and practice - banning faiths, prohibiting conversion, favoring one religion) " +
      "and the Social Hostilities Index (SHI, 13 measures of religion-related hostility by private individuals " +
      "and groups - mob violence, harassment over religious attire, religion-related armed conflict). Unlike " +
      "this site's other Pew datasets, it carries no per-respondent religion variable, so it has no " +
      "Latter-day-Saint-specific breakout; Pew's Dec. 2024 report found restrictions held at their highest " +
      "level yet recorded in 2022, continuing a rise that began around 2010.",
    citation:
      "Pew Research Center, \"Government Restrictions on Religion Stayed at Peak Levels Globally in 2022,\" " +
      "Dec. 18, 2024, based on the \"Global Restrictions on Religion\" cumulative dataset (2007-2022, 198 " +
      "countries and territories).",
    sourceUrl: "https://www.pewresearch.org/religion/2024/12/18/government-restrictions-on-religion-stayed-at-peak-levels-globally-in-2022/",
    graphics: [pewGlobalRestrictionsGriGraphic()],
  },
  {
    slug: "pew-india-2021",
    name: "India Religion Survey (2019-2020)",
    shortDescription:
      "Pew's massive face-to-face survey of religion across India, fielded 2019-2020, oversampling religious minorities including Christians.",
    sponsor: "Pew Research Center",
    fielder: "Pew Research Center, fieldwork directed by RTI International",
    fieldedPeriod: "2019-2020",
    description:
      "Pew Research Center's face-to-face survey of religion in India: 29,999 adults surveyed across " +
      "26 states and three union territories in 17 languages, fielded November 17, 2019-March 23, " +
      "2020. Muslims, Christians, Sikhs, Buddhists, Jains, and Northeast-region residents were " +
      "deliberately oversampled, yielding 1,011 Christian respondents - enough for reliable subgroup " +
      "analysis of India's ~2% Christian minority. Underlies Pew's 2021 report \"Religion in India: " +
      "Tolerance and Segregation.\"",
    sourceUrl: "https://www.pewresearch.org/religion/2021/06/29/religion-in-india-tolerance-and-segregation/",
    graphics: [christianNeighborAcceptanceGraphic()],
  },
  {
    slug: "pew-church-tax-western-europe",
    name: "Being Christian in Western Europe (Church Tax Add-On)",
    shortDescription:
      "Pew's Western Europe religion survey, augmented with three questions about who currently pays — or is opting out of — the church tax.",
    sponsor: "Pew Research Center",
    fielder: "GfK Belgium",
    fieldedPeriod: "2017",
    description:
      "Pew's \"Being Christian in Western Europe\" survey: 26,096 adults interviewed by " +
      "telephone (cellphone and landline) April–August 2017 across 15 Western European " +
      "countries plus Slovakia, under the direction of GfK Belgium. This version adds three " +
      "church-tax items (Q13, Q14a, Q14b) Pew fielded later for its 2019 report. Church tax " +
      "exists in only 9 of the 16 countries surveyed — mandatory in Austria, Denmark, " +
      "Finland, Germany, Sweden, and Switzerland; voluntary opt-in in Italy, Portugal, and " +
      "Spain — and Q13 was asked only in those 9.",
    citation:
      "Pew Research Center. 2019. \"In Western European Countries With Church Taxes, Support " +
      "for the Tradition Remains Strong.\"",
    sourceUrl: "https://www.pewresearch.org/religion/2019/04/30/in-western-european-countries-with-church-taxes-support-for-the-tradition-remains-strong/",
    graphics: [paysChurchTaxGraphic()],
  },
  {
    slug: "pew-religious-composition-2010-2020",
    name: "How the Global Religious Landscape Changed From 2010 to 2020",
    shortDescription:
      "Country-level Christian, Muslim, and other religious-population estimates for 2010 and 2020, across 201 countries and territories.",
    sponsor: "Pew Research Center",
    fielder: "Pew Research Center",
    fieldedPeriod: "2010 and 2020",
    description:
      "Population estimates for seven broad religious categories - Christians, Muslims, " +
      "Hindus, Buddhists, Jews, Other religions, and the religiously unaffiliated - for " +
      "2010 and 2020, across 201 countries and territories covering 99.98% of the " +
      "world's population. Compiled from more than 2,700 national censuses, demographic " +
      "surveys, and population registers, not a single fielded survey. There is no " +
      "Latter-day Saint-specific breakout; LDS people are folded into the broad " +
      "Christian category, so this dataset's chart tells the global-Christianity " +
      "backdrop against which the Church's own growth numbers (elsewhere on this site) " +
      "play out.",
    citation:
      "Pew Research Center. 2026. \"How the Global Religious Landscape Changed From 2010 " +
      "to 2020.\" (dataset updated Feb. 12, 2026 with a Religious Diversity Index.)",
    sourceUrl: "https://www.pewresearch.org/religion/2026/02/12/religious-diversity-around-the-world/",
    graphics: [christianShareDeclineGraphic()],
  },
  {
    slug: "pew-religion-migration",
    name: "Religious Composition of the World's Migrants, 1990-2020",
    shortDescription:
      "Pew's global estimate of the religious composition of the world's international migrants, 1990-2020.",
    sponsor: "Pew Research Center",
    fielder: "Pew Research Center",
    fieldedPeriod: "1990-2020",
    description:
      "Pew's estimate of the religious composition of the world's international migrant stock " +
      "— people living outside the country where they were born — for seven benchmark years " +
      "from 1990 to 2020, broken out by country, region, and world total, and by direction " +
      "(incoming to a destination vs. outgoing from an origin). Built primarily from 270 " +
      "censuses and surveys, filled out with Pew's own indirect-estimation methodology where " +
      "a country's migrant population lacks a direct religious breakdown. There is no " +
      "Latter-day Saint/Mormon-specific breakout — categories are broad (Christian, Muslim, " +
      "Unaffiliated, Hindu, Buddhist, Jewish, Other).",
    citation:
      "Kramer, Stephanie, Yunping Tong and Anne Fengyan Shi. 2024. \"Religious Composition of " +
      "the World's Migrants, 1990-2020.\" Pew Research Center.",
    sourceUrl: "https://www.pewresearch.org/religion/2024/08/19/religious-composition-of-the-worlds-migrants-1990-2020/",
    graphics: [globalMigrantCompositionGraphic()],
  },
  {
    slug: "pew-atp-w114-2022",
    name: "American Trends Panel, Wave 114 (September 2022)",
    shortDescription:
      "A general Pew American Trends Panel wave, fielded September 2022, that fed Pew's 'Christian nation' research.",
    sponsor: "Pew Research Center",
    fielder: "Pew Research Center (American Trends Panel)",
    fieldedPeriod: "September 2022",
    description:
      "Wave 114 of Pew's American Trends Panel: 10,588 U.S. adults surveyed online " +
      "September 13–18, 2022, in English and Spanish. It fed several Pew reports on " +
      "religion and politics, most notably \"45% of Americans Say U.S. Should Be a " +
      "'Christian Nation'\" (October 27, 2022). Unlike some other ATP waves in this " +
      "collection, it does not carry the finer F_RELTRAD frame variable — religious " +
      "breakouts here use F_RELIG, which still separately identifies Mormon/LDS " +
      "respondents (coded 3.0).",
    sourceUrl: "https://www.pewresearch.org/religion/2022/10/27/45-of-americans-say-u-s-should-be-a-christian-nation/",
    graphics: [christianNationGraphic(), essentJesusGraphic(), essentAttendGraphic(), relfavMormonsGraphic()],
  },
  {
    slug: "pew-atp-w117-2022",
    name: "American Trends Panel, Wave 117 (November 2022)",
    shortDescription:
      "A general Pew American Trends Panel wave, fielded November 2022, carrying a religious-tradition variable.",
    sponsor: "Pew Research Center",
    fielder: "Pew Research Center (American Trends Panel)",
    fieldedPeriod: "November 2022",
    description:
      "Wave 117 of Pew's American Trends Panel: 11,377 U.S. adults surveyed online " +
      "November 16–27, 2022, in English and Spanish. Like other ATP waves, it carries a " +
      "F_RELTRAD frame variable classifying each respondent's religious tradition " +
      "(Latter-day Saints coded 20000), which is what makes an otherwise general-topic " +
      "wave usable for breaking its questions out by religion. It underlies several 2023 " +
      "Pew reports on religious-service attendance, including \"How the Pandemic Has " +
      "Affected Attendance at U.S. Religious Services.\"",
    sourceUrl: "https://www.pewresearch.org/religion/2023/03/28/how-the-pandemic-has-affected-attendance-at-u-s-religious-services/",
    graphics: [
      inpersonAttendanceW117Graphic(),
      watchOnlineMonthlyGraphic(),
      nontechPrayerGroupsGraphic(),
      followsOwnLeadersGraphic(),
    ],
  },
  {
    slug: "pew-atp-w132-2023",
    name: "American Trends Panel, Wave 132 (August 2023)",
    shortDescription:
      "A general Pew American Trends Panel wave on spirituality, fielded August 2023.",
    sponsor: "Pew Research Center",
    fielder: "Pew Research Center (American Trends Panel)",
    fieldedPeriod: "August 2023",
    description:
      "Wave 132 of Pew's American Trends Panel: 11,201 U.S. adults surveyed online " +
      "July 31–Aug. 6, 2023, in English and Spanish. Unlike other ATP waves in this " +
      "collection, it carries no F_RELTRAD frame variable — religion is broken out " +
      "here using F_RELIG instead (Latter-day Saints/Mormons coded 3.0). Most of the " +
      "wave is a large battery of belief and experience items about spirituality, " +
      "likely feeding Pew's Dec. 2023 \"Spirituality Among Americans\" report.",
    sourceUrl: "https://www.pewresearch.org/religion/2023/12/07/spirituality-among-americans/",
    graphics: [beyondThisWorldGraphic(), religiousCommunityGraphic(), hasCrossGraphic()],
  },
  {
    slug: "pew-atp-w143-2024",
    name: "American Trends Panel, Wave 143 (February 2024)",
    shortDescription:
      "A Pew American Trends Panel wave on religion and politics, fielded February 2024.",
    sponsor: "Pew Research Center",
    fielder: "Pew Research Center (American Trends Panel)",
    fieldedPeriod: "February 2024",
    description:
      "Wave 143 of Pew's American Trends Panel: 12,693 U.S. adults surveyed online (a small " +
      "phone subsample), Feb. 13-25, 2024, in English and Spanish, with oversamples of Jewish " +
      "and Muslim Americans. Unlike most ATP waves in this collection, it does not carry the " +
      "usual F_RELTRAD frame variable; religious-tradition breakouts here instead use F_RELIG " +
      "(Latter-day Saints coded 3, \"Mormon\"). It fed a wide slate of 2024-25 Pew releases on " +
      "religion, politics, and the Israel-Hamas war.",
    sourceUrl: "https://www.pewresearch.org/our-methods/u-s-surveys/american-trends-panel/",
    graphics: [
      religiousMinorityGraphic(),
      w143FastsGraphic(),
      w143CandlesGraphic(),
      w143DiscrimMuslimsGraphic(),
      w143DiscrimJewsGraphic(),
      w143PresStrongBeliefsGraphic(),
      w143PresSameBeliefsGraphic(),
      w143AfterlifeGraphic(),
      w143AncestorSpiritsGraphic(),
      w143DiscrimBlackGraphic(),
      w143WearsReligiousItemsGraphic(),
    ],
  },
  {
    slug: "pew-atp-w162-2025",
    name: "American Trends Panel, Wave 162 (February 2025)",
    shortDescription:
      "A Pew American Trends Panel wave on Catholicism and religion's place in American life, fielded February 2025.",
    sponsor: "Pew Research Center",
    fielder: "Pew Research Center (American Trends Panel)",
    fieldedPeriod: "February 2025",
    description:
      "Wave 162 of Pew's American Trends Panel: 9,544 U.S. adults surveyed online and by phone " +
      "February 3–9, 2025, in English and Spanish. Focused mainly on Catholicism, plus general " +
      "religion and civic-trust items. Unlike most other ATP waves, it carries no F_RELTRAD " +
      "frame variable; its RELIG_W162 present-religion variable (code 3.0 = Mormon/LDS) is used " +
      "instead to break out Latter-day Saints. Fed Pew's October 2025 report on religion's " +
      "growing perceived influence in American life.",
    sourceUrl: "https://www.pewresearch.org/religion/2025/10/20/growing-share-of-us-adults-say-religion-is-gaining-influence-in-american-life/",
    graphics: [
      religiousConflictGraphic(),
      devotionToSaintsGraphic(),
      cathessentGraphic(),
      confessionFrequencyGraphic(),
      wearReligiousItemsGraphic(),
      w162AttendanceGraphic(),
    ],
  },
  {
    slug: "pew-10-country-religion-2007",
    name: "Spirit and Power: A 10-Country Survey of Pentecostals (2006)",
    shortDescription:
      "A cross-national Pew survey of Pentecostal and Charismatic (\"renewalist\") Christianity across ten countries, fielded 2006.",
    sponsor: "Pew Research Center",
    fielder: "Pew Research Center, Forum on Religion & Public Life",
    fieldedPeriod: "2006",
    description:
      "Pew Forum's cross-national study of \"renewalist\" Christianity — Pentecostals " +
      "and Charismatics — surveyed 11,028 respondents (7,475 general public plus a " +
      "renewalist oversample) across ten countries — Brazil, Chile, Guatemala, India, " +
      "Kenya, Nigeria, the Philippines, South Africa, South Korea, and the United " +
      "States — between May and September 2006. Covers religious belief, practice, " +
      "and Pentecostal/Charismatic identity, with a derived RENEWALIST variable " +
      "usable for cross-country comparison.",
    citation: "Pew Research Center, Forum on Religion & Public Life. 2006. \"Spirit and Power: A 10-Country Survey of Pentecostals.\"",
    sourceUrl: "https://www.pewresearch.org/religion/2006/10/05/spirit-and-power/",
    graphics: [renewalistShareGraphic()],
  },
  {
    slug: "pew-hispanics-religion-2007",
    name: "Pew Hispanic Center/Pew Forum Survey of Latinos (2006)",
    shortDescription:
      "A 2006 Pew survey of U.S. Latino adults focused on religious switching, with a small Mormon breakout.",
    sponsor: "Pew Research Center",
    fielder: "Pew Hispanic Center and Pew Forum on Religion & Public Life",
    fieldedPeriod: "2006",
    description:
      "A telephone survey of 4,016 U.S. Hispanic adults, conducted August 10-October 4, 2006, " +
      "in English and Spanish. It deliberately oversampled 2,000 non-Catholic respondents to " +
      "study religious switching among Latinos in detail, and underlies the report \"Changing " +
      "Faiths: Latinos and the Transformation of American Religion.\" Its recoded religion " +
      "variable carries an explicit Mormon category, with 34 unweighted respondents.",
    citation:
      "Pew Research Center (Pew Hispanic Center and Pew Forum on Religion & Public Life). " +
      "\"Changing Faiths: Latinos and the Transformation of American Religion,\" survey of 4,016 " +
      "U.S. Hispanic adults, fielded Aug. 10-Oct. 4, 2006.",
    sourceUrl: "https://www.pewresearch.org/race-and-ethnicity/2007/04/25/changing-faiths-latinos-and-the-transformation-of-american-religion/",
    graphics: [latinoReligiousConvertsGraphic()],
  },
];

/** Site-wide Data Explorer rule: every dataset's graphics gallery
 * (/data-explorer/[slug]/graphics) lists its charts in alphabetical order
 * by title, not in whatever order they were added to RAW_DATASETS above -
 * see BRANDING_AND_DESIGN.md's "Charts" section for the canonical
 * statement of the rule. Applying it once here, centrally, means a
 * dataset's own `graphics: [...]` array (or a helper like
 * `stateOfTheologyGraphics()` that builds one dynamically) never has to
 * get its entries hand-sorted or re-sorted when a new graphic is added -
 * whatever order is most convenient to write stays correct. `localeCompare`
 * with base sensitivity (case/accent-insensitive) matches how a reader
 * would alphabetize by eye. Leading punctuation is stripped before
 * comparing (not left to ICU's default collation) - straight quotes sort
 * as ignorable there, but curly/smart quotes (voter-survey-panel's one
 * “...”-quoted title) don't, and would otherwise sort before every plain
 * letter instead of alongside its neighbors. */
function sortGraphicsAlphabetically(graphics: Graphic[]): Graphic[] {
  const sortKey = (title: string) => title.replace(/^[^\p{L}\p{N}]+/u, "");
  return [...graphics].sort((a, b) =>
    sortKey(a.title).localeCompare(sortKey(b.title), "en", { sensitivity: "base" }),
  );
}

export const DATASETS: Dataset[] = RAW_DATASETS.map((d) => ({
  ...d,
  graphics: sortGraphicsAlphabetically(d.graphics),
}));

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

function tenLargestChurchesGraphic(): Graphic {
  const { denomination_order: order, denominations } = tenLargestChurchesData;
  const rows = [...order].sort(
    (a, b) => denominations[b as keyof typeof denominations].last_reported_members -
      denominations[a as keyof typeof denominations].last_reported_members,
  );
  const alt = rows
    .map((slug) => {
      const d = denominations[slug as keyof typeof denominations];
      const flag = d.confidence === "low" ? " (low-confidence sourcing)" : "";
      return `${d.name}: ${d.last_reported_members.toLocaleString()} in ${d.last_reported_year} ` +
        `-> ${d.projected_2035_members.toLocaleString()} projected in 2035 ` +
        `(${d.projected_pct_change > 0 ? "+" : ""}${d.projected_pct_change}%)${flag}`;
    })
    .join(", ");
  return {
    title: "Ten largest U.S.-rooted churches, projected to 2035",
    description:
      "Each denomination's own last-reported membership vs. a simple straight-line trend extended to 2035.",
    imageSrc: "/data-explorer/ten-largest-us-churches-2035/projected-2035.png",
    width: 1080, height: 1350,
    alt: `Log-scale dumbbell chart: ten denominations' last-reported U.S. membership (LDS Church figure is worldwide) ` +
      `vs. a linear-trend projection to 2035, largest to smallest. ${alt}. Neither projection is a forecast.`,
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

function coreBeliefsGraphic(): Graphic {
  const { item_order: order, believe_pct: results } = coreBeliefsData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "What do Mormons believe about Jesus and eternity?",
    description: "Share of Mormons who believe each of a set of core Christian/LDS belief items.",
    imageSrc: "/data-explorer/pew-mormon-survey-2011/core-beliefs.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of Mormons who believe core Christian/LDS belief items. ${alt}.`,
  };
}

function polygamyMoralityGraphic(): Graphic {
  const { item_order: order, polygamy_view_pct: results } = polygamyMoralityData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Do Mormons see polygamy as moral?",
    description: "Mormons' own view of polygamy - having more than one wife.",
    imageSrc: "/data-explorer/pew-mormon-survey-2011/polygamy-morality.png",
    width: 1080, height: 1350,
    alt: `Bar chart: Mormons' own view of polygamy's morality. ${alt}.`,
  };
}

function foodStorageByActivityGraphic(): Graphic {
  const { activity_order: order, keeps_food_storage_yes: results } = foodStorageByActivityData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Who keeps a food storage supply?",
    description: "Share of Mormons who keep a supply of food in storage for emergencies, by activity level.",
    imageSrc: "/data-explorer/pew-mormon-survey-2011/food-storage-by-activity.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of Mormons keeping a food storage supply, by activity level in the Church. ${alt}.`,
  };
}

function missionTitheByConvertGraphic(): Graphic {
  const { row_order: order, results } = missionTitheByConvertData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Converts vs. lifelong Mormons",
    description: "Share serving a full-time mission and paying a full tithe, by whether they converted or were raised Mormon.",
    imageSrc: "/data-explorer/pew-mormon-survey-2011/mission-and-tithe-by-convert.png",
    width: 1080, height: 1350,
    alt: `Bar chart: mission service and full-tithe payment among Mormons, by convert vs. lifelong status. ${alt}.`,
  };
}

function presidentReadinessGraphic(): Graphic {
  const { group_order: order, ready_for_mormon_president: results } = presidentReadinessData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Ready for a Mormon president?",
    description: "Share of Mormons saying Americans are ready to elect a Mormon president, by the Mormon respondent's own party.",
    imageSrc: "/data-explorer/pew-mormon-survey-2011/president-readiness-by-party.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of Mormons saying Americans are ready to elect a Mormon president, by the respondent's own party. ${alt}.`,
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

function overallScoreGraphic(): Graphic {
  const { group_order: order, results, n_items } = overallScoreData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].mean_correct}`)
    .join(", ");
  return {
    title: "Who scored best on the religious knowledge quiz?",
    description: `Average number correct out of ${n_items} questions, by the respondent's own religion.`,
    imageSrc: "/data-explorer/pew-religious-knowledge-2010/overall-score.png",
    width: 1080, height: 1350,
    alt: `Bar chart: average number correct out of ${n_items} religious knowledge questions, by respondent's own religion. ${alt}.`,
  };
}

function churchStateLawGraphic(): Graphic {
  const { item_order: order, correct_pct: results } = churchStateLawData;
  const alt = order
    .map((r) => `${r} ${results[r as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "What can public school teachers do?",
    description: "Share correctly identifying whether the Constitution permits each action in a public school classroom.",
    imageSrc: "/data-explorer/pew-religious-knowledge-2010/church-state-law.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share correctly identifying whether the Constitution permits each classroom action. ${alt}.`,
  };
}

function jesusBirthplaceKnowledgeGraphic(): Graphic {
  const { group_order: order, correct_pct: results } = jesusBirthplaceKnowledgeData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Who knows where Jesus was born?",
    description: "Share correctly saying Bethlehem, by the respondent's own religion.",
    imageSrc: "/data-explorer/pew-religious-knowledge-2010/jesus-birthplace-knowledge.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share correctly saying the Bible places Jesus's birth in Bethlehem, by respondent's own religion. ${alt}.`,
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

function retentionRateGraphic(): Graphic {
  const { group_order: order, retained_pct: results } = retentionRateData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Who stays in the religion they were raised in?",
    description: "Share raised in each tradition who still identify with that same tradition as adults.",
    imageSrc: "/data-explorer/pew-rls-2007/retention-rate.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share raised in each tradition who still identify with it as adults, 2007. ${alt}.`,
  };
}

function ldsShareByRegionGraphic(): Graphic {
  const { region_order: order, share_of_mormons: results } = ldsShareByRegionData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Where do Mormons live?",
    description: "Share of U.S. Mormons living in each Census region, 2007.",
    imageSrc: "/data-explorer/pew-rls-2007/lds-share-by-region.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of U.S. Mormons living in each Census region, 2007. ${alt}.`,
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

function millennialShareGraphic(): Graphic {
  const { group_order: order, millennial_pct: results } = millennialShareData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Which traditions skew young?",
    description: "Share born 1981-1996 (Millennials), by religious tradition, 2014.",
    imageSrc: "/data-explorer/pew-rls-2014/millennial-share.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of Millennials, by religious tradition, 2014. ${alt}.`,
  };
}

function nonesGrowthGraphic(): Graphic {
  const { wave_order: order, unaffiliated_pct: results } = nonesGrowthData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "The rise of the \"nones\"",
    description: "Religiously unaffiliated share of U.S. adults, 2007 vs. 2014.",
    imageSrc: "/data-explorer/pew-rls-2014/nones-growth-2007-2014.png",
    width: 1080, height: 1350,
    alt: `Bar chart: religiously unaffiliated share of U.S. adults, 2007 vs. 2014. ${alt}.`,
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

function attendWithSpouseGraphic(): Graphic {
  const { group_order: order, attend_with_spouse: results } = attendWithSpouseData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Do you attend with your spouse?",
    description: "Share who typically attend religious services with their spouse or partner, by current tradition.",
    imageSrc: "/data-explorer/pew-rls-2014-recontact/attend-with-spouse.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share who typically attend religious services with their spouse, by current tradition. ${alt}.`,
  };
}

function spouseReligiousDisagreementGraphic(): Graphic {
  const { group_order: order, disagree_a_lot: results } = spouseReligiousDisagreementData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Do you and your spouse disagree about religion?",
    description: "Share saying they disagree with their spouse or partner about religion a lot, by current tradition.",
    imageSrc: "/data-explorer/pew-rls-2014-recontact/spouse-religious-disagreement.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share saying they disagree with their spouse about religion a lot, by current tradition. ${alt}.`,
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

function transubstantiationGraphic(): Graphic {
  const { group_order: order, believe_transubstantiation: results } = transubstantiationData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Do the bread and wine become Christ's body?",
    description: "Share across Latin America who believe that in communion, the bread and wine actually become the body and blood of Christ, by their own religion.",
    imageSrc: "/data-explorer/pew-latin-america-2014/transubstantiation.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share believing the bread and wine become Christ's body and blood in communion, by respondent's own religion, across Latin America. ${alt}.`,
  };
}

function latinAmericaWeeklyAttendanceGraphic(): Graphic {
  const { group_order: order, attend_weekly: results } = latinAmericaWeeklyAttendanceData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Who attends religious services weekly?",
    description: "Share across Latin America attending religious services once a week or more, by their own religion.",
    imageSrc: "/data-explorer/pew-latin-america-2014/weekly-attendance.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share across Latin America attending religious services weekly or more, by their own religion. ${alt}.`,
  };
}

function latinAmericaReligionImportanceGraphic(): Graphic {
  const { group_order: order, religion_very_important: results } = latinAmericaReligionImportanceData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "How important is religion?",
    description: "Share across Latin America saying religion is very important in their life, by their own religion.",
    imageSrc: "/data-explorer/pew-latin-america-2014/religion-importance.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share across Latin America saying religion is very important in their life, by their own religion. ${alt}.`,
  };
}

function latinAmericaSamesexMarriageGraphic(): Graphic {
  const { group_order: order, favor_samesex_marriage: results } = latinAmericaSamesexMarriageData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Support for same-sex marriage",
    description: "Share across Latin America favoring same-sex marriage, by their own religion.",
    imageSrc: "/data-explorer/pew-latin-america-2014/samesex-marriage.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share across Latin America favoring same-sex marriage, by their own religion. ${alt}.`,
  };
}

function witchcraftBeliefGraphic(): Graphic {
  const { group_order: order, believe_witchcraft: results } = witchcraftBeliefData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Belief in witchcraft",
    description: "Share across Latin America believing magic, sorcery, or witchcraft can influence people's lives, by their own religion.",
    imageSrc: "/data-explorer/pew-latin-america-2014/witchcraft-belief.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share across Latin America believing magic, sorcery, or witchcraft can influence people's lives, by their own religion. ${alt}.`,
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

function reasonsLeftReligionGraphic(): Graphic {
  const { reason_order: order, important_reason_pct: results } = reasonsLeftReligionData;
  const alt = order
    .map((r) => `${r} ${results[r as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Why do people leave their childhood religion?",
    description: "Share of religious switchers calling each factor an important reason they left the religion they grew up in.",
    imageSrc: "/data-explorer/pew-faith-in-flux-2008/reasons-left-religion.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of religious switchers calling each factor an important reason for leaving. ${alt}.`,
  };
}

function leaveVsJoinGraphic(): Graphic {
  const { motive_order: order, motive_pct: results } = leaveVsJoinData;
  const alt = order
    .map((r) => `${r} ${results[r as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Leaving, or joining?",
    description: "When people changed religion, was it driven more by wanting to leave the old one, or join the new one?",
    imageSrc: "/data-explorer/pew-faith-in-flux-2008/leave-vs-join.png",
    width: 1080, height: 1350,
    alt: `Bar chart: whether changing religion was driven more by wanting to leave the old religion or join the new one. ${alt}.`,
  };
}

function leavingDecisionMakerGraphic(): Graphic {
  const { decision_order: order, decision_pct: results } = leavingDecisionMakerData;
  const alt = order
    .map((r) => `${r} ${results[r as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Whose decision was it to leave?",
    description: "Among people who left their childhood religion, who mainly made that decision?",
    imageSrc: "/data-explorer/pew-faith-in-flux-2008/leaving-decision-maker.png",
    width: 1080, height: 1350,
    alt: `Bar chart: who mainly decided to leave the childhood religion, among religious switchers. ${alt}.`,
  };
}

function faithStrengthBeforeAfterGraphic(): Graphic {
  const { time_order: order, strong_faith_pct: results } = faithStrengthBeforeAfterData;
  const alt = order
    .map((r) => `${r} ${results[r as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Did switching strengthen their faith?",
    description: "Share of religious switchers with strong faith, as a teenager vs. now.",
    imageSrc: "/data-explorer/pew-faith-in-flux-2008/faith-strength-before-after.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of religious switchers with strong faith, as a teenager vs. now. ${alt}.`,
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

function prayerCovidCopingGraphic(): Graphic {
  const { group_order: order, prayed_daily_covid: results } = prayerCovidCopingData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Praying to cope with COVID",
    description: "Share who prayed daily to help cope with the coronavirus outbreak, by religious tradition, July 2020.",
    imageSrc: "/data-explorer/pew-atp-w70-2020/prayer-covid-coping.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share praying daily to cope with the coronavirus outbreak, by religious tradition, July 2020. ${alt}.`,
  };
}

function inpersonAttendanceCovidGraphic(): Graphic {
  const { group_order: order, attended_inperson_covid: results } = inpersonAttendanceCovidData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Who kept attending in person?",
    description: "Share who attended religious services in person in the past month, by religious tradition, July 2020.",
    imageSrc: "/data-explorer/pew-atp-w70-2020/inperson-attendance-covid.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share attending religious services in person in the past month, by religious tradition, July 2020. ${alt}.`,
  };
}

function financialThreatCovidGraphic(): Graphic {
  const { group_order: order, major_financial_threat: results } = financialThreatCovidData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "COVID as a financial threat",
    description: "Share calling the coronavirus outbreak a major threat to their personal finances, by religious tradition, July 2020.",
    imageSrc: "/data-explorer/pew-atp-w70-2020/financial-threat-covid.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share calling COVID a major threat to their personal finances, by religious tradition, July 2020. ${alt}.`,
  };
}

function blmSermonsGraphic(): Graphic {
  const { group_order: order, heard_blm_support_sermon: results } = blmSermonsData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Hearing BLM support from the pulpit",
    description: "Share who heard a sermon expressing support for the Black Lives Matter protests, by religious tradition, July 2020.",
    imageSrc: "/data-explorer/pew-atp-w70-2020/blm-sermons.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of monthly attenders hearing a pro-Black Lives Matter sermon, by religious tradition, July 2020. ${alt}.`,
  };
}

/** Formats a {pct} results record (insertion order) into alt text for the
 * five household-types graphics below. */
function householdTypeAlt(results: Record<string, { pct: number }>): string {
  return Object.entries(results).map(([g, r]) => `${g} ${r.pct.toFixed(0)}%`).join(", ");
}

function raisedByMarriedParentsGraphic(): Graphic {
  const results = householdTypesData.raised_by_married_mother_father;
  return {
    title: "Raised by a married mother and father?",
    description: "Share saying this is as good an arrangement for raising children as any other, by religion, 2015.",
    imageSrc: "/data-explorer/pew-catholic-family-2015/raised-by-married-mother-father.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share saying a married mother and father is as good an arrangement as any other, by religion, 2015. ${householdTypeAlt(results)}.`,
  };
}

function raisedBySingleParentGraphic(): Graphic {
  const results = householdTypesData.raised_by_single_parent;
  return {
    title: "Raised by a single parent?",
    description: "Share saying this is as good an arrangement for raising children as any other, by religion, 2015.",
    imageSrc: "/data-explorer/pew-catholic-family-2015/raised-by-single-parent.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share saying a single parent is as good an arrangement as any other, by religion, 2015. ${householdTypeAlt(results)}.`,
  };
}

function raisedByDivorcedParentsGraphic(): Graphic {
  const results = householdTypesData.raised_by_divorced_parents;
  return {
    title: "Raised by divorced parents?",
    description: "Share saying this is as good an arrangement for raising children as any other, by religion, 2015.",
    imageSrc: "/data-explorer/pew-catholic-family-2015/raised-by-divorced-parents.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share saying divorced parents is as good an arrangement as any other, by religion, 2015. ${householdTypeAlt(results)}.`,
  };
}

function raisedByCohabitingParentsGraphic(): Graphic {
  const results = householdTypesData.raised_by_cohabiting_unmarried_parents;
  return {
    title: "Raised by unmarried parents living together?",
    description: "Share saying this is as good an arrangement for raising children as any other, by religion, 2015.",
    imageSrc: "/data-explorer/pew-catholic-family-2015/raised-by-cohabiting-unmarried-parents.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share saying unmarried cohabiting parents is as good an arrangement as any other, by religion, 2015. ${householdTypeAlt(results)}.`,
  };
}

function raisedByGayLesbianCoupleGraphic(): Graphic {
  const results = householdTypesData.raised_by_gay_lesbian_couple;
  return {
    title: "Raised by a gay or lesbian couple?",
    description: "Share saying this is as good an arrangement for raising children as any other, by religion, 2015.",
    imageSrc: "/data-explorer/pew-catholic-family-2015/raised-by-gay-lesbian-couple.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share saying a gay or lesbian couple is as good an arrangement as any other, by religion, 2015. ${householdTypeAlt(results)}.`,
  };
}

function annulmentCommunionGraphic(): Graphic {
  const { group_order: order, should_allow_communion_after_remarriage: results } = annulmentCommunionData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Communion after remarriage, no annulment",
    description: "Share of U.S. Catholics saying the Church should let divorced Catholics who remarry without an annulment take Communion, by Mass attendance, 2015.",
    imageSrc: "/data-explorer/pew-catholic-family-2015/annulment-communion.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of U.S. Catholics saying the Church should let divorced Catholics who remarry without an annulment receive Communion, by Mass attendance frequency, 2015. ${alt}.`,
  };
}

function charismaticChristiansGraphic(): Graphic {
  const { group_order: order, charismatic_christian_share: results } = charismaticChristiansData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Charismatic Christianity across Sub-Saharan Africa",
    description: "Share of Christians who describe themselves as a Charismatic Christian, by country, top 12 of 18, 2008-09.",
    imageSrc: "/data-explorer/pew-subsaharan-africa-2010/charismatic-christians.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of Christians describing themselves as a Charismatic Christian, by country, top 12 of 18, 2008-09. ${alt}.`,
  };
}

function womenLeadersGraphic(): Graphic {
  const { group_order: order, women_should_lead: results } = womenLeadersData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Should women lead congregations?",
    description: "Share of Black Americans saying women should be allowed to serve as a congregation's senior religious leader, by religion.",
    imageSrc: "/data-explorer/pew-black-faith-2021/women-leaders.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of Black Americans saying women should be allowed to serve as a congregation's senior religious leader, by religion. ${alt}.`,
  };
}

function religiousNationalIdentityGraphic(): Graphic {
  const { group_order: order, important_to_share_dominant_faith: results } = religiousNationalIdentityData;
  const alt = order
    .map((c) => `${c} ${results[c as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Being Orthodox (or Catholic) and belonging",
    description:
      "Share saying it's \"very important\" to belong to their country's own dominant Christian tradition to be truly a citizen, 6 highest- and 6 lowest-ranked of 18 Central/Eastern European countries surveyed, 2015-16.",
    imageSrc: "/data-explorer/pew-eastern-europe-2015/religious-national-identity.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share saying it's very important to belong to their country's dominant Christian tradition to be truly a citizen, 6 highest and 6 lowest of 18 countries surveyed, 2015-2016. ${alt}.`,
  };
}

function pewGlobalRestrictionsGriGraphic(): Graphic {
  const { year_order: years, series } = pewGlobalRestrictionsGriData;
  const milestones = [years[0], 2010, 2015, years[years.length - 1]];
  const alt = milestones
    .map((y) => `${y}: ${series[String(y) as keyof typeof series].median_gri.toFixed(2)}`)
    .join(", ");
  return {
    title: "Government restrictions on religion, worldwide",
    description: "The global median score on Pew's 0-10 Government Restrictions Index climbed from 1.76 in 2007 to a peak of 3.00 in 2021-2022.",
    imageSrc: "/data-explorer/pew-global-restrictions-religion/gri-trend.png",
    width: 1080, height: 1350,
    alt: `Line chart: global median Government Restrictions Index (GRI) score, 0-10 scale, by year, 2007-2022. Selected years - ${alt}.`,
  };
}

function christianNeighborAcceptanceGraphic(): Graphic {
  const { group_order: order, accept_christian_neighbor: results } = christianNeighborAcceptanceData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Would you accept a Christian neighbor?",
    description: "Share of India's other major religious communities willing to accept a Christian as a neighbor, by the respondent's own religion, 2019-2020.",
    imageSrc: "/data-explorer/pew-india-2021/christian-neighbor-acceptance.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share willing to accept a Christian neighbor, by respondent's own religion, India 2019-2020. ${alt}.`,
  };
}

function paysChurchTaxGraphic(): Graphic {
  const { group_order: order, pays_church_tax: results } = paysChurchTaxData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Who still pays the church tax",
    description: "Share of adults who currently pay their country's church tax, among the 9 Western European countries where it exists, 2017.",
    imageSrc: "/data-explorer/pew-church-tax-western-europe/pays-church-tax.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share who currently pay their country's church tax, by country, 2017. ${alt}.`,
  };
}

function christianShareDeclineGraphic(): Graphic {
  const { group_order: order, christian_share_decline_pp: results } = christianShareDeclineData;
  const alt = order
    .map((c) => `${c} ${results[c as keyof typeof results].decline_pp}pp`)
    .join(", ");
  return {
    title: "Where the Christian share fell the most",
    description: "The ten countries and territories where the Christian share of population fell the most, 2010 to 2020.",
    imageSrc: "/data-explorer/pew-religious-composition-2010-2020/christian-share-decline.png",
    width: 1080, height: 1350,
    alt: `Bar chart: percentage-point decline in the Christian share of population, 2010 to 2020, ten largest declines worldwide. ${alt}.`,
  };
}

function globalMigrantCompositionGraphic(): Graphic {
  const { group_order: order, global_composition: results } = globalMigrantCompositionData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "The world's migrants, by religion",
    description: "Religious composition of the world's ~281 million international migrants, 2020.",
    imageSrc: "/data-explorer/pew-religion-migration/global-migrant-composition.png",
    width: 1080, height: 1350,
    alt: `Bar chart: religious composition of the world's ~281 million international migrants, 2020. ${alt}.`,
  };
}

function christianNationGraphic(): Graphic {
  const { group_order: order, should_be_christian_nation: results } = christianNationData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Should the U.S. be a Christian nation?",
    description: "Share saying yes, by religious affiliation, September 2022.",
    imageSrc: "/data-explorer/pew-atp-w114-2022/christian-nation.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share saying the U.S. should be a Christian nation, by religious affiliation, September 2022. ${alt}.`,
  };
}

function essentJesusGraphic(): Graphic {
  const { group_order: order, personal_relationship_jesus_essential: results } = essentJesusData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "A personal relationship with Jesus Christ",
    description: "Share of Christians saying this is essential to what being faithful to their tradition means, September 2022.",
    imageSrc: "/data-explorer/pew-atp-w114-2022/essent-jesus.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of Christians saying a personal relationship with Jesus Christ is essential to their faith, by tradition, September 2022. ${alt}.`,
  };
}

function essentAttendGraphic(): Graphic {
  const { group_order: order, attend_services_essential: results } = essentAttendData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Is attending services essential to your faith?",
    description: "Share saying regular religious attendance is essential to what being faithful to their tradition means, September 2022.",
    imageSrc: "/data-explorer/pew-atp-w114-2022/essent-attend.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share saying regular religious attendance is essential to their faith, by tradition, September 2022. ${alt}.`,
  };
}

function relfavMormonsGraphic(): Graphic {
  const { group_order: order, favorable_toward_mormons: results } = relfavMormonsData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "How favorably do Americans view Mormons?",
    description: "Share with a favorable view of Mormons, by the respondent's own religion, September 2022.",
    imageSrc: "/data-explorer/pew-atp-w114-2022/relfav-mormons.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share with a favorable view of Mormons, by the respondent's own religion, September 2022. ${alt}.`,
  };
}

function inpersonAttendanceW117Graphic(): Graphic {
  const { group_order: order, attended_in_person: results } = inpersonAttendanceW117Data;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Who's back in the pews",
    description: "Share who attended religious services in person in the past month, by religious tradition, November 2022.",
    imageSrc: "/data-explorer/pew-atp-w117-2022/inperson-attendance.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share attending religious services in person in the past month, by religious tradition, November 2022. ${alt}.`,
  };
}

function nontechPrayerGroupsGraphic(): Graphic {
  const { group_order: order, participates_in_person_study_group: results } = nontechPrayerGroupsData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Prayer groups and scripture study",
    description: "Share who participate in in-person prayer groups, scripture study groups, or religious education programs, by religious tradition, November 2022.",
    imageSrc: "/data-explorer/pew-atp-w117-2022/nontech-prayer-groups.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share who participate in in-person prayer groups, scripture study groups, or religious education programs, by religious tradition, November 2022. ${alt}.`,
  };
}

function watchOnlineMonthlyGraphic(): Graphic {
  const { group_order: order, watches_online_monthly: results } = watchOnlineMonthlyData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Watching church online",
    description: "Share who watch religious services online or on TV at least monthly, by religious tradition, November 2022.",
    imageSrc: "/data-explorer/pew-atp-w117-2022/watch-online-monthly.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share who watch religious services online or on TV at least monthly, by religious tradition, November 2022. ${alt}.`,
  };
}

function followsOwnLeadersGraphic(): Graphic {
  const { group_order: order, follows_own_religious_leaders: results } = followsOwnLeadersData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Following their own religious leaders",
    description: "Among social media users, share who follow or keep track of their own religious leaders online or on social media, by religious tradition, November 2022.",
    imageSrc: "/data-explorer/pew-atp-w117-2022/follows-own-leaders.png",
    width: 1080, height: 1350,
    alt: `Bar chart: among social media users, share who follow or keep track of their own religious leaders online or on social media, by religious tradition, November 2022. ${alt}.`,
  };
}

function beyondThisWorldGraphic(): Graphic {
  const { group_order: order, felt_beyond_this_world_connection: results } = beyondThisWorldData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "A feeling of connection beyond this world",
    description: "Share who have ever had a sudden or unexpected feeling of connection with something from beyond this world, by religion, 2023.",
    imageSrc: "/data-explorer/pew-atp-w132-2023/beyond-this-world.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share who have ever had a sudden or unexpected feeling of connection with something from beyond this world, by religion, 2023. ${alt}.`,
  };
}

function hasCrossGraphic(): Graphic {
  const { group_order: order, has_cross_for_spiritual_purposes: results } = hasCrossData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Do you have a cross for spiritual purposes?",
    description: "Share who have a cross \"for spiritual purposes,\" by religion, 2023.",
    imageSrc: "/data-explorer/pew-atp-w132-2023/has-cross.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share who have a cross for spiritual purposes, by religion, 2023. ${alt}.`,
  };
}

function religiousCommunityGraphic(): Graphic {
  const { group_order: order, involved_in_religious_community: results } = religiousCommunityData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Involved in a religious community",
    description: "Share involved in \"a religious community, such as a church or religious congregation,\" by religion, 2023.",
    imageSrc: "/data-explorer/pew-atp-w132-2023/religious-community.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share involved in a religious community, by religion, 2023. ${alt}.`,
  };
}

/** Formats a {pct} results record (insertion order) into alt text for the
 * four W143 holiday-batch graphics below. */
function w143BatchAlt(results: Record<string, { pct: number }>): string {
  return Object.entries(results).map(([g, r]) => `${g} ${r.pct.toFixed(0)}%`).join(", ");
}

function w143FastsGraphic(): Graphic {
  const results = w143HolidayBatchData.fasts_for_holy_times;
  return {
    title: "Who fasts for holy times?",
    description: "Share who fast for certain periods during holy times, by religion, February 2024.",
    imageSrc: "/data-explorer/pew-atp-w143-2024/fasts-for-holy-times.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share who fast for holy times, by religion, February 2024. ${w143BatchAlt(results)}.`,
  };
}

function w143CandlesGraphic(): Graphic {
  const results = w143HolidayBatchData.lights_candles_incense;
  return {
    title: "Who lights candles or incense?",
    description: "Share who light incense or candles for spiritual or religious reasons, by religion, February 2024.",
    imageSrc: "/data-explorer/pew-atp-w143-2024/lights-candles-incense.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share who light candles or incense for spiritual/religious reasons, by religion, February 2024. ${w143BatchAlt(results)}.`,
  };
}

function w143DiscrimMuslimsGraphic(): Graphic {
  const results = w143HolidayBatchData.discrimination_against_muslims;
  return {
    title: "Discrimination against Muslims?",
    description: "Share saying Muslims face \"a lot\" of discrimination in society today, by religion, February 2024.",
    imageSrc: "/data-explorer/pew-atp-w143-2024/discrimination-against-muslims.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share saying Muslims face a lot of discrimination today, by religion, February 2024. ${w143BatchAlt(results)}.`,
  };
}

function w143DiscrimJewsGraphic(): Graphic {
  const results = w143HolidayBatchData.discrimination_against_jews;
  return {
    title: "Discrimination against Jewish Americans?",
    description: "Share saying Jewish people face \"a lot\" of discrimination in society today, by religion, February 2024.",
    imageSrc: "/data-explorer/pew-atp-w143-2024/discrimination-against-jews.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share saying Jewish people face a lot of discrimination today, by religion, February 2024. ${w143BatchAlt(results)}.`,
  };
}

function w143PresStrongBeliefsGraphic(): Graphic {
  const results = w143HolidayBatch2Data.president_strong_beliefs_important;
  return {
    title: "Want a president with strong religious beliefs?",
    description: "Share saying it's very important to have a president with strong religious beliefs, even if different from their own, by religion, February 2024.",
    imageSrc: "/data-explorer/pew-atp-w143-2024/president-strong-beliefs.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share saying it's very important to have a president with strong religious beliefs, by religion, February 2024. ${w143BatchAlt(results)}.`,
  };
}

function w143PresSameBeliefsGraphic(): Graphic {
  const results = w143HolidayBatch2Data.president_same_beliefs_important;
  return {
    title: "Want a president who shares your beliefs?",
    description: "Share saying it's very important to have a president whose religious beliefs are the same as their own, by religion, February 2024.",
    imageSrc: "/data-explorer/pew-atp-w143-2024/president-same-beliefs.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share saying it's very important to have a president who shares their own religious beliefs, by religion, February 2024. ${w143BatchAlt(results)}.`,
  };
}

function w143AfterlifeGraphic(): Graphic {
  const results = w143HolidayBatch2Data.definitely_life_after_death;
  return {
    title: "Is there definitely life after death?",
    description: "Share saying there is definitely life after death, by religion, February 2024.",
    imageSrc: "/data-explorer/pew-atp-w143-2024/definitely-life-after-death.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share saying there is definitely life after death, by religion, February 2024. ${w143BatchAlt(results)}.`,
  };
}

function w143AncestorSpiritsGraphic(): Graphic {
  const results = w143HolidayBatch2Data.believe_ancestor_spirits;
  return {
    title: "Can ancestors' spirits help or harm you?",
    description: "Share who believe the spirits of ancestors can help or harm them, by religion, February 2024.",
    imageSrc: "/data-explorer/pew-atp-w143-2024/believe-ancestor-spirits.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share who believe ancestors' spirits can help or harm them, by religion, February 2024. ${w143BatchAlt(results)}.`,
  };
}

function w143DiscrimBlackGraphic(): Graphic {
  const results = w143HolidayBatch3Data.discrimination_against_black_americans;
  return {
    title: "Discrimination against Black Americans?",
    description: "Share saying Black people face \"a lot\" of discrimination in society today, by religion, February 2024.",
    imageSrc: "/data-explorer/pew-atp-w143-2024/discrimination-against-black-americans.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share saying Black Americans face a lot of discrimination today, by religion, February 2024. ${w143BatchAlt(results)}.`,
  };
}

function w143WearsReligiousItemsGraphic(): Graphic {
  const results = w143HolidayBatch3Data.wears_religious_items;
  return {
    title: "Who wears religious items or symbols?",
    description: "Share who wear or carry religious items or symbols, by religion, February 2024.",
    imageSrc: "/data-explorer/pew-atp-w143-2024/wears-religious-items.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share who wear or carry religious items or symbols, by religion, February 2024. ${w143BatchAlt(results)}.`,
  };
}

function confessionFrequencyGraphic(): Graphic {
  const { item_order: order, confession_frequency_pct: results } = confessionFrequencyData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "How often do Catholics go to confession?",
    description: "Share of Catholics saying how often they go to confession with a priest, February 2025.",
    imageSrc: "/data-explorer/pew-atp-w162-2025/confession-frequency.png",
    width: 1080, height: 1350,
    alt: `Bar chart: how often Catholics go to confession, February 2025. ${alt}.`,
  };
}

/** Formats a {pct} results record (insertion order) into alt text for the
 * five W44 knowledge-quiz graphics below. */
function w44BatchAlt(results: Record<string, { pct: number }>): string {
  return Object.entries(results).map(([g, r]) => `${g} ${r.pct.toFixed(0)}%`).join(", ");
}

function w44ConstitutionGraphic(): Graphic {
  const results = w44KnowledgeBatchData.knows_constitution_no_religious_test;
  return {
    title: "What does the Constitution say about religion?",
    description: "Share correctly saying the Constitution requires no religious test for federal officeholders, by religion, February 2019.",
    imageSrc: "/data-explorer/pew-atp-w44-2018/knows-constitution-no-religious-test.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share correctly identifying the Constitution's no-religious-test clause, by religion, February 2019. ${w44BatchAlt(results)}.`,
  };
}

function w44EasterGraphic(): Graphic {
  const results = w44KnowledgeBatchData.knows_easter_is_resurrection;
  return {
    title: "What's commemorated on Easter Sunday?",
    description: "Share correctly identifying the Resurrection of Jesus, by religion, February 2019.",
    imageSrc: "/data-explorer/pew-atp-w44-2018/knows-easter-is-resurrection.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share correctly identifying the Resurrection as what Easter commemorates, by religion, February 2019. ${w44BatchAlt(results)}.`,
  };
}

function w44RamadanGraphic(): Graphic {
  const results = w44KnowledgeBatchData.knows_ramadan_is_islamic;
  return {
    title: "What is Ramadan?",
    description: "Share correctly identifying Ramadan as an Islamic holy month, by religion, February 2019.",
    imageSrc: "/data-explorer/pew-atp-w44-2018/knows-ramadan-is-islamic.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share correctly identifying Ramadan as an Islamic holy month, by religion, February 2019. ${w44BatchAlt(results)}.`,
  };
}

function w44RoshHashanaGraphic(): Graphic {
  const results = w44KnowledgeBatchData.knows_rosh_hashana_is_new_year;
  return {
    title: "What is Rosh Hashana?",
    description: "Share correctly identifying Rosh Hashana as the Jewish New Year, by religion, February 2019.",
    imageSrc: "/data-explorer/pew-atp-w44-2018/knows-rosh-hashana-is-new-year.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share correctly identifying Rosh Hashana as the Jewish New Year, by religion, February 2019. ${w44BatchAlt(results)}.`,
  };
}

function w44MeccaGraphic(): Graphic {
  const results = w44KnowledgeBatchData.knows_mecca_is_pilgrimage_city;
  return {
    title: "Where do Muslims make a pilgrimage?",
    description: "Share correctly identifying Mecca as Islam's pilgrimage city, by religion, February 2019.",
    imageSrc: "/data-explorer/pew-atp-w44-2018/knows-mecca-is-pilgrimage-city.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share correctly identifying Mecca as Islam's pilgrimage city, by religion, February 2019. ${w44BatchAlt(results)}.`,
  };
}

function w44FaithAloneGraphic(): Graphic {
  const results = w44KnowledgeBatchData.knows_protestantism_teaches_faith_alone;
  return {
    title: "Which tradition teaches salvation by faith alone?",
    description: "Share correctly identifying Protestantism as the tradition teaching salvation through faith alone, by religion, February 2019.",
    imageSrc: "/data-explorer/pew-atp-w44-2018/knows-protestantism-faith-alone.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share correctly identifying Protestantism as teaching salvation by faith alone, by religion, February 2019. ${w44BatchAlt(results)}.`,
  };
}

function w44WarmthGraphic(): Graphic {
  const results = w44WarmthData.warmth_toward_mormons;
  const alt = Object.entries(results).map(([g, r]) => `${g} ${r.mean}/100`).join(", ");
  return {
    title: "How warmly do Americans feel toward Mormons?",
    description: "Mean feeling-thermometer rating toward Mormons (0=coldest, 100=warmest), by the rater's own religion, February 2019.",
    imageSrc: "/data-explorer/pew-atp-w44-2018/warmth-toward-mormons.png",
    width: 1080, height: 1350,
    alt: `Bar chart: mean feeling-thermometer rating toward Mormons, by rater's own religion, February 2019. ${alt}.`,
  };
}

function communionBeliefGraphic(): Graphic {
  const { item_order: order, belief_pct: results } = communionBeliefData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Do Catholics believe in transubstantiation?",
    description: "What U.S. Catholics personally believe about the bread and wine used for Communion, February 2019.",
    imageSrc: "/data-explorer/pew-atp-w44-2018/communion-belief.png",
    width: 1080, height: 1350,
    alt: `Bar chart: what U.S. Catholics personally believe about Communion bread and wine, February 2019. ${alt}.`,
  };
}

function religiousMinorityGraphic(): Graphic {
  const { group_order: order, religious_minority: results } = religiousMinorityData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Feeling like a religious minority",
    description: "Share who consider themselves part of a minority group because of their religious beliefs, by religion, February 2024.",
    imageSrc: "/data-explorer/pew-atp-w143-2024/religious-minority.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share considering themselves part of a religious minority, by religion, February 2024. ${alt}.`,
  };
}

function religiousConflictGraphic(): Graphic {
  const { group_order: order, religious_belief_conflict: results } = religiousConflictData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Feeling out of step with mainstream culture",
    description: "Share who feel at least some conflict between their own religious beliefs and mainstream American culture, by present religion, February 2025.",
    imageSrc: "/data-explorer/pew-atp-w162-2025/religious-conflict.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share feeling at least some conflict between their own religious beliefs and mainstream American culture, by present religion, February 2025. ${alt}.`,
  };
}

function wearReligiousItemsGraphic(): Graphic {
  const { group_order: order, wear_religious_items_weekly_plus: results } = wearReligiousItemsData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Wearing your faith",
    description: "Share who wear religious items or symbols, or carry them with them, daily or weekly, by present religion, February 2025.",
    imageSrc: "/data-explorer/pew-atp-w162-2025/wear-religious-items.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share who wear religious items or symbols, or carry them with them, daily or weekly, by present religion, February 2025. ${alt}.`,
  };
}

function w162AttendanceGraphic(): Graphic {
  const { group_order: order, attend_weekly_plus: results } = w162AttendanceData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "How often Americans attend services",
    description: "Share attending religious services in person at least weekly, by present religion, February 2025.",
    imageSrc: "/data-explorer/pew-atp-w162-2025/attendance.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share attending religious services in person at least weekly, by present religion, February 2025. ${alt}.`,
  };
}

function cathessentGraphic(): Graphic {
  const { item_order: order, essential_pct: results } = cathessentData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "What's essential to being Catholic?",
    description: "Share of Catholics calling each item essential to what being Catholic means to them, February 2025.",
    imageSrc: "/data-explorer/pew-atp-w162-2025/cathessent.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of Catholics calling each item essential to being Catholic, February 2025. ${alt}.`,
  };
}

function devotionToSaintsGraphic(): Graphic {
  const results = w162HolidayBatchData.devotion_to_saints_weekly_plus;
  const alt = Object.entries(results).map(([g, r]) => `${g} ${r.pct.toFixed(0)}%`).join(", ");
  return {
    title: "Who practices devotion to saints?",
    description: "Share practicing devotion to the Virgin Mary or a favorite saint at least weekly, by religion, February 2025.",
    imageSrc: "/data-explorer/pew-atp-w162-2025/devotion-to-saints.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share practicing devotion to the Virgin Mary or a favorite saint at least weekly, by religion, February 2025. ${alt}.`,
  };
}

function renewalistShareGraphic(): Graphic {
  const { group_order: order, renewalist_share: results } = renewalistShareData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "How renewalist is each country?",
    description: "Share of the general public who are Pentecostal or Charismatic Christians, by country, 2006.",
    imageSrc: "/data-explorer/pew-10-country-religion-2007/renewalist-share.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of the general public who are Pentecostal or Charismatic Christians, by country, 2006. ${alt}.`,
  };
}

function latinoReligiousConvertsGraphic(): Graphic {
  const { group_order: order, converted_to_current_religion: results } = latinoReligiousConvertsData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Latino converts to their faith",
    description: "Share of U.S. Latino adults who converted to their current religion, rather than being raised in it, by religious group, 2006.",
    imageSrc: "/data-explorer/pew-hispanics-religion-2007/latino-religious-converts.png",
    width: 1080, height: 1350,
    alt: `Bar chart: share of U.S. Latino adults who converted to their current religion rather than being raised in it, by religious group, 2006. ${alt}.`,
  };
}

export function getDataset(slug: string): Dataset | undefined {
  return DATASETS.find((d) => d.slug === slug);
}

/** Stable per-dataset graphic id: the imageSrc basename minus ".png".
 * Used as the /data-explorer/[slug]/graphics/[graphicId] URL segment and
 * as graphic_posts.graphic_id (see supabase/migrations/0049_graphic_posts.sql)
 * - renaming a PNG changes it, so treat basenames as stable identifiers. */
export function graphicId(graphic: Graphic): string {
  return graphic.imageSrc.split("/").pop()!.replace(/\.png$/, "");
}

export function getGraphic(datasetSlug: string, id: string): Graphic | undefined {
  return getDataset(datasetSlug)?.graphics.find((g) => graphicId(g) === id);
}

// Build-time guard: graphic ids are URL segments and database keys, so they
// must be unique within a dataset. Throws at module load so `next build`
// fails loudly on a collision rather than silently mis-linking a share URL.
for (const d of DATASETS) {
  const seenIds = new Set<string>();
  for (const g of d.graphics) {
    const id = graphicId(g);
    if (seenIds.has(id)) {
      throw new Error(`Duplicate graphic id "${id}" in dataset "${d.slug}"`);
    }
    seenIds.add(id);
  }
}

/** GROUP_COLORS keys from scripts/chart_style.py, plus common alias phrases
 * (from that file's GROUP_ALIASES) that graphic title/alt text uses instead
 * of the canonical name - e.g. Ryan Burge's CCES graphics say "Mormon", not
 * "Latter-day Saint". Keep in sync with chart_style.py when either changes. */
const TRADITION_MATCHERS: { canonical: string; phrases: string[] }[] = [
  { canonical: "Latter-day Saint", phrases: ["Latter-day Saint", "Mormon"] },
  { canonical: "Catholic", phrases: ["Catholic"] },
  { canonical: "Protestant", phrases: ["Protestant"] },
  { canonical: "Orthodox Christian", phrases: ["Orthodox Christian", "Orthodox"] },
  { canonical: "Jehovah's Witness", phrases: ["Jehovah's Witness"] },
  { canonical: "Muslim", phrases: ["Muslim"] },
  { canonical: "Hindu", phrases: ["Hindu"] },
  { canonical: "Buddhist", phrases: ["Buddhist"] },
  { canonical: "Jewish", phrases: ["Jewish"] },
  { canonical: "Religiously unaffiliated", phrases: ["Religiously unaffiliated", "Unaffiliated", "religious \"nones\"", "the nones"] },
  { canonical: "Evangelical Protestant", phrases: ["Evangelical Protestant", "Evangelical"] },
  { canonical: "Mainline Protestant", phrases: ["Mainline Protestant", "Mainline"] },
  { canonical: "Historically Black Protestant", phrases: ["Historically Black Protestant"] },
  { canonical: "Agnostic", phrases: ["Agnostic"] },
  { canonical: "Atheist", phrases: ["Atheist"] },
  { canonical: "Nothing in particular", phrases: ["Nothing in particular"] },
  { canonical: "Southern Baptist", phrases: ["Southern Baptist"] },
  { canonical: "United Methodist", phrases: ["United Methodist"] },
];

/** Derives which religious traditions a graphic breaks its data out by, via
 * a keyword pass over its title/alt text against TRADITION_MATCHERS - gives
 * every existing graphic retroactive coverage for the gallery's tradition
 * filter without hand-tagging 195 entries. Order follows TRADITION_MATCHERS,
 * not order of appearance in the text. */
export function deriveTraditions(graphic: Graphic): string[] {
  const haystack = `${graphic.title} ${graphic.alt}`;
  return TRADITION_MATCHERS.filter((m) =>
    m.phrases.some((phrase) => haystack.includes(phrase)),
  ).map((m) => m.canonical);
}

export type GalleryGraphic = Graphic & {
  datasetSlug: string;
  datasetName: string;
  fieldedPeriod: string;
  traditions: string[];
};

/** Every graphic across every dataset, flattened for the public gallery at
 * /data-explorer/gallery. */
export function getAllGraphics(): GalleryGraphic[] {
  return DATASETS.flatMap((d) =>
    d.graphics.map((g) => ({
      ...g,
      datasetSlug: d.slug,
      datasetName: d.name,
      fieldedPeriod: d.fieldedPeriod,
      traditions: deriveTraditions(g),
    })),
  );
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
 * Six holiday-calendar-driven "by tradition" graphics (Labor Day,
 * happiness/mental-health days, Hispanic Heritage Month, Constitution Day
 * x2, Family Proclamation anniversary, Religious Freedom/Human Rights Day)
 * built from holiday-batch.json (scripts/pew-rls/holiday_batch.py),
 * rendered by scripts/pew-rls/render_holiday_batch.py.
 */
function pewWorksForPayGraphic(): Graphic {
  const alt = pctAlt(HOLIDAY_BATCH_ORDER, holidayBatchData.works_for_pay);
  return {
    title: "Who works full or part time for pay?",
    description: "Share who currently work for pay, by religious tradition.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/labor-day-works-for-pay.png",
    width: 1080, height: 1350,
    alt: `Bar chart, share who work full or part time for pay, by religious tradition: ${alt}.`,
  };
}

function pewHappinessGraphic(): Graphic {
  const alt = pctAlt(HOLIDAY_BATCH_ORDER, holidayBatchData.very_happy);
  return {
    title: "Who says they're very happy with life?",
    description: "Share saying they are \"very happy\" with life these days, by religious tradition.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/happiness-by-tradition.png",
    width: 1080, height: 1350,
    alt: `Bar chart, share saying they are very happy with life, by religious tradition: ${alt}.`,
  };
}

function pewHispanicShareGraphic(): Graphic {
  const alt = pctAlt(HOLIDAY_BATCH_ORDER, holidayBatchData.hispanic);
  return {
    title: "Who is Hispanic, Latino, or Spanish?",
    description: "Share of each religious tradition identifying as Hispanic, Latino, or Spanish.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/hispanic-share-by-tradition.png",
    width: 1080, height: 1350,
    alt: `Bar chart, Hispanic/Latino/Spanish share, by religious tradition: ${alt}.`,
  };
}

function pewChristianNationGraphic(): Graphic {
  const alt = pctAlt(HOLIDAY_BATCH_ORDER, holidayBatchData.christian_nation_favor);
  return {
    title: "Should the U.S. be declared a Christian nation?",
    description: "Share favoring the federal government declaring the U.S. a Christian nation, by religious tradition.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/christian-nation-favor.png",
    width: 1080, height: 1350,
    alt: `Bar chart, share favoring declaring the U.S. a Christian nation, by religious tradition: ${alt}.`,
  };
}

function pewStayHomeParentGraphic(): Graphic {
  const alt = pctAlt(HOLIDAY_BATCH_ORDER, holidayBatchData.stay_home_parent_better);
  return {
    title: "Is a stay-at-home parent better for kids?",
    description:
      "Share saying children are better off when a parent stays home to focus on family, " +
      "rather than both parents working outside the home, by religious tradition.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/stay-home-parent-view.png",
    width: 1080, height: 1350,
    alt: `Bar chart, share saying kids are better off with a stay-at-home parent, by religious tradition: ${alt}.`,
  };
}

function pewReligiousSymbolsGraphic(): Graphic {
  const alt = pctAlt(HOLIDAY_BATCH_ORDER, holidayBatchData.religious_symbols_favor);
  return {
    title: "Religious symbols on public property?",
    description: "Share favoring cities and towns placing religious symbols on public property, by religious tradition.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/religious-symbols-public-property.png",
    width: 1080, height: 1350,
    alt: `Bar chart, share favoring religious symbols on public property, by religious tradition: ${alt}.`,
  };
}

function pewSchoolPrayerGraphic(): Graphic {
  const alt = pctAlt(HOLIDAY_BATCH_ORDER, holidayBatchData.school_prayer_favor);
  return {
    title: "Teacher-led prayer in public schools?",
    description:
      "Share favoring public school teachers leading classes in prayers that refer to Jesus, " +
      "by religious tradition.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/school-prayer-jesus-favor.png",
    width: 1080, height: 1350,
    alt: `Bar chart, share favoring teacher-led Jesus-referencing school prayer, by religious tradition: ${alt}.`,
  };
}

/**
 * Three more holiday-calendar-driven "by tradition" graphics (Valentine's
 * Day, AANHPI Heritage Month, Mother's/Father's Day) built from
 * holiday-batch-2.json (scripts/pew-rls/holiday_batch_2.py), rendered by
 * scripts/pew-rls/render_holiday_batch_2.py.
 */
function pewSameFaithSpouseGraphic(): Graphic {
  const alt = pctAlt(HOLIDAY_BATCH_ORDER, holidayBatch2Data.same_faith_spouse);
  return {
    title: "Whose spouse shares their religion?",
    description: "Share of married/partnered adults whose spouse or partner shares their current religion, by tradition.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/same-faith-spouse.png",
    width: 1080, height: 1350,
    alt: `Bar chart, share whose spouse/partner shares their current religion, by tradition: ${alt}.`,
  };
}

function pewAsianShareGraphic(): Graphic {
  const alt = pctAlt(HOLIDAY_BATCH_ORDER, holidayBatch2Data.asian_or_asian_american);
  return {
    title: "Who is Asian or Asian-American?",
    description: "Share of each religious tradition identifying as Asian or Asian-American.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/asian-share-by-tradition.png",
    width: 1080, height: 1350,
    alt: `Bar chart, Asian/Asian-American share, by religious tradition: ${alt}.`,
  };
}

function pewTwoPlusChildrenGraphic(): Graphic {
  const alt = pctAlt(HOLIDAY_BATCH_ORDER, holidayBatch2Data.two_or_more_children);
  return {
    title: "Who has two or more children?",
    description: "Share with two or more children ever born, by religious tradition.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/two-or-more-children.png",
    width: 1080, height: 1350,
    alt: `Bar chart, share with two or more children ever born, by religious tradition: ${alt}.`,
  };
}

function pewStayHomeParentGenderGraphic(): Graphic {
  const alt = pctAlt(HOLIDAY_BATCH_ORDER, stayHomeParentGenderData.should_be_mother);
  return {
    title: "If a parent stays home, should it be the mother?",
    description: "Of those who say a parent should stay home to focus on family, share saying specifically the mother, by tradition.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/stay-home-parent-gender.png",
    width: 1080, height: 1350,
    alt: `Bar chart, share saying it should specifically be the mother who stays home, by tradition: ${alt}.`,
  };
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
 * Same as pewAttendDistributionGraphic, restricted to Christian traditions
 * only (Latter-day Saint, Catholic, Protestant, Orthodox Christian,
 * Jehovah's Witness). Rendered by
 * scripts/pew-rls/render_christian_only_variants.py.
 */
function pewAttendDistributionChristianGraphic(): Graphic {
  const { attend_distribution: results, attend_order: order } = practiceData;
  const alt = GENERALIZED_GROUP_ORDER.map((group) => {
    const g = results[group as keyof typeof results];
    const shares = order
      .map((label) => `${label} ${g.shares_pct[label as keyof typeof g.shares_pct].toFixed(0)}%`)
      .join(", ");
    return `${group}: ${shares}`;
  }).join("; ");

  return {
    title: "Attendance frequency, full distribution (Christian only)",
    description: "How often each Christian tradition's members attend religious services in person.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/practice-attend-distribution-christian.png",
    width: 1080,
    height: 1350,
    alt: `100%-stacked bar chart, religious attendance frequency by Christian tradition. ${alt}.`,
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
 * Same as pewAttendMonthlyPlusGraphic, restricted to Christian traditions
 * only. Rendered by scripts/pew-rls/render_christian_only_variants.py.
 */
function pewAttendMonthlyPlusChristianGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, practiceData.attend_monthly_plus_either);
  return {
    title: "Attend in-person and/or online, monthly+ (Christian only)",
    description:
      "Share of each Christian tradition attending religious services monthly or more, " +
      "either in person or online/on TV.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/practice-attend-monthly-plus-christian.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share attending religious services monthly+ in person and/or online, Christian traditions only: ${alt}.`,
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
 * Same as pewMembGraphic, restricted to Christian traditions only.
 * Rendered by scripts/pew-rls/render_christian_only_variants.py.
 */
function pewMembChristianGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, practiceData.memb_member);
  return {
    title: "Member of a house of worship (Christian only)",
    description:
      "Share of each Christian tradition personally a member of a church, synagogue, " +
      "mosque, temple, or other house of worship.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/practice-memb-christian.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who are a member of a house of worship, by Christian tradition: ${alt}.`,
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
 * Same as pewPrayDistributionGraphic, restricted to Christian traditions
 * only. Rendered by scripts/pew-rls/render_christian_only_variants.py.
 */
function pewPrayDistributionChristianGraphic(): Graphic {
  const { pray_distribution: results, pray_order: order } = practiceData;
  const alt = GENERALIZED_GROUP_ORDER.map((group) => {
    const g = results[group as keyof typeof results];
    const shares = order
      .map((label) => `${label} ${g.shares_pct[label as keyof typeof g.shares_pct].toFixed(0)}%`)
      .join(", ");
    return `${group}: ${shares}`;
  }).join("; ");

  return {
    title: "Prayer frequency (Christian only)",
    description: "How often each Christian tradition's members pray, outside of attending religious services.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/practice-pray-distribution-christian.png",
    width: 1080,
    height: 1350,
    alt: `100%-stacked bar chart, prayer frequency by Christian tradition. ${alt}.`,
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
 * Same as pewPracbGraphic, restricted to Christian traditions only.
 * Rendered by scripts/pew-rls/render_christian_only_variants.py.
 */
function pewPracbChristianGraphic(): Graphic {
  const alt = pctAlt(GENERALIZED_GROUP_ORDER, practiceData.pracb_weekly_plus);
  return {
    title: "Read scripture outside of services, weekly+ (Christian only)",
    description: "Share of each Christian tradition reading scripture at least once a week, outside of religious services.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/practice-pracb-christian.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share reading scripture weekly+ outside of services, by Christian tradition: ${alt}.`,
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
 * Same as pewSoulBeliefGraphic, restricted to Christian traditions plus
 * the religiously unaffiliated. Rendered by
 * scripts/pew-rls/render_christian_only_variants.py.
 */
function pewSoulBeliefChristianGraphic(): Graphic {
  const alt = pctAlt(CHRISTIAN_ONLY_PLUS_UNAFFILIATED_GROUP_ORDER, beliefsData.soul_belief);
  return {
    title: "Believe people have a soul or spirit (Christian only)",
    description:
      "Share of Christian traditions (plus the unaffiliated) who believe people have a soul " +
      "or spirit in addition to their physical body.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/beliefs-soul-christian.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who believe in a soul or spirit, Christian traditions and the unaffiliated: ${alt}.`,
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
 * Same as pewHeavenBeliefGraphic, restricted to Christian traditions plus
 * the religiously unaffiliated. Rendered by
 * scripts/pew-rls/render_christian_only_variants.py.
 */
function pewHeavenBeliefChristianGraphic(): Graphic {
  const alt = pctAlt(CHRISTIAN_ONLY_PLUS_UNAFFILIATED_GROUP_ORDER, beliefsData.heaven_belief);
  return {
    title: "Believe in heaven (Christian only)",
    description:
      "Share of Christian traditions (plus the unaffiliated) who believe there is a heaven " +
      "where people who led good lives are eternally rewarded.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/beliefs-heaven-christian.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who believe in heaven, Christian traditions and the unaffiliated: ${alt}.`,
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
 * Same as pewHellBeliefGraphic, restricted to Christian traditions plus
 * the religiously unaffiliated. Rendered by
 * scripts/pew-rls/render_christian_only_variants.py.
 */
function pewHellBeliefChristianGraphic(): Graphic {
  const alt = pctAlt(CHRISTIAN_ONLY_PLUS_UNAFFILIATED_GROUP_ORDER, beliefsData.hell_belief);
  return {
    title: "Believe in hell (Christian only)",
    description:
      "Share of Christian traditions (plus the unaffiliated) who believe there is a hell " +
      "where people who led bad lives are eternally punished.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/beliefs-hell-christian.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who believe in hell, Christian traditions and the unaffiliated: ${alt}.`,
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
 * Same as pewHeavenVsHellGraphic, restricted to Christian traditions plus
 * the religiously unaffiliated. Rendered by
 * scripts/pew-rls/render_christian_only_variants.py.
 */
function pewHeavenVsHellChristianGraphic(): Graphic {
  const alt = CHRISTIAN_ONLY_PLUS_UNAFFILIATED_GROUP_ORDER.map((group) => {
    const h = beliefsData.heaven_belief[group as keyof typeof beliefsData.heaven_belief];
    const l = beliefsData.hell_belief[group as keyof typeof beliefsData.hell_belief];
    return `${group} heaven ${h.pct.toFixed(0)}%, hell ${l.pct.toFixed(0)}%`;
  }).join(", ");

  return {
    title: "Belief in heaven vs. hell (Christian only)",
    description: "The same two questions, compared side by side, Christian traditions and the unaffiliated.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/beliefs-heaven-vs-hell-christian.png",
    width: 1080,
    height: 1350,
    alt: `Paired bar chart, belief in heaven vs. hell, Christian traditions and the unaffiliated: ${alt}.`,
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
 * Same as pewEvolutionGuidedGraphic, restricted to Christian traditions
 * plus the religiously unaffiliated. Rendered by
 * scripts/pew-rls/render_christian_only_variants.py.
 */
function pewEvolutionGuidedChristianGraphic(): Graphic {
  const alt = pctAlt(CHRISTIAN_ONLY_PLUS_UNAFFILIATED_GROUP_ORDER, beliefsData.evolution_guided_by_god);
  return {
    title: "Evolution guided by God (Christian only)",
    description:
      "Share of Christian traditions (plus the unaffiliated) who say humans evolved over " +
      "time due to processes guided or allowed by God.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/beliefs-evolution-christian.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who say evolution was guided by God, Christian traditions and the unaffiliated: ${alt}.`,
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
 * Same as pewRelimpactGraphic, restricted to Christian traditions plus
 * the religiously unaffiliated. Rendered by
 * scripts/pew-rls/render_christian_only_variants.py.
 */
function pewRelimpactChristianGraphic(): Graphic {
  const alt = pctAlt(CHRISTIAN_ONLY_PLUS_UNAFFILIATED_GROUP_ORDER, publicLifeData.relimpact_more_good);
  return {
    title: "Religion does more good than harm (Christian only)",
    description:
      "Share of Christian traditions (plus the unaffiliated) who say religion's overall " +
      "impact on American society is more good than harm.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/public-relimpact-christian.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who say religion does more good than harm, Christian traditions and the unaffiliated: ${alt}.`,
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

/**
 * Same as pewVol12Graphic, restricted to Christian traditions plus the
 * religiously unaffiliated. Rendered by
 * scripts/pew-rls/render_christian_only_variants.py.
 */
function pewVol12ChristianGraphic(): Graphic {
  const alt = pctAlt(CHRISTIAN_ONLY_PLUS_UNAFFILIATED_GROUP_ORDER, publicLifeData.vol12_volunteered);
  return {
    title: "Volunteered in the past 12 months (Christian only)",
    description: "Share of Christian traditions (plus the unaffiliated) who spent any time volunteering in the past 12 months.",
    imageSrc: "/data-explorer/pew-religious-landscape-study/public-vol12-christian.png",
    width: 1080,
    height: 1350,
    alt: `Bar chart, share who volunteered in the past 12 months, Christian traditions and the unaffiliated: ${alt}.`,
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
 * Currently a labor union member - Labor Day hook. Same population, data
 * source, and render script as the graphics above.
 */
function cces2016UnionGraphic(): Graphic {
  const alt = cces2016PctAlt(cces2016Data.union_currently);
  return {
    title: "Who is currently a labor union member?",
    description: "Share who are currently a member of a labor union, by religion.",
    imageSrc: "/data-explorer/cces-2016/union.png",
    width: 1080,
    height: 1350,
    credit: "via Ryan Burge",
    alt: `Bar chart, share currently a labor union member, by religion: ${alt}.`,
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

/**
 * Average number of non-religious causes volunteered for per person
 * (mean count across the 16 non-religious categories in
 * voter-ideas-volunteering.json's own battery, excluding religious
 * organizations), baseline wave. Narrower group set than every other
 * VOTER Panel chart - Agnostic, Nothing in particular, and Something else
 * dropped, per this chart's own request (Orthodox/Muslim/Hindu still
 * dropped as too thin, matching the rest of this family). Built from
 * voter-volunteering-summary.json (scripts/ryan-burge/voter_volunteering_summary.py),
 * rendered by scripts/ryan-burge/render_voter_volunteering_summary_chart.py.
 */
function voterNonreligiousCausesGraphic(): Graphic {
  const { group_order: order, nonreligious_causes_avg: results } = voterVolunteeringSummaryData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].avg_causes.toFixed(2)}`)
    .join(", ");
  return {
    title: "Average non-religious causes volunteered for",
    description:
      "Of 16 non-religious cause types, average number each person volunteered for in the " +
      "past 12 months (baseline wave).",
    imageSrc: "/data-explorer/voter-survey-panel/volunteer-nonreligious-avg.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Bar chart, average number of non-religious causes volunteered for per person, by religion: ${alt}.`,
  };
}

/**
 * Share who volunteered for a religious organization specifically - the
 * one category the graphic above excludes. Same data source and render
 * script as the graphic above.
 */
function voterReligiousOrgVolunteerGraphic(): Graphic {
  const { group_order: order, religious_org_pct: results } = voterVolunteeringSummaryData;
  const alt = order
    .map((g) => `${g} ${results[g as keyof typeof results].pct}%`)
    .join(", ");
  return {
    title: "Volunteer for a religious organization",
    description: "Share who volunteered for a religious organization in the past 12 months (baseline wave).",
    imageSrc: "/data-explorer/voter-survey-panel/volunteer-religious-org.png",
    width: 1080, height: 1350, credit: "via Ryan Burge",
    alt: `Bar chart, share who volunteered for a religious organization, by religion: ${alt}.`,
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
