"""Deseret Alphabet transliteration for the local MCP, via the package in /deseret (Node).

This is a script conversion of English text, not a translation. Words with no Deseret spelling
stay in Latin script and are reported. Markdown files keep frontmatter, code, tables, footnote
labels and references, links and URLs unchanged.
"""
import json
import shutil
import subprocess

from . import config, segment

CLI = config.REPO / "deseret" / "bin" / "deseret.mjs"
SEP = "\n§\n"     # a lone section sign on its own line passes through transliteration untouched


def available() -> tuple[bool, str]:
    if not CLI.exists():
        return False, f"deseret package not found at {CLI}"
    if not shutil.which("node"):
        return False, "Node.js is not installed or not on PATH"
    return True, "ok"


def _run(text: str, *flags: str) -> str:
    ok, why = available()
    if not ok:
        raise RuntimeError(why)
    r = subprocess.run(["node", str(CLI), *flags], input=text, capture_output=True, text=True,
                       encoding="utf-8", timeout=120)
    if r.returncode:
        raise RuntimeError(f"deseret conversion failed: {r.stderr.strip()[:200]}")
    return r.stdout


def convert_many(strings, confident_only=False):
    """Convert strings together (one process, shared context). Returns (strings, coverage)."""
    flags = ["--confident-only"] if confident_only else []
    joined = SEP.join(strings)
    out = _run(joined, *flags).split(SEP)
    if len(out) != len(strings):
        raise RuntimeError("conversion changed the number of strings")
    cov = json.loads(_run(joined, "--coverage", *flags))
    return out, {"words": cov["words"], "converted": cov["converted"], "left_in_latin": cov["left_latin"][:50]}


def convert_text(text: str, confident_only=False):
    out, cov = convert_many([text], confident_only)
    return out[0], cov


def convert_document(text: str, confident_only=False):
    """Markdown/plain document -> Deseret, preserving structure. Returns (text, coverage)."""
    blocks = segment.split_document(text)
    segs = [b for b in blocks if b.is_seg]
    masked = [segment.protect_markup(b.text) for b in segs]
    out, cov = convert_many([m for m, _ in masked], confident_only) if masked else ([], {"words": 0, "converted": 0, "left_in_latin": []})
    for b, (_, ph), conv in zip(segs, masked, out):
        b.target = segment.restore(conv, ph)
    return segment.join_blocks(blocks), cov
