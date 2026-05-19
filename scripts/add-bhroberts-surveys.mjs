import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';
const env = Object.fromEntries(
  readFileSync(new URL('../.env.local', import.meta.url), 'utf8')
    .split('\n').filter(l => l.includes('=')).map(l => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);
const c = createClient(env.NEXT_PUBLIC_SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY);

const rows = [
  {
    slug: 'bh-roberts-current-former-lds-survey-2023',
    title: '2023 National Current and Former Latter-day Saint Survey',
    authors: ['B. H. Roberts Foundation'],
    year: 2023,
    source: 'B. H. Roberts Foundation',
    abstract: 'A 2023 national survey of current and former Latter-day Saints conducted by the B. H. Roberts Foundation. Recruitment used 80,000 postcards mailed to a national LDS sample frame — a probability-based design that contrasts with convenience-recruited online surveys of disaffiliated members. The survey covers cross-generational faith patterns and applies Moral Foundations Theory to current and former Latter-day Saints. Detailed methodology and findings are published in the foundation\'s summary and methodology PDFs.',
    findings: [
      'Approximately 80,000 postcards distributed to a national LDS sample frame.',
      'Probability-based recruitment design, weighted using U.S. Religious Census proportions.',
      'Covers cross-generational faith patterns among current and former Latter-day Saints.',
      'Applies Moral Foundations Theory (Haidt) to current vs. former members.',
      'Belief-level findings (e.g. ~85%+ affirming the First Vision, ~90% affirming the Book of Mormon among current members) reported in Deseret News coverage.',
    ],
    tags: ['Belief', 'Survey', 'Representative Sample', 'Disaffiliation', 'Moral Foundations'],
    external_url: 'https://bhroberts.org/projects/survey2023',
    secondary_url: 'https://bhroberts.org/2023BHRSurveySummary.pdf',
    source_type: 'study',
    category: 'Major Demographic Surveys',
    featured: false,
    limitations: 'Mail-recruited surveys still face response-rate bias; weighting can correct demographic but not psychological self-selection. Single national wave — trend claims require pairing with the 2022 NLDSS or later waves.',
    flagged_problematic: false,
    flag_reason: null,
    context_note: null,
  },
  {
    slug: 'bh-roberts-national-lds-survey-2022',
    title: '2022 National Latter-day Saint Survey (NLDSS)',
    authors: ['B. H. Roberts Foundation'],
    year: 2022,
    source: 'B. H. Roberts Foundation',
    abstract: 'The 2022 National Latter-day Saint Survey (NLDSS) by the B. H. Roberts Foundation — an independent (non-Church-affiliated) national survey of U.S. Latter-day Saints covering belief, practice, demographics, and attitudes. Methodology and infographics are published in the foundation\'s linked press kit.',
    findings: [
      'Independent (non-Church-affiliated) national survey of U.S. Latter-day Saints.',
      'Covers belief, religious practice, demographics, and social attitudes.',
      'Companion baseline used alongside the 2023 Current and Former LDS Survey for cross-year comparisons.',
      'Published methodology and an infographics press kit at bhroberts.org.',
    ],
    tags: ['Belief', 'Survey', 'Demographics', 'Representative Sample'],
    external_url: 'https://bhroberts.org/projects/survey2022',
    secondary_url: 'https://bhroberts.org/2022NLDSS_infographic',
    source_type: 'study',
    category: 'Major Demographic Surveys',
    featured: false,
    limitations: 'Detailed sample size and response rate are published in the methodology PDF rather than the landing page. As with most surveys of low-incidence religious groups, the LDS subsample carries wider confidence intervals than the full survey.',
    flagged_problematic: false,
    flag_reason: null,
    context_note: null,
  },
];

for (const row of rows) {
  const { error } = await c.from('studies').upsert(row, { onConflict: 'slug' });
  if (error) { console.error(row.slug, error.message); process.exit(1); }
  console.log('upserted', row.slug);
}
