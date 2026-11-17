# deseret.wiki — Site Plan

A wiki, document library and learning toolkit for the Deseret Alphabet (𐐔𐐯𐑅𐐮𐑉𐐯𐐻), styled like a mid‑1850s Deseret imprint.

## 1. Goals
1. **Library** — scans of primary sources (First/Second Readers, Book of Mormon 1869, Deseret News, the 1854 charts, the Hopi vocabulary) with metadata, transcriptions and download links.
2. **Wiki** — linked entries on the alphabet's history, people (Watt, Pratt, Young, Board of Regents), letters/sounds, publications, variants and Unicode.
3. **Learn** — interactive tools: chart, flashcards, transliterator, reader/quiz, typing practice.
4. **Fonts & typing** — every known Deseret font with specimens, licenses, download and a web keyboard.

## 2. Information architecture
| Section | Contents |
|---|---|
| `/` | Hero in 1850s broadside style, today's letter, search |
| `/wiki/…` | Entries (Markdown, one file each). Namespaces: People, Letters, Works, Places, Terms, Variants |
| `/library/…` | Document pages: viewer, metadata, source link, transcription, parallel text |
| `/learn/…` | Chart, Lessons (letter groups), Flashcards, Reading practice, Typing drill |
| `/tools/transliterate` | English ⇄ Deseret (phonetic/IPA), font picker, copy / PNG export |
| `/tools/keyboard` | On‑screen + physical layout guidance |
| `/fonts` | Specimen grid, license badges, downloads |
| `/timeline` | 1849 → today (Regents, readers, 1869 BoM, Unicode 3.1, revival) |
| `/about`, `/sources`, `/contribute` | Provenance, credits, corrections |

## 3. Visual design — "old"
- **Palette**: parchment `#efe3c6`, aged paper edge `#d8c79e`, iron‑gall ink `#2a2118`, Deseret red‑brown `#7a2e1d`, beehive gold `#b8892b`, faded blue `#3c5a6e`.
- **Texture**: paper grain + subtle foxing (CSS/SVG noise, no heavy images), inked edge vignette, letterpress text‑shadow.
- **Type**: Latin headings in an Old‑Style/Clarendon feel (e.g. IM Fell / Cormorant via Google Fonts or self‑hosted); body in a book serif. Deseret display via **Mellifera Deseret Master** / **Bee Skep Serif** (period feel); Deseret text via **Noto Sans Deseret** (reliable, OFL) with Bee fonts as selectable options.
- **Ornaments**: beehive, "Holiness to the Lord" border rules, printer's fleurons, double‑rule column dividers, small‑caps nav styled as a broadside masthead.
- **Layout**: two‑column "newspaper" for wiki, single‑column "book page" for readers, side‑by‑side parallel Deseret/English view. Must degrade to a clean mobile layout.
- **Dark mode**: "candlelit" — dark brown paper, cream ink.

## 4. Tech
- **Static site, Astro** + Markdown/MDX content collections (cheap, fast, git‑based; contributors edit Markdown). Alternative if you want live editing later: MediaWiki or Wiki.js, but static is recommended for a curated reference.
- **Search**: Pagefind (client‑side, indexes Latin and Deseret).
- **Tools**: vanilla TS modules; transliterator uses Unicode block U+10400–U+1044F, rules table + CMU‑dict style lookup for English→phonemes→Deseret; letter data in `data/letters.json` (name, IPA, 1854/1859/1868 shapes, Unicode, example words).
- **PDF viewing**: pdf.js for in‑page viewing; thumbnails + extracted text generated at build time.
- **Hosting**: Vercel or GitHub Pages from `Samuel-Baird/deseret`, custom domain `deseret.wiki` (DNS A/CNAME at the registrar).
- Large PDFs (>25 MB) go to object storage/Git LFS or the Internet Archive, not plain git.

## 5. Content already collected
**`assets/fonts/`** — 61 files, from the Baybayin Project's font set (all 35 Deseret fonts it offers, plus variants). Credits/licences listed there:
- Noto Sans Deseret (Google, OFL) · Analecta (G. Douros, PD) · Code2001 (freeware) · MPH 2B Damase (PD) · desalph (Beesley/Brennan, OFL) · IDC Xylocopa, Nomada (OFL), Hesperapis (OFL), Xenoglossa + Alt (MIT) · Mellifera (sigilante) · Unifont Upper (OFL/GPL)
- Joshua Erickson "Bee" family: AdamicBee, TimesBee, TumbleBee, QueenBee (+Star), DeseretBee, HoneyBee, ReaderBee, ZarahemlaBee, TuBee Blunt/Round (+Hollow/Shadow) — listed as "Free"; **verify redistribution terms before bundling on the public site** (link to Erickson's page instead if unclear).
- Legacy: Deseret / DESERET / Deseret_ (Bateman, Thibault/Kass, Kearney), HuneyBee, Bee Skep (Spicer).
- Mind the `unicode added` folder: same fonts re‑mapped to U+10400.

**`assets/source-pdfs/`** — Deseret‑alphabet renderings of The Family, The Living Christ, The Restoration, Articles of Faith (plain + parallel), from the Baybayin Project.

**`assets/gsa-pdfs/`** (from the Gospel Scholar Archive; hits for "Deseret alphabet"):
| File | Why |
|---|---|
| Ricks/Hoskisson/Smith/Gee, *Dictionary of Proper Names & Foreign Words in the BoM* (2022) | 294 entries each with a Deseret spelling + IPA — ready‑made dataset for names and the transliterator test set |
| *Interpreter* vol. 15 (2015), pp. 49–56 | article on the 1868 Deseret News pronunciation guide and Deseret Alphabet classics |
| *BYU Studies* 55‑4 (2016), pp. 189–192 | review of *English‑Hopi Vocabulary 1860* in Deseret |
| *BYU Studies* 18‑1 (1977) | George D. Watt article (first reader, Deseret Alphabet) |

Other GSA hits worth reading but not downloaded (large volumes; link instead): Complete Discourses of Brigham Young vols 3–5 (Regents, alphabet), Allen & Leonard *Story of the Latter‑day Saints* p. 365, Arrington *American Moses* p. 336, Givens & Grow *Parley P. Pratt* p. 410, *Encyclopedia of Mormonism* vol. 1 p. 19 / vol. 4 p. 367, *Journal of Discourses* vol. 12 p. 140, Griffiths & Woodger *50 Relics* p. 79–93, A Mormon Bibliography 1830–1930 p. 116.

**`C:\Users\b13ll\Downloads\deseret\`** (your files, not yet copied): First & Second Readers, BoM/Bible/Apocrypha PDFs, Burton *City of the Saints*, Beadle, Remy, Watt, German book, 1854/1859 charts, comparison tables, Unicode chapter 20 + docs, SVG lineups, images.

## 6. Link sources to mine
deseretalphabet.org · 2deseret.com · churchofjesuschrist.org Deseret Alphabet topic · restorethealphabet.com · deseretalphabet.info (Classics, BoM EPUB) · U of Utah "Designing Deseret" exhibit · Baybayin Project transliterator. Record licence/permission for each before copying text or images; link out where unclear.

## 7. Phases
1. **Scaffold** (Astro, theme, nav, fonts via `@font-face`, deploy to deseret.wiki)
2. **Library** — import PDFs with metadata (title, date, author, source URL, licence)
3. **Data** — `letters.json`, name dictionary from the Ricks et al. book, timeline
4. **Wiki** — seed 40–60 entries
5. **Learn + tools** — chart, transliterator, flashcards, keyboard
6. **Polish** — search, accessibility, print stylesheet, OG images in broadside style

## 8. Open decisions
- Static (Astro) vs. editable wiki engine · Where to host big PDFs · Whether to bundle "Free"-licensed Bee fonts · Whether a Deseret-flavored contributor workflow (GitHub PRs) is acceptable.
