-- Close ticket 12.1 (hymnbook dataset): /hymns and data/lds-hymns.* shipped in PR #64.
-- The gaps it left are carried into a new ticket, 12.4, so they stay on the list.
-- Leaves 12.1 alone if it was already closed in the UI; on conflict do nothing for 12.4.

update public.admin_tickets
   set status = 'done',
       notes = case when notes = '' then n.note else notes || E'\n\n' || n.note end
  from (select '2026-11-18: closed. /hymns and data/lds-hymns.json/.csv shipped in PR #64 (1835, 1841, 1985 and Hymns—For Home and Church so far; 837 records). Missing hymns and later editions moved to 12.4.'::text as note) n
 where ref = '12.1'
   and status not in ('done', 'dropped');

insert into public.admin_tickets
  (ref, parent_ref, title, summary, notes, category, status, visibility,
   priority, impact, traffic, revenue, ease, monetization, tags, links)
values
('12.4', '12', 'Hymnbook: find the missing hymns and add the editions between 1841 and 1985',
 'Fill the gaps listed at samuelbaird.com/data/lds-hymns-missing.csv, then add the 1840-1912 Sacred Hymns and Spiritual Songs, Latter-day Saint Hymns (1927) and Hymns (1948/1950).',
$$Gaps (notes on what was tried and where to look: sites/samuelbaird.com/scripts/hymn-missing.json; add finds to scripts/hymn-additions.json with their source, then run node scripts/fetch-hymns.mjs and the build):
- 1841 Nauvoo no. 75: entered from the archive.org scan (collectionofsacr01smit, p. 83) as "O thou in whose presence". Check the page image, then set verify to false.
- Hymns (1985) no. 86 How Great Thou Art, no. 219 Because I Have Been Given Much, no. 299 Children of Our Heavenly Father: no first line online (licensing notice only). Check a printed 1985 hymnbook or hymnary.org in a browser.
- Hymns—For Home and Church 1079-1200: not published yet; rerun the fetcher after each release.
Editions: scans are on archive.org (hymns-1948, latter-day-saint-hymns-1927-a, sacredhymnsspiri00chur*); their OCR indexes need hand checking. Once 1948/1950 is in, 1985 gets added/kept/removed.$$,
 'data', 'backlog', 'public', 3, 4, 3, 2, 2, '{print}', '{editions,hymns}',
 '[{"label":"Known gaps (CSV)","url":"https://samuelbaird.com/data/lds-hymns-missing.csv"},{"label":"/hymns","url":"https://samuelbaird.com/hymns"}]')
on conflict (ref) do nothing;
