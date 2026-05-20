import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';
const env = Object.fromEntries(
  readFileSync(new URL('../.env.local', import.meta.url), 'utf8')
    .split('\n').filter(l => l.includes('=')).map(l => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);
const c = createClient(env.NEXT_PUBLIC_SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY);

const UTAH_DEFAULT_CONTEXT = 'Utah and "Latter-day Saint" are not synonymous. Only roughly 40% of Utahns identify as Latter-day Saint (see Cragun & Brewer, "Mormons Are No Longer a Majority in Utah: Causes, Consequences, and Implications for the Sociology of Religion," 2023 — https://doi.org/10.1093/socrel/srad022). Findings about Utah should not be applied to or attributed to the Latter-day Saint population without further analysis isolating religious affiliation.';

const row = {
  slug: 'chevinsky-2021-ssb-intake-50-states',
  title: 'Prevalence of Self-Reported Intake of Sugar-Sweetened Beverages Among US Adults in 50 States and the District of Columbia, 2010 and 2015',
  authors: ['Jennifer R. Chevinsky', 'Seung Hee Lee', 'Heidi M. Blanck', 'Sohyun Park'],
  year: 2021,
  source: 'Preventing Chronic Disease (CDC), 18:E35',
  abstract: 'Cross-sectional analysis of combined 2010 and 2015 National Health Interview Survey Cancer Control Supplement data estimating the state-level prevalence of daily sugar-sweetened beverage (SSB) intake among US adults aged 18 and older. Roughly two-thirds of US adults reported consuming SSBs at least daily, with substantial variation across states and sociodemographic groups. The authors recommend that interventions account for geographic and sociodemographic differences in SSB consumption.',
  findings: [
    'About 63% of US adults reported consuming sugar-sweetened beverages at least once per day, combined across 2010 and 2015.',
    'Utah daily SSB prevalence was 53.6% (95% CI 49.1–58.1), n = 734 — below the national average and in the lower-to-middle tier of states.',
    'Six states exceeded 70% daily SSB prevalence: Hawaii, Arkansas, Wyoming, South Dakota, Connecticut, and South Carolina.',
    'Daily SSB intake varied significantly by sex, age, race/ethnicity, education, and income across states.',
  ],
  tags: ['Utah', 'Nutrition', 'Public Health', 'NHIS', 'State Comparison'],
  external_url: 'https://pubmed.ncbi.nlm.nih.gov/33856977/',
  secondary_url: 'https://www.cdc.gov/pcd/issues/2021/20_0434.htm',
  source_type: 'study',
  category: 'Utah',
  featured: false,
  limitations: 'Self-reported intake (no objective measurement); frequency only, with no volume or amount captured; data are from 2010 and 2015 and may not reflect current consumption (SSB intake has declined over time); combining two survey years can mask within-period changes. State-level sample sizes vary, and the survey does not capture religious affiliation, so Utah-specific findings cannot be partitioned by religion.',
  context_note: UTAH_DEFAULT_CONTEXT,
};

const { data, error } = await c.from('studies').upsert(row, { onConflict: 'slug' }).select('slug');
if (error) { console.error(error); process.exit(1); }
console.log('upserted', data);
