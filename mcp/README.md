# urim-translate: local translation MCP

Free, fully local en to pt/es translation for Latter-day Saint texts. No paid APIs or usage limits.

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

Optional: seed the translation memory with the Church's own aligned paragraphs (needs `../pulpit-vault`):

```bash
mcp/.venv/Scripts/python -m urim_translate seed-tm
mcp/.venv/Scripts/python -m urim_translate status
```

### Backends

| Backend | Purpose | Setup |
|---|---|---|
| `argos` | fast CPU draft translation | `pip install -e "mcp[argos]"`; the packages install on first run |
| `libretranslate` | optional HTTP alternative | run LibreTranslate, set `URIM_LIBRETRANSLATE_URL=http://localhost:5000` |
| `ollama` | terminology-sensitive passages, post-editing | installed and the model pulled on first run |

Settings can be environment variables (`URIM_OLLAMA_MODEL`, `URIM_BACKENDS`, `URIM_HOME`, ...) or `~/.urim/urim.toml`. To add a backend, subclass `Backend` in `backends.py` and register it in `make_backends()`.

Without any backend installed, the server still returns Church translation-memory hits, glossary matching, validation and lookup; other segments are returned unchanged and flagged.

## Tools

`translate_text`, `translate_file`, `get_translation`, `match_glossary`, `check_translation`, `lookup_term`, `glossary_add`, `glossary_remove`, `glossary_list`, `search_memory`, `backends_status`, plus two for the Deseret Alphabet:

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
