-- 2026-11-18: close 2.2, note the 2.1 store submission, and add agent briefs to 12.1 and 12.3.
-- Notes are appended, never replaced. Status changes skip rows already closed in the UI.

create or replace function pg_temp.ticket_note(p_ref text, p_status text, p_note text)
returns void language sql as $$
  update public.admin_tickets
     set status = case when p_status is null or status in ('done', 'dropped') then status else p_status end,
         notes = case when notes = '' then p_note else notes || E'\n\n' || p_note end
   where ref = p_ref;
$$;

select pg_temp.ticket_note('2.2', 'done',
  '2026-11-18: closed. Plain caption conversion ships with the 2.1 extension (its live-update watcher). The stacked English + Deseret mode is dropped as too bulky.');

select pg_temp.ticket_note('2.1', null,
  '2026-11-18: submitted to the store; waiting on review. Close when it is live.');

-- 12.1 -------------------------------------------------------------------------------------
select pg_temp.ticket_note('12.1', null, $$Agent brief:
- Branch `feat/hymnbook` from origin/main. Read the root CLAUDE.md first (GSA rule, private projects).
- Build it the way /temples and /historic-sites are built (PRs #53 and #60): a dependency-free fetcher in sites/samuelbaird.com/scripts/, open data at sites/samuelbaird.com/data/lds-hymns.json and .csv, a /hymns page from scripts/build.mjs with a pre-rendered table and a schema.org Dataset, and links from /data and the sitemap.
- Records: one per hymn per edition. Fields: edition, number, title, first line, author(s), composer(s), year written, author's denomination, and whether it was added, kept or removed relative to the previous edition, plus a source URL.
- Editions: the 1835 Emma Smith collection, the major Church hymnbooks after it, the 1985 Hymns, and Hymns—For Home and Church. Start with 1985 against Hymns—For Home and Church (most searched), then go back in time.
- Sources: the Church's own hymn pages for current editions; hymnary.org, Wikidata and public-domain scans (archive.org, BYU ScholarsArchive) for older editions and authors. Every record keeps its source URL. Never fill a fact from memory; leave it blank.
- Copyright: facts only. Full lyrics only for texts published before 1930; quote nothing else beyond the first line.
- Page: search, an edition filter, "added/removed in this edition" views, and per-hymn history. State it is not an official Church site. Add Deseret entries for the title words (scripts/deseret-words.mjs).
- Verify: build.mjs and family-sync --check; revert timestamp-only and line-ending-only changes; check the page at phone width. Open a PR, do not merge, and report record counts per edition and gaps.$$);

-- 12.3 -------------------------------------------------------------------------------------
select pg_temp.ticket_note('12.3', null, $$Agent brief:
- Branch `feat/handbook-changes` from origin/main. Read the root CLAUDE.md first.
- Build it like /temples (PR #53): a dependency-free fetcher, open data at sites/samuelbaird.com/data/lds-handbook-changes.json and .csv, a /handbook-changes page with a pre-rendered table and a schema.org Dataset, and links from /data and the sitemap.
- Records: one per change. Fields: date published, chapter and section number, section title, kind (new, revised, removed, renumbered), a one-line description in your own words, and the official URL of the section and of the announcement.
- Sources: the General Handbook on churchofjesuschrist.org, starting from the Church's own published summaries of updates; Church News and Newsroom articles for older changes. Every record keeps its source URL. Never fill a fact from memory.
- Copyright: describe changes in your own words. Do not copy handbook text beyond a few words to identify a passage.
- Page: a timeline newest first, a filter by chapter, and search. State it is not an official Church site. Add Deseret entries for the title words.
- Later, optional: a weekly workflow like .github/workflows/temples.yml that notices new update summaries.
- Verify: build.mjs and family-sync --check; revert timestamp-only and line-ending-only changes; check the page at phone width. Open a PR, do not merge, and report how far back the log goes.$$);
