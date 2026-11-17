# Deseret MCP

- Sister project of Urim (`../urim`): same shape (hosted MCP at `api/mcp.js`, static `site/` on Vercel, no front-end build step), scoped to the Deseret Alphabet.
- Transliteration follows the Deseret Wiki (`../deseret/scripts/deseret-words.mjs`, `src/lib/dsrt.js`): keep `PHONE` in `src/dsrt.mjs` and the first block of `data/overrides.json` in step with it.
- `../deseret` is read-only input (`npm run build:wiki`); never edit, stash or commit there. Other sessions commit to it.
- Never present a guessed spelling as dictionary-backed: unknown words stay in Latin and are listed; built-from-parts words are listed as `derived`.
- Keep satire projects (antimormonstories, neomormonism) out of this repo entirely.
