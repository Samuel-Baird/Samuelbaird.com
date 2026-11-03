# @urim/deseret: Deseret Alphabet transliteration

Transliterates English text into the Deseret Alphabet (𐐔𐐯𐑅𐐨𐑉𐐯𐐻, U+10400 to U+1044F). It is a **script** for English, not a translation: the output is a pure function of the input text plus committed tables.

This package is the lookup runtime of [pulpit-vault](https://github.com/Noah-Airmet/pulpit-vault)'s Deseret engine (see that repo's `docs/deseret.md` and `schema/deseret/conventions.md`), vendored here so Urim can use it in the browser, on the command line and in its hosted MCP.

## How it works

1. Each English word is looked up in a prebuilt word list (`data/words.tsv`, 73,207 spellings).
2. A few dozen heteronyms (*read, live, use, blessed, ...*) are resolved from the neighbouring words, so "we have read" and "to read" differ (`data/heteronyms.json`).
3. The Latin word's capitalization is reapplied (lower, Title, UPPER; mixed case title-cases the first glyph).
4. A word with no spelling is **left in Latin script**, never guessed at runtime. Punctuation, digits, tags and URLs are untouched.

Output follows the 38-letter standard of the 1868-69 printings (no dedicated *oi*, *ew* or short *ah*); a test checks that no word in the data uses those three letters.

`data/overrides.json` holds Urim's own curated pronunciations (for example initialisms such as *AI* spelled letter by letter). They take precedence over the word list.

## Use

```js
// Node
import { loadTransliterator } from "@urim/deseret/node";
const t = loadTransliterator();               // { confidentOnly: true } leaves guessed spellings in Latin
t.text("The priesthood is the power of God.");
t.html("<p>See <a href='/x'>priesthood</a></p>"); // text nodes only; never tags, attributes, entities or <code>/<pre>
t.coverage("some text");                       // { words, converted, left_latin: [...] }
```

```js
// Browser (no Node APIs): fetch the data yourself
import { createTransliterator, parseWords } from "/deseret/lib/index.mjs";
const t = createTransliterator({ words: parseWords(tsv), heteronyms, overrides });
```

```bash
echo "The priesthood is the power of God." | node deseret/bin/deseret.mjs
node deseret/bin/deseret.mjs --coverage text.txt
node deseret/bin/deseret.mjs --html page.html
```

`text()` is for plain text. For markup use `html()`, which is what Pulpit uses: running `text()` over markdown would transliterate link URLs.

On the Urim site, the sidebar's **Deseret script** button loads the same package and converts English text in place. Portuguese and Spanish text is marked `lang="pt"` / `lang="es"` and never converted. The hosted MCP exposes it as the `to_deseret` tool.

## Data and provenance

`python -m pipeline.deseret_data` regenerates everything from a pulpit-vault checkout and records the commit in `data/PROVENANCE.json`:

| Output | From |
|---|---|
| `data/words.tsv` (word, Deseret, confident) | `indexes/deseret/wordlist.tsv` |
| `data/heteronyms.json` | `schema/deseret/heteronyms.yaml` |
| `src/{arpabet,case,tokens,schwa,html,heteronyms}.mjs` | `scripts/deseret/*.mjs`, copied unchanged with a header |

Of the 73,207 spellings, 54,918 are *confident* (CMUdict, curated tables, simple morphology) and 18,289 are G2P or stemming guesses. By default all are used, which matches the Pulpit edition; pass `confidentOnly` to keep guesses in Latin.

Stage A of Pulpit's pipeline (building the word list from CMUdict and a G2P fallback) is **not** part of this package. To add words, extend the word list upstream in pulpit-vault, or add a pronunciation to `data/overrides.json`.

## Checks

```bash
cd deseret && npm test
```

13 tests: the reserved-letter guard over the whole word list, letter-name words, case, unknown words, heteronyms, apostrophes, overrides, HTML safety, coverage of the atlas vocabulary, and (when a pulpit-vault checkout sits next to this repo) agreement with Pulpit's committed Deseret edition. Comparing four talks across eras against that edition, 124 of 125 English paragraphs transliterate to exactly the same text; the one difference is a straight versus curly closing apostrophe from Pulpit's markdown typography.

## Credits and licensing

- Engine, conventions, tables and word list: pulpit-vault (Noah Airmet and contributors). That repository has no licence file at the time of writing, so confirm terms with its owner before redistributing this package outside Urim.
- Spelling conventions and test oracle: John H. Jenkins' Deseret Book of Mormon, deseretalphabet.info. Part of the curated lexicon in the word list was seeded from it.
- Pronunciations: CMU Pronouncing Dictionary (stage A of Pulpit's build).
- Font on the Urim site: Noto Sans Deseret (SIL Open Font License), loaded from Google Fonts.
