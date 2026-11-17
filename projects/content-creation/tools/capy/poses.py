"""Saint Capybara's pose roster plus the rhetorical-function -> pose lookup
used when a beat specifies `function:` instead of a literal `pose:` (see
../../docs/saint-capybara/script-format.md and brand.md).

**Pose NAMES below are kept in sync with the finalized AI-generated art**
at `D:\\saint-capybara\\finalized images\\saint-capybara-<pose>.png` (see
brand.md sec 5) -- this is what `capy.beats.validate()` checks beat poses
against. Two poses were renamed from the original 21-pose brief in
production: `reading_source` -> `source`, `explaining_quote` -> `quote`.
The `sign-*` poses (originally generated for the retired sign-of-the-cross
outro -- see git history) are not currently part of this roster; the art
files still exist under FINALIZED_SPRITES_DIR if ever repurposed.

The per-pose *recipe* dicts below (eyes/brows/mouth/paws/props/extras) are
vestigial, left over from the retired code-drawn PIL renderer
(`capy/compose.py`, `capy/parts.py` -- brand.md sec "Sprite art is
AI-generated, not code-drawn"). They are not read by anything in the
current (finalized-art) pipeline; kept only so the old renderer doesn't
error if it's ever run standalone. Do not treat them as meaningful when
adding a new pose -- only the *name* needs to match a finalized PNG.

A pose recipe is a dict of kwargs consumed by capy.compose.compose():
    eyes, brows, mouth, paws, props (list[str]), extras (list[str]),
    head_dy (int, small vertical offset for the face parts only --
    "looking down/up" -- applied to eyes/brows/snout/nose-mouth, not the
    body/ears, since the head no longer separates from the body),
    mouth_open (str | None) -- if set, this is the alternate mouth style
    used for the 2-frame talking flicker (compose() renders a second
    "<pose>_b" image using this style in place of `mouth`).
"""
from __future__ import annotations

Pose = dict

POSES: dict[str, Pose] = {
    "neutral": {
        "eyes": "open", "brows": "neutral", "mouth": "closed",
        "paws": "rest", "props": [], "extras": [], "head_dy": 0,
    },
    "talking": {
        "eyes": "open", "brows": "neutral", "mouth": "small_o",
        "paws": "rest", "props": [], "extras": [], "head_dy": 0,
        "mouth_open": "open",
    },
    "teaching": {
        "eyes": "open", "brows": "raised", "mouth": "small_o",
        "paws": "point_up", "props": [], "extras": [], "head_dy": 0,
        "mouth_open": "open",
    },
    "reading": {
        "eyes": "half", "brows": "neutral", "mouth": "closed",
        "paws": "hold_book_open", "props": [], "extras": [], "head_dy": 2,
    },
    "thoughtful": {
        "eyes": "side", "brows": "raised", "mouth": "flat",
        "paws": "rest", "props": [], "extras": [], "head_dy": -1,
    },
    "pointing": {
        "eyes": "side", "brows": "neutral", "mouth": "closed",
        "paws": "point_side", "props": [], "extras": [], "head_dy": 0,
    },
    "happy": {
        "eyes": "open", "brows": "neutral", "mouth": "smile",
        "paws": "rest", "props": [], "extras": [], "head_dy": 0,
    },
    "concerned": {
        "eyes": "half", "brows": "furrowed", "mouth": "flat",
        "paws": "rest", "props": [], "extras": [], "head_dy": 1,
    },
    "confused": {
        "eyes": "narrow", "brows": "asym", "mouth": "flat",
        "paws": "rest", "props": [], "extras": ["question"], "head_dy": -1,
    },
    "surprised": {
        "eyes": "wide", "brows": "raised", "mouth": "open",
        "paws": "rest", "props": [], "extras": [], "head_dy": 0,
    },
    "skeptical": {
        "eyes": "narrow", "brows": "asym", "mouth": "flat",
        "paws": "rest", "props": [], "extras": [], "head_dy": 0,
    },
    "amused": {
        "eyes": "half", "brows": "raised", "mouth": "smile",
        "paws": "rest", "props": [], "extras": [], "head_dy": 0,
    },
    "prayerful": {
        "eyes": "closed", "brows": "neutral", "mouth": "flat",
        "paws": "prayer", "props": [], "extras": [], "head_dy": 1,
    },
    "solemn": {
        "eyes": "half", "brows": "neutral", "mouth": "flat",
        "paws": "rest", "props": [], "extras": [], "head_dy": 1,
    },
    "encouraging": {
        "eyes": "open", "brows": "raised", "mouth": "smile",
        "paws": "open_palms", "props": [], "extras": [], "head_dy": 0,
        "mouth_open": "open",
    },
    "source": {
        "eyes": "side", "brows": "neutral", "mouth": "closed",
        "paws": "hold_scroll", "props": [], "extras": [], "head_dy": 1,
    },
    "researching": {
        "eyes": "half", "brows": "neutral", "mouth": "closed",
        "paws": "rest", "props": ["books_left", "papers"], "extras": [], "head_dy": 0,
    },
    "quote": {
        "eyes": "side", "brows": "raised", "mouth": "small_o",
        "paws": "point_side", "props": [], "extras": [], "head_dy": 0,
        "mouth_open": "open",
    },
    "listening": {
        "eyes": "open", "brows": "neutral", "mouth": "closed",
        "paws": "rest", "props": [], "extras": [], "head_dy": 0,
    },
    "deadpan": {
        "eyes": "narrow", "brows": "neutral", "mouth": "flat",
        "paws": "rest", "props": [], "extras": [], "head_dy": 0,
    },
    "disappointed": {
        "eyes": "half", "brows": "furrowed", "mouth": "frown",
        "paws": "paw_forehead", "props": [], "extras": [], "head_dy": 2,
    },
}

POSE_ORDER = [
    "neutral", "talking", "teaching", "reading", "thoughtful", "pointing",
    "happy", "concerned", "confused", "surprised", "skeptical", "amused",
    "prayerful", "solemn", "encouraging", "source", "researching",
    "quote", "listening", "deadpan", "disappointed",
]
assert set(POSE_ORDER) == set(POSES), "POSE_ORDER and POSES must match exactly"

# Poses that also get a mouth-open "_b" frame for the 2-frame talking
# flicker during narration (see docs/saint-capybara/script-format.md and
# capy_render.py). These are the poses actually usable while narrating.
TALKING_CAPABLE = {"talking", "teaching", "encouraging", "quote"}

# Rhetorical function -> ordered pose preference (script-format.md picks
# the first entry unless the beat overrides with a literal `pose:`).
FUNCTION_TO_POSE: dict[str, list[str]] = {
    "evidence": ["source", "reading", "neutral"],
    "uncertainty": ["thoughtful", "confused"],
    "serious": ["concerned", "solemn"],
    "questionable_premise": ["skeptical"],
    "factual_failure": ["disappointed", "deadpan"],
    "light": ["amused", "happy"],
    "explain": ["teaching", "quote", "pointing"],
    "listen": ["listening"],
    "closing": ["encouraging", "prayerful"],
}

# Never selected on a beat (or whole video) marked sensitive: true --
# enforced by tools/capy_check_sources.py, not just a docs convention.
SENSITIVE_FORBIDDEN = {"amused", "happy"}
