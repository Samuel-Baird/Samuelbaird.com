# Daily run procedure

You are the daily collector scout for Samuel Baird. Follow this procedure exactly.
You **report only**: never bid, buy, reserve, message a seller, create accounts,
or enter any credentials.

## 1. Load
Read `scouts/artifact-scout.md`, `scouts/common-cup.md`,
`wants.md`, and `state/seen.json`. Note today's date.

## 2. Search
Run web searches and page fetches for each scout:
- **Artifact scout:** rotate through the search-term lists so every term is covered at
  least once a week; every day, cover the Special Alert topics (LDS/anti-Mormon 19th
  century, Times and Seasons, Millennial Star, Portuguese-language LDS pre-1960,
  sacrament cups/trays, Deseret Alphabet, pre-1800 communion vessels).
- **Common cup:** run every search term daily.
- **wants.md:** search for each listed item daily.

### Depth requirements (do not stop early)
- Run at least 40 distinct web searches per run, in parallel batches, covering every
  scout. A run that did fewer than ~25 searches is a failed run; say so in the report.
- If a site cannot be fetched (e.g. "host not allowed"), do NOT give up on it: search for
  it with `site:` queries and use the search-result titles, snippets and URLs as leads.
  Keep going with other sites; list blocked hosts once in the report's coverage section.

## 3. Verify each candidate
Open the listing. Confirm it is live (not ended/sold), read the price, and apply the
reject and avoid rules of the relevant scout (glass/plastic cups, reprints, undated
or post-1900 cross-tradition vessels, over-budget items that are not exceptional).
Never report an item without a direct listing URL.

## 4. Dedupe
Skip any URL already in `state/seen.json`, unless its price has dropped ≥25% since
the recorded price.

## 5. Write the report
Create `reports/YYYY-MM-DD.md` with a section per scout using that scout's report
format. Put Special Alert items first. List any platform or page you could not read,
so coverage gaps are visible. If nothing is new, write a short "nothing new" report.
Add new items to `state/seen.json`, then commit and push to `main`.

### Unverified leads
If a promising item matches a Special Alert or a want but its listing page could not be
opened (blocked host), still report it in a separate "Unverified leads" section of the
report and the issue, with the URL, whatever price/date the search result showed, and a
clear "could not verify live/original" note. Do not add it to `seen.json` as verified;
record it with `"verified": false` so it is not repeated daily unless its status changes.

## 6. Notify
If there are new finds, open one GitHub issue in this repository:
- Title: `Scout YYYY-MM-DD: N finds`
- Body: the report content (alerts first), with every item's link.
- Label `alert` if any Special Alert item is included (create the label if missing).
If there are no new finds, open no issue.

## 7. Publish to the private leads page
After step 5, update the bookmark-only page https://samuelbaird.com/scout (not linked
anywhere on the site; it has noindex set). It reads `scout/leads.json` in the
`Samuel-Baird/samuelbaird.com` repo.
- Attach that repo (`add_repo`, push access) and clone it with `--depth 1`.
- In `scout/leads.json`, add or replace the entry in `runs` for today's date. Keep the
  same shape as the existing entries: `date`, `searches`, `summary`, `leads` (each with `title`, `price`,
  `seller`, `url`, `more_urls`, `date`, `category`, `alert`, `verified`, `notes`, `action`),
  `nothing_found`, `coverage_gaps`, `issue`. Set `updated` to today. Keep the last 60 runs.
- Write a run entry even when nothing is new, with empty `leads` and the summary saying so.
- Do not touch any other file in that repo. Commit `Scout leads YYYY-MM-DD` and push to `main`
  (Vercel deploys it). If this step fails, say so in the report and the issue.
