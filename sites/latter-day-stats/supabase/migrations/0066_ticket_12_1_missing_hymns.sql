-- 2026-11-18: record the hymns still missing from the 12.1 hymnbook dataset (PR #64), so they can be
-- tracked down later. Appends to notes; leaves status alone.

update public.admin_tickets
   set notes = case when notes = '' then n.note else notes || E'\n\n' || n.note end
  from (select $$2026-11-18: missing hymns to find (live list: samuelbaird.com/data/lds-hymns-missing.csv; notes on what was tried and where to look in sites/samuelbaird.com/scripts/hymn-missing.json):
- 1841 Nauvoo no. 75: the Joseph Smith Papers table of contents skips it. Entered by hand from the archive.org scan (collectionofsacr01smit, printed p. 83) as "O thou in whose presence". Check the page image, then set verify to false in scripts/hymn-additions.json.
- Hymns (1985) no. 86 How Great Thou Art, no. 219 Because I Have Been Given Much, no. 299 Children of Our Heavenly Father: no first line. The Church's pages and PDFs show only a licensing notice. Check a printed 1985 hymnbook (or its Index of First Lines) or hymnary.org in a browser. Wikidata has candidates for 219 and 299, but the 1985 texts are altered, so don't use them unchecked.
- Hymns—For Home and Church 1079-1200: not published yet; rerun node scripts/fetch-hymns.mjs after each release.
- Editions still to add: Sacred Hymns and Spiritual Songs (1840-1912), Latter-day Saint Hymns (1927), Hymns (1948/1950).$$::text as note) n
 where ref = '12.1';
