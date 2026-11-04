"""MCP server (stdio). Tools return small JSON: ids, paths and stats, not full translations."""
import functools
from pathlib import Path

from mcp.server.mcpserver import MCPServer

from . import config, deseret, segment, workflow
from .glossary import Glossary
from .translator import Seg, Translator

mcp = MCPServer(
    "urim",
    instructions=(
        "Free local translation for Latter-day Saint texts (English -> pt, es). Church-attested terminology is "
        "enforced from the Urim glossary; only relevant entries are ever surfaced. Large outputs are saved to "
        "disk and returned as a path/doc_id; read them selectively with get_translation. "
        "TRANSLATE A FILE YOURSELF (any agent; recommended): the server never calls a model, you write the translation and "
        "it does the rest. 1) prepare_translation(path, lang) returns a job_id and the chunk numbers in `todo`. 2) For the first "
        "chunk n: get_chunk(job_id, n) gives English `source` (one line per paragraph), the Church `terms` to use and "
        "ids such as [[S1]] that stand for Church scripture text inserted for you. 3) submit_chunk(job_id, n, translation): "
        "one output line per source line, same order. If it returns problems, fix those lines and resubmit that chunk only. "
        "4) finish_translation(job_id) writes the file. Chunks are independent, so run them in parallel if you can. "
        "If get_chunk returns a machine `draft`, review it and send only your corrections with submit_chunk(job_id, n, edits={\"3\": \"...\"}). "
        "No capable agent? translate_file uses local models (Argos/Ollama) instead."
    ),
)
_T = {}


def tool(fn):
    """Register a tool; bad arguments come back as {"ok": false, "error": ...} that says what to change, never a bare failure."""
    @functools.wraps(fn)
    def run(*a, **k):
        try:
            return fn(*a, **k)
        except (ValueError, TypeError, KeyError, OSError) as e:
            return {"ok": False, "error": f"{type(e).__name__}: {e}", "hint": "check the arguments (lang is 'es' or 'pt')"}
    return mcp.tool()(run)


def T() -> Translator:
    if "t" not in _T:
        _T["t"] = Translator()
    return _T["t"]


def _check_lang(lang):
    if lang not in config.UI_LANGS:
        raise ValueError(f"unsupported language '{lang}'; supported: {', '.join(config.UI_LANGS)}")


@tool
def translate_text(text: str, lang: str) -> dict:
    """Translate English text into `lang` ('pt' or 'es') with the LOCAL models (Argos/Ollama): free but slower
    and rougher than translating it yourself with match_glossary + check_translation. Short results are returned
    inline; long ones are saved to a file and returned as doc_id + path."""
    _check_lang(lang)
    t = T()
    blocks, results = t.translate_document(text, lang)
    out_text = segment.join_blocks(blocks)
    info = t.summarize(results)
    if len(out_text) <= config.INLINE_LIMIT:
        return {"translation": out_text, **info}
    doc_id = t.doc_id("text", lang, text)
    path = t.save_job(doc_id, lang, None, blocks, results)
    return {"doc_id": doc_id, "output_path": str(path), **info}


@tool
def translate_file(path: str, lang: str, output_path: str = "") -> dict:
    """Fallback for when you cannot write the translation yourself: translates a markdown/text file into `lang`
    with the LOCAL models (Argos/Ollama; minutes on a CPU, lower quality). If you are a capable model, use
    prepare_translation / get_chunk / submit_chunk / finish_translation instead: faster, cheaper and closer to
    the Church's own wording. Preserves frontmatter, code, footnotes, links and structure, localizes scripture
    citations, writes the result to disk and returns doc_id, output_path and stats."""
    _check_lang(lang)
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    t = T()
    blocks, results = t.translate_document(text, lang)
    doc_id = t.doc_id(p.name, lang, text)
    out = t.save_job(doc_id, lang, str(p), blocks, results, output_path or None)
    return {"doc_id": doc_id, "output_path": str(out), **t.summarize(results)}


@tool
def prepare_translation(path: str, lang: str, output_path: str = "", max_words: int = 900, draft: bool | None = None) -> dict:
    """Step 1 of translating a file yourself. Splits the markdown/text file into independent chunks at paragraph
    boundaries (frontmatter, footnotes and structure are kept), reuses the Church's own paragraphs, inserts the
    Church's scripture text for quotations and fills footnotes that are only scripture citations. Returns job_id,
    the chunks (number, words, status), `todo` (chunk numbers to translate) and short instructions. Calling it again
    for the same file resumes the same job. `output_path` is where finish_translation writes the result. `draft=true` (or URIM_DRAFT=1) pre-translates every line with the local machine translator (Argos/LibreTranslate) so you only send corrections; ignored if none is available."""
    return workflow.prepare(T(), path, lang, output_path, max_words)


@tool
def get_chunk(job_id: str, n: int) -> dict:
    """Step 2. One chunk to translate: `source` (English lines separated by blank lines), the Church `terms` that
    must appear in your translation (only those present in this chunk), `scripture` ids like [[S1]] to keep as they
    are, and `quotes` (Church wording for partly quoted verses). Chunk numbers start at 1."""
    return workflow.get_chunk(job_id, n)


@tool
def submit_chunk(job_id: str, n: int, translation: str = "", edits: dict[str, str] | None = None, include_next: bool = True) -> dict:
    """Step 3. Send your translation of chunk n: one line per `source` line, same order (blank lines between are
    fine; keep leading '## ' or '[^n]: ' markers). Returns ok with the chunks still to do, or a list of problems
    (line number, what is wrong) to fix; then resubmit this chunk only. Checked: line count, kept [^n] marks, URLs and
    [[Sn]] ids, Church glossary renderings, numbers, length, untranslated lines. If get_chunk gave a machine `draft`, you may send only `edits` ({"3": "corrected line 3"}, line numbers as in `draft`); lines you do not list are accepted as drafted. On success the next chunk to do is returned as `next_chunk` (set include_next=false if several agents share the job)."""
    return workflow.submit_chunk(T(), job_id, n, translation, edits, include_next)


@tool
def job_status(job_id: str) -> dict:
    """Progress of a translation job: chunks and which are still to do (use it to resume)."""
    return workflow.job_status(job_id)


@tool
def finish_translation(job_id: str, output_path: str = "", fill_missing_locally: bool = False) -> dict:
    """Step 4. Assemble all chunks into the final file (scripture ids replaced by the Church's text, title and
    structure restored), write it to `output_path` (or the path given to prepare_translation) and return the path
    and stats. If chunks are missing it lists them; `fill_missing_locally=true` translates those with the local
    backends (Argos/Ollama) and flags them for review."""
    return workflow.finish(T(), job_id, output_path, fill_missing_locally)


@tool
def get_translation(doc_id: str, start: int = 0, end: int = 20, flagged_only: bool = False) -> dict:
    """Read back segments (source + translation) of a saved job. `flagged_only` returns only segments needing
    review. At most 20 segments per call."""
    import json
    job = T().store.job_get(doc_id)
    if not job:
        raise ValueError(f"unknown doc_id {doc_id}")
    rep = json.loads((config.HOME / "jobs" / doc_id / "report.json").read_text(encoding="utf-8"))
    rows = [r for r in rep if (r["flags"] or not flagged_only)] if flagged_only else rep[start:end]
    return {"doc_id": doc_id, "total": len(rep), "segments": rows[:20]}


@tool
def match_glossary(text: str, lang: str) -> dict:
    """Return only the glossary entries relevant to `text` (the cheap way to translate it yourself with
    correct Church terminology). 'use' is the required rendering; confidence 'hint' means unconfirmed."""
    _check_lang(lang)
    g = T().glossary(lang)
    seen, out = set(), []
    for m in g.match(text):
        if m.entry.id not in seen:
            seen.add(m.entry.id)
            out.append(m.entry.brief())
    return {"lang": lang, "glossary_version": g.version, "terms": out}


@tool
def check_translation(source: str, translation: str, lang: str) -> dict:
    """Validate a translation against the glossary (required renderings) plus number and length checks.
    Returns what to fix, not the full text."""
    _check_lang(lang)
    t = T()
    seg = Seg(source, masked=source, matches=t.glossary(lang).match(source))
    probs = t.problems(seg, translation, t.glossary(lang))
    return {"ok": not probs, "problems": probs}


@tool
def lookup_term(term: str, lang: str) -> dict:
    """Look up a term in English OR in pt/es (reverse lookup). Returns the preferred Church rendering, variants,
    confidence (approved / attested / user / hint) and a link to the Urim atlas page with sources."""
    _check_lang(lang)
    g = T().glossary(lang)
    return {"lang": lang, "results": [e.brief() for e in g.lookup(term)]}


@tool
def glossary_add(en: str, target: str, lang: str, note: str = "") -> dict:
    """Add or replace a user glossary override (enforced, takes precedence over the Church glossary)."""
    _check_lang(lang)
    T().store.override_put(lang, en, target, note)
    T().reload_glossary(lang)
    return {"ok": True, "glossary_version": T().glossary(lang).version}


@tool
def glossary_remove(en: str, lang: str) -> dict:
    """Remove a user glossary override."""
    _check_lang(lang)
    ok = T().store.override_delete(lang, en)
    T().reload_glossary(lang)
    return {"removed": ok}


@tool
def glossary_list(lang: str, query: str = "") -> dict:
    """List user overrides plus counts for the Church glossary; with `query`, list matching entries."""
    _check_lang(lang)
    t = T()
    g = t.glossary(lang)
    res = {"lang": lang, "version": g.version, "entries": len(g.entries),
           "by_confidence": {c: sum(e.confidence == c for e in g.entries) for c in ("approved", "attested", "hint", "user")},
           "user_overrides": t.store.overrides(lang)}
    if query:
        res["matches"] = [e.brief() for e in g.lookup(query, 15)]
    return res


@tool
def search_memory(query: str, lang: str = "", origin: str = "", limit: int = 10) -> dict:
    """Full-text search of the translation memory (source and target). `origin`: 'church' for official Church
    paragraphs, or a backend name (argos, ollama...)."""
    rows = T().store.tm_search(query, lang or None, origin or None, min(limit, 20))
    for r in rows:
        r["source"], r["target"] = r["source"][:300], r["target"][:300]
    return {"results": rows, "memory": T().store.tm_stats()}


@tool
def to_deseret(text: str, confident_only: bool = False) -> dict:
    """Transliterate English text into the Deseret Alphabet (the 38-letter script of the 1860s Church
    printings), using the pulpit-vault engine: dictionary spellings, context-resolved heteronyms
    (read/live/use), capitalization kept. English only. Words with no spelling stay in Latin script
    and are listed. `confident_only` also leaves machine-guessed spellings in Latin. For markdown or
    long documents use deseret_file."""
    if not text.strip():
        raise ValueError("text is required")
    out, cov = deseret.convert_text(text[:20000], confident_only)
    return {"deseret": out, **cov}


@tool
def deseret_file(path: str, output_path: str = "", confident_only: bool = False) -> dict:
    """Transliterate a markdown/text file into the Deseret Alphabet. Frontmatter, code blocks, tables,
    footnote labels and references, links and URLs are kept as they are. The result is written to disk
    (default under the Urim jobs folder, or `output_path`) and only its path and coverage are returned."""
    import hashlib
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    out, cov = deseret.convert_document(text, confident_only)
    if output_path:
        dest = Path(output_path)
    else:
        doc_id = hashlib.sha1(f"{p}|{text[:5000]}".encode("utf-8")).hexdigest()[:10]
        dest = config.HOME / "jobs" / doc_id / f"{p.stem}.dsrt{p.suffix or '.txt'}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")
    return {"output_path": str(dest), **cov}


@tool
def backends_status() -> dict:
    """Which translation backends are available (Argos, LibreTranslate, Ollama) and why not, if unavailable."""
    return {"backends": T().status(), "ollama_model": config.OLLAMA_MODEL, "home": str(config.HOME),
            "deseret": deseret.available()[1]}


def main():
    from . import setup
    setup.auto()                    # first run: install Argos packages, Ollama and its model in the background
    mcp.run()
