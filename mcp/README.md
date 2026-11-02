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
mcp/.venv/Scripts/python -m pip install -e mcp          # add  "mcp[argos]"  for Argos (large download)
mcp/.venv/Scripts/python -m urim_translate seed-tm      # optional: Church translation memory (needs ../pulpit-vault)
mcp/.venv/Scripts/python -m urim_translate status
```

Register with Claude Code:

```bash
claude mcp add urim -- <repo>/mcp/.venv/Scripts/python -m urim_translate
```

### Backends

| Backend | Purpose | Setup |
|---|---|---|
| `argos` | fast CPU draft translation | `pip install -e "mcp[argos]"`, then install the en to pt and en to es packages (`argospm install translate-en_pt`) |
| `libretranslate` | optional HTTP alternative | run LibreTranslate, set `URIM_LIBRETRANSLATE_URL=http://localhost:5000` |
| `ollama` | terminology-sensitive passages, post-editing | install Ollama, `ollama pull qwen3.5:4b` (about 3.4 GB) |

Settings can be environment variables (`URIM_OLLAMA_MODEL`, `URIM_BACKENDS`, `URIM_HOME`, ...) or `~/.urim/urim.toml`. To add a backend, subclass `Backend` in `backends.py` and register it in `make_backends()`.

Without any backend installed, the server still returns Church translation-memory hits, glossary matching, validation and lookup; other segments are returned unchanged and flagged.

## Tools

`translate_text`, `translate_file`, `get_translation`, `match_glossary`, `check_translation`, `lookup_term`, `glossary_add`, `glossary_remove`, `glossary_list`, `search_memory`, `backends_status`.

User overrides (`glossary_add`) are enforced and take precedence over the Church glossary; they live only in your local database.

## Limits

- Segments are lines; each Pulpit-style paragraph is one line. Hard-wrapped paragraphs are translated line by line.
- Glossary entries of confidence `hint` are suggested to the model but never enforced.
- Validation checks that a required rendering appears (inflection and accent tolerant); it does not judge grammar.

## Tests

```bash
mcp/.venv/Scripts/python -m pytest mcp/tests tests
```
