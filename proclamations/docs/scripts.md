# Languages, scripts and special cases

How the proclamations generator decides what it can typeset, and what to do for each special case.
Texts are always the Church's own published translation (`texts/<code>/<doc>.yaml`, fetched from
churchofjesuschrist.org); nothing is translated here. A language the Church has not translated a
proclamation into gets no edition for it.

## Pipeline for a language

1. `python -m proclamations.discover`: probes every Church language for each of the four documents
   (404 = not translated) and writes `language-survey.json` (code, native name, script, which documents).
2. `python -m proclamations.fetch_texts --all`: writes `texts/<code>/*.yaml` for every language with at least one document.
3. `python -m proclamations.register`: for each language whose texts the font chain can fully draw, writes an
   entry in `languages.generated.yaml`. Languages it cannot draw are printed as "need a script handler".
4. `python -m proclamations.generate --size all --jobs 6`: renders every edition; `--edition`, `--doc`, `--size` narrow it.
5. `python -m proclamations.check --outputs`: format parity with the Church's PDFs, plus per-PDF integrity
   (page size, nothing clipped, every word of the source present).
6. `python -m proclamations.publish` copies Letter and A4 to `site/posters/<slug>/`; poster sizes stay in
   `proclamations/out/` and are uploaded to Google Drive under the same `<slug>/` folder names.

`<slug>` is the lower-case ASCII folder name without hyphens (native name when it folds to ASCII, otherwise the
English name; `ept` is `portugueseuropeu`). `<code>` is the Church's `?lang=` code and the `texts/` folder name.

## What the engine supports

Simple text layout: left-to-right, one glyph per character, Unicode-cased or caseless, breaking at spaces and
hyphenation points. A face chain per family (`fonts.py`) draws each character with the first face that has it.
Currently Latin (incl. Vietnamese), Cyrillic, Greek, Armenian, Georgian, Ethiopic and Deseret: 98 generated
languages plus English, Spanish, Portuguese and the Deseret edition.

## Special cases and how to handle them

| Case | Symptom | Handling |
|---|---|---|
| No translation | survey lists no documents | No edition. Re-run `discover` when the Church adds one. |
| Partial set (some documents only) | fewer than 4 documents | Only available documents are generated; the language page shows what exists. |
| No hyphenation dictionary | ragged lines in justified text | `register.HYPHENATION` maps a Church code to a pyphen dictionary; without one the language is set ragged-right (`justify: false`), which is correct for languages without one. Add a mapping to turn on justification. |
| Caseless script (Georgian, Ethiopic, Armenian lower only) | upper-casing breaks glyphs | `caps: none` in the entry (`register.CASELESS`); headings use the script's own weight and tracking instead of capitals. |
| Own numerals (Ethiopic) | verse numbers not digits | `fetch_texts` stores `label` with the printed numeral and `n` as a sequence number. |
| Compatibility characters | square boxes in output | `fonts.sanitize` (NFKC) swaps drawable equivalents (Roman numeral characters etc.). Anything still undrawable stops registration. |
| Articles of Faith heading | the Church has one heading "Articles of Faith of The Church of ..." | `split_aof_heading` splits it at the Church's name (read from that language's Living Christ page), tolerating inflected names and name-first languages; `aof_split` in `languages.yaml` forces a marker. Burmese (`mya`) has no heading at all. |
| Church name first (e.g. Hungarian-style order) | title and subtitle swapped | handled by the "prefix" match in `_fuzzy_match`. |
| Japanese ruby (furigana) | readings merged into text | `Blocks` ignores `<rt>`/`<rp>`. |
| Missing glyphs | `register` lists the language as needing a handler | Add a Noto face for the script to `fonts.FAMILIES`, re-run `register`. |

## Scripts not yet supported (text is fetched, no PDF)

These need work the simple engine does not do. Texts are already in `texts/<code>/`.

| Script | Codes | What is needed |
|---|---|---|
| Arabic script | `ara`, `urd`, `pes`, `ckb` | right-to-left layout (bidi), contextual shaping (joining forms), mirrored two-column order. Urdu is traditionally Nastaliq. Plan: HarfBuzz shaping (uharfbuzz) + python-bidi, glyph-run drawing in `render.seg`. |
| Indic | `hin`, `mar`, `nep` (Devanagari), `ben`, `guj`, `tam`, `tel`, `kan`, `mal`, `sin` | conjunct and vowel-sign reordering via shaping (HarfBuzz) and per-script faces; line breaking at syllable boundaries. |
| Thai / Lao / Khmer / Myanmar | `tha`, `lao`, `khm`, `mya`, `ksw` | shaping plus dictionary or syllable-based line breaking (no spaces between words; ICU break iterator). |
| Chinese, Japanese | `zhs`, `zho`, `yue`, `jpn` | break between any two characters (kinsoku rules), large CJK face (`NotoSerifCJK`, an OTF/CFF font ReportLab cannot embed, so convert to TrueType or use another PDF backend), vertical-friendly punctuation. |
| Korean | `kor` | large Hangul face (same font-size/embedding issue), break at spaces or between syllables. |

To add one: implement shaping in `fonts.py` (`runs` would return glyph ids and advances instead of substrings), teach
`layout.py` its break opportunities, register the font in `FAMILIES`, then re-run `register` and `generate`.

## Adding or updating a language by hand

Edit `languages.yaml` (hand-written entries win over generated ones). Fields: `kind` (`language` or `script`),
`code`, `native`, `english`, `font` (`serif`/`sans`), `hyphenation` (pyphen code or null), `justify`, `caps`,
`credit` (localized unofficial-copy line; English by default), `hints` (verified title/subtitle line breaks and
lead-in words; automatic when omitted), `aof_split`.
