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
   entry in `languages.generated.yaml`, with the script settings from `RULES` in `register.py`.
   Languages it cannot draw are printed as "need a script handler".
4. `python -m proclamations.generate --size all --jobs 6`: renders every edition; `--edition`, `--doc`, `--size` narrow it.
5. `python -m proclamations.check --outputs`: format parity with the Church's PDFs, plus per-PDF integrity
   (page size, nothing clipped, no overlapping text, every word or letter of the source present).
   `--dir DIR` checks another output folder, `--sizes letter,a4` only those sizes.
6. `python -m proclamations.publish` copies Letter and A4 to `site/posters/<slug>/`; poster sizes stay in
   `proclamations/out/` and are uploaded to Google Drive under the same `<slug>/` folder names.

`<slug>` is the lower-case ASCII folder name without hyphens (native name when it folds to ASCII, otherwise the
English name; `ept` is `portugueseuropeu`). `<code>` is the Church's `?lang=` code and the `texts/` folder name.

## How each kind of script is handled

| Kind | Languages | How |
|---|---|---|
| Plain left-to-right (Latin, Cyrillic, Greek, Armenian, Georgian, Ethiopic, Deseret) | most of them | one glyph per character, font chain in `fonts.py`, hyphenation by `pyphen` where a dictionary exists, ragged-right where not |
| Shaped, left-to-right (Devanagari, Bengali, Gujarati, Tamil, Telugu, Kannada, Malayalam, Sinhala, Thai, Lao, Khmer, Myanmar) | hin, mar, nep, ben, guj, tam, tel, kan, mal, sin, tha, lao, khm, mya, ksw | faces flagged `shape` are shaped with HarfBuzz (`fonts.shape`) and drawn as glyph outlines (`render.Page._shaped`), with an invisible text layer so the PDF is searchable. Conjuncts, vowel signs and mark placement come from the font |
| Shaped, right-to-left (Arabic script) | ara, urd, pes, ckb | as above with HarfBuzz in RTL mode; `Script.rtl` mirrors the whole design (`Page.X`): columns, drop cap, rules and signature blocks start on the right; a run of Latin words (a name, a number) keeps left-to-right reading order (`render.visual_order`). The text layer is written in visual order, as other PDF writers do |
| Han and Hangul | zhs, zho, yue, jpn, kor | subset TrueType faces (`build_cjk.py`) drawn as ordinary text; Chinese and Japanese break between any two characters under kinsoku rules (`linebreak.cjk`) and spread the slack between characters (`char_justify`); Korean breaks at spaces |

### Registry settings (`languages.yaml`, `languages.generated.yaml`)

`font` (a chain in `fonts.FAMILIES`: `serif`, `sans`, `serif-arabic`, `serif-devanagari`, ..., `serif-sc/tc/jp/kr`),
`rtl`, `breaks` (`cjk`, `thai`, `khmer`, `lao`, `myanmar`), `spaced` (false: no lead-in small-caps words, since
"words" are phrases), `char_justify`, `lead` (line-spacing multiplier for tall scripts), `dc_scale` (drop-cap size
factor), `tracked` (false: no letter-spacing, which breaks joined and combining scripts), `caps: none`
(caseless), `hyphenation` (pyphen dictionary), `justify`, `credit`, `hints`, `aof_split`.

## Special cases and how to handle them

| Case | Symptom | Handling |
|---|---|---|
| No translation | survey lists no documents | No edition. 26 Church languages have none. Re-run `discover` when the Church adds one. |
| Partial set (some documents only) | fewer than 4 documents | Only available documents are generated; the language page shows what exists (e.g. Nepali has no Family; Central Kurdish no Articles of Faith). |
| No hyphenation dictionary | ragged lines in justified text | `register.HYPHENATION` maps a Church code to a pyphen dictionary; without one the language is set ragged-right. |
| Caseless script (Georgian-style, Ethiopic, Indic, Arabic, Thai, ...) | no capitals | `caps: none`; the small-caps lead-in becomes bold body-size text (`layout.small_caps_word`). Headings use the script's own weight. |
| Own numerals (Ethiopic, Persian, Arabic-Indic) | verse numbers not digits | `fetch_texts` stores `label` with the printed numeral and `n` as a sequence number. |
| Compatibility characters | boxes in output | `fonts.sanitize` (NFKC) swaps drawable equivalents. Anything still undrawable stops registration. |
| Drop caps | the first code point is not a letter | the drop cap is the first grapheme cluster (`fonts.initial_split`) and the indent uses its ink width (`fonts.drop_width`) so signs and medials do not hit the text. Scripts with deep or tall letters use `dc_scale` (Arabic 0.7, Myanmar 0.32). |
| Tall scripts | lines collide | `lead` multiplies the line spacing (1.25 to 1.5); the Living Christ title shrinks with it. |
| Letter-spacing | joined letters pulled apart | restoration's tracked subtitle uses `Script.tracked`; off for every joined or combining script. |
| Text without spaces | whole paragraph is one word | `breaks` gives break opportunities (kinsoku for CJK, BudouX for Thai, ZWSP and syllables for Khmer, Lao, Myanmar); lead-ins are skipped (`spaced: false`); unspaced headings are split at the nearest opportunity. |
| Zero-width joiners and marks | shaping breaks at run boundaries | `fonts.runs` keeps combining marks and ZWJ/ZWNJ/ZWSP with the preceding character's face. |
| Articles of Faith heading | one heading "Articles of Faith of The Church of ..." | `split_aof_heading` splits it at the Church's name (read from that language's Living Christ page), tolerating inflected and name-first orders; `aof_split` forces a marker. Burmese has no heading. |
| Japanese ruby (furigana) | readings merged into text | `Blocks` in `fetch_texts.py` ignores `<rt>`/`<rp>`. |
| Long translated notes and group headings | text runs off the page or into a neighbor | `centered_note` uses three lines then a smaller size; Living Christ group headings shrink to their column. The checker's overlap test catches regressions. |
| Missing glyphs | `register` lists the language as needing a handler | add a Noto face for the script to `fonts.FAMILIES` and a rule to `register.RULES`. |

### Known limits

- Urdu is set in Naskh. The Church's own Urdu is Nastaliq (`NotoNastaliqUrdu` is bundled and `SHAPED` has a
  `urdu` chain); switching needs larger line spacing and a check of the stacked baseline.
- Text extraction of Arabic-script PDFs can split a word at a mark (readers guess word gaps from glyph positions
  of the invisible layer); the checker compares letters for those scripts.
- Chinese and Japanese titles are split at the nearest break opportunity rather than at a verified phrase boundary.
- Cantonese uses Traditional (TC) glyphs; Hong Kong forms (HK) may differ for a few characters.
- Fonts: shaped scripts use Noto Serif/Naskh faces (OFL); the four CJK faces are subsets of Noto Serif CJK made by
  `build_cjk.py` from the full OpenType files, and contain only the characters of the current texts. After
  fetching new CJK text, re-run `build_cjk.py` or characters will be reported missing.

## Adding or updating a language by hand

Edit `languages.yaml` (hand-written entries win over generated ones) with the fields above plus `kind`, `code`,
`native`, `english`. For a new script: add a Noto face chain to `fonts.FAMILIES` (and to `SHAPED` if it needs
shaping), put a rule in `register.RULES`, add a break function to `linebreak.py` if it has no spaces, then run
`register`, `generate --edition <slug> --size letter`, and `check --outputs --dir <out>`; look at the PDF.
