import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';
const env = Object.fromEntries(
  readFileSync(new URL('../.env.local', import.meta.url), 'utf8')
    .split('\n').filter(l => l.includes('=')).map(l => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);
const c = createClient(env.NEXT_PUBLIC_SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY);

const updates = [
  {
    slug: 'byu-studies-issue-63-4',
    findings: [
      'Issue contains Ogletree\'s analysis of perfectionism and adolescent mental health in Latter-day Saint contexts.',
      'Reports LDS adolescent suicide ideation rates lower than commonly assumed in public discourse.',
      'Covers related topics including pornography exposure and adolescent wellbeing.',
    ],
    source_type: 'study',
    category: 'Mental Health',
    limitations: 'Journal issue rather than a single study; findings depend on the individual articles within. See linked Ogletree article for specifics.',
  },
  {
    slug: 'byustudies-religion-sexual-orientation-utah-youth-suicidality',
    findings: [
      'Examines religion and sexual orientation as joint predictors of suicidality in Utah youth.',
      'Religious participation generally associated with reduced suicidality, including among LGB youth in many measures.',
      'Findings complicate the assumption that LDS religious context uniformly increases LGB youth suicide risk.',
    ],
    source_type: 'study',
    category: 'Mental Health',
    limitations: 'Utah-specific sample limits generalizability; cross-sectional design precludes causal inference; self-reported religiosity and sexual orientation.',
  },
  {
    slug: 'called-to-serve-prosocial-behavior',
    findings: [
      'Active Latter-day Saints volunteer substantially more hours per year than the U.S. national average.',
      'Charitable giving (both religious and secular) among active members exceeds national norms.',
      'Civic engagement measures (voting, community involvement) are above U.S. averages.',
      'Service patterns persist across age, gender, and income brackets within the active LDS sample.',
    ],
    source_type: 'study',
    category: 'Service & Civic Engagement',
    limitations: 'Sample focuses on "active" members, which may oversample the most engaged; self-reported volunteer hours subject to recall and social-desirability bias.',
  },
  {
    slug: 'dyer-18-years-lds-mental-health-2023',
    findings: [
      'Practicing Latter-day Saints show lower substance abuse than non-LDS peers.',
      'Lower rates of depression, anxiety, and suicidal ideation among active members.',
      'Better body image outcomes than national averages.',
      'LGBTQ Latter-day Saints show better mental health outcomes on many measures than commonly assumed.',
    ],
    source_type: 'secondary_analysis',
    category: 'Mental Health',
    limitations: 'Opinion/perspective piece summarizing 18 years of research; not itself peer-reviewed. Findings depend on cited underlying studies.',
  },
  {
    slug: 'fair-2024-coates-moral-foundations',
    findings: [
      'Applies Haidt\'s moral foundations theory (care, fairness, loyalty, authority, sanctity, liberty) to LDS thought.',
      'Latter-day Saint moral reasoning draws on all six foundations rather than a narrow subset.',
      'Frames Latter-day Saint ethics in cross-cultural moral-psychology terms.',
    ],
    source_type: 'secondary_analysis',
    category: 'Belief & Practice',
    limitations: 'Conference presentation rather than peer-reviewed empirical study; applies an existing framework rather than presenting new data.',
  },
  {
    slug: 'lds-lgb-youth-mental-health-pubmed-27633316',
    findings: [
      'LGB Latter-day Saint youth in this sample showed lower depression than non-LGB LDS peers.',
      'Result challenges the assumption that LDS religious context uniformly harms LGB youth mental health.',
      'Effect persists after demographic controls in the analyzed sample.',
    ],
    source_type: 'study',
    category: 'Mental Health',
    limitations: 'Cross-sectional sample; self-reported sexual orientation and mental health; sample size and recruitment limit generalizability.',
  },
  {
    slug: 'mormonr-polygamy-prevalence',
    findings: [
      'Most historians estimate 15–30% of 19th-century LDS men entered plural marriage.',
      'Roughly 1 in 5 LDS men had plural wives at the practice\'s peak.',
      'Plural marriage was never universal among Church members.',
    ],
    source_type: 'secondary_analysis',
    category: 'History',
    limitations: 'Historical estimates vary by time period, community, and source; 19th-century recordkeeping limits precision.',
  },
  {
    slug: 'mormons-no-longer-majority-utah',
    findings: [
      'Latter-day Saints no longer constitute a majority of Utah\'s population.',
      'Primary drivers: in-migration of non-LDS residents, declining LDS birth rates, and religious disaffiliation.',
      'Demographic shift carries implications for the sociology of religion in the American West.',
    ],
    source_type: 'study',
    category: 'Major Demographic Surveys',
    limitations: 'Working paper rather than final peer-reviewed publication at time of indexing; relies on multiple data sources of varying methodologies.',
  },
  {
    slug: 'ogletree-perfectionism-adolescent-mental-health-2024',
    findings: [
      'LDS adolescent suicide ideation rates are lower than commonly assumed.',
      'Perfectionism is identified as a relevant — but not unique-to-LDS — factor in adolescent mental health.',
      'Discusses pornography exposure and its relationship to adolescent wellbeing.',
    ],
    source_type: 'study',
    category: 'Mental Health',
    limitations: 'Published in BYU Studies (faith-affiliated outlet); audience and framing oriented toward LDS readers.',
  },
  {
    slug: 'pew-2010-religious-knowledge-survey',
    findings: [
      'Latter-day Saints scored notably higher on Bible questions than the U.S. average.',
      'LDS were among the top-scoring religious traditions on biblical literacy.',
    ],
    source_type: 'primary_dataset',
    category: 'Belief & Practice',
    limitations: 'Short knowledge battery; small LDS subsample within the overall national survey.',
  },
  {
    slug: 'pew-2012-mormons-beliefs-practices',
    findings: [
      'Baseline portrait of U.S. Latter-day Saints across belief, practice, family life, and demographics.',
      'High rates of weekly attendance, daily prayer, and scripture engagement relative to other U.S. traditions.',
      'Frequently cited as the comparison baseline for later Pew waves.',
    ],
    source_type: 'primary_dataset',
    category: 'Major Demographic Surveys',
    limitations: 'Survey now over a decade old; some measures have shifted in later Pew waves.',
  },
  {
    slug: 'pew-2012-mormons-family-life',
    findings: [
      'LDS men more likely than LDS women to favor ordaining women to the priesthood.',
      'LDS respondents rate "being a good parent" and "having a successful marriage" as top life priorities at higher rates than the general U.S. population.',
      'Family-centered values consistently distinctive in cross-tradition comparisons.',
    ],
    source_type: 'primary_dataset',
    category: 'Family & Marriage',
    limitations: 'Cross-sectional snapshot; gender-priesthood views may have shifted since 2012.',
  },
  {
    slug: 'pew-2023-warmth-toward-religious-groups',
    findings: [
      'Americans hold more negative views of Latter-day Saints than of any other major religious group measured.',
      'Roughly 1 in 4 Americans view Latter-day Saints unfavorably.',
      'Latter-day Saints themselves rate every other religious group more positively than they are rated in return.',
    ],
    source_type: 'primary_dataset',
    category: 'Perception & Image',
    limitations: 'Feeling-thermometer measures capture warmth, not specific attitudes or behavior.',
  },
  {
    slug: 'pew-2025-decline-christianity-lds-racial',
    findings: [
      'U.S. Christian decline has slowed and may be leveling off.',
      'Latter-day Saint membership is becoming more racially diverse — the white-to-non-white ratio is shifting.',
    ],
    source_type: 'primary_dataset',
    category: 'Major Demographic Surveys',
    limitations: 'Trend interpretations sensitive to short time windows; LDS subsample carries ±6.2-point margin of error.',
  },
  {
    slug: 'pew-2025-importance-religion-and-bible',
    findings: [
      'About 46% of Orthodox, Catholic, and mainline Protestant respondents say the Bible is very important to them.',
      'Among Latter-day Saints, Evangelicals, and historically Black Protestants, that figure climbs to ~80%.',
    ],
    source_type: 'primary_dataset',
    category: 'Belief & Practice',
    limitations: 'Self-reported importance is subject to social-desirability effects within highly religious groups.',
  },
  {
    slug: 'pew-2025-religion-and-science-compatibility',
    findings: [
      'Latter-day Saints report the highest perceived compatibility between religion and science of any major U.S. religious tradition.',
    ],
    source_type: 'primary_dataset',
    category: 'Belief & Practice',
    limitations: 'Measures perception of compatibility, not actual scientific literacy or engagement.',
  },
  {
    slug: 'pew-2025-religion-and-views-of-right-and-wrong',
    findings: [
      'U.S. religious groups differ on whether moral rules are absolute or situational.',
      'Latter-day Saints lean strongly toward "belief in God is necessary for being moral and having good values."',
    ],
    source_type: 'primary_dataset',
    category: 'Belief & Practice',
    limitations: 'Binary framing of "absolute vs. situational" morality oversimplifies complex moral reasoning.',
  },
  {
    slug: 'pew-2025-religion-immigration-diversity',
    findings: [
      'Latter-day Saints more likely than members of other major U.S. religious traditions to view racial and ethnic diversity as a strength for society.',
    ],
    source_type: 'primary_dataset',
    category: 'Belief & Practice',
    limitations: 'Attitudes toward diversity measured at one point in time; political polarization may shift these views.',
  },
  {
    slug: 'pew-2025-religious-identity',
    findings: [
      'Latter-day Saint affiliation in the United States is fairly stable across the past decade.',
      'LDS share of the U.S. population has neither grown nor declined substantially even as overall U.S. Christian affiliation shifted.',
    ],
    source_type: 'primary_dataset',
    category: 'Major Demographic Surveys',
    limitations: 'Stability finding sensitive to the ±6.2-point LDS subsample margin of error.',
  },
  {
    slug: 'pope-religious-worship-attendance-cellphone-2024',
    findings: [
      'Only ~5% of Americans actually attend religious services in a given week, despite 22% reporting that they do.',
      'Latter-day Saints are the most regular churchgoers in the U.S. — more consistent than Catholics despite ~14× the Catholic population.',
      'Typical LDS services run ~115 minutes (tied with Orthodox Christians and Jehovah\'s Witnesses).',
      'Latter-day Saints show the lowest cellphone-observed visits to tobacco shops, liquor stores, and strip clubs (1.7%).',
      'Utah ranks highest of any state for alignment between stated religious identity and observed behavior.',
    ],
    source_type: 'study',
    category: 'Belief & Practice',
    limitations: 'Cellphone-location data has coverage gaps (low-income populations, phone-off behavior); inference of "religious attendance" from location requires modeling assumptions.',
  },
  {
    slug: 'psycnet-apa-sgd-0000517',
    findings: [
      'Examines intersections of sexual orientation, gender diversity, and religious participation.',
      'Published in APA\'s flagship LGBTQ-psychology journal; subject to peer review.',
    ],
    source_type: 'study',
    category: 'Mental Health',
    limitations: 'Listing-level entry; specifics depend on the underlying article — see external source for full title, authors, and findings.',
  },
  {
    slug: 'pubmed-11867352',
    findings: [
      'Peer-reviewed research on religion and mental health indexed in PubMed.',
      'Specifics available at the linked source.',
    ],
    source_type: 'study',
    category: 'Mental Health',
    limitations: 'Listing-level entry; methodology and findings depend on the underlying article.',
  },
  {
    slug: 'qsaltlake-2018-utah-faith-suicide-research',
    findings: [
      'News coverage of Utah-specific research linking faith communities and suicide outcomes.',
      'Frames religious community involvement as a relevant factor in youth and LGBTQ suicide discussion.',
    ],
    source_type: 'secondary_analysis',
    category: 'Mental Health',
    limitations: 'News article rather than primary research; LGBTQ-press framing shapes which findings are emphasized.',
  },
  {
    slug: 'sltrib-2025-pew-lds-religious-practice',
    findings: [
      'Latter-day Saints lead U.S. religious traditions in family-level religious practice.',
      'Higher rates of family prayer and family scripture reading than any other tradition surveyed.',
      'Higher overall prayer frequency, scripture reading outside formal worship, and in-person attendance.',
    ],
    source_type: 'secondary_analysis',
    category: 'Belief & Practice',
    limitations: 'News article summarizing Pew data — see the Pew RLS 2024 source for the underlying methodology.',
  },
  {
    slug: 'tandf-mhrc-13674670110059569',
    findings: [
      'Peer-reviewed article in Mental Health, Religion & Culture (Taylor & Francis).',
      'Specifics available at the linked source.',
    ],
    source_type: 'study',
    category: 'Mental Health',
    limitations: 'Listing-level entry; methodology and findings depend on the underlying article.',
  },
  {
    slug: 'times-and-seasons-2025-are-lds-happier',
    findings: [
      'Active commitment to the LDS Church is associated with higher measures of human flourishing in the Pew 2025 RLS data.',
      'Effect persists across happiness, meaning, and relationship-quality measures.',
      'Independent (non-Church) analysis of publicly available Pew data.',
    ],
    source_type: 'secondary_analysis',
    category: 'Wellbeing & Flourishing',
    limitations: 'Blog analysis rather than peer-reviewed; cross-sectional Pew data cannot establish causation.',
  },
];

// Also add limitations to the seeded studies (those that already had findings) where useful.
const limitationsBackfill = [
  { slug: 'harvard-global-flourishing-study-2025', limitations: 'Self-reported flourishing measures; associations between attendance and flourishing are correlational, not causal.' },
  { slug: 'gfs-latter-day-saint-breakdown', limitations: 'LDS subsample within U.S. GFS data carries wider margins of error; secondary analysis depends on Deseret News\'s slicing of the data.' },
  { slug: 'gallup-healthways-wellbeing-index', limitations: 'Cross-sectional; "very religious" self-identification may differ across traditions in what it measures.' },
  { slug: 'judd-religiosity-mental-health-lds', limitations: 'Literature review aggregates studies of varying methodological quality; coverage ends in 1995.' },
  { slug: 'utah-antidepressant-paradox', limitations: 'Synthesis of mixed evidence; conclusions depend on which underlying studies are weighted most heavily.' },
  { slug: 'pew-religious-landscape-study-2024', limitations: 'LDS subsample margin of error ±6.2 points; small-share groups subject to wider confidence intervals.' },
  { slug: 'next-mormons-survey-2016', limitations: 'Independent online (Qualtrics) sample is non-probability; weighting limits but does not eliminate selection bias relative to a true random sample.' },
  { slug: 'byu-lds-religious-seismology-survey', limitations: 'BYU-conducted survey on LDS topics may face response bias; retention estimates depend on definitional choices.' },
  { slug: 'enstrom-health-practices-mortality-california-mormons', limitations: 'Cohort restricted to active California high priests and wives — healthier-than-average baseline; results may not generalize to all LDS adults.' },
  { slug: 'merrill-life-expectancy-lds-utah', limitations: 'Utah-specific; LDS vs. non-LDS comparison within Utah may not generalize nationally; some confounds (income, education) only partially controlled.' },
  { slug: 'pew-rls-retention-trend', limitations: 'Retention computed from cross-sectional waves rather than a true panel; "raised LDS" relies on retrospective self-report.' },
  { slug: 'soce-among-current-or-former-lds-church-members-2015', limitations: 'Non-probability online sample weighted toward those who experienced SOCE; retrospective self-report of harm and effectiveness; sampling does not capture those who did not seek or remember change attempts.' },
];

const all = [...updates, ...limitationsBackfill];
let ok = 0, fail = 0;
for (const u of all) {
  const { slug, ...patch } = u;
  const { error } = await c.from('studies').update(patch).eq('slug', slug);
  if (error) { console.error(slug, error.message); fail++; }
  else { console.log('updated', slug); ok++; }
}
console.log(`\nDone. ${ok} updated, ${fail} failed.`);
