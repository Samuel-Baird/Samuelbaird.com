import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';
const env = Object.fromEntries(
  readFileSync(new URL('../.env.local', import.meta.url), 'utf8')
    .split('\n').filter(l => l.includes('=')).map(l => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);
const c = createClient(env.NEXT_PUBLIC_SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY);

const row = {
  slug: 'mormon-metrics-ex-mormon-political-affiliation-2026',
  title: 'Ex-Mormons Are the Most Republican Religious Leavers in America',
  authors: ['Alex Bass'],
  year: 2026,
  source: 'Mormon Metrics (Substack)',
  abstract: 'A secondary analysis of Pew\'s 2014 and 2024 Religious Landscape Studies examining political party identification among people who left the religion they were raised in. The analysis finds that disaffiliated Latter-day Saints are the only major religious leaver group in which Republicans outnumber Democrats — and that ex-Mormon Republican identification grew from 32% to 41% between the two survey waves, challenging the common perception that ex-Mormons are predominantly progressive.',
  findings: [
    'Among ex-Mormons, 41% identify as Republican and 37% as Democrat (Pew RLS 2024, n=316 disaffiliated; leaners folded into their party).',
    'Ex-Mormons are the only major religious tradition in America where Republicans outnumber Democrats among religious leavers.',
    'Ex-Mormon Republican identification increased from 32% (2014) to 41% (2024); the author notes this shift alone lacks statistical significance but is analytically consistent.',
    'For comparison, Jewish, Muslim, Buddhist, Orthodox Christian, Protestant, and Catholic leavers all lean Democratic by wide margins (49–64% Democratic).',
    'The visible ex-Mormon community (podcasters, memoirists) skews progressive, creating availability bias that obscures the broader partisan distribution of those who leave.',
  ],
  tags: ['Political Identity', 'Disaffiliation', 'Party Affiliation', 'Pew RLS', 'Ex-Mormon'],
  external_url: 'https://mormonmetrics.com/p/ex-mormons-are-the-most-republican',
  secondary_url: null,
  source_type: 'secondary_analysis',
  category: 'Retention & Generational Change',
  featured: false,
  limitations: 'Small ex-Mormon sample (n=316 disaffiliated); the author explicitly flags that the 2014-to-2024 partisan shifts are not statistically significant in isolation. Leaners folded into their party, which reduces the Independent share and may overstate partisan polarization. Pew RLS is a cross-sectional survey, so it cannot determine whether political identity changed before or after disaffiliation.',
};

const { data, error } = await c.from('studies').upsert(row, { onConflict: 'slug' }).select('slug');
if (error) { console.error(error); process.exit(1); }
console.log('upserted', data);
