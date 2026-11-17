import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';
const env = Object.fromEntries(
  readFileSync(new URL('../.env.local', import.meta.url), 'utf8')
    .split('\n').filter(l => l.includes('=')).map(l => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);
const c = createClient(env.NEXT_PUBLIC_SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY);

const row = {
  slug: 'strong-torn-disaffiliation-survey',
  title: 'Torn: Why People We Love Are Leaving the Church and What We Can Learn from Them',
  authors: ['Jeff Strong'],
  year: 2026,
  source: 'Self-published (forthcoming book) — surfaced via Deseret News opinion coverage',
  abstract: 'A ~20,000-respondent survey of current and former Latter-day Saints, recruited through social-media posts (including Reddit\'s ex-Mormon community) and the mailing lists of both apologetic and ex-Mormon podcasts. The survey is the data basis for the forthcoming book "Torn." A widely circulated headline finding is that roughly 1 in 3 active members surveyed "no longer believes the Church is what it claims."',
  findings: [
    'Reports that roughly 1 in 3 active members in the sample say they no longer believe the Church is what it claims.',
    'Recruitment via Reddit ex-Mormon communities, apologetic podcasts, and ex-Mormon podcast mailing lists.',
    'Sample size approximately 20,000 respondents.',
  ],
  tags: ['Disaffiliation', 'Survey', 'Belief', 'Online Sample'],
  external_url: 'https://www.deseret.com/opinion/2026/05/07/latter-day-saint-stats-representative-data/',
  secondary_url: null,
  source_type: 'study',
  category: 'Retention & Generational Change',
  featured: false,
  limitations: 'Non-probability online recruitment from highly activated communities (Reddit r/exmormon, apologetic and ex-Mormon podcast lists). Sample frame is not the LDS membership at large.',
  flagged_problematic: true,
  flag_reason: 'Severe selection bias: recruitment was concentrated in self-selected online communities — most prominently Reddit\'s ex-Mormon forum and ex-Mormon / apologetic podcast mailing lists — which dramatically oversample disaffiliated, questioning, and activated members relative to typical Sunday attendance. Despite this, headline figures (e.g., "1 in 3 active members no longer believes") are presented as if generalizable to active Latter-day Saints overall. They are not. This sample frame cannot support population-level claims about belief among active members; comparable probability samples (Pew RLS 2023–24, BYU Religious Seismology Survey, Global Flourishing Study) show very different distributions.',
  context_note: 'Use this study only as a description of the surveyed online sample, not as evidence about active Latter-day Saints generally. For population-representative belief and retention figures, see Pew RLS 2023–24, the BYU Religious Seismology Survey, and the Next Mormons Survey.',
};

const { data, error } = await c.from('studies').upsert(row, { onConflict: 'slug' }).select('slug');
if (error) { console.error(error); process.exit(1); }
console.log('upserted', data);
