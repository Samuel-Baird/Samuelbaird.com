"""beats.yaml schema, loading, validation, and duration resolution for the
Saint Capybara video type.

See docs/saint-capybara/script-format.md for the full field reference (this
module's BEAT_KINDS / REQUIRED_FIELDS mirror that doc exactly -- if you
change one, change the other) and docs/saint-capybara/brand.md sec 5a for
why the outro sequence below is fixed and not something each project's
beats.yaml hand-authors.

    from capy.beats import load_beats, validate, resolve_durations

    doc = load_beats(Path("script/beats.yaml"))   # auto-appends the outro
    issues = validate(doc)                         # list[Issue]
    total, per_beat = resolve_durations(doc, tts_durations={"n01": 4.2, ...})
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

BEAT_KINDS = {"clip", "narration", "card", "evidence", "chart", "outro"}

# Words-per-minute used to *estimate* a hold/TTS duration before real TTS
# has run (Step 3 lock: 0.9-0.95 speed, ~140-150 wpm target -- see brand.md
# sec 6). Only used pre-TTS (storyboard/lint preview); once capy_tts.py has
# rendered a beat, its measured wav duration always wins in
# resolve_durations() via the tts_durations map.
ESTIMATE_WORDS_PER_SECOND = 145 / 60.0
HOLD_BASE_SECONDS = 3.0
HOLD_PER_WORD_SECONDS = 0.15
OUTRO_MIN_SECONDS = 1.2

# ---------------------------------------------------------------------------
# Mandatory sign-of-the-cross outro (brand.md sec 5a). This is a fixed,
# non-optional structural rule of the Saint Capybara type -- every project's
# beats.yaml gets this appended automatically by load_beats() if it isn't
# already present, and validate() rejects any beats.yaml whose trailing
# outro sequence doesn't match this exactly in pose order/count (wording
# may be adjusted slightly for TTS phrasing per the brief, but the four
# poses, their order, and the overall line's meaning must not change).
# ---------------------------------------------------------------------------
OUTRO_POSES = ["sign-father", "sign-son", "sign-holy", "sign-spirit-amen"]
OUTRO_BEATS: list[dict] = [
    {"id": "outro-01", "kind": "outro", "pose": "sign-father", "text": "In the name of the Father,"},
    {"id": "outro-02", "kind": "outro", "pose": "sign-son", "text": "and of the Son,"},
    {"id": "outro-03", "kind": "outro", "pose": "sign-holy", "text": "and of the Holy Ghost,"},
    {"id": "outro-04", "kind": "outro", "pose": "sign-spirit-amen", "text": "Amen."},
]


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


def has_outro_sequence(beats: list[dict]) -> bool:
    """True if `beats` already ends with the exact 4-pose outro sequence
    (by pose + kind, not necessarily verbatim wording)."""
    if len(beats) < 4:
        return False
    tail = beats[-4:]
    if any(b.get("kind") != "outro" for b in tail):
        return False
    return [b.get("pose") for b in tail] == OUTRO_POSES


def ensure_mandatory_outro(doc: dict) -> dict:
    """Return a copy of `doc` with the fixed sign-of-the-cross outro
    appended to `beats` if it isn't already present. Idempotent."""
    doc = copy.deepcopy(doc)
    beats = doc.setdefault("beats", [])
    if not has_outro_sequence(beats):
        beats.extend(copy.deepcopy(OUTRO_BEATS))
    return doc


def load_beats(path: Path | str) -> dict:
    """Load beats.yaml, applying defaults and auto-appending the mandatory
    outro sequence if the file doesn't already end with it. Does NOT
    write the file back -- callers that want the outro persisted to disk
    (e.g. `new_project.ps1` scaffolding, or an explicit `--write-outro`
    flag on a tool) should re-dump the returned doc themselves."""
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw.setdefault("version", 1)
    raw.setdefault("sensitive", False)
    raw.setdefault("music", None)
    raw.setdefault("tags", [])
    raw.setdefault("format", {})
    fmt = raw["format"]
    fmt.setdefault("width", 1080)
    fmt.setdefault("height", 1920)
    fmt.setdefault("fps", 30)
    fmt.setdefault("min_seconds", 60)
    fmt.setdefault("max_seconds", 180)
    raw.setdefault("voice", {"name": "am_michael", "speed": 0.95})
    return ensure_mandatory_outro(raw)


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

        if kind == "evidence" and not beat.get("evidence", {}).get("image"):
            issues.append(Issue("error", bid, "evidence beat missing evidence.image"))

        if kind == "card" and not beat.get("card", {}).get("quote"):
            issues.append(Issue("error", bid, "card beat missing card.quote"))

        pose = resolve_pose(beat, sensitive=bool(doc.get("sensitive")))
        if pose and POSES and pose not in POSES and pose not in OUTRO_POSES:
            issues.append(Issue("error", bid, f"pose '{pose}' is not in the sprite roster"))
        if doc.get("sensitive") and pose in SENSITIVE_FORBIDDEN:
            issues.append(Issue("error", bid, f"pose '{pose}' is forbidden on a sensitive-flagged video/beat"))

    if not has_outro_sequence(beats):
        issues.append(Issue("error", None, "beats.yaml does not end with the mandatory sign-of-the-cross outro sequence (sign-father -> sign-son -> sign-holy -> sign-spirit-amen); run through capy.beats.load_beats/ensure_mandatory_outro to auto-append it"))
    else:
        tail = beats[-4:]
        expected_texts = [b["text"] for b in OUTRO_BEATS]
        for got, exp in zip(tail, expected_texts):
            if not got.get("text"):
                issues.append(Issue("warning", got.get("id"), "outro beat has no narration text"))

    hook = doc.get("hook")
    if not hook:
        issues.append(Issue("warning", None, "no 'hook' text set for the first 3 seconds"))

    return issues


def resolve_durations(doc: dict, tts_durations: dict[str, float] | None = None) -> tuple[float, dict[str, float]]:
    """Compute per-beat duration in seconds and the total runtime.

    tts_durations: {beat_id: measured_seconds} for beats that have already
    been rendered by capy_tts.py. Any beat missing from this map falls
    back to the pre-TTS estimate (word-count / wpm, or the outro floor).
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
            if kind == "outro":
                dur = max(dur, OUTRO_MIN_SECONDS)
        else:
            dur = estimate_hold_seconds(beat.get("text"))
            if kind == "outro":
                dur = max(dur, OUTRO_MIN_SECONDS)
        per_beat[bid] = round(dur, 3)
    total = round(sum(per_beat.values()), 3)
    return total, per_beat


def check_duration_budget(doc: dict, total_seconds: float, *, draft: bool = False) -> list[Issue]:
    fmt = doc.get("format", {})
    lo, hi = fmt.get("min_seconds", 60), fmt.get("max_seconds", 180)
    level = "warning" if draft else "error"
    issues = []
    if total_seconds < lo:
        issues.append(Issue(level, None, f"total runtime {total_seconds:.1f}s is under the {lo}s minimum"))
    if total_seconds > hi:
        issues.append(Issue(level, None, f"total runtime {total_seconds:.1f}s exceeds the {hi}s maximum -- consider splitting into two slugs"))
    return issues
