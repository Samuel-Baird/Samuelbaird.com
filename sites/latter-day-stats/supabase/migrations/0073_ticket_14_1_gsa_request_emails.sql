-- 2026-11-19: ticket 14.1, email requesters when their GSA material is added (idea, from the owner).
-- GSA is private (rule R): hidden ticket. No GSA URLs, Drive IDs or form IDs here.
insert into public.admin_tickets
  (ref, parent_ref, title, summary, notes, category, status, visibility,
   priority, impact, traffic, revenue, ease, monetization, tags, links)
values
('14.1', '14', 'GSA: email requesters when their material is added',
 'Requests come in through a Google Form, so the pipeline could send each requester an email once their requested material has been added to the Drive.',
$$Owner idea, noted 2026-11-19. Not started.

What exists:
- The request form already collects verified email addresses, so each Forms response carries respondentEmail. The intake poller deliberately does not store it today.
- Publication ends with a verified Drive file ID and a dated Requests & Updates entry; that is the natural trigger.

Sketch:
- On intake, keep the respondent email with the form request (private SQLite only), linked to each work triaged from that response.
- After a verified upload and changelog entry, send one short email per requester: what was added, where to find it in the archive, and the dated entry. Several requesters of one work each get their own email; a response that names several works gets one email per added work (or a digest).
- Record the send in the pipeline's append-only events so retries never send twice.
- Also consider a "can't add this one" email for requests closed as not available.

Needs before building:
- Staff approval of notifications (already on the decisions list for David), the sending account, and the wording.
- A sending path: Gmail API send scope on a staff-approved account, or an Apps Script on the form owner's account.
- Retention: how long requester emails are kept, and deleting them after the notice is sent.$$,
 'tool', 'idea', 'hidden', 3, 3, 1, 1, 3, '{}', '{gsa,notifications,email,forms}', '[]')
on conflict (ref) do nothing;
