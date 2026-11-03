"""The edition registry (languages.yaml): folders, names, Church codes and typographic settings."""
from functools import lru_cache
from pathlib import Path

import yaml

REGISTRY = Path(__file__).resolve().parent / "languages.yaml"


@lru_cache(maxsize=1)
def load():
    """slug -> entry, in file order (which is the order editions are generated and listed)."""
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    for slug, e in data.items():
        if "-" in slug or slug != slug.lower() or not slug.isascii():
            raise ValueError(f"language slug '{slug}' must be lower-case ASCII without hyphens")
        e.setdefault("kind", "language")
        e.setdefault("hints", {})
        e["slug"] = slug
    return data


def slugs(kind=None):
    return [s for s, e in load().items() if kind is None or e["kind"] == kind]


def get(slug):
    try:
        return load()[slug]
    except KeyError:
        raise KeyError(f"unknown edition '{slug}'; choose from {', '.join(load())}")


def by_code(code):
    for e in load().values():
        if e["code"] == code:
            return e
    raise KeyError(f"no edition with code '{code}'")


def church_languages():
    """code -> entry for editions whose text is fetched from the Church website."""
    return {e["code"]: e for e in load().values() if e["kind"] == "language"}
