import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';
const env = Object.fromEntries(readFileSync(new URL('../.env.local', import.meta.url), 'utf8').split('\n').filter(l=>l.includes('=')).map(l=>{const i=l.indexOf('=');return [l.slice(0,i).trim(),l.slice(i+1).trim()];}));
const c = createClient(env.NEXT_PUBLIC_SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY);
const { data, error } = await c.from('studies').select('slug,title,authors,year,source,abstract,findings,tags,external_url,secondary_url,source_type,category,featured,limitations,flagged_problematic,flag_reason,context_note,pdf_path').order('slug');
if (error) { console.error(error); process.exit(1); }
console.log(JSON.stringify(data, null, 2));
