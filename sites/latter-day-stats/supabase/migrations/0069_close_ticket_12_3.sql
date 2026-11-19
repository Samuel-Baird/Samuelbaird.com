-- Close ticket 12.3 (General Handbook change log) after /handbook-changes and
-- data/lds-handbook-changes.* shipped in PR #65.
-- Leaves 12.3 alone if it was already closed in the UI.

update public.admin_tickets
   set status = 'done',
       notes = case when notes = '' then n.note else notes || E'\n\n' || n.note end
  from (select '2026-11-19: closed. /handbook-changes and data/lds-handbook-changes.json/.csv shipped in PR #65 (882 section and chapter changes across all 15 releases from February 19, 2020 to October 22, 2026), refreshed weekly by .github/workflows/handbook-changes.yml.'::text as note) n
 where ref = '12.3'
   and status not in ('done', 'dropped');
