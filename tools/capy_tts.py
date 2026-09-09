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

`--project` mode renders real per-beat narration and is gated by Gate A
(docs/saint-capybara/script-format.md) at the human-process level, not by
this tool itself -- the caller must have the user's explicit script
approval in hand before invoking it.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from capy.beats import load_beats

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


def _synthesize(text: str, voice: str, speed: float, entries: list[dict], *, print_phonemes: bool = False):
    """Run one text through Kokoro. Returns (audio: np.ndarray, timings: list[dict])."""
    try:
        from kokoro import KPipeline
    except ImportError as e:
        print(f"error: kokoro not importable ({e}). See tools/requirements.txt.", file=sys.stderr)
        raise

    import numpy as np

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

    return np.concatenate(chunks), timings


def render_sample(text: str, out_path: Path, voice: str, speed: float, *, print_phonemes: bool = False) -> float:
    import soundfile as sf

    entries = load_pronunciation_dict(None)
    full, timings = _synthesize(text, voice, speed, entries, print_phonemes=print_phonemes)
    sf.write(str(out_path), full, SAMPLE_RATE)
    duration = len(full) / SAMPLE_RATE

    timing_path = out_path.with_suffix(".timing.json")
    timing_path.write_text(json.dumps(timings, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} ({duration:.2f}s, {len(timings)} word timings) and {timing_path}")
    return duration


def normalize_wav(src: Path, dst: Path, *, target_lufs: float = TARGET_LUFS, head_pad: float = HEAD_PAD_SECONDS) -> None:
    """Gain-only loudness normalization to `target_lufs`, resampled to
    48kHz stereo with `head_pad` seconds of silence padded on both ends.

    Two-pass ffmpeg loudnorm: a single-pass filter is only a rough
    estimate (confirmed off by ~5 LU on a 2s test clip here), especially
    on short narration beats. Pass 1 measures the clip's actual
    integrated loudness/true-peak/range; pass 2 feeds those measured
    values back in with `linear=true`, which applies a single fixed gain
    (no dynamic compression -- still "gain-only" per the plan) instead of
    the coarse single-pass estimate. Word timings (measured against the
    un-padded, pre-normalization .wav) still line up afterward since
    gain-only normalization and the head-pad delay don't change timing.
    """
    measure_cmd = [
        "ffmpeg", "-i", str(src),
        "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11:print_format=json",
        "-f", "null", "-",
    ]
    result = subprocess.run(measure_cmd, capture_output=True, text=True, check=True)
    stderr = result.stderr
    json_start = stderr.rfind("{")
    json_end = stderr.rfind("}") + 1
    measured = json.loads(stderr[json_start:json_end])

    filt = (
        f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11:"
        f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
        f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
        f"offset={measured['target_offset']}:linear=true:print_format=none,"
        f"adelay={int(head_pad * 1000)}|{int(head_pad * 1000)},"
        f"apad=pad_dur={head_pad}"
    )
    apply_cmd = [
        "ffmpeg", "-y", "-i", str(src),
        "-af", filt,
        "-ar", "48000", "-ac", "2",
        str(dst),
    ]
    subprocess.run(apply_cmd, capture_output=True, check=True)


BEAT_KINDS_WITH_NARRATION = {"narration", "card", "evidence", "chart", "outro"}


def render_project(
    project: Path,
    *,
    voice: str,
    speed: float,
    only: set[str] | None = None,
    force: bool = False,
    print_phonemes: bool = False,
) -> int:
    """Render real narration for every narration-family beat with `text`
    in `project`'s script/beats.yaml. Writes audio/<id>.wav (24kHz raw),
    audio/<id>.timing.json (per-word {w,s,e}, relative to the un-padded
    wav), and audio/<id>.norm.wav (48kHz stereo, -16 LUFS, head/tail
    padded) for each. Returns the count of beats rendered."""
    import soundfile as sf

    beats_path = project / "script" / "beats.yaml"
    doc = load_beats(beats_path)
    entries = load_pronunciation_dict(project)
    audio_dir = project / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    rendered = 0
    for beat in doc["beats"]:
        bid, kind = beat["id"], beat["kind"]
        if kind not in BEAT_KINDS_WITH_NARRATION:
            continue
        text = beat.get("text")
        if not text:
            continue
        if only and bid not in only:
            continue

        wav_path = audio_dir / f"{bid}.wav"
        norm_path = audio_dir / f"{bid}.norm.wav"
        timing_path = audio_dir / f"{bid}.timing.json"
        if wav_path.exists() and norm_path.exists() and timing_path.exists() and not force:
            print(f"skip {bid} (already rendered; use --force to re-render)")
            continue

        full, timings = _synthesize(text, voice, speed, entries, print_phonemes=print_phonemes)
        sf.write(str(wav_path), full, SAMPLE_RATE)
        timing_path.write_text(json.dumps(timings, indent=2), encoding="utf-8")
        normalize_wav(wav_path, norm_path)
        duration = len(full) / SAMPLE_RATE
        print(f"{bid}: {duration:.2f}s raw, {len(timings)} word timings -> {norm_path.name}")
        rendered += 1

    return rendered


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
        only = set(args.only.split(",")) if args.only else None
        if args.timestamps == "whisper":
            print("error: --timestamps whisper (post-hoc realignment fallback) is not implemented yet; only 'kokoro' (the default) is supported.", file=sys.stderr)
            return 4
        n = render_project(
            args.project, voice=args.voice, speed=args.speed,
            only=only, force=args.force, print_phonemes=args.print_phonemes,
        )
        print(f"\n{n} beat(s) rendered.")
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
