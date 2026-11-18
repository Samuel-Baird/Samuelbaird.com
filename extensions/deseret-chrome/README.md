# Deseret Alphabet: Read Any Page (Chrome extension)

Switches any web page, and YouTube captions, between the Latin and Deseret alphabets.

- **Whole pages**: toolbar button, <kbd>Alt</kbd>+<kbd>Shift</kbd>+<kbd>D</kbd>, or right-click > "Switch page between Latin and Deseret". Pages written in Deseret switch to Latin.
- **Stays on as you browse**: once a tab is in Deseret, later pages on the same site load in Deseret until you switch back or leave the site. "Always show this site in Deseret" makes it permanent; Options can turn on every site.
- **YouTube captions** (youtube.com and embedded players): switch between English and Deseret with the 𐐔 button in the player controls, <kbd>Alt</kbd>+<kbd>Shift</kbd>+<kbd>C</kbd>, or the popup. Choosing Deseret turns YouTube's captions on. Auto-generated captions convert as each word appears; lines that are mostly not English (another language's track) are left alone.
- **Spelling**: the CMU Pronouncing Dictionary, as on the Deseret Wiki. "Dictionary words only" (Options) leaves built-from-parts words in Latin.
- **Fonts**: five bundled (Noto Sans Deseret, Analecta, Mellifera, desalph, IDC Nomada) or the system font. A size slider scales only the Deseret letters.
- **Converter box** in the popup: type English or Deseret, copy the result.
- New content (infinite scroll, single-page apps, live captions) converts as it appears. Code, inputs, editors and icon fonts are left alone. Words the dictionary can't spell stay in Latin rather than being guessed.

## How it works

- `background.js` loads the transliteration engine from Deseret MCP (`sites/deseret-mcp/src/dsrt.mjs`: CMU Pronouncing Dictionary, 126k words, plus the Latter-day Saint name overrides). It is the same engine and data as Deseret MCP and the Deseret Wiki, so spellings match everywhere.
- `captions.js` (YouTube only) watches the caption container, converts each line through the same worker (cached) and swaps the text in place, keeping YouTube's caption styling. The page converter skips captions so the two never fight.
- `content.js` only rewrites text node values (never the DOM structure) and remembers the originals, so switching back is exact and frameworks keep working. The font is registered from bytes through the FontFace API with `unicode-range: U+10400-1044F`, so page CSPs can't block it and Latin text keeps its own font.
- Everything runs locally. No page text leaves the browser and nothing is collected.

## Build and try it

```sh
node extensions/deseret-chrome/build.mjs
```

This writes `dist/` (gitignored) and `dist.zip`. Then open `chrome://extensions`, turn on Developer mode, click **Load unpacked** and pick `extensions/deseret-chrome/dist`. After changing the engine (`sites/deseret-mcp`) or anything in `src/`, rebuild and click the extension's reload button.

## Publishing to the Chrome Web Store

Store item ID `hekmmnnmeacmjpblgakcopaogikiljoe` (publisher "Samuel Baird", contact ithinksamofficial@gmail.com). 0.2.0 submitted for review 2026-11-17, set to publish automatically when approved; listing URL once live: https://chromewebstore.google.com/detail/hekmmnnmeacmjpblgakcopaogikiljoe. Updates: upload a new `dist.zip` under Package, then submit again.

1. Bump `version` in `src/manifest.json` and rebuild.
2. Upload `dist.zip` in the [Developer Dashboard](https://chrome.google.com/webstore/devconsole) (one-time $5 registration).
3. Listing notes:
   - **Permissions**: "Access all sites" is needed to convert any page you choose and to auto-convert the sites you mark.
   - **Privacy**: no data is collected or transmitted.
   - **Single purpose**: display web page text and video captions in the Deseret Alphabet.

## Licenses

Dictionary: CMU Pronouncing Dictionary (BSD-2-Clause, `engine/CMUDICT-LICENSE`). Fonts: see `fonts/README.txt` (SIL OFL 1.1 or public domain; license texts included). Only fonts that allow redistribution are bundled.
