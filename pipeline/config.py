"""Paths and language settings shared by the pipeline."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PULPIT = Path(os.environ.get("URIM_PULPIT", ROOT.parent / "pulpit-vault")).resolve()

# Urim language code -> Pulpit file stem / Church ?lang= code / display name
LANGS = {
    "pt": {"pulpit": "pt", "church": "por", "name": "Português (Brasil)"},
    "es": {"pulpit": "es", "church": "spa", "name": "Español"},
}

MASTER = PULPIT / "schema" / "glossary" / "glossary-master.md"
APPROVED = {"es": PULPIT / "schema" / "approved-terms" / "es.md"}
GLOSSARY = {l: PULPIT / "schema" / "glossary" / f"glossary-{l}.md" for l in LANGS}
CORPUS = {l: PULPIT / "indexes" / f"parallel-corpus-{LANGS[l]['pulpit']}.jsonl" for l in LANGS}
SCRIPTURES = {l: PULPIT / "indexes" / "scriptures" / f"{l}.jsonl" for l in ("en", *LANGS)}

CONCEPTS = ROOT / "concepts"
DATA = ROOT / "data"
SITE = ROOT / "site"
