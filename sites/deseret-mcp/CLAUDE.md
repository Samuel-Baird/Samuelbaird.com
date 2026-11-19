# Deseret MCP

- Sister project of Urim (`../urim`): same shape (hosted MCP at `api/mcp.js`, static `site/` on Vercel, no front-end build step), scoped to the Deseret Alphabet.
- Transliteration follows the Deseret Wiki (`../deseret/scripts/deseret-words.mjs`, `src/lib/dsrt.js`): keep `PHONE` in `src/dsrt.mjs` and the first block of `data/overrides.json` in step with it.
- `../deseret` is read-only input (`npm run build:wiki`); never edit, stash or commit there. Other sessions commit to it.
- Never present a guessed spelling as dictionary-backed: unknown words stay in Latin and are listed; built-from-parts words are listed as `derived`.
- Keep satire projects (antimormonstories, neomormonism) out of this repo entirely.
- `src/dsrt.mjs` and `data/` are also shipped inside the Chrome extension (`../../extensions/deseret-chrome`, copied by its build). Keep `dsrt.mjs` dependency-free and browser-safe (no `node:` imports). `historical1868` (1868 printing conventions) is available to callers but not used by the extension; add a rule only with a printed example.
- Cloudflare (migration from Vercel; `vercel.json` stays until cutover): `wrangler.jsonc` deploys Worker `deseret-mcp`. `site/` is Workers static assets; only `/api/*` runs `src/worker.mjs` (same endpoint as `api/mcp.js`). Workers have no filesystem, so the worker bundles `data/` (JSON imports, `cmudict.tsv` as a Text module) and hands it to `provideData()` in `src/load.mjs`; Node paths (bin, tests, Vercel) still read `data/` from disk. `npm run cf:dev` / `npm run cf:deploy`; `npx wrangler deploy --dry-run --outdir <dir>` checks the bundle (~0.95 MiB gzipped). The dictionary is parsed at Worker startup (~200 ms CPU locally), not per request. Routes / custom domain get added at cutover. No env vars or secrets.
