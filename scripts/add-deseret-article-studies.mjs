import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';
const env = Object.fromEntries(
  readFileSync(new URL('../.env.local', import.meta.url), 'utf8')
    .split('\n').filter(l => l.includes('=')).map(l => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);
const c = createClient(env.NEXT_PUBLIC_SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY);

const inserts = [
  {
    slug: 'bh-roberts-current-former-lds-survey-2023',
    title: 'Current and Former Latter-day Saint Survey (2023)',
    authors: ['B.H. Roberts Foundation'],
    year: 2023,
    source: 'B.H. Roberts Foundation',
    abstract: 'A 2023 representative survey of current and former Latter-day Saints in the LDS Corridor region. Recruitment used random mail routes weighted to U.S. Religious Census proportions — a probability-based sample frame, in contrast to convenience-recruited online surveys of disaffiliated members.',
    findings: [
      'Over 85% of respondents believed Joseph Smith saw God the Father and Jesus Christ.',
      'Around 90% believed the Book of Mormon is a true record of ancient people.',
      'Recruitment used random mail routes weighted to U.S. Religious Census proportions for the LDS Corridor.',
    ],
    tags: ['Belief', 'Survey', 'Representative Sample', 'LDS Corridor'],
    external_url: 'https://www.deseret.com/opinion/2026/05/07/latter-day-saint-stats-representative-data/',
    secondary_url: null,
    source_type: 'study',
    category: 'Major Demographic Surveys',
    featured: false,
    limitations: 'LDS Corridor sample (Utah / surrounding states) — does not represent Latter-day Saints outside the Mountain West. Mail-recruited surveys still face response-rate bias even when the frame is random.',
  },
  {
    slug: 'burge-danforth-lds-belief-2023',
    title: 'Danforth Center on Religion and Politics — Latter-day Saint Belief Analysis',
    authors: ['Ryan Burge'],
    year: 2023,
    source: 'Danforth Center on Religion and Politics (Washington University in St. Louis)',
    abstract: 'Analysis by political scientist Ryan Burge of a nationally representative sample of 907 Latter-day Saints, measuring core Christian belief by attendance level. Cited in Deseret News coverage as a counterweight to non-representative online surveys of LDS belief.',
    findings: [
      '96% of weekly-attending Latter-day Saints agreed Jesus was resurrected.',
      '92% of weekly attenders identified Jesus as the Son of God.',
      '85% of all Latter-day Saints (regardless of attendance) said Jesus is the Son of God.',
      'Nationally representative sample of 907 Latter-day Saints.',
    ],
    tags: ['Belief', 'Christology', 'Survey', 'Representative Sample'],
    external_url: 'https://www.deseret.com/opinion/2026/05/07/latter-day-saint-stats-representative-data/',
    secondary_url: null,
    source_type: 'secondary_analysis',
    category: 'Belief & Practice',
    featured: false,
    limitations: 'LDS subsample of n=907 carries a wider margin of error than the full survey; cross-sectional snapshot.',
  },
];

// Update the existing Pew 2012 row with the specific belief figures cited in the article.
const pewUpdate = {
  slug: 'pew-2012-mormons-beliefs-practices',
  patch: {
    findings: [
      '91% of Latter-day Saints believed the Book of Mormon was written by ancient prophets and translated by Joseph Smith.',
      '94% believed the Church president is a prophet of God.',
      'Baseline portrait of U.S. Latter-day Saints across belief, practice, family life, and demographics.',
      'Frequently cited as the comparison baseline for later Pew waves.',
    ],
    external_url: 'https://www.pewresearch.org/religion/2012/01/12/mormons-in-america-executive-summary/',
  },
};

for (const row of inserts) {
  const { error } = await c.from('studies').upsert(row, { onConflict: 'slug' });
  if (error) { console.error(row.slug, error.message); process.exit(1); }
  console.log('upserted', row.slug);
}

const { error: pErr } = await c.from('studies').update(pewUpdate.patch).eq('slug', pewUpdate.slug);
if (pErr) { console.error('pew update', pErr.message); process.exit(1); }
console.log('updated', pewUpdate.slug);
