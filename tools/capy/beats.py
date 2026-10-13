"""beats.yaml schema, loading, validation, and duration resolution for the
Saint Capybara video type.

See docs/saint-capybara/script-format.md for the full field reference (this
module's BEAT_KINDS / REQUIRED_FIELDS mirror that doc exactly -- if you
change one, change the other). Every video's closing beat ends on "...God
bless." (brand.md sec 5a) -- an ordinary narration beat, not a special kind;
there is no fixed/mandatory structural sequence to auto-append (that was
the sign-of-the-cross outro, retired 2026-09-09 -- see git history if ever
needed).

    from capy.beats import load_beats, validate, resolve_durations

    doc = load_beats(Path("script/beats.yaml"))
    issues = validate(doc)                         # list[Issue]
    total, per_beat = resolve_durations(doc, tts_durations={"n01": 4.2, ...})

`excerpt` beats (article/text-source mode, see
docs/saint-capybara/script-format.md "Excerpt fairness") are the source's
own words quoted from source/source.md -- the file-access-requiring checks
(verbatim substring, paragraph anchor resolution, sha256 pin) live in
capy.excerpts / capy_check_sources.py, not here; this module only owns the
structural rules that need no file access.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

try:
    from capy.poses import FUNCTION_TO_POSE, SENSITIVE_FORBIDDEN, POSES
except ImportError:  # pragma: no cover - allows use without tools/ on sys.path in ad-hoc tests
    FUNCTION_TO_POSE, SENSITIVE_FORBIDDEN, POSES = {}, set(), {}

BEAT_KINDS = {"clip", "narration", "card", "evidence", "chart", "excerpt"}

# Beat kinds that carry narration/spoken text and need a resolved voice
# and duration from TTS (mirrors capy_tts.BEAT_KINDS_WITH_NARRATION, kept
# here too since resolve_voice() needs it and beats.py has no reverse
# dependency on capy_tts.py).
NARRATION_FAMILY_KINDS = {"narration", "card", "evidence", "chart", "excerpt"}

# Words-per-minute used to *estimate* a hold/TTS duration before real TTS
# has run (Step 3 lock: 0.9-0.95 speed, ~140-150 wpm target -- see brand.md
# sec 6). Only used pre-TTS (storyboard/lint preview); once capy_tts.py has
# rendered a beat, its measured wav duration always wins in
# resolve_durations() via the tts_durations map.
ESTIMATE_WORDS_PER_SECOND = 220 / 60.0
HOLD_BASE_SECONDS = 3.0
HOLD_PER_WORD_SECONDS = 0.15

# The three Saint Capybara video types (script-format.md "Video types"):
# runtime budget, canvas orientation, and canvas size. Both long-form
# types are opted into explicitly by the user per video -- never chosen
# by the agent to make an over-long short fit -- and must carry
# `long_form_requested:` recording the user's own request.
VIDEO_TYPES = {
    "short":          {"budget": (60, 180),   "orientation": "portrait",  "size": (1080, 1920)},
    "long-instagram": {"budget": (180, 1200), "orientation": "portrait",  "size": (1080, 1920)},
    "long-youtube":   {"budget": (180, 1200), "orientation": "landscape", "size": (1920, 1080)},
}
LONG_FORM_TYPES = {"long-instagram", "long-youtube"}
# `length: long` (2026-10-09, before YouTube long form existed) meant
# Instagram long form; still accepted when `video_type:` is absent.
LEGACY_LENGTH_TO_TYPE = {"short": "short", "long": "long-instagram"}

# Locked 2026-09-09 (user confirmed after watching dont-read-the-bom's
# render) -- see docs/saint-capybara/brand.md sec 6. am_michael at speed
# 1.5 (raised from the original 0.95 lock the same day, also user
# direction).
DEFAULT_VOICE = {"name": "am_michael", "speed": 1.5}
DEFAULT_VOICES = {
    "quote_male": {"name": "am_michael", "speed": 1.0},
    "quote_female": {"name": "af_heart", "speed": 1.0},
    "quote_default": "quote_male",
}


@dataclass
class Issue:
    level: str  # "error" | "warning" | "info"
    beat_id: str | None
    message: str

    def __str__(self) -> str:
        loc = f"[{self.beat_id}] " if self.beat_id else ""
        return f"{self.level.upper():7s} {loc}{self.message}"


def _word_count(text: str | None) -> int:
    if not text:
        return 0
    return len(text.split())


def estimate_hold_seconds(text: str | None) -> float:
    """Pre-TTS duration estimate for a narration-family beat: either a
    words-per-second read-time estimate, or the plan's `hold` formula
    (3s + 0.15s/word) when text is empty (a pure evidence/image hold)."""
    words = _word_count(text)
    if words == 0:
        return HOLD_BASE_SECONDS
    return words / ESTIMATE_WORDS_PER_SECOND


def load_beats(path: Path | str) -> dict:
    """Load beats.yaml, applying defaults. Does NOT write the file back."""
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw.setdefault("version", 1)
    raw.setdefault("sensitive", False)
    raw.setdefault("music", None)
    raw.setdefault("tags", [])
    if "video_type" not in raw:
        raw["video_type"] = LEGACY_LENGTH_TO_TYPE.get(raw.get("length", "short"), raw.get("length"))
    spec = VIDEO_TYPES.get(raw["video_type"], VIDEO_TYPES["short"])
    raw.setdefault("format", {})
    fmt = raw["format"]
    fmt.setdefault("width", spec["size"][0])
    fmt.setdefault("height", spec["size"][1])
    fmt.setdefault("fps", 30)
    lo, hi = spec["budget"]
    fmt.setdefault("min_seconds", lo)
    fmt.setdefault("max_seconds", hi)
    raw.setdefault("voice", dict(DEFAULT_VOICE))
    raw.setdefault("voices", copy.deepcopy(DEFAULT_VOICES))
    return raw


def dump_beats(doc: dict, path: Path | str) -> None:
    Path(path).write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")


def resolve_pose(beat: dict, *, sensitive: bool) -> str | None:
    """Resolve a beat's effective pose: an explicit `pose:` wins; else the
    first entry of FUNCTION_TO_POSE[beat['function']] that isn't forbidden
    when `sensitive` is set."""
    if beat.get("pose"):
        return beat["pose"]
    fn = beat.get("function")
    if not fn or fn not in FUNCTION_TO_POSE:
        return None
    candidates = FUNCTION_TO_POSE[fn]
    if sensitive:
        candidates = [p for p in candidates if p not in SENSITIVE_FORBIDDEN] or candidates
    return candidates[0] if candidates else None


def resolve_voice(doc: dict, beat: dict) -> dict:
    """{name, speed[, role]}: delegates to capy.excerpts.resolve_voice
    (an inline `voice: {name, speed}` dict wins; else a role name via
    doc['voices'] merged over capy.excerpts.DEFAULT_VOICES; else the kind
    default -- excerpt -> voices.quote_default, everything else ->
    doc['voice']). Falls back to a local, more permissive implementation
    (never raises on an unknown role) if capy.excerpts isn't importable,
    so this module has no hard dependency on the article-mode workstream."""
    try:
        from capy.excerpts import resolve_voice as _resolve_voice
        return _resolve_voice(doc, beat)
    except ImportError:
        pass
    v = beat.get("voice")
    if isinstance(v, dict):
        return {"name": v["name"], "speed": v.get("speed", 1.0)}
    voices = doc.get("voices") or {}
    if isinstance(v, str):
        role = voices.get(v)
        if isinstance(role, dict):
            return {"name": role["name"], "speed": role.get("speed", 1.0)}
    if beat.get("kind") == "excerpt":
        default_role = voices.get("quote_default", "quote_male")
        role = voices.get(default_role)
        if isinstance(role, dict):
            return {"name": role["name"], "speed": role.get("speed", 1.0)}
    host = doc.get("voice") or DEFAULT_VOICE
    return {"name": host["name"], "speed": host.get("speed", 1.0)}


def validate(doc: dict) -> list[Issue]:
    """Structural + editorial validation. Returns a list of Issue; callers
    (capy_check_sources.py, capy_storyboard.py) decide whether "error"-level
    issues are hard-fail (they should be, before Gate A) or downgraded with
    --draft."""
    issues: list[Issue] = []

    for key in ("slug", "title", "beats"):
        if not doc.get(key):
            issues.append(Issue("error", None, f"missing required top-level field: {key}"))

    beats = doc.get("beats", [])
    if not beats:
        issues.append(Issue("error", None, "beats list is empty"))
        return issues

    seen_ids: set[str] = set()
    for i, beat in enumerate(beats):
        bid = beat.get("id")
        if not bid:
            issues.append(Issue("error", None, f"beat #{i} missing 'id'"))
            bid = f"#{i}"
        elif bid in seen_ids:
            issues.append(Issue("error", bid, "duplicate beat id"))
        seen_ids.add(bid)

        kind = beat.get("kind")
        if kind not in BEAT_KINDS:
            issues.append(Issue("error", bid, f"unknown kind '{kind}' (expected one of {sorted(BEAT_KINDS)})"))
            continue

        if kind == "clip":
            if beat.get("start") is None or beat.get("end") is None:
                issues.append(Issue("error", bid, "clip beat requires 'start' and 'end'"))
            elif beat["end"] <= beat["start"]:
                issues.append(Issue("error", bid, "clip 'end' must be after 'start'"))
            span = (beat.get("end", 0) - beat.get("start", 0))
            if span > 20:
                issues.append(Issue("warning", bid, f"clip beat is {span:.1f}s, longer than the 20s continuous-span guideline"))

        if kind in ("narration", "card", "evidence", "chart"):
            if not beat.get("text") and not beat.get("evidence", {}).get("image"):
                issues.append(Issue("warning", bid, "no text and no evidence image -- beat will just be a hold"))
            if not beat.get("opinion") and not beat.get("sources"):
                issues.append(Issue("error", bid, "factual beat cites no sources and isn't marked opinion: true"))

        # excerpt structural rules (text/para/highlight/voice-role) and the
        # stage:freeze-needs-a-prior-clip rule both live in
        # capy.excerpts.validate_excerpt_beats (delegated to below) so
        # article-mode and video-mode share one implementation.
        if beat.get("stage") == "freeze" and kind != "narration":
            issues.append(Issue("warning", bid, "stage: freeze is only meaningful on narration (HOST-mode) beats"))

        if kind == "evidence" and not beat.get("evidence", {}).get("image"):
            issues.append(Issue("error", bid, "evidence beat missing evidence.image"))

        if kind == "card" and not beat.get("card", {}).get("quote"):
            issues.append(Issue("error", bid, "card beat missing card.quote"))

        pose = resolve_pose(beat, sensitive=bool(doc.get("sensitive")))
        if pose and POSES and pose not in POSES:
            issues.append(Issue("error", bid, f"pose '{pose}' is not in the sprite roster"))
        if doc.get("sensitive") and pose in SENSITIVE_FORBIDDEN:
            issues.append(Issue("error", bid, f"pose '{pose}' is forbidden on a sensitive-flagged video/beat"))

    last_beat = beats[-1]
    last_text = (last_beat.get("text") or "").strip().rstrip(".!…").rstrip()
    if not last_text.lower().endswith("god bless"):
        issues.append(Issue("error", last_beat.get("id"), "every video's closing beat must end on \"...God bless.\" (brand.md sec 5a) -- last beat's text doesn't"))

    hook = doc.get("hook")
    if not hook:
        issues.append(Issue("warning", None, "no 'hook' text set for the description/title"))

    issues.extend(validate_video_type(doc))

    try:
        from capy.excerpts import validate_excerpt_beats
        issues.extend(validate_excerpt_beats(doc))
    except ImportError:
        pass  # capy.excerpts not present yet (article-mode workstream)

    return issues


def orientation_for(doc: dict) -> str:
    """'portrait' (9:16) or 'landscape' (16:9) for a loaded beats.yaml."""
    return VIDEO_TYPES.get(doc.get("video_type", "short"), VIDEO_TYPES["short"])["orientation"]


def validate_video_type(doc: dict) -> list[Issue]:
    """`video_type: short | long-instagram | long-youtube` and the format it
    permits. A `format.max_seconds` above the short ceiling is only allowed
    on a long-form type, and a long-form type is only allowed with
    `long_form_requested:` set -- so a short can't drift long by editing
    its budget, and long form can't be chosen without the user asking.
    `format.width/height` must match the type's orientation (the render
    tools pick the 9:16 or 16:9 layout from `video_type`, not from
    `format`)."""
    issues: list[Issue] = []
    vt = doc.get("video_type", "short")
    if vt not in VIDEO_TYPES:
        return [Issue("error", None, f"unknown video_type '{vt}' (expected one of {sorted(VIDEO_TYPES)})")]
    spec = VIDEO_TYPES[vt]
    fmt = doc.get("format", {})
    _, short_hi = VIDEO_TYPES["short"]["budget"]
    _, budget_hi = spec["budget"]
    hi = fmt.get("max_seconds", budget_hi)
    if vt == "short" and hi > short_hi:
        issues.append(Issue("error", None, f"format.max_seconds {hi}s exceeds the {short_hi}s short-form ceiling -- "
                                           "split into two slugs, or use a long-form video_type only if the user explicitly asked for long form"))
    if hi > budget_hi:
        issues.append(Issue("error", None, f"format.max_seconds {hi}s exceeds the {budget_hi}s {vt} ceiling"))
    if vt in LONG_FORM_TYPES and not str(doc.get("long_form_requested") or "").strip():
        issues.append(Issue("error", None, f"video_type: {vt} requires long_form_requested: (date + the user's own words asking for it) -- "
                                           "never choose long form on the agent's own initiative"))
    w, h = fmt.get("width", spec["size"][0]), fmt.get("height", spec["size"][1])
    if (w > h) != (spec["orientation"] == "landscape"):
        issues.append(Issue("error", None, f"format {w}x{h} doesn't match video_type {vt} "
                                           f"({spec['orientation']}, {spec['size'][0]}x{spec['size'][1]})"))
    return issues


def resolve_durations(doc: dict, tts_durations: dict[str, float] | None = None) -> tuple[float, dict[str, float]]:
    """Compute per-beat duration in seconds and the total runtime.

    tts_durations: {beat_id: measured_seconds} for beats that have already
    been rendered by capy_tts.py. Any beat missing from this map falls
    back to the pre-TTS estimate (word-count / wpm).
    """
    tts_durations = tts_durations or {}
    per_beat: dict[str, float] = {}
    for beat in doc.get("beats", []):
        bid = beat["id"]
        kind = beat["kind"]
        if kind == "clip":
            speed = beat.get("speed", 1.0) or 1.0
            dur = (beat["end"] - beat["start"]) / speed
        elif bid in tts_durations:
            dur = tts_durations[bid]
        else:
            dur = estimate_hold_seconds(beat.get("text"))
        per_beat[bid] = round(dur, 3)
    total = round(sum(per_beat.values()), 3)
    return total, per_beat


def source_time_seconds(doc: dict, per_beat: dict[str, float]) -> float:
    """Total seconds of `clip` + `excerpt` beats -- the source-time
    fairness budget (script-format.md "Clip fairness" / "Excerpt
    fairness": <= 30% of runtime)."""
    total = 0.0
    for beat in doc.get("beats", []):
        if beat.get("kind") in ("clip", "excerpt"):
            total += per_beat.get(beat["id"], 0.0)
    return total


def check_duration_budget(doc: dict, total_seconds: float, *, draft: bool = False) -> list[Issue]:
    fmt = doc.get("format", {})
    vt = doc.get("video_type", "short")
    default_lo, default_hi = VIDEO_TYPES.get(vt, VIDEO_TYPES["short"])["budget"]
    lo, hi = fmt.get("min_seconds", default_lo), fmt.get("max_seconds", default_hi)
    level = "warning" if draft else "error"
    issues = []
    if total_seconds < lo:
        hint = " -- too short for long form; make it a short (video_type: short)" if vt in LONG_FORM_TYPES else ""
        issues.append(Issue(level, None, f"total runtime {total_seconds:.1f}s is under the {lo}s minimum{hint}"))
    if total_seconds > hi:
        hint = ("trim or split into two long-form slugs" if vt in LONG_FORM_TYPES
                else "consider splitting into two slugs (long form only if the user explicitly asks for it)")
        issues.append(Issue(level, None, f"total runtime {total_seconds:.1f}s exceeds the {hi}s maximum -- {hint}"))
    return issues
