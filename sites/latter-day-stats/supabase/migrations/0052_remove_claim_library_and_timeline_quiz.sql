-- Remove the public claim library (0044) and the timeline quiz (0038).
--
-- Both features and every page/route that used them have been removed from
-- the app. claim_occurrences and claims are dropped outright; the promotion
-- link column added onto hub_claims by 0044 goes with them, but hub_claims
-- itself (0039) stays — the hub keeps recording per-video claims, it just has
-- no public promotion path anymore.
--
-- quiz_answers (0038) was the eternal-increase/timeline quiz's answer store.
-- This is unrelated to evangelical_quiz_answers (0045), which stays.

drop table if exists public.claim_occurrences;

alter table public.hub_claims drop column if exists claim_id;

drop table if exists public.claims;

drop function if exists public.claims_search_tsv_refresh();

drop table if exists public.quiz_answers;
