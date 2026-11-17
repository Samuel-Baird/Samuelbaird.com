"""The edition registry: languages.yaml (hand-written) plus languages.generated.yaml (python -m proclamations.register)."""
from functools import lru_cache
from pathlib import Path

import yaml

REGISTRY = Path(__file__).resolve().parent / "languages.yaml"
GENERATED = Path(__file__).resolve().parent / "languages.generated.yaml"


@lru_cache(maxsize=1)
def load():
    """slug -> entry, in file order (which is the order editions are generated and listed)."""
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    if GENERATED.exists():                       # hand-written entries win; generated ones fill in the rest
        have = {e["code"] for e in data.values()}
        for slug, e in (yaml.safe_load(GENERATED.read_text(encoding="utf-8")) or {}).items():
            if slug not in data and e["code"] not in have:
                data[slug] = e
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
