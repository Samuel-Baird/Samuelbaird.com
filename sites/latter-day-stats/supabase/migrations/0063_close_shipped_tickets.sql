-- Ticket tracker housekeeping, 2026-11-18: close what shipped and move work that is waiting
-- on a merge or a manual step to "review". Rows already marked done or dropped in the UI
-- are left alone, and notes are appended, never replaced.

create or replace function pg_temp.ticket_note(p_ref text, p_status text, p_note text)
returns void language sql as $$
  update public.admin_tickets
     set status = p_status,
         notes = case when notes = '' then p_note else notes || E'\n' || p_note end
   where ref = p_ref
     and status not in ('done', 'dropped');
$$;

-- Shipped (merged to main) ---------------------------------------------------------------
select pg_temp.ticket_note('R.1', 'done',
  '2026-11-18: shipped in PR #52. Omni is hidden (projects.json "hidden", robots.txt, X-Robots-Tag).');
select pg_temp.ticket_note('0', 'done',
  '2026-11-18: tracker shipped in PR #52. The broader dashboard continues as 0.4.');
select pg_temp.ticket_note('1.1', 'done',
  '2026-11-18: shipped in PR #53: /temples map plus /data/lds-temples.json and .csv, refreshed weekly by .github/workflows/temples.yml.');
select pg_temp.ticket_note('13', 'done',
  '2026-11-18: shipped in PR #55. Sun, moon and stars on every family site; each site already had its own sidebar.');

-- Merged, waiting on a manual step ----------------------------------------------------------
select pg_temp.ticket_note('2.1', 'review',
  '2026-11-18: extension merged in PR #54 (extensions/deseret-chrome). Left: try dist/ unpacked in Chrome, then publish to the Chrome Web Store ($5 developer account).');

-- Open PRs ---------------------------------------------------------------------------------
select pg_temp.ticket_note('0.3', 'review',
  '2026-11-18: PR #58 puts every referral tag in packages/family/referrals.mjs. Left: apply to eBay Partner Network, then set EBAY_CAMPAIGN_ID.');
select pg_temp.ticket_note('0.4', 'review',
  '2026-11-18: PR #56. Before merging: apply migration 0062 and set VERCEL_TOKEN on the samuelbaird-com Vercel project.');
select pg_temp.ticket_note('1.2', 'doing',
  '2026-11-18: in progress on feat/historic-sites: /historic-sites map and open dataset, built the same way as /temples.');

-- Possibly already covered: decide in the UI --------------------------------------------
select pg_temp.ticket_note('5.1', 'review',
  '2026-11-18: sites/urim/bench already scores six April 2026 talks in es and pt against the official translations (bench/results.md). Close this if that counts as the test, or run a whole conference.');
