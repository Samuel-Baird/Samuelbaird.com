"""Settings. Environment variables override ~/.urim/urim.toml, which overrides defaults."""
import os
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

HOME = Path(os.environ.get("URIM_HOME", Path.home() / ".urim"))


def _file():
    p = HOME / "urim.toml"
    return tomllib.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


_F = _file()


def get(key: str, default):
    return os.environ.get("URIM_" + key.upper(), _F.get(key, default))


def jobs_dir() -> Path:
    """Where agent-pipeline jobs live (default <URIM_HOME>/jobs); set URIM_JOBS_DIR to keep runs apart."""
    return Path(get("jobs_dir", HOME / "jobs"))


GLOSSARY_DIR = Path(get("glossary_dir", REPO / "data" / "glossary"))
BOOKS_FILE = Path(get("books_file", REPO / "data" / "scripture_books.json"))
PULPIT = Path(get("pulpit", REPO.parent / "pulpit-vault"))

OLLAMA_URL = get("ollama_url", "http://localhost:11434")
OLLAMA_MODEL = get("ollama_model", "qwen3.5:4b")
LIBRETRANSLATE_URL = get("libretranslate_url", "")  # e.g. http://localhost:5000; empty = off
BACKENDS = [b.strip() for b in str(get("backends", "argos,libretranslate,ollama")).split(",") if b.strip()]

INLINE_LIMIT = int(get("inline_limit", 1500))   # chars returned inline before spilling to a file
LLM_BATCH_SEGMENTS = int(get("llm_batch_segments", 6))
LLM_BATCH_CHARS = int(get("llm_batch_chars", 2000))
UI_LANGS = {"pt": "Brazilian Portuguese", "es": "Spanish"}
ARGOS_CODE = {"pt": "pt", "es": "es"}
