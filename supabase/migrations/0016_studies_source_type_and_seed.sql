-- Add source_type, category, and secondary_url to studies.
-- source_type: 'primary_dataset' | 'study' | 'secondary_analysis'
-- category: free-text section heading for grouped display
-- secondary_url: optional second canonical link (e.g., data-access portal)

alter table public.studies
  add column if not exists source_type text,
  add column if not exists category text,
  add column if not exists secondary_url text;

-- Seed 11 external studies. pdf_path stays null (external_url is the source).
-- ON CONFLICT (slug) lets re-running this be safe.

insert into public.studies (
  slug, title, authors, year, source,
  abstract, findings, tags,
  external_url, secondary_url,
  source_type, category,
  featured, flagged_problematic
) values

-- ── Wellbeing & Flourishing ──────────────────────────────────────────────────

(
  'harvard-global-flourishing-study-2025',
  'Harvard / Baylor Global Flourishing Study — Flagship Paper',
  array['Tyler J. VanderWeele', 'Brendan Case', 'Ying Chen'],
  2025,
  'Nature Mental Health',
  'Longitudinal panel of 200,000+ participants across 22 countries, nationally representative, run with Gallup and the Center for Open Science. Measures six domains: health, happiness, meaning, character, relationships, and financial security.',
  array[
    'Greater religious service attendance is associated with greater flourishing worldwide.',
    'Age, marital status, and attendance show the strongest associations with wellbeing.',
    'Results hold across diverse religious traditions and national contexts.'
  ],
  array['Flourishing', 'Religion', 'Longitudinal', 'International'],
  'https://www.nature.com/articles/s44220-025-00423-5',
  'https://hfh.fas.harvard.edu/global-flourishing-study',
  'primary_dataset',
  'Wellbeing & Flourishing',
  true,
  false
),

(
  'gfs-latter-day-saint-breakdown',
  'Global Flourishing Study — Latter-day Saint Breakdown',
  array['Deseret News Analysis'],
  2026,
  'Deseret News / GFS U.S. data',
  'Analysis of the GFS U.S. data filtered to Latter-day Saint respondents, comparing depression, happiness, attendance, and childhood relationship measures against other religious groups.',
  array[
    'LDS reported one of the lowest depression rates (8.5%) — 2–3× lower than "no religion" (16%) and atheist/agnostic/never-religious (~19%).',
    'LDS near the top for "highly happy" (30%, vs ~11–16% for the least religious groups).',
    'Highest weekly attendance of any group measured (65%).',
    'Highest reports of feeling loved by mother and father in childhood.'
  ],
  array['Flourishing', 'Depression', 'Latter-day Saints', 'Secondary Analysis'],
  'https://www.deseret.com/opinion/2026/05/17/harvard-global-flourishing-study-latter-day-saints/',
  null,
  'secondary_analysis',
  'Wellbeing & Flourishing',
  false,
  false
),

(
  'gallup-healthways-wellbeing-index',
  'Gallup-Healthways Well-Being Index',
  array['Frank Newport', 'Dan Witters'],
  2012,
  'Gallup',
  '676,000+ interviews measuring wellbeing by religiosity and faith group with demographic controls.',
  array[
    'Very religious Americans of every faith had higher overall wellbeing than moderately or nonreligious counterparts (statistically significant after controls).',
    'Mormons were the most religious group measured (73.4% "very religious").',
    'Jews and Mormons had the highest overall wellbeing of any faith group.'
  ],
  array['Wellbeing', 'Religion', 'Gallup', 'Demographics'],
  'https://news.gallup.com/poll/152732/religious-higher-wellbeing-across-faiths.aspx',
  null,
  'primary_dataset',
  'Wellbeing & Flourishing',
  false,
  false
),

-- ── Mental Health ─────────────────────────────────────────────────────────────

(
  'judd-religiosity-mental-health-lds',
  'Religiosity, Mental Health, and the Latter-day Saints',
  array['Daniel K. Judd'],
  1999,
  'BYU Religious Studies Center',
  'Synthesis of approximately 540 studies on religion and mental health, including LDS-specific MMPI data, covering the period 1923–1995.',
  array[
    'LDS who live consistent with their beliefs show greater general wellbeing and family stability.',
    'Lower rates of delinquency, depression, anxiety, and substance abuse among practicing members.',
    'Of 540 studies, 51% found a positive religion–mental-health association, 16% negative.',
    'No standardized-test study links LDS belief or practice to increased depression.'
  ],
  array['Mental Health', 'Depression', 'Literature Review', 'Latter-day Saints'],
  'https://rsc.byu.edu/latter-day-saint-social-life/religiosity-mental-health-latter-day-saints-preliminary-review-literature-1923-95',
  null,
  'study',
  'Mental Health',
  false,
  false
),

(
  'utah-antidepressant-paradox',
  'Utah Antidepressant Paradox — Mixed Evidence Overview',
  array['MormonR.org / Public Square Magazine'],
  2023,
  'MormonR.org; Public Square Magazine',
  'Overview of the mixed evidence on Utah and LDS depression rates, high antidepressant use, and the competing explanations.',
  array[
    'Studies are mixed: some show LDS less depressed, some show more.',
    'Utah ranks poorly on some state mental-health metrics.',
    'High antidepressant use may reflect more help-seeking and less self-medication rather than more illness.',
    'LDS-heavy counties show lower antidepressant use than the Utah state average.',
    'Suicide and high life-satisfaction co-occurrence linked to comparison effects and altitude.'
  ],
  array['Mental Health', 'Depression', 'Utah', 'Critical Review'],
  'https://mormonr.org/qnas/kxclp/antidepressants_in_utah',
  'https://publicsquaremag.org/health/mental-health/are-utahns-more-depressed-than-everyone-else/',
  'secondary_analysis',
  'Mental Health',
  false,
  false
),

-- ── Major Demographic / Belief Surveys ───────────────────────────────────────

(
  'pew-religious-landscape-study-2024',
  'Pew Research — Religious Landscape Study 2023–24',
  array['Pew Research Center'],
  2024,
  'Pew Research Center',
  'Nationally representative survey of 36,908 U.S. adults (July 2023–March 2024), address-based sampling. Paired with 2007 and 2014 waves for trend analysis. LDS margin of error ±6.2 points.',
  array[
    'LDS share of the U.S. virtually unchanged across all three waves (~2%).',
    'LDS rank at or near the top on weekly attendance, daily prayer, scripture reading, and "religion very important."',
    'U.S. Christian decline has slowed or leveled off in the most recent wave.'
  ],
  array['Demographics', 'Pew', 'Attendance', 'Belief', 'Trend'],
  'https://www.pewresearch.org/religious-landscape-study/religious-tradition/latter-day-saint-mormon/',
  'https://www.pewresearch.org/religious-landscape-study/2024/',
  'primary_dataset',
  'Major Demographic Surveys',
  true,
  false
),

(
  'next-mormons-survey-2016',
  'The Next Mormons Survey (NMS)',
  array['Jana Riess', 'Benjamin Knoll'],
  2016,
  'Oxford University Press / thenextmormons.org',
  'Independent online survey (Qualtrics) spanning four generations of current and former Mormons; not Church-affiliated. Basis for the book "The Next Mormons."',
  array[
    'Belief levels among young-adult Mormons remain strong but institutional loyalty is weaker than among older generations.',
    'Identifies specific subgroups leaving and their primary reasons.',
    'Most former members still believe in God.'
  ],
  array['Demographics', 'Retention', 'Generational', 'Disaffiliation'],
  'https://thenextmormons.org/methodology/',
  'https://thenextmormons.org/survey-results/',
  'primary_dataset',
  'Major Demographic Surveys',
  true,
  false
),

(
  'byu-lds-religious-seismology-survey',
  'BYU Latter-day Saint Religious Seismology Survey',
  array['BYU College of Religious Education'],
  2025,
  'BYU / Deseret News',
  'BYU survey focused on retention and disaffiliation among Latter-day Saints, paired with Pew RLS data.',
  array[
    '~50% retention of those raised LDS.',
    'Identifies four distinct subgroups among those who disaffiliate, varying by importance of religion, warmth toward LDS, belief in afterlife, and belief in Jesus.',
    'LDS Millennials and Gen Z who are highly involved score among the highest in wellbeing.'
  ],
  array['Demographics', 'Retention', 'Disaffiliation', 'BYU'],
  'https://foundations.byu.edu/0000019b-1343-d613-a59b-17df82980000/latterdaysaintreligiosity-pdf',
  'https://www.deseret.com/faith/2025/12/15/latter-day-saint-retention/',
  'primary_dataset',
  'Major Demographic Surveys',
  false,
  false
),

-- ── Physical Health & Longevity ───────────────────────────────────────────────

(
  'enstrom-health-practices-mortality-california-mormons',
  'Health Practices and Mortality among Active California Mormons',
  array['James E. Enstrom'],
  1989,
  'BYU Religious Studies Center',
  'First prospective cohort study of Mormons: 1979 questionnaire, 5,231 high priests plus 4,613 wives, with 8-year and 14-year mortality follow-up.',
  array[
    'Middle-aged high priests following three health habits had 34% the cancer-mortality of comparable U.S. white males.',
    '14% the cardiovascular-mortality rate of comparable U.S. white males.',
    '22% the overall-mortality rate of comparable U.S. white males.',
    'Estimated life expectancy in the mid-80s for compliant members.'
  ],
  array['Health', 'Mortality', 'Word of Wisdom', 'Longevity', 'Cohort Study'],
  'https://rsc.byu.edu/latter-day-saint-social-life/health-practices-cancer-mortality-among-active-california-mormons',
  'https://rsc.byu.edu/latter-day-saint-social-life/health-practices-mortality-among-active-california-mormons-1980-93',
  'study',
  'Physical Health & Longevity',
  false,
  false
),

(
  'merrill-life-expectancy-lds-utah',
  'Life Expectancy among LDS and Non-LDS in Utah',
  array['Ray M. Merrill'],
  2004,
  'ResearchGate / Social Science & Medicine',
  'Utah life-expectancy comparison between LDS and non-member counterparts, with disease-specific analysis.',
  array[
    'LDS males live ~7.3 years longer than non-member Utah males.',
    'LDS females live ~5.8 years longer than non-member Utah females.',
    'Lower coronary disease and cancer risk than national averages.',
    'Less multiple sclerosis incidence than national averages.'
  ],
  array['Health', 'Longevity', 'Life Expectancy', 'Utah'],
  'https://www.researchgate.net/publication/4746341_Life_expectancy_among_LDS_and_non-LDS_in_Utah',
  null,
  'study',
  'Physical Health & Longevity',
  false,
  false
),

-- ── Retention & Generational Change ──────────────────────────────────────────

(
  'pew-rls-retention-trend',
  'Pew RLS Retention Trend (2007–2024)',
  array['Times and Seasons / MormonMetrics'],
  2025,
  'Times and Seasons; MormonMetrics',
  'Secondary analysis computing retention rates from three Pew Religious Landscape Study waves (2007, 2014, 2023–24).',
  array[
    'Share of those raised LDS who still identify as LDS: 70% (2007) → 64% (2014) → 54% (2023–24).',
    'Race and marital status remain strong predictors of retained LDS identity.',
    'Education''s effect on leaving has weakened in the most recent wave.'
  ],
  array['Retention', 'Generational Change', 'Pew', 'Trend', 'Secondary Analysis'],
  'https://timesandseasons.org/index.php/2025/05/a-lot-more-people-are-leaving-the-church-now/',
  'https://mormonmetrics.com/p/data-update-from-the-new-2024-prls',
  'secondary_analysis',
  'Retention & Generational Change',
  false,
  false
)

on conflict (slug) do update set
  title          = excluded.title,
  authors        = excluded.authors,
  year           = excluded.year,
  source         = excluded.source,
  abstract       = excluded.abstract,
  findings       = excluded.findings,
  tags           = excluded.tags,
  external_url   = excluded.external_url,
  secondary_url  = excluded.secondary_url,
  source_type    = excluded.source_type,
  category       = excluded.category,
  featured       = excluded.featured,
  updated_at     = now();
