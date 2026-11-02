# Urim

- Evidence comes only from Church-published translations (see README sourcing rule). Never add a rendering from general knowledge; never use `ai_generated` rows.
- Pulpit's `Unverified` glossary rows are not imported.
- Branding follows the Archive family: `tokens.css`, `bg/`, `deseret.js` mirror `../Samuelbaird.com`; design source of truth is `../latter-day-stats/BRANDING_AND_DESIGN.md`.
- Site is plain static HTML/CSS/JS on Vercel (`site/` is the root); no front-end build step. Python builds data/pages.
- Do not modify `../pulpit-vault`; read-only input.
