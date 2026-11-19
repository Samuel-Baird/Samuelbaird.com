# Samuel Baird monorepo

Every website and project in one private repo. Each site deploys as its own Cloudflare Worker (`sites/<folder>/wrangler.jsonc`), by `.github/workflows/deploy.yml` on every push to main that touches its folder or `packages/family`. (Until the Vercel projects are deleted after cutover, their `vercel.json` files stay in place; don't rely on them.)

**Read [`GOALS.md`](GOALS.md) first.** It holds the owner's immediate, 5-year and long-term goals. Right now school comes first and family time is protected. Use it to decide what matters before you plan or prioritize anything.

## Agent instructions

- **Never say "Chrome is disconnected."** If the Claude in Chrome (or ChatGPT) extension isn't responding, open Chrome yourself with Computer Use, or from the shell, in the right profile, then try again: `open -na "Google Chrome" --args --profile-directory="Profile 1"` (b13llama@gmail.com, used for almost every project) or `--profile-directory="Default"` (samuel.baird@transfigurism.org, used for MTA and spare-usage personal projects). You can also click the profile picker with Computer Use. Only ask the owner after both of those fail, and say what you tried.

| Folder | Live at | Worker | Stack |
|---|---|---|---|
| `sites/samuelbaird.com` | https://samuelbaird.com | samuelbaird-com | static HTML, `scripts/build.mjs`; `worker/index.mjs` runs `api/` and forwards the apps |
| `sites/latter-day-stats` | https://samuelbaird.com/latter-day-stats | latter-day-stats | Next.js (basePath) on OpenNext, Supabase, Cron Triggers |
| `sites/urim` | https://samuelbaird.com/urim | urim | static + Python pipeline |
| `sites/omni` | https://samuelbaird.com/omni (hidden: unlisted, noindex) | omni | Next.js (basePath) on OpenNext |
| `sites/peepstone` | https://samuelbaird.com/peepstone | peepstone | Next.js (basePath) on OpenNext |
| `sites/deseret-wiki` | https://deseret.wiki | deseret-wiki | Astro, static assets only |
| `sites/deseret-mcp` | https://mcp.deseret.wiki | deseret-mcp | static + Node MCP |
| `extensions/deseret-chrome` | Chrome Web Store (not yet published) | — | MV3 extension; `node extensions/deseret-chrome/build.mjs` copies the Deseret MCP engine in |
| `projects/school`, `projects/collector-items`, `projects/content-creation` | private, not deployed | — | — |

## URLs

- Everything except the Deseret Wiki family lives at `https://samuelbaird.com/<id>`. The samuelbaird-com Worker (`sites/samuelbaird.com/worker/index.mjs`) forwards `/<id>` and `/<id>/*` to the app's Worker over a service binding (Host stays samuelbaird.com), and each app runs under that base path. Without a binding (local dev) it proxies the app's `origin` from `packages/family/projects.json` instead; keep the `APPS` list there in step with `projects.json`.
- Hosting limits to keep in mind: Workers have no filesystem at runtime (bundle data as modules or read it from the ASSETS binding), static assets cost nothing and don't count as requests, and Worker scripts must stay under 10 MiB gzipped (Workers Paid).
- The old hosts (latterdaystats.samuelbaird.com, urim.samuelbaird.com, omni.samuelbaird.com) are custom domains on their app's Worker: they 301 every page to the new path but keep their `/api` (and LDS's `/auth`) endpoints answering, so connectors, webhooks and crons keep working. Don't remove them. urim.samuelbaird.com's page redirects are a zone Redirect Rule (its pages are static assets, which never run the Worker). Peepstone's only address is https://samuelbaird.com/peepstone/mcp (the old peepstone.vercel.app was deleted with the Vercel project).
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

- `samuelbaird.com/admin` (private, noindex, unlinked) is the owner's dashboard (ticket 0.4): revenue and people from `public.admin_dashboard_summary()` (migration `0062_admin_dashboard.sql`, aggregates only, owner only), the latest Cloudflare deploy per Worker (needs secrets `CLOUDFLARE_API_TOKEN` (Workers Scripts: Read) and `CLOUDFLARE_ACCOUNT_ID` on samuelbaird-com), a live uptime check, ticket counts and links to every admin tool. API: `sites/samuelbaird.com/api/admin/dashboard.js`. `/admin/tickets` is the project tracker: rows in `public.admin_tickets` (Latter-day Stats Supabase, migration `0061_admin_tickets.sql`), read and written by `sites/samuelbaird.com/api/admin/tickets.js`. RLS allows only the owner account (`public.is_site_owner()`, hardcoded like migration 0003), not every Latter-day Stats admin.
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
