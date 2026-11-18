# Samuel Baird monorepo

Every website and project in one private repo. Each site deploys as its own Vercel project, with its Root Directory set to the folder below.

| Folder | Live at | Vercel project | Stack |
|---|---|---|---|
| `sites/samuelbaird.com` | https://samuelbaird.com | samuelbaird-com | static HTML, `scripts/build.mjs` |
| `sites/latter-day-stats` | https://samuelbaird.com/latter-day-stats | latter-day-stats | Next.js (basePath), Supabase |
| `sites/urim` | https://samuelbaird.com/urim | urim | static + Python pipeline |
| `sites/omni` | https://samuelbaird.com/omni (hidden: unlisted, noindex) | omni | Next.js (basePath) |
| `sites/peepstone` | https://samuelbaird.com/peepstone | peepstone | Next.js (basePath) |
| `sites/deseret-wiki` | https://deseret.wiki | deseret-wiki | Astro |
| `sites/deseret-mcp` | https://mcp.deseret.wiki | deseret-mcp | static + Node MCP |
| `extensions/deseret-chrome` | Chrome Web Store (not yet published) | — | MV3 extension; `node extensions/deseret-chrome/build.mjs` copies the Deseret MCP engine in |
| `projects/school`, `projects/collector-items`, `projects/content-creation` | private, not deployed | — | — |

## URLs

- Everything except the Deseret Wiki family lives at `https://samuelbaird.com/<id>`. samuelbaird.com's `vercel.json` rewrites `/<id>/*` to the app's own custom domain (`origin` in `packages/family/projects.json`), and each app runs under that base path.
- The old hosts (latterdaystats.samuelbaird.com, urim.samuelbaird.com, omni.samuelbaird.com, peepstone.vercel.app) 301 every page to the new path but keep their `/api` (and Peepstone's `/mcp`, LDS's `/auth`) endpoints answering, so connectors, webhooks and crons keep working. Don't remove those custom domains: they are the proxy origins.
- In the Next apps, Next adds the base path to `<Link>`, router and `redirect()` paths. Raw `<a>`/`<Script>` paths, OAuth callback URLs and `NextResponse.redirect` URLs need it added by hand (`BASE_PATH` in LDS's `src/lib/site.ts`).
- robots.txt only counts at the domain root, so the apps' private paths and sitemaps are listed in samuelbaird.com's robots.txt, generated from `projects.json` (`privatePaths`, `sitemap`).

## Shared style

All sites share the Deseret Wiki's look and one sidebar: see `packages/family/STYLE.md`. After changing the package or the project list, run `node scripts/family-sync.mjs`, then `node sites/samuelbaird.com/scripts/build.mjs`. `node scripts/dev-hub.mjs` serves the multi-zone routing locally on :4310.

## Rules

- The repo is private. Never list or link private projects (school, collector-items, content-creation) on any site. content-creation holds a pseudonymous channel whose anonymity rules forbid any link to Samuel Baird's names.
- **The Gospel Scholar Archive (GSA) is never public-facing.** Never link, embed or name corpus.restorationcommons.org, its bookshelf, page images or MCP host on a public page, API response, sitemap or llms.txt. Sites and tools may *use* it server-side (search it, then cite the book by author/title/year/page and link a public copy or an Amazon referral), but nothing may point back to it.
- Omni proxies GSA, so Omni stays hidden: `"hidden": true` in `projects.json` keeps it off every sidebar, footer, `/projects`, llms.txt and the sitemap, and robots.txt plus an `X-Robots-Tag` header keep `/omni` out of search. Its endpoint keeps working for the owner's connectors; don't publish its URL. Every other MCP (Peepstone, Deseret MCP, Latter-day Stats, Urim, Pulpit) may be public.
- antimormonstories and neomormonism are separate and must never be mentioned here or share this branding.
- Each site's own CLAUDE.md/README still applies inside its folder.

## Admin, tickets and single sign-on

- `samuelbaird.com/admin` (private, noindex, unlinked) is the owner's dashboard (ticket 0.4): revenue and people from `public.admin_dashboard_summary()` (migration `0062_admin_dashboard.sql`, aggregates only, owner only), the latest Vercel deploy per project (needs `VERCEL_TOKEN`, optional `VERCEL_TEAM`, on samuelbaird-com), a live uptime check, ticket counts and links to every admin tool. API: `sites/samuelbaird.com/api/admin/dashboard.js`. `/admin/tickets` is the project tracker: rows in `public.admin_tickets` (Latter-day Stats Supabase, migration `0061_admin_tickets.sql`), read and written by `sites/samuelbaird.com/api/admin/tickets.js`. RLS allows only the owner account (`public.is_site_owner()`, hardcoded like migration 0003), not every Latter-day Stats admin.
- One login for the whole domain: the Latter-day Stats Google login sets the Supabase session cookie on samuelbaird.com, so every app under `samuelbaird.com/*` can read it (`sites/samuelbaird.com/api/_lib/session.js`). Send people to `/latter-day-stats/login?return_to=/any/path` to come back anywhere on the domain. deseret.wiki is another domain and is not covered yet (ticket 0.1).
- New to-dos go in the ticket tracker, not in markdown files. Seed or bulk changes: a new numbered migration in latter-day-stats.
- **Agents reading a ticket:** you can't query the live tracker (owner-only RLS), so read its history in the repo: `grep -n "'<ref>'" sites/latter-day-stats/supabase/migrations/*.sql`. The seed is `0061_admin_tickets.sql`; later migrations append to `notes` in file order, so read them all, oldest first. A note starting "Agent brief:" holds the instructions for working the ticket. When the work merges, add a new migration that closes the ticket (see `0064_close_ticket_5_1.sql`).

## Retired repos

All nine old repos (deseret-mcp, omni, Peepstone, urim, deseret, collector-items, school, content_creation, latter-day-stats) are archived on GitHub. Nothing was lost:

- `archive/<repo>/<branch>`: every branch that was not merged into its old main, exactly as it was.
- `port/<repo>/<branch>`: those branches moved onto the monorepo layout. Triaged 2026-11-18: every school and content_creation port is merged into main except `port/content_creation/claude/vibrant-maxwell-w5mqsw` (superseded by `review/new-five-triage`). `port/deseret/local-buy-json` was dropped: a stale 40-item buy.json without the `kind` field that would have emptied the Buy page.
- Latter-day Stats branches without a port were already in main (squash-merged) or superseded; `archive/latter-day-stats/*` keeps them.
- `archive/content_creation/saint-capybara-visual-overhaul`: its review scripts and `docs/saint-capybara/common-issues` + `exemplars` are merged; its tooling (Chatterbox TTS, capy_build/qc/resolve_build, tone check, description generator), voices, agents and process docs are not, because they replace the locked Kokoro voice. `archive/content_creation/review/ig-dd4ahhgy8zj` is a subset of it plus a BITE review that `bite-model-football-script` supersedes.
- The old local folders (`AI projects/<repo>`) can no longer push. Work in this repo instead.
