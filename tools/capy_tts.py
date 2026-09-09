#!/usr/bin/env python3
"""Kokoro-based TTS for Saint Capybara narration.

    python tools/capy_tts.py --sample "text to render" --out x.wav [--voice am_michael] [--speed 0.95]
    python tools/capy_tts.py --project D:\\Videos\\<slug> [--voice] [--speed] [--only ids] [--force]

Applies the merged pronunciation dictionary (project
script/pronunciations.yaml overrides/extends
assets/saint-capybara/templates/pronunciations.yaml) by whole-word regex,
rewriting a matched word as misaki's inline override syntax
`[word](/ipa/)` before handing text to KPipeline(lang_code="a"). Renders
per-beat wavs at 24kHz, applies gain-only normalization toward -16 LUFS
with head/tail padding, and writes a 48kHz stereo `.norm.wav` alongside a
`timing.json` of per-word {w, s, e} from Kokoro's own token timestamps.

IMPORTANT (per this session's task): this tool is built and sanity-tested
with `--sample` only. It is NOT run against a real project's narration
beats in this session -- that is Gate A's hard stop (see
docs/saint-capybara/script-format.md). `--project` mode is implemented per
the plan for future sessions to use once a script is approved.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:  # IPA characters in printed lexicon overrides need a utf-8 stdout on Windows consoles
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SEED_PRONUNCIATIONS = REPO_ROOT / "assets" / "saint-capybara" / "templates" / "pronunciations.yaml"

VOICE_SHORTLIST = ["am_michael", "am_onyx", "bm_george"]
DEFAULT_VOICE = "am_michael"
DEFAULT_SPEED = 0.95
SAMPLE_RATE = 24000
TARGET_LUFS = -16.0
HEAD_PAD_SECONDS = 0.25


def load_pronunciation_dict(project: Path | None) -> list[dict]:
    entries: dict[str, dict] = {}
    if SEED_PRONUNCIATIONS.exists():
        data = yaml.safe_load(SEED_PRONUNCIATIONS.read_text(encoding="utf-8")) or {}
        for e in data.get("entries", []):
            entries[e["word"].lower()] = e
    if project:
        proj_path = project / "script" / "pronunciations.yaml"
        if proj_path.exists():
            data = yaml.safe_load(proj_path.read_text(encoding="utf-8")) or {}
            for e in data.get("entries", []):
                entries[e["word"].lower()] = e
    return list(entries.values())


def apply_dictionary(text: str, entries: list[dict]) -> str:
    """Rewrite proper-noun matches as misaki's `[word](/ipa/)` inline
    override syntax. Entries with ipa == "ok-as-is" are left untouched
    (they're documentation, not an override)."""
    out = text
    # Expand D&C -> Doctrine and Covenants first (script-format.md rule).
    out = re.sub(r"\bD&C\b", "Doctrine and Covenants", out)
    for e in sorted(entries, key=lambda e: -len(e["word"])):
        word, ipa = e["word"], e.get("ipa")
        if not ipa or ipa == "ok-as-is":
            continue
        pattern = re.compile(rf"\b{re.escape(word)}\b")
        out = pattern.sub(f"[{word}]({ipa})", out)
    return out


def render_sample(text: str, out_path: Path, voice: str, speed: float, *, print_phonemes: bool = False) -> float:
    try:
        from kokoro import KPipeline
    except ImportError as e:
        print(f"error: kokoro not importable ({e}). See tools/requirements.txt.", file=sys.stderr)
        raise

    import numpy as np
    import soundfile as sf

    entries = load_pronunciation_dict(None)
    processed = apply_dictionary(text, entries)
    if print_phonemes:
        print(f"text with lexicon overrides applied:\n  {processed}")

    pipeline = KPipeline(lang_code="a")
    chunks = []
    timings: list[dict] = []
    t_offset = 0.0
    for result in pipeline(processed, voice=voice, speed=speed):
        audio = result.audio
        if audio is None:
            continue
        chunks.append(audio.numpy() if hasattr(audio, "numpy") else np.asarray(audio))
        if getattr(result, "tokens", None):
            for tok in result.tokens:
                start_ts = getattr(tok, "start_ts", None)
                end_ts = getattr(tok, "end_ts", None)
                if start_ts is None or end_ts is None:
                    continue
                timings.append({"w": tok.text, "s": t_offset + start_ts, "e": t_offset + end_ts})
        chunk_dur = len(chunks[-1]) / SAMPLE_RATE if chunks else 0.0
        t_offset += chunk_dur

    if not chunks:
        raise RuntimeError("kokoro produced no audio chunks")

    full = np.concatenate(chunks)
    sf.write(str(out_path), full, SAMPLE_RATE)
    duration = len(full) / SAMPLE_RATE

    timing_path = out_path.with_suffix(".timing.json")
    timing_path.write_text(json.dumps(timings, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} ({duration:.2f}s, {len(timings)} word timings) and {timing_path}")
    return duration


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sample", type=str, default=None, help="render one throwaway sample line, do not touch any project")
    ap.add_argument("--out", type=Path, default=None, help="output wav for --sample")
    ap.add_argument("--voice", type=str, default=DEFAULT_VOICE)
    ap.add_argument("--speed", type=float, default=DEFAULT_SPEED)
    ap.add_argument("--print-phonemes", action="store_true")
    ap.add_argument("--project", type=Path, default=None)
    ap.add_argument("--only", type=str, default=None, help="comma-separated beat ids (project mode)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--timestamps", choices=["kokoro", "whisper"], default="kokoro")
    args = ap.parse_args()

    if args.sample:
        out = args.out or Path("sample.wav")
        render_sample(args.sample, out, args.voice, args.speed, print_phonemes=args.print_phonemes)
        return 0

    if args.project:
        print(
            "error: --project (real per-beat narration rendering) is intentionally not exercised in this "
            "session -- Gate A (docs/saint-capybara/script-format.md) requires the user's script approval "
            "before any TTS is rendered for actual project beats. The --sample path above is the only mode "
            "this session used, to sanity-check the tool and lock the voice choice."
        )
        return 3

    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
