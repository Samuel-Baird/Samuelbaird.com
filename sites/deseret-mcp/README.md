# Deseret MCP: the Deseret Alphabet for any AI assistant

An MCP server that writes English in the Deseret Alphabet (𐐔𐐯𐑅𐐨𐑉𐐯𐐻), reads it back, and answers questions about the
alphabet from every source on [deseret.wiki](https://deseret.wiki), with links back to the page each answer came from.
Landing page and install steps: <https://mcp.deseret.wiki>. Sister project of [Urim](https://github.com/Samuel-Baird/urim).

Independent project; not affiliated with The Church of Jesus Christ of Latter-day Saints.

## Tools

| Tool | What it does |
|---|---|
| `to_deseret(text, format?, strict?, spellings?)` | English text (a word, a passage, a whole document up to 100,000 characters) to Deseret. `format` `markdown` or `html` keeps code, links, URLs, frontmatter, footnote marks and tags as they are. |
| `deseret_word(word)` | One word: ARPAbet phones, each letter with its name, sound and key word, every dictionary pronunciation. |
| `from_deseret(text)` | Deseret back to Latin letters, listing homophones (𐐺𐐴 = by / buy / bye) and words it had to respell letter by letter. |
| `search_wiki(query, kind?, limit?)` | Ranked search over the wiki: article sections, library, sermons, resources, videos, fonts, books & prints, quotes, the letter chart. Each hit has its deseret.wiki `url` and, where the wiki links out, `source_url`. |
| `read_wiki(id)` | Full text of one record with a ready-made citation, licence and (for article sections) the previous and next section. |
| `wiki_contents(kind?)` | What the wiki holds, by kind, then every record of a kind. |
| `deseret_file(path, output_path?)` | **Local server only.** Transliterates a `.txt`, `.md` or `.html` file and writes `name.dsrt.md` beside it (never over the input, never over an existing file unless `overwrite`). Returns the path and the word report, not the text. |

Every transliteration result says what it could not do:

- `unknown`: words with no spelling, **left in Latin letters**, with counts. Pass `spellings` (`{"Zxqvb": "Z IH1 K"}` or Deseret text) to supply them.
- `derived`: words not in the dictionary that were spelled from their parts (`unfaithfulness` = `unfaithful` + `-ness`). `strict: true` leaves them in Latin too.
- `heteronyms`: words such as *read*, *live*, *lead* whose spelling depends on sense, with the spellings used and the alternatives.

## How the transliteration works

The same method as the Deseret Wiki (`deseret/scripts/deseret-words.mjs`, `src/lib/dsrt.js`), extended to all of English:

1. Each word is looked up in the [CMU Pronouncing Dictionary](https://github.com/cmusphinx/cmudict) (126,052 words, pinned commit,
   `data/cmudict.tsv`), and each ARPAbet phone maps to one Deseret letter by the wiki's table (Y + UW is 𐑏, OY is 𐑎, ER is 𐐲𐑉).
2. Hand corrections in `data/overrides.json` win: the wiki's own (*and*, *not*, *Deseret*, ...) and Book of Mormon names after the
   Church's pronunciation guide.
3. A word the dictionary lacks is built from a dictionary stem plus a regular ending or prefix (-s, -ed, -ing, -ness, -ful, un-,
   re-, ...) or a common compound head (-keeper, -house, -man). Anything else stays in Latin and is reported, never guessed.
4. A few heteronyms are resolved from the word before (*have read* is 𐑉𐐯𐐼, *will read* is 𐑉𐐨𐐼); others use their common reading.
5. Case is kept: lower, Title, UPPER. Digits, URLs, emails and IPA are not touched.

On the Deseret Wiki article itself (7,741 words, many of them names and technical terms) 97.0% are spelled from the dictionary,
0.6% are built from their parts and 2.4% are reported as unknown. Against the wiki's own word table the engine agrees on every
word except four heteronyms (lead, read, use, wind) where it deliberately picks the common reading.

Reading Deseret back uses the same dictionary reversed; homophones are ranked by how often each word appears on the wiki.

## Wiki sources

`data/wiki.json` is built from a checkout of [Samuel-Baird/deseret](https://github.com/Samuel-Baird/deseret) (read only):

| Kind | From |
|---|---|
| `article` | `src/pages/wiki/*.md` and `src/content/**/*.md`, one record per section, with the heading anchor the site uses |
| `page` | the visible text of each `.astro` page |
| `letter` | the 38-letter chart on the front page |
| `library`, `resource`, `video` | the lists in `library.astro`, `resources.astro`, `videos.astro` (new lists on any page are picked up automatically) |
| `font`, `book`, `quote` | `src/data/fonts.json`, `buy.json`, `quotes.json` (when present) and `social-quote.json` |

```bash
npm run build:wiki            # DESERET_WIKI=path/to/deseret, default ../deseret
```

The article text is from Wikipedia (CC BY-SA 4.0); `read_wiki` returns that attribution with every article section.

## Install

Hosted (no install). Claude Code:

```bash
claude mcp add --transport http deseret https://mcp.deseret.wiki/api/mcp
```

Claude or ChatGPT apps: add a custom connector with that address and no sign-in; step-by-step instructions are on the
[Connect page](https://mcp.deseret.wiki/connect).

Local (adds `deseret_file`). Needs Node.js 20 or newer and nothing else; there are no dependencies to install:

```bash
git clone https://github.com/Samuel-Baird/deseret-mcp
claude mcp add deseret -- node <repo>/bin/deseret-mcp.mjs
```

Other clients that speak stdio:

```json
{ "mcpServers": { "deseret": { "command": "node", "args": ["<repo>/bin/deseret-mcp.mjs"] } } }
```

The same script is a small command line tool:

```bash
node bin/deseret-mcp.mjs to "The Deseret Alphabet"
node bin/deseret-mcp.mjs from "𐐜𐐲 𐐔𐐯𐑅𐐨𐑉𐐯𐐻 𐐈𐑊𐑁𐐲𐐺𐐯𐐻"
node bin/deseret-mcp.mjs file notes.md
node bin/deseret-mcp.mjs search "gold coin"
```

## Layout

- `src/dsrt.mjs` transliteration engine (no I/O), `src/wiki.mjs` search and read, `src/tools.mjs` tools and the JSON-RPC handler
- `api/mcp.js` hosted MCP at `/api/mcp` (streamable HTTP, stateless, JSON responses, no data kept)
- `bin/deseret-mcp.mjs` local stdio server and CLI
- `data/` committed data: `cmudict.tsv`, `overrides.json`, `wiki.json`
- `scripts/` `build-dict.mjs` (CMUdict) and `build-wiki.mjs` (the wiki)
- `site/` static landing site (Vercel root, no build step)
- `wrangler.jsonc`, `src/worker.mjs` the same site and endpoint as a Cloudflare Worker (static assets + `/api/mcp`, data bundled in): `npm install`, then `npm run cf:dev` / `npm run cf:deploy`

## Tests

```bash
npm test
```

Engine (case, overrides, derivation, strict mode, heteronyms, markdown and HTML safety, round trip, agreement with the wiki's
table), wiki corpus (every kind present, anchors match the built site, search, read, the build script on a fixture with a
`quotes.json`), and the MCP over both transports.

## Limits

- Spellings follow one American dictionary pronunciation, not the 1860s printings' conventions or a regional accent.
- Heteronyms outside the short list use CMUdict's first reading; check the `heteronyms` report.
- Reading Deseret back is exact only for spellings that match the dictionary; older and personal spellings are respelled.
- The wiki index is a snapshot; rebuild it when the wiki changes.

## Credits

- Pronunciations: CMU Pronouncing Dictionary, Carnegie Mellon University (BSD-2-Clause, `data/CMUDICT-LICENSE`).
- Method, phone table and overrides: the Deseret Wiki. Letter names and key words: the wiki's letter chart.
- Article text: Wikipedia contributors, CC BY-SA 4.0. Other records are the wiki's own descriptions, linking to their sources.
- Site background: GlyphWind (MIT, Henry Fan; `site/bg/LICENSE-glyphwind.txt`), as on Urim.
