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

UI_LANGS = {"pt": "Brazilian Portuguese", "es": "Spanish"}
