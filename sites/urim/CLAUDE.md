# Urim

- Evidence comes only from Church-published translations (see README sourcing rule). Never add a rendering from general knowledge; never use `ai_generated` rows.
- Pulpit's `Unverified` glossary rows are not imported.
- Served at https://samuelbaird.com/urim (monorepo `sites/urim`). Pages carry `<!--family:*-->` markers; after every pipeline build run `node scripts/family-sync.mjs` at the repo root, which stamps the shared sidebar/header/colophon and prefixes root-relative links with `/urim`. Style guide: `packages/family/STYLE.md`.
- Site is plain static HTML/CSS/JS on Vercel (`site/` is the root); no front-end build step. Python builds data/pages.
- Do not modify `../../../pulpit-vault` (outside this repo); read-only input.
