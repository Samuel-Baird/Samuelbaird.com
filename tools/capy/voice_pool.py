"""Speaker -> pool-voice assignment, persisted so the same quoted person
always gets the same Chatterbox reference voice, both across beats
within one project AND across separate projects/pipeline runs that quote
them again later.

    from capy.voice_pool import speaker_slug, assign

    slug = speaker_slug(beat, default=byline_slug)   # beat['speaker'] wins
    spec = assign("quote_male", slug, QUOTE_MALE_POOL)  # -> one pool member dict

Assignment is a stable hash of the slug into the pool, computed once per
(pool name, slug) pair and written to
`assets/saint-capybara/voice_pool_assignments.json` (repo-level, shared
across all projects -- not per-project). A slug already recorded there
always returns the same member regardless of hashing (so manually
editing the file to correct/reassign a specific person works and
sticks). A pool of size 1 (today's quote_female) always assigns index 0
-- no hash collision possible or meaningful.

Not thread-safe / not safe for concurrent writers -- this repo's tools
run one at a time, so a plain read-modify-write is fine.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ASSIGNMENTS_PATH = REPO_ROOT / "assets" / "saint-capybara" / "voice_pool_assignments.json"

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(name: str) -> str:
    """'Brigham Young' -> 'brigham-young'. Collapses any run of
    non-alphanumeric characters to a single hyphen and strips leading/
    trailing hyphens. Empty/whitespace-only input -> ''."""
    s = _SLUG_RE.sub("-", name.strip().lower()).strip("-")
    return s


def speaker_slug(beat: dict, *, default: str | None = None) -> str:
    """The beat's own `speaker:` field wins (slugified if not already
    slug-shaped); else `default` (already expected to be a slug, e.g.
    derived from the source's byline by the caller -- this module never
    touches source_info.json itself); else 'unknown' so callers never
    have to special-case a missing speaker (every unattributed quote
    shares one pool slot rather than erroring)."""
    raw = beat.get("speaker")
    if raw:
        return slugify(str(raw))
    if default:
        return slugify(str(default))
    return "unknown"


def load_assignments() -> dict[str, dict[str, int]]:
    if not ASSIGNMENTS_PATH.exists():
        return {}
    return json.loads(ASSIGNMENTS_PATH.read_text(encoding="utf-8"))


def save_assignments(data: dict[str, dict[str, int]]) -> None:
    ASSIGNMENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ASSIGNMENTS_PATH.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _hash_index(pool_name: str, slug: str, pool_size: int) -> int:
    """Deterministic (not random-per-run) index in [0, pool_size) for a
    (pool_name, slug) pair, from a stable sha256 hash -- not Python's
    salted hash(), which changes between interpreter runs."""
    h = hashlib.sha256(f"{pool_name}:{slug}".encode("utf-8")).hexdigest()
    return int(h, 16) % pool_size


def assign(pool_name: str, slug: str, pool: list[dict[str, Any]]) -> dict[str, Any]:
    """The pool-member voice spec for `slug` in `pool_name`'s pool.
    Persists (and reuses) the assignment in voice_pool_assignments.json.
    Raises ValueError if `pool` is empty (a misconfigured pool, not a
    normal runtime condition -- callers should let this surface loudly
    rather than silently falling back to some other voice)."""
    if not pool:
        raise ValueError(f"voice pool {pool_name!r} is empty -- nothing to assign")

    data = load_assignments()
    pool_assignments = data.setdefault(pool_name, {})

    idx = pool_assignments.get(slug)
    if idx is None or not (0 <= idx < len(pool)):
        # Either never assigned, or the pool shrank since the last
        # assignment (index out of range) -- (re)assign deterministically.
        idx = _hash_index(pool_name, slug, len(pool))
        pool_assignments[slug] = idx
        save_assignments(data)

    return pool[idx]
