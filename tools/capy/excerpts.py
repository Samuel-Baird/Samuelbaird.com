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

# Voice roles. `host` is doc["voice"]. quote_male/quote_female are POOLS
# (lists of voice specs, not a single voice) -- LOCKED 2026-09-11 to
# Chatterbox reference-clip pools (host_andrew_kennedy stays HOST-only;
# see assets/saint-capybara/voices/PROVENANCE.md for every clip's
# source/license). Each role resolves to one pool member via
# capy.voice_pool.assign(), keyed on the beat's `speaker:` slug so the
# same quoted person always gets the same voice.
VOICE_ROLES = {"quote_male", "quote_female"}
from capy.beats import DEFAULT_VOICE as _HOST_VOICE, QUOTE_MALE_POOL, QUOTE_FEMALE_POOL  # noqa: E402

DEFAULT_VOICES: dict[str, Any] = {
    "quote_male": QUOTE_MALE_POOL,
    "quote_female": QUOTE_FEMALE_POOL,
    "quote_default": "quote_male",
}
DEFAULT_HOST_VOICE = _HOST_VOICE


def is_excerpt(beat: dict) -> bool:
    return beat.get("kind") == EXCERPT_KIND


def _voices_table(doc: dict) -> dict:
    merged: dict[str, Any] = dict(DEFAULT_VOICES)
    for k, v in (doc.get("voices") or {}).items():
        merged[k] = v
    return merged


def known_voice_roles(doc: dict) -> set[str]:
    table = _voices_table(doc)
    return {k for k, v in table.items() if isinstance(v, (dict, list))} | {"host"}


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
        if beat.get("stage") == "video" and not seen_clip and beat.get("background_start") is None:
            issues.append(Issue("error", bid, "stage: video with no preceding clip beat and no explicit 'background_start' -- there is no source-video position to composite; add background_start (seconds into source.mp4) or use stage: freeze/image/blank"))
        if beat.get("stage") == "image" and not beat.get("background"):
            issues.append(Issue("error", bid, "stage: image requires a 'background' field (project-relative image path)"))
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
            engine = v.get("engine")
            if not engine:
                issues.append(Issue("error", bid, "inline voice needs 'engine' (kokoro|chatterbox)"))
            elif engine == "kokoro" and not v.get("name"):
                issues.append(Issue("error", bid, "inline kokoro voice needs 'name' (and optional 'speed')"))
            elif engine == "chatterbox" and not v.get("ref"):
                issues.append(Issue("error", bid, "inline chatterbox voice needs 'ref' (path to a reference clip, and optional speed/exaggeration/cfg_weight)"))
        elif isinstance(v, str):
            if v not in roles:
                issues.append(Issue("error", bid, f"unknown voice role '{v}' (expected one of {sorted(roles)} or an inline {{engine, ...}} dict)"))
        elif v is not None:
            issues.append(Issue("error", bid, "voice must be a role name or an inline {engine, ...} dict"))

        speaker = beat.get("speaker")
        if speaker is not None and not isinstance(speaker, str):
            issues.append(Issue("error", bid, "'speaker' must be a string (a stable name/slug for the quoted person -- see capy.voice_pool)"))

        if beat.get("sources"):
            issues.append(Issue("info", bid, "excerpt beats are validated against source.md, not sources:; the sources list here is ignored"))
    return issues


# ---------------------------------------------------------------------------
# Voice resolution
# ---------------------------------------------------------------------------

def resolve_voice(doc: dict, beat: dict, *, default_speaker: str | None = None) -> dict:
    """The beat's full effective voice spec, tagged with `role` for
    debugging/logging: an inline `voice: {...}` dict wins (engine
    required, everything else engine-specific -- e.g. {engine: kokoro,
    name, speed} or {engine: chatterbox, ref, speed, exaggeration,
    cfg_weight}); else a role name looked up in doc["voices"] (merged
    over DEFAULT_VOICES) -- when that role is a POOL (a list of voice
    specs: quote_male/quote_female), the member is picked by
    capy.voice_pool.assign(), keyed on the beat's `speaker:` slug (falls
    back to `default_speaker`, e.g. the source's byline for excerpt
    beats, then to a shared 'unknown' slot -- see
    capy.voice_pool.speaker_slug) so the same quoted person always gets
    the same voice; else the kind default -- excerpt ->
    voices.quote_default, everything else -> doc["voice"]."""
    from capy.voice_pool import assign, speaker_slug

    v = beat.get("voice")
    table = _voices_table(doc)
    host = dict(DEFAULT_HOST_VOICE)
    host.update(doc.get("voice") or {})

    def _with_role(spec: dict, role: str) -> dict:
        out = dict(spec)
        out["role"] = role
        return out

    def _resolve_role(role: str) -> dict:
        if role == "host":
            return _with_role(host, "host")
        spec = table.get(role)
        if spec is None:
            raise KeyError(f"beat {beat.get('id')}: unknown voice role {role!r} (defined: {sorted(known_voice_roles(doc))})")
        if isinstance(spec, list):  # a pool -- pick this speaker's assigned member
            if not spec:
                raise KeyError(f"beat {beat.get('id')}: voice role {role!r} is an empty pool")
            slug = speaker_slug(beat, default=default_speaker)
            return _with_role(assign(role, slug, spec), role)
        if not isinstance(spec, dict):
            raise KeyError(f"beat {beat.get('id')}: voice role {role!r} is neither a voice dict nor a pool (defined: {sorted(known_voice_roles(doc))})")
        return _with_role(spec, role)

    if isinstance(v, dict):
        if not v.get("engine"):
            raise ValueError(f"beat {beat.get('id')}: inline voice needs 'engine' (kokoro|chatterbox)")
        return _with_role(v, "inline")

    if isinstance(v, str):
        return _resolve_role(v)

    if is_excerpt(beat):
        return _resolve_role(table.get("quote_default", "quote_male"))

    return _with_role(host, "host")


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
