"""The `excerpt` beat: an article source's own words, anchored to a
numbered paragraph, read by a second Kokoro voice, rendered as a
pull-quote card, budgeted as source time (plan Part 4.3-4.4).

Standalone-importable. capy.beats does NOT import this module yet; the
owner of beats.py wires it in (see the hand-off notes):

    from capy.excerpts import validate_excerpt_beats, resolve_voice, speech_text

    issues += validate_excerpt_beats(doc)           # structural, no file access
    spec = resolve_voice(doc, beat)                 # {"name","speed","role"}
    text = speech_text(beat)                        # for TTS, before apply_dictionary

File-backed rules (verbatim match against source.md, sha256 pin, the
source-time budget) live in tools/capy_check_sources.py and use
capy.source.

`Issue` is imported lazily inside the functions so this module can be
imported from capy.beats without a circular import.
"""
from __future__ import annotations

import re
from typing import Any

from capy.source import (
    ELLIPSIS_TOKEN,
    excerpt_fragments,
    para_span,
    strip_outer_quotes,
    word_count,
)

EXCERPT_KIND = "excerpt"
SOURCE_TIME_KINDS = {"clip", EXCERPT_KIND}

EXCERPT_MAX_WORDS = 60          # warning above this
EXCERPT_HARD_MAX_WORDS = 100    # error above this
EXCERPT_MIN_FRAGMENT_WORDS = 3  # each `[...]`-separated piece
EXCERPT_MAX_PARAGRAPHS = 2      # one paragraph boundary at most
SOURCE_TIME_MAX_FRACTION = 0.30 # clips + excerpts vs total runtime

# Voice roles. `host` is doc["voice"]; the quote voices are TENTATIVE
# until the Part 3 bake-off locks them (quote_male is a locally-present
# pack so TTS works offline; af_heart is upstream's top-graded female
# voice and auto-downloads ~520 KB on first use).
VOICE_ROLES = {"quote_male", "quote_female"}
DEFAULT_VOICES: dict[str, Any] = {
    "quote_male": {"name": "bm_george", "speed": 1.0},
    "quote_female": {"name": "af_heart", "speed": 1.0},
    "quote_default": "quote_male",
}
DEFAULT_HOST_VOICE = {"name": "am_michael", "speed": 0.95}


def is_excerpt(beat: dict) -> bool:
    return beat.get("kind") == EXCERPT_KIND


def _voices_table(doc: dict) -> dict:
    merged: dict[str, Any] = dict(DEFAULT_VOICES)
    for k, v in (doc.get("voices") or {}).items():
        merged[k] = v
    return merged


def known_voice_roles(doc: dict) -> set[str]:
    table = _voices_table(doc)
    return {k for k, v in table.items() if isinstance(v, dict)} | {"host"}


# ---------------------------------------------------------------------------
# Structural validation (no file access)
# ---------------------------------------------------------------------------

def validate_excerpt_beats(doc: dict) -> list:
    """Rules from plan 4.4 that need no file access. Returns list[Issue].

    - `text` + `para` required; `para` is an int or [a, b] with b == a+1
    - `[...]` never at the start or end; each fragment >= 3 words
    - `highlight:` forbidden (captions come from the excerpt's own timing)
    - > EXCERPT_MAX_WORDS warning, > EXCERPT_HARD_MAX_WORDS error
    - `voice:` must be a known role or an inline {name[, speed]} dict
    - any beat with `stage: freeze` before the first clip beat -> error
      (today it silently renders blank)
    """
    from capy.beats import Issue  # lazy: avoid a cycle once beats.py imports this module

    issues: list[Issue] = []
    beats = doc.get("beats") or []
    roles = known_voice_roles(doc)
    quote_default = _voices_table(doc).get("quote_default")
    if quote_default not in roles:
        issues.append(Issue("error", None, f"voices.quote_default '{quote_default}' is not a defined voice role ({sorted(roles)})"))

    seen_clip = False
    for i, beat in enumerate(beats):
        bid = beat.get("id") or f"#{i}"
        kind = beat.get("kind")

        if beat.get("stage") == "freeze" and not seen_clip:
            issues.append(Issue("error", bid, "stage: freeze but no clip beat precedes it -- there is no frame to freeze (would render blank); use stage: blank"))
        if kind == "clip":
            seen_clip = True

        if kind != EXCERPT_KIND:
            continue

        text = beat.get("text")
        if not text or not str(text).strip():
            issues.append(Issue("error", bid, "excerpt beat requires 'text' (the source's verbatim words)"))
        para = beat.get("para")
        if para is None:
            issues.append(Issue("error", bid, "excerpt beat requires 'para' (int paragraph number, or [a, b] across one boundary)"))
        else:
            try:
                nums = para_span(para)
                if any(n < 1 for n in nums):
                    issues.append(Issue("error", bid, "para numbers start at 1"))
                if len(nums) > EXCERPT_MAX_PARAGRAPHS:
                    issues.append(Issue("error", bid, f"excerpt spans {len(nums)} paragraphs; at most {EXCERPT_MAX_PARAGRAPHS} (one boundary) are allowed -- split into two excerpt beats"))
                elif len(nums) == 2 and nums[1] != nums[0] + 1:
                    issues.append(Issue("error", bid, f"para [{nums[0]}, {nums[1]}] must be consecutive paragraphs"))
            except TypeError as e:
                issues.append(Issue("error", bid, f"invalid para: {e}"))

        if text:
            t = strip_outer_quotes(str(text))
            if t.startswith(ELLIPSIS_TOKEN) or t.endswith(ELLIPSIS_TOKEN):
                issues.append(Issue("error", bid, "excerpt must not start or end with [...] -- trim to the words actually quoted"))
            frags = excerpt_fragments(t)
            if not frags:
                issues.append(Issue("error", bid, "excerpt text has no words outside [...]"))
            for j, frag in enumerate(frags):
                if len(frag.split()) < EXCERPT_MIN_FRAGMENT_WORDS:
                    issues.append(Issue("error", bid, f"excerpt fragment #{j + 1} (“{frag}”) is under {EXCERPT_MIN_FRAGMENT_WORDS} words -- too short to verify as a quotation"))
            if re.search(r"\.\.\.|…", t.replace(ELLIPSIS_TOKEN, "")):
                issues.append(Issue("warning", bid, "excerpt contains a bare ellipsis; use [...] for an editorial cut so it is validated and drawn consistently"))
            n = word_count(t)
            if n > EXCERPT_HARD_MAX_WORDS:
                issues.append(Issue("error", bid, f"excerpt is {n} words (> {EXCERPT_HARD_MAX_WORDS}); cut it down or split it"))
            elif n > EXCERPT_MAX_WORDS:
                issues.append(Issue("warning", bid, f"excerpt is {n} words (> {EXCERPT_MAX_WORDS} guideline)"))

        if beat.get("highlight"):
            issues.append(Issue("error", bid, "highlight: is forbidden on excerpt beats (the source's words are never colour-emphasised)"))

        v = beat.get("voice")
        if isinstance(v, dict):
            if not v.get("name"):
                issues.append(Issue("error", bid, "inline voice needs 'name' (and optional 'speed')"))
        elif isinstance(v, str):
            if v not in roles:
                issues.append(Issue("error", bid, f"unknown voice role '{v}' (expected one of {sorted(roles)} or an inline {{name, speed}} dict)"))
        elif v is not None:
            issues.append(Issue("error", bid, "voice must be a role name or an inline {name, speed} dict"))

        if beat.get("sources"):
            issues.append(Issue("info", bid, "excerpt beats are validated against source.md, not sources:; the sources list here is ignored"))
    return issues


# ---------------------------------------------------------------------------
# Voice resolution
# ---------------------------------------------------------------------------

def resolve_voice(doc: dict, beat: dict) -> dict:
    """{name, speed, role}: inline dict wins; else a role name looked up in
    doc["voices"] (merged over DEFAULT_VOICES); else the kind default --
    excerpt -> voices.quote_default, everything else -> doc["voice"]."""
    v = beat.get("voice")
    table = _voices_table(doc)
    host = dict(DEFAULT_HOST_VOICE)
    host.update(doc.get("voice") or {})

    if isinstance(v, dict):
        if not v.get("name"):
            raise ValueError(f"beat {beat.get('id')}: inline voice needs 'name'")
        return {"name": v["name"], "speed": float(v.get("speed", 1.0)), "role": "inline"}

    if isinstance(v, str):
        role = v
    elif is_excerpt(beat):
        role = table.get("quote_default", "quote_male")
    else:
        return {"name": host["name"], "speed": float(host.get("speed", 0.95)), "role": "host"}

    if role == "host":
        return {"name": host["name"], "speed": float(host.get("speed", 0.95)), "role": "host"}
    spec = table.get(role)
    if not isinstance(spec, dict) or not spec.get("name"):
        raise KeyError(f"beat {beat.get('id')}: unknown voice role {role!r} (defined: {sorted(known_voice_roles(doc))})")
    return {"name": spec["name"], "speed": float(spec.get("speed", 1.0)), "role": role}


# ---------------------------------------------------------------------------
# Text for TTS
# ---------------------------------------------------------------------------

_PAUSE_TRAIL_RE = re.compile(r"[,;:\-\s]+$")


def speech_text(beat: dict) -> str:
    """What Kokoro reads for a beat: outer quote marks dropped, each `[...]`
    turned into a sentence pause. The literal brackets would otherwise
    collide with misaki's `[word](/ipa/)` override syntax, so this must run
    BEFORE capy_tts.apply_dictionary."""
    text = str(beat.get("text") or "")
    if not is_excerpt(beat):
        return text
    t = strip_outer_quotes(text)
    frags = excerpt_fragments(t)
    if not frags:
        return ""
    out = frags[0]
    for frag in frags[1:]:
        out = _PAUSE_TRAIL_RE.sub("", out)
        if not out.endswith((".", "!", "?")):
            out += "."
        out += " " + frag
    return re.sub(r"\s+", " ", out).strip()


def caption_text(beat: dict) -> str:
    """Excerpt text as captions see it: `[...]` dropped, outer quotes
    dropped (the card shows the brackets; captions never do)."""
    t = strip_outer_quotes(str(beat.get("text") or ""))
    return re.sub(r"\s+", " ", t.replace(ELLIPSIS_TOKEN, " ")).strip()


# ---------------------------------------------------------------------------
# Source-time budget
# ---------------------------------------------------------------------------

def source_time_seconds(doc: dict, per_beat: dict[str, float]) -> float:
    """Seconds of the source's own material (clip + excerpt beats)."""
    return round(sum(per_beat.get(b["id"], 0.0) for b in doc.get("beats") or [] if b.get("kind") in SOURCE_TIME_KINDS), 3)


def excerpt_word_total(doc: dict) -> int:
    return sum(word_count(strip_outer_quotes(str(b.get("text") or ""))) for b in doc.get("beats") or [] if is_excerpt(b))
