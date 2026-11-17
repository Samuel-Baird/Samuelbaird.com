# Samuel Baird monorepo

Every website and project in one private repo. Each site deploys as its own Vercel project, with its Root Directory set to the folder below.

| Folder | Live at | Vercel project | Stack |
|---|---|---|---|
| `sites/samuelbaird.com` | https://samuelbaird.com | samuelbaird-com | static HTML, `scripts/build.mjs` |
| `sites/latter-day-stats` | https://samuelbaird.com/latter-day-stats | latter-day-stats | Next.js (basePath), Supabase |
| `sites/urim` | https://samuelbaird.com/urim | urim | static + Python pipeline |
| `sites/omni` | https://samuelbaird.com/omni | omni | Next.js (basePath) |
| `sites/peepstone` | https://samuelbaird.com/peepstone | peepstone | Next.js (basePath) |
| `sites/deseret-wiki` | https://deseret.wiki | deseret-wiki | Astro |
| `sites/deseret-mcp` | https://mcp.deseret.wiki | deseret-mcp | static + Node MCP |
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
- Never link the Gospel Scholar Archive (corpus.restorationcommons.org or its MCP host) on a public page.
- antimormonstories and neomormonism are separate and must never be mentioned here or share this branding.
- Each site's own CLAUDE.md/README still applies inside its folder.
