# samuelbaird.com: notes for working in this repo

Plain static HTML, CSS and JS on Vercel (`cleanUrls`, no build step). Pages: home (`index.html`), `/books`, `/donate`, `/sacred-sites` (map, `photos/`, `stats/`).

## Branding must stay consistent with Latter-day Stats

This site and `latterdaystats.samuelbaird.com` (repo `Samuel-Baird/latter-day-stats`) are one visual family. Keep them looking the same.

- The source of truth is `BRANDING_AND_DESIGN.md` in the Latter-day Stats repo ("the Archive"). Read it before changing any UI here.
- `tokens.css` mirrors that site's dark tokens (`--background`, `--surface`, `--border`, `--accent`, `--honey`, `--radius` 3px) and fonts (Fraunces for headings, Inter for body). Change a value here only if it changes there too, and vice versa.
- One 3px radius, borders instead of shadows, small-caps labels, no pills, honey as the identity color and blue (`--accent`) for anything clickable.
- Every page loads `tokens.css`, the glyph background (`bg/`), and `deseret.js`. New pages must do the same.
- Page titles (`<h1>`) get the Deseret "translation" reveal from `deseret.js`, a port of `DeseretTitle` in Latter-day Stats. It is decorative only: the Latin text stays in the HTML, it is skipped under `prefers-reduced-motion`, and the glyph mapping is not a real transliteration. If the mapping or timing changes in one repo, change the other.

## Contact and donations

- Public contact email: ithinksamofficial@gmail.com.
- The Amazon wishlist (`https://www.amazon.com/hz/wishlist/ls/3ECBMMP7G2LZ4`) appears on `/donate` and in the home page Support section. Keep it on every donation page.
