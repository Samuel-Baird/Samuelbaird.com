-- Seed three studies from Deseret News articles (June 2026 batch).
-- The Dec-2025 retention article is already stored as secondary_url on
-- byu-lds-religious-seismology-survey, so only two new rows are added here.

insert into public.studies (
  slug, title, authors, year, source,
  abstract, findings, tags,
  external_url, secondary_url,
  source_type, category,
  featured, flagged_problematic
) values

-- ── Physical Health & Longevity ───────────────────────────────────────────────

(
  'wheatley-religion-physical-health-2026',
  'Religion and Physical Health — Wheatley Institute Report',
  array['Loren Marks', 'Wheatley Institute at BYU', 'Duke University'],
  2026,
  'Wheatley Institute at Brigham Young University',
  'Systematic review and narrative synthesis of 1,069 high-quality studies on the relationship between religious participation and 15 physical health outcomes, drawing on selections from the "Handbook of Religion and Health" (Duke/Harvard). Released June 2026.',
  array[
    'Positive findings outnumbered negative ones 7:1 for physical health and 10:1 for mental health.',
    'Religious individuals show lower rates of smoking, substance abuse, cardiovascular disease, cancer, and Alzheimer''s disease.',
    'Benefits require "high involvement" — weekly or more frequent worship attendance sustained over years.',
    'Religion works best as a complement to professional medical and mental health care, not a replacement.',
    'Protective effects attributed to health codes, social connectedness, and beliefs about bodily stewardship.'
  ],
  array['Health', 'Physical Health', 'Systematic Review', 'Religion', 'BYU', 'Wheatley Institute'],
  'https://www.deseret.com/lifestyle/2026/06/04/religion-improves-health-outcomes-study-byu/',
  null,
  'study',
  'Physical Health & Longevity',
  false,
  false
),

-- ── Wellbeing & Flourishing ──────────────────────────────────────────────────

(
  'dyer-lds-trends-us-byu-studies-2026',
  'Latter-day Saint Trends in the United States: Religiousness, Well-being, and Retention',
  array['Justin Dyer'],
  2026,
  'BYU Studies',
  'Peer-reviewed synthesis (double-blind review) of the best available national datasets — University of Chicago General Social Survey, Harvard, and Pew Research Center — covering LDS religiousness, wellbeing, and retention trends. Published as a BYU Studies online book.',
  array[
    'Young Latter-day Saints attend religious services monthly at 76% — the highest rate among all U.S. faith groups measured.',
    'Latter-day Saint college students report the lowest rates of depressive symptoms among peers of any faith tradition.',
    '42% of younger Latter-day Saints rate their lives as "very happy."',
    'Approximately half of those raised LDS identify as members in adulthood — retention competitive with or higher than comparable Christian denominations.',
    'LDS active Millennials and Gen Z rank among the highest in overall wellbeing across all measured groups.'
  ],
  array['Demographics', 'Retention', 'Wellbeing', 'Mental Health', 'Generational', 'BYU', 'Peer Reviewed'],
  'https://www.deseret.com/opinion/2026/06/05/from-deficit-oriented-to-data-driven-latter-day-saint-public-discourse/',
  null,
  'secondary_analysis',
  'Wellbeing & Flourishing',
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
