-- Close ticket 1.2 after the historic sites map and open dataset shipped in PR #60.
-- Leave the row alone if it was already closed in the UI.

update public.admin_tickets
   set status = 'done',
       notes = case when notes = '' then n.note else notes || E'\n' || n.note end
  from (select '2026-11-18: closed. PR #60 shipped the Church history map at /historic-sites and the open dataset in CSV and JSON.'::text as note) n
 where ref = '1.2'
   and status not in ('done', 'dropped');
