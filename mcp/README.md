# urim-translate: translation MCP for any agent

Free en to pt/es translation tools for Latter-day Saint texts. The server never calls a hosted model and needs no API
key, vendor SDK or client feature: **your agent (any model that speaks MCP) writes the translation, the server does
everything deterministic around it** (chunking, the Church's own paragraphs and scripture text, glossary, validation).
A fully local route (Argos/Ollama) is kept as an optional fallback for users without a capable agent.

## Translate a file with your own agent (recommended)

```
prepare_translation(path, lang)      -> job_id, chunks [{n, words, lines, status}], todo, instructions
get_chunk(job_id, n)                 -> source (English lines), terms (Church renderings present in this chunk), placeholders
submit_chunk(job_id, n, translation) -> ok + remaining chunks, or the exact problems to fix
finish_translation(job_id)           -> writes the file, returns output_path and stats
```

**Recipe for any agent** (the same text is in the server instructions):

1. `prepare_translation(path, lang)` with `lang` `"es"` or `"pt"`; optional `output_path` and `max_words` (default 900 per chunk).
2. For each chunk number in `todo`: `get_chunk(job_id, n)`. Translate every line of `source`: one output line per input
   line, same order (blank lines between are fine). Keep a leading `## `, `- ` or `[^n]: `, keep `[^n]` marks, and keep
   ids like `[[S1]]` (Church scripture text that is inserted for you, inside your quotation marks) and `[[L1]]` (a link
   address) exactly once. Use every rendering in `terms`. Where `quotes` is present, reuse the Church wording given there.
3. `submit_chunk(job_id, n, translation)`. On `ok: false` read `problems` (line number, what is wrong), fix those lines and
   resubmit that chunk only (on success `submit_chunk` also returns the next chunk as `next_chunk`, saving a call; `include_next=false` turns that off). After three attempts a chunk whose only problems are soft (glossary, numbers, length) is accepted
   and flagged; structural problems (line count, lost ids, untranslated lines) must always be fixed.
4. When `remaining` is empty, `finish_translation(job_id)`. If you cannot translate some chunks,
   `finish_translation(job_id, fill_missing_locally=true)` fills them with the local backends and flags them.

Chunks are independent and each is saved on its own, so an agent that can run sub-agents may translate them in parallel;
one that cannot just goes in order. `prepare_translation` on the same file resumes the same job (`job_status` shows where it is).
Tool results are small (ids, paths, stats); nothing returns the whole talk.

What is done before your agent writes a word:

- **Church translation memory:** a paragraph the Church already published in exactly this form (needs `seed-tm`) is filled in verbatim.
- **Scripture:** a quotation that reproduces a cited verse word for word is replaced by `[[Sn]]` and filled with the Church's own text of
  that verse in the target language (`data/scriptures/`, Church book names). Partly quoted verses are given to the agent as references,
  and a warning is returned if the translation does not follow them. Footnotes that are only scripture citations are completed with the Church's book names.
- **Glossary:** only the entries present in a chunk are listed; `submit_chunk` rejects a missing Church rendering (accent- and inflection-tolerant).
- **Structure:** frontmatter, headings, footnotes and code are kept; the `title:` is translated and `language:` set.

Validation is deterministic: line count, `[^n]` marks, `[[Sn]]`/`[[Ln]]` ids, untranslated or English lines, numbers, length ratio, glossary.
It does not judge grammar or style. Jobs live in `<URIM_HOME>/jobs/<job_id>/`.

## Local route (optional fallback)

Fully local, no usage limits.

- **Glossary enforcement:** Church-attested renderings come from Urim's `data/glossary/{pt,es}.json`. Only the entries that occur in the text are used or shown, never the whole glossary.
- **Translation memory (SQLite, `~/.urim/urim.sqlite`):** previous translations are reused. It can be seeded with the Church's own aligned conference paragraphs, so text the Church already translated comes back verbatim (`tm:church`).
- **Routing:** segments with no glossary hit go to a fast MT backend (Argos or LibreTranslate). Segments with hits are validated. A failed draft gets one batched, feedback-driven post-edit by the local LLM (Ollama, default `qwen3.5:4b`). If it still fails, the best output is kept and marked `needs_review`.
- **Structure:** frontmatter, code blocks, table rows, footnote labels/refs, links and URLs pass through unchanged. Scripture citations are rewritten from the Church's own book names (`D&C` for pt, `D. y C.` for es).
- **Low token use:** results are saved under `~/.urim/jobs/<doc_id>/`; tools return a `doc_id`, a path and stats. Read back only what you need with `get_translation`.

## Install

```bash
cd urim
python -m venv mcp/.venv
mcp/.venv/Scripts/python -m pip install -e "mcp[argos]"
claude mcp add urim -- <repo>/mcp/.venv/Scripts/python -m urim_translate
```

**First run installs the rest by itself.** The first time the server starts (or when you run
`python -m urim_translate setup`) it downloads the Argos en to pt and en to es packages (about 100 MB each), installs
Ollama (winget on Windows, Homebrew on macOS, the install script on Linux) and pulls the model (`qwen3.5:4b`, about
3.4 GB). It runs in the background, so the tools work straight away: until a step finishes, `backends_status` shows
what is still missing and segments needing that backend come back flagged. Argos is optional: if the OS blocks its engine (Windows Application Control does on some machines), setup says so and Ollama translates every segment, only slower. Progress goes to stderr; a `setup.json`
marker in `URIM_HOME` is written only when every step succeeded, so a partial setup retries on the next start. Every
step is skipped if already done. Set `URIM_AUTO_SETUP=0` to turn the automatic run off.

The agent pipeline needs none of that setup (no models); `translate_file`/`translate_text` and `fill_missing_locally` do.

Optional: seed the translation memory with the Church's own aligned paragraphs (needs `../pulpit-vault`; `--exclude=2026-04` leaves a conference out, for benchmarks):

```bash
mcp/.venv/Scripts/python -m urim_translate seed-tm
mcp/.venv/Scripts/python -m urim_translate status
```

The Church scripture text in `data/scriptures/` is committed. To rebuild it from `../pulpit-vault` (read-only): `python -m urim_translate build-scriptures`.

### Backends

| Backend | Purpose | Setup |
|---|---|---|
| `argos` | fast CPU draft translation | `pip install -e "mcp[argos]"`; the packages install on first run |
| `libretranslate` | optional HTTP alternative | run LibreTranslate, set `URIM_LIBRETRANSLATE_URL=http://localhost:5000` |
| `ollama` | terminology-sensitive passages, post-editing | installed and the model pulled on first run |

Settings can be environment variables (`URIM_OLLAMA_MODEL`, `URIM_BACKENDS`, `URIM_HOME`, ...) or `~/.urim/urim.toml`. To add a backend, subclass `Backend` in `backends.py` and register it in `make_backends()`.

Without any backend installed, the server still returns Church translation-memory hits, glossary matching, validation and lookup; other segments are returned unchanged and flagged.

## Tools

`prepare_translation`, `get_chunk`, `submit_chunk`, `job_status`, `finish_translation`, plus `translate_text`, `translate_file` (local route), `get_translation`, `match_glossary`, `check_translation`, `lookup_term`, `glossary_add`, `glossary_remove`, `glossary_list`, `search_memory`, `backends_status`, plus two for the Deseret Alphabet:

- `to_deseret(text)` transliterates English text; `deseret_file(path)` does a markdown/text file (frontmatter, code, tables, footnotes, links and URLs stay as they are) and writes it to disk. This is a script conversion, not a translation, so it needs no models. It runs the package in `../deseret` and needs Node.js; words with no Deseret spelling stay in Latin script and are listed.

User overrides (`glossary_add`) are enforced and take precedence over the Church glossary; they live only in your local database.

## Limits

- Segments are lines; each Pulpit-style paragraph is one line. Hard-wrapped paragraphs are translated line by line.
- Glossary entries of confidence `hint` are suggested to the model but never enforced.
- Validation checks that a required rendering appears (inflection and accent tolerant); it does not judge grammar.

## Tests

```bash
mcp/.venv/Scripts/python -m pytest mcp/tests tests
```
