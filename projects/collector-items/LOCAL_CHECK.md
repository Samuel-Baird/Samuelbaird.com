# Local check procedure (runs on the homelab Mac Studio, in Chrome)

The daily scout run (`RUNBOOK.md`, 7:00) uses WebFetch, which cannot open most marketplace
pages (403/404/410), so its leads are mostly snippets. This local check runs at 8:00 on the
same Mac Studio (launchd job `com.samuel.scout.check`, wrapper `~/Scout/bin/scout-run.sh check`,
dedicated clone `~/Scout/Samuelbaird.com`), uses the real Chrome
browser, and does two jobs: verify the scout run's leads, and search the sites WebFetch cannot reach.

**Report only.** Never bid, buy, add to cart, message a seller, create an account, sign
in, enter credentials, accept site terms, or solve a CAPTCHA. If a site demands a login
or CAPTCHA, skip it and record it as `blocked`.

Use the Claude in Chrome tools. Open each page in a tab you create, and close every tab
you opened when finished.

## 1. Load
- `git pull` in the monorepo checkout (`Samuel-Baird/Samuelbaird.com`, wherever the machine
  running this keeps it; check out `main`
  and make sure the working tree is clean first. If it is not clean, stop and say so).
  This folder is `projects/collector-items` in that repo; the old `collector-items` repo is archived.
- Read today's run in `sites/samuelbaird.com/scout/leads.json` (the entry whose `date` is
  today; if there is none yet, create it with empty `leads`).
- Read `scouts/artifact-scout.md`, `scouts/common-cup.md`, `wants.md`,
  `state/seen.json`, `state/dismissed.json`.

## 2. Verify existing leads
For every lead in today's run with `status: "unknown"` (and the most recent earlier run's
unknown leads), skipping dismissed URLs:
1. Open the URL in Chrome.
2. Decide from the page itself: `live` (available / bidding open / add-to-cart present),
   `sold` (sold banner, "no longer available", sale price shown on a closed lot),
   `ended` (auction over), or `gone` (404/410 or redirects to a generic page).
3. For `live`, also set `price` from the page, `image` from `og:image` or the main product
   photo (direct https URL, never a stock image), and `verified: true`.
4. Remove `sold`, `ended` and `gone` leads from `leads.json`, and record their status in
   `state/seen.json`.

## 3. Search the platforms WebFetch cannot reach
For each platform below, run searches with a rotating subset of the scout search terms
(every term at least weekly) **plus all Special Alert, Deseret Alphabet, common-cup and
`wants.md` terms every day**. Open candidate listings and verify they are live.
- eBay: `https://www.ebay.com/sch/i.html?_nkw=TERM&LH_BIN=1` and `...&LH_Auction=1`
  (active listings only; never report ended or sold)
- AbeBooks: `https://www.abebooks.com/servlet/SearchResults?kn=TERM`
- Biblio: `https://www.biblio.com/search.php?keyisbn=TERM`
- ViaLibri: `https://www.vialibri.net/searches_results?q=TERM`
- LiveAuctioneers: `https://www.liveauctioneers.com/search/?q=TERM` (open lots only)
- Heritage Auctions: `https://www.ha.com/c/search-results.zx?N=0&Ntt=TERM`
- RR Auction: `https://www.rrauction.com/search/?q=TERM`
- Etsy: `https://www.etsy.com/search?q=TERM`
- WorthPoint: `https://www.worthpoint.com/search?query=TERM`
- Estante Virtual: `https://www.estantevirtual.com.br/busca?q=TERM`
- Mercado Livre Brasil: `https://lista.mercadolivre.com.br/TERM`
- Dealers: Ken Sanders Rare Books, Moon's Rare Books, Schilb Antiquarian, Panoply Books

Apply every reject/avoid rule in the scout files (reprints, glass or plastic cups,
post-1900 cross-tradition vessels, budget limits). Skip URLs already in `seen.json` or
`dismissed.json` (normalized as `host/path?query`, see RUNBOOK.md),
except re-report a seen URL if its price dropped by 25% or more.

## 4. Write results
- Add new live finds to today's run in `leads.json` in the same shape as the existing
  entries (`title`, `price`, `seller`, `url`, `more_urls`, `date`, `category`, `alert`,
  `verified: true`, `status: "live"`, `image`, `notes`, `action`). Categories are exactly:
  `Deseret Alphabet`, `LDS sacrament ware`, `Early LDS print`, `Anti-Mormon literature`,
  `Portuguese-language LDS`, `LDS relics & art`, `Luther & Reformation`,
  `Historic Christianity`, `Communion vessels (pre-1900)`, `Wants`.
- Set or replace the run's `coverage` list: one `{site, status: searched|blocked|skipped,
  results}` object per platform above, plus any the scout run recorded. Update `searches`
  and `summary` to include the local check.
- Add every new, sold, ended and gone URL to `state/seen.json`.
- Append a "Local check" section to `projects/collector-items/reports/<today>.md`.
- Commit and push to `main` in one commit ("Local check YYYY-MM-DD"): the files under
  `projects/collector-items/` and `sites/samuelbaird.com/scout/leads.json`. Do not touch any
  other file under `sites/`. The push redeploys samuelbaird.com to Cloudflare.
- If the local check added verified Special Alert items, add a comment to today's GitHub
  issue (or open `Scout YYYY-MM-DD: N finds`, label `alert`, if the scout run opened none).
