# urim-translate: translation MCP for any agent

En to es/pt translation tools for Latter-day Saint texts. The server never calls a hosted model and needs no API key, vendor
SDK or client feature: **your agent (any model that speaks MCP) writes the translation, the server does everything
deterministic around it** (chunking, the Church's own paragraphs and scripture text, glossary, validation).

## Translate a file

```
prepare_translation(path, lang)      -> job_id, chunks [{n, words, lines, status}], todo, instructions
get_chunk(job_id, n)                 -> source (English lines), terms (Church renderings present in this chunk), placeholders
submit_chunk(job_id, n, translation) -> ok + remaining chunks, or the exact problems to fix
finish_translation(job_id)           -> writes the file, returns output_path and stats
```

**Recipe for any agent** (the same text is in the server instructions):

1. `prepare_translation(path, lang)` with `lang` `"es"` or `"pt"`; optional `output_path` and `max_words` (default 450 per chunk).
2. For each chunk number in `todo`: `get_chunk(job_id, n)`. Translate every line of `source`: one output line per input
   line, same order (blank lines between are fine). Keep a leading `## `, `- ` or `[^n]: `, keep `[^n]` marks, and keep
   ids like `[[S1]]` (Church scripture text that is inserted for you, inside your quotation marks) and `[[L1]]` (a link
   address) exactly once. Use every rendering in `terms`. Where `quotes` is present, reuse the Church wording given there.
3. `submit_chunk(job_id, n, translation)`. On `ok: false` read `problems` (line number, what is wrong), fix those lines and
   resubmit that chunk only. After three attempts a chunk whose only problems are soft (glossary, numbers, length) is accepted
   and flagged; structural problems (line count, lost ids, untranslated lines) must always be fixed.
4. When `remaining` is empty, `finish_translation(job_id)`.

Chunks are independent and each is saved on its own, so an agent that can run sub-agents may translate them in parallel;
one that cannot just goes in order. `prepare_translation` on the same file resumes the same job (`job_status` shows where it is).
Tool results are small (ids, paths, stats); nothing returns the whole talk. Bad arguments return `{"ok": false, "error": ...}`.

What is done before your agent writes a word:

- **Church translation memory:** a paragraph the Church already published in exactly this form (needs `seed-tm`) is filled in verbatim.
- **Scripture:** a quotation that reproduces a cited verse word for word (cited by footnote, `(Ref)` or `([Ref](url))`) is replaced by
  `[[Sn]]` and filled with the Church's own text of that verse in the target language (`data/scriptures/`, Church book names).
  Partly quoted verses are given to the agent as references, and a warning is returned if the translation does not follow them.
  Footnotes that are only scripture citations are completed with the Church's book names.
- **Glossary:** only the entries present in a chunk are listed; `submit_chunk` rejects a missing Church rendering (accent- and inflection-tolerant).
- **Structure:** frontmatter, headings, footnotes and code are kept; the `title:` is translated and `language:` set.

Validation is deterministic: line count, `[^n]` marks, `[[Sn]]`/`[[Ln]]` ids, untranslated or English lines (not applied to reference
footnotes), numbers, length ratio, glossary. It does not judge grammar or style. Jobs live in `<URIM_HOME>/jobs/<job_id>/`
(`URIM_JOBS_DIR` overrides).

## Install

```bash
cd urim
python -m venv mcp/.venv
mcp/.venv/Scripts/python -m pip install -e mcp
claude mcp add urim -- <repo>/mcp/.venv/Scripts/python -m urim_translate
```

No models or downloads are needed. Optional: seed the translation memory with the Church's own aligned paragraphs
(needs `../pulpit-vault`; `--exclude=2026-04` leaves a conference out, for benchmarks):

```bash
mcp/.venv/Scripts/python -m urim_translate seed-tm
mcp/.venv/Scripts/python -m urim_translate status
```

The Church scripture text in `data/scriptures/` is committed. To rebuild it from `../pulpit-vault` (read-only): `python -m urim_translate build-scriptures`.
Settings can be environment variables (`URIM_HOME`, `URIM_GLOSSARY_DIR`, ...) or `~/.urim/urim.toml`.

## Other tools

`match_glossary` (glossary entries relevant to a text), `check_translation` (validate a translation against the glossary), `lookup_term`
(English or target-language lookup with sources), `glossary_add` / `glossary_remove` / `glossary_list` (your own overrides, enforced and
local to your database), `search_memory`, and two for the Deseret Alphabet:

- `to_deseret(text)` transliterates English text; `deseret_file(path)` does a markdown/text file (frontmatter, code, tables, footnotes, links and URLs stay as they are) and writes it to disk. This is a script conversion, not a translation. It runs the package in `../deseret` and needs Node.js; words with no Deseret spelling stay in Latin script and are listed.

## Limits

- Segments are lines; each Pulpit-style paragraph is one line. Hard-wrapped paragraphs are translated line by line.
- Glossary entries of confidence `hint` are suggested to the agent but never enforced.
- Validation checks that a required rendering appears (inflection and accent tolerant); it does not judge grammar.

## Tests

```bash
mcp/.venv/Scripts/python -m pytest mcp/tests tests
```
