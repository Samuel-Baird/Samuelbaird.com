-- 2026-11-19: new ticket 14, the GSA request pipeline (torrenting worker + staff review queue).
-- GSA is private (rule R): hidden ticket, and the review page is login-only and noindex.
-- On conflict do nothing.

insert into public.admin_tickets
  (ref, parent_ref, title, summary, notes, category, status, visibility,
   priority, impact, traffic, revenue, ease, monetization, tags, links)
values
('14', null, 'GSA: request pipeline with an approve/deny review queue',
 'Missionary form requests (and bulk lists) go through the torrenting worker in projects/gsa, then wait in a simple review queue. A reviewer views the file, edits the name, picks the folder, and approves or denies it before anything reaches the Drive.',
$$Today: missionaries submit the request form; we read the responses, work through them by hand, then clear the submissions. This replaces that loop.

What the owner asked for (keep it plain, not flashy):
- A queue page: one row per candidate file with a ✓ approve button, an ✗ deny button and a View button that opens the file in a built-in PDF viewer.
- A text box with the proposed file name, editable. Use the manual's format: "Lastname, Title.pdf", "Lastname1 & Lastname2, Title.pdf".
- A folder picker with an auto-recommended folder (the closest existing shelf, usually under Read) that the reviewer can change.
- Approve uploads to the chosen Drive folder with that name; deny removes the candidate. Nothing is added to the Drive without approval.
- Prefer scans and true PDFs over EPUB-converted PDFs: rank them first, and flag a converted PDF (Calibre/ebook-converter producer, reflowed text with no page images) so the reviewer sees it.
- Access: login required, a short allowlist of Google accounts (owner plus a few GSA staff). Not the owner-only is_site_owner() check, which would lock staff out.

Agent brief:
- Read the root CLAUDE.md (GSA rule) and projects/gsa/README.md (intake, matching, acquisition, validation, publish, recovery, rollout phases) first.
- Rule R in full: the page is private (noindex, robots.txt, X-Robots-Tag, unlinked, not in projects.json, sidebar, sitemap or llms.txt). No GSA URLs, Drive IDs or staff config in the repo; secrets go in Worker secrets / Keychain.
- Pieces: (1) intake from the form (Forms responses.list, read-only, deduped by response ID) and bulk CSV into one queue; (2) the projects/gsa Mac worker finds, downloads and validates candidates (type, malware scan, completeness, SHA-256, duplicate check against the Table of Contents and destination folder) and stages them; (3) the review page; (4) on approve, upload to Drive, verify file ID/name/folder, then add the dated entry to Requests & Updates.
- Suggested home: a login-only page under samuelbaird.com/admin (reuses the domain-wide Google sign-in), with its own staff allowlist table and RLS, and the queue rows in Supabase. Staged files stay off public hosting; serve them to the viewer only through the authenticated API.
- Build on mock submissions and a sandbox Drive folder first (README rollout table); the live form and Drive need David's sign-off.
- Verify the queue works end to end at phone width, open a PR, and report what still needs staff access.$$,
 'tool', 'next', 'hidden', 4, 4, 1, 1, 2, '{}', '{gsa,torrenting,queue,review}',
 '[{"label":"Plan: projects/gsa/README.md","url":"https://github.com/Samuel-Baird/Samuelbaird.com/blob/main/projects/gsa/README.md"}]')
on conflict (ref) do nothing;
