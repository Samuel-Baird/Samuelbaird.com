-- Close ticket 5.1 (Urim translation test in es and pt): sites/urim/bench already scores
-- six April 2026 talks in Spanish and Portuguese against the official translations
-- (bench/results.md). Leaves the row alone if it was already closed in the UI.

update public.admin_tickets
   set status = 'done',
       notes = case when notes = '' then n.note else notes || E'\n' || n.note end
  from (select '2026-11-18: closed. The bench in sites/urim/bench covers it (six April 2026 talks, es and pt; see bench/results.md).'::text as note) n
 where ref = '5.1'
   and status not in ('done', 'dropped');
