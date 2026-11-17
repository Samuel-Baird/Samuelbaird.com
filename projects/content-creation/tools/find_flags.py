#!/usr/bin/env python3
"""Find candidate blooper/repeat-take cuts in a Whisper JSON transcript.

Two tiers, per ../docs/transcription.md:

  CUT   -- confident: repeated-take overlap between adjacent segments,
           false starts (next segment reopens with the same words), or an
           explicit self-correction phrase ("sorry", "let me start again",
           "take two", "scratch that", ...).
  CHECK -- possible: an interior silence gap > 3s inside one take (needs
           --audio for ffmpeg silencedetect), a single word whose duration
           exceeds ~1.2s (the "swallowed retake" signature), or an ordinary
           pause of 1.5-3s worth a pacing look.

Input is the .json Whisper writes with --word_timestamps True (segments with
per-word start/end). Output is flags.json: a list of
{tier, start, end, reason, text} records, ordered by start time, which
build_script_docx.py turns into inline markup.

Usage:
    python find_flags.py TRANSCRIPT.json --out flags.json
    python find_flags.py TRANSCRIPT.json --out flags.json --audio SOURCE.wav
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path

SELF_CORRECTION_PATTERNS = [
    r"\bsorry\b",
    r"\blet me (start|try) (that|this)?\s*again\b",
    r"\btake two\b",
    r"\bscratch that\b",
    r"\blet me redo that\b",
    r"\bone more time\b",
    r"\bwait,? let me\b",
]
SELF_CORRECTION_RE = re.compile("|".join(SELF_CORRECTION_PATTERNS), re.IGNORECASE)

WORD_DURATION_FLAG_SECONDS = 1.2
PAUSE_CHECK_MIN_SECONDS = 1.5
PAUSE_CHECK_MAX_SECONDS = 3.0
INTERIOR_SILENCE_FLAG_SECONDS = 3.0
REPEATED_TAKE_RATIO = 0.6
FALSE_START_TOKEN_MATCH = 3
REPEAT_LOOKAHEAD_SECONDS = 90.0


def normalize_tokens(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9'\s]", " ", text)
    return [t for t in text.split() if t]


def flag(tier: str, start: float, end: float, reason: str, text: str) -> dict:
    return {"tier": tier, "start": round(start, 2), "end": round(end, 2),
            "reason": reason, "text": text.strip()}


def _segment_similarity(tokens_a: list[str], tokens_b: list[str]) -> float:
    if not tokens_a or not tokens_b:
        return 0.0
    return SequenceMatcher(None, tokens_a, tokens_b).ratio()


def find_repeated_takes(segments: list[dict]) -> list[dict]:
    """Find re-read spans, from a single repeated line up to a whole
    re-read paragraph. A retake is rarely the very next segment -- the
    speaker often re-reads several sentences, so this searches a lookahead
    window rather than only comparing segment i to i+1, and once a matching
    pair is found it extends forward as long as the following segments keep
    matching too (so a 6-sentence paragraph re-read is flagged as one CUT
    spanning the whole earlier reading, not caught piecemeal or missed).
    The EARLIER reading is flagged as the one to cut; the later, presumably
    corrected, reading is left as the keeper.
    """
    flags: list[dict] = []
    n = len(segments)
    tokens = [normalize_tokens(s["text"]) for s in segments]
    consumed: set[int] = set()

    for i in range(n):
        if i in consumed or not tokens[i]:
            continue
        for j in range(i + 1, n):
            if segments[j]["start"] - segments[i]["start"] > REPEAT_LOOKAHEAD_SECONDS:
                break
            if j in consumed:
                continue
            ratio = _segment_similarity(tokens[i], tokens[j])
            if ratio >= REPEATED_TAKE_RATIO:
                block_len = 1
                while (
                    i + block_len < j
                    and j + block_len < n
                    and _segment_similarity(tokens[i + block_len], tokens[j + block_len])
                    >= REPEATED_TAKE_RATIO
                ):
                    block_len += 1
                first, last = segments[i], segments[i + block_len - 1]
                span_text = " ".join(
                    segments[i + k]["text"].strip() for k in range(block_len)
                )
                flags.append(flag(
                    "CUT", first["start"], last["end"],
                    f"repeated take: re-read starting at {segments[j]['start']:.1f}s "
                    f"(similarity {ratio:.2f}, {block_len} segment"
                    f"{'s' if block_len > 1 else ''}) -- keep the later reading",
                    span_text,
                ))
                consumed.update(range(i, i + block_len))
                break
            if (
                tokens[i][:FALSE_START_TOKEN_MATCH] == tokens[j][:FALSE_START_TOKEN_MATCH]
                and len(tokens[i]) >= FALSE_START_TOKEN_MATCH
                and j == i + 1
            ):
                flags.append(flag(
                    "CUT", segments[i]["start"], segments[i]["end"],
                    f"false start (next segment reopens with the same "
                    f"{FALSE_START_TOKEN_MATCH} words)", segments[i]["text"],
                ))
                consumed.add(i)
                break
    return flags


def find_self_corrections(segments: list[dict]) -> list[dict]:
    flags = []
    for seg in segments:
        if SELF_CORRECTION_RE.search(seg["text"]):
            flags.append(flag(
                "CUT", seg["start"], seg["end"],
                "explicit self-correction phrase", seg["text"],
            ))
    return flags


def find_swallowed_words(segments: list[dict]) -> list[dict]:
    flags = []
    for seg in segments:
        for w in seg.get("words", []):
            dur = w["end"] - w["start"]
            if dur >= WORD_DURATION_FLAG_SECONDS:
                flags.append(flag(
                    "CHECK", w["start"], w["end"],
                    f"word duration {dur:.2f}s -- possible swallowed retake "
                    f"(word: \"{w['word'].strip()}\")", seg["text"],
                ))
    return flags


def find_pauses(segments: list[dict]) -> list[dict]:
    flags = []
    all_words = [w for seg in segments for w in seg.get("words", [])]
    for i in range(len(all_words) - 1):
        gap = all_words[i + 1]["start"] - all_words[i]["end"]
        if gap >= INTERIOR_SILENCE_FLAG_SECONDS:
            flags.append(flag(
                "CHECK", all_words[i]["end"], all_words[i + 1]["start"],
                f"interior gap {gap:.2f}s inside continuous speech", "",
            ))
        elif PAUSE_CHECK_MIN_SECONDS <= gap < INTERIOR_SILENCE_FLAG_SECONDS:
            flags.append(flag(
                "CHECK", all_words[i]["end"], all_words[i + 1]["start"],
                f"pause {gap:.2f}s -- pacing check", "",
            ))
    return flags


def run_silencedetect(audio: Path, noise_db: str = "-30dB", min_dur: float = 0.6) -> list[tuple[float, float]]:
    """Return (start, end) silence ranges via ffmpeg silencedetect."""
    cmd = [
        "ffmpeg", "-i", str(audio),
        "-af", f"silencedetect=noise={noise_db}:d={min_dur}",
        "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    ranges: list[tuple[float, float]] = []
    start = None
    for line in result.stderr.splitlines():
        m_start = re.search(r"silence_start:\s*([\d.]+)", line)
        m_end = re.search(r"silence_end:\s*([\d.]+)", line)
        if m_start:
            start = float(m_start.group(1))
        elif m_end and start is not None:
            ranges.append((start, float(m_end.group(1))))
            start = None
    return ranges


def find_interior_silence(segments: list[dict], silence_ranges: list[tuple[float, float]]) -> list[dict]:
    flags = []
    for seg in segments:
        for s_start, s_end in silence_ranges:
            dur = s_end - s_start
            interior = (s_start - seg["start"] > 0.3) and (seg["end"] - s_end > 0.3)
            if interior and dur > INTERIOR_SILENCE_FLAG_SECONDS:
                flags.append(flag(
                    "CHECK", s_start, s_end,
                    f"interior silence {dur:.2f}s inside a planned continuous "
                    f"take -- check for an embedded flub+pause+redo", seg["text"],
                ))
    return flags


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript", type=Path, help="Whisper .json output (word_timestamps)")
    parser.add_argument("--out", type=Path, required=True, help="Where to write flags.json")
    parser.add_argument("--audio", type=Path, default=None,
                         help="Source audio for ffmpeg silencedetect (optional)")
    args = parser.parse_args()

    data = json.loads(args.transcript.read_text(encoding="utf-8"))
    segments = data.get("segments", [])
    if not segments:
        print("error: no segments in transcript", file=sys.stderr)
        return 1

    all_flags: list[dict] = []
    all_flags += find_repeated_takes(segments)
    all_flags += find_self_corrections(segments)
    all_flags += find_swallowed_words(segments)
    all_flags += find_pauses(segments)

    if args.audio:
        if args.audio.exists():
            silence_ranges = run_silencedetect(args.audio)
            all_flags += find_interior_silence(segments, silence_ranges)
        else:
            print(f"warning: --audio path not found, skipping silencedetect: {args.audio}",
                  file=sys.stderr)

    all_flags.sort(key=lambda f: f["start"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(all_flags, indent=2), encoding="utf-8")

    cut_count = sum(1 for f in all_flags if f["tier"] == "CUT")
    check_count = sum(1 for f in all_flags if f["tier"] == "CHECK")
    print(f"Wrote {len(all_flags)} flags ({cut_count} CUT, {check_count} CHECK) to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
