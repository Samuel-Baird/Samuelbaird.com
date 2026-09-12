#!/usr/bin/env python3
"""TTS for Saint Capybara narration -- Chatterbox (locked default,
2026-09-11) or Kokoro, chosen per-beat by each resolved voice spec's
`engine` field. Both engines are fully supported side by side; see
`docs/saint-capybara/brand.md` sec 6 for the locked voices and why
Chatterbox replaced Kokoro as the default.

    python tools/capy_tts.py --sample "text to render" --out x.wav [--voice am_michael] [--speed 0.95]
    python tools/capy_tts.py --sample "text" --out x.wav --engine chatterbox --ref assets/saint-capybara/voices/host_andrew_kennedy.wav
    python tools/capy_tts.py --project D:\\Videos\\<slug> [--voice] [--speed] [--only ids] [--force]

Kokoro path (`engine: kokoro`): applies the merged pronunciation
dictionary (project script/pronunciations.yaml overrides/extends
assets/saint-capybara/templates/pronunciations.yaml) by whole-word
regex, rewriting a matched word as misaki's inline override syntax
`[word](/ipa/)` before handing text to KPipeline(lang_code="a").
Produces its own per-word {w, s, e} timing from Kokoro's own token
timestamps.

Chatterbox path (`engine: chatterbox`): rendered via a batch subprocess
call to the isolated tools/.venv-chatterbox (capy.tts_chatterbox ->
capy/_chatterbox_worker.py -- see requirements-chatterbox.txt for why
it's a separate venv). Chatterbox's tokenizer has no phoneme-override
mechanism, so the pronunciation dictionary's IPA rewriting is skipped
for these beats (D&C -> "Doctrine and Covenants" still applies, a plain
literal substitution) -- an accepted, known regression, see
pronunciations.md. Chatterbox exposes no timing of its own, so
capy.align.align_timing() reconciles a Whisper transcription of the
rendered wav against the known script text to produce {w, s, e} timing.

Both paths render at 24kHz, apply gain-only normalization toward -16
LUFS with head/tail padding, and write a 48kHz stereo `.norm.wav`
alongside the `timing.json`.

Per-beat voice: each beat's effective voice spec is resolved via
capy.beats.resolve_voice(doc, beat) -- an inline `voice: {engine, ...}`
on the beat, else a role name via `voices:` (quote_male/quote_female are
POOLS, resolved per-speaker via the beat's `speaker:` field -- see
capy.voice_pool and script-format.md), else the kind default (`excerpt`
-> `voices.quote_default`, everything else -> the top-level `voice:`).
`--voice`/`--speed` on this CLI now only override the project's *host*
voice (doc["voice"]), FORCED to engine=kokoro (see main()'s --voice
help) -- they do not force every beat onto one voice/engine, and don't
touch Chatterbox beats at all.

`audio/<id>.meta.json` records the full resolved voice spec actually
used for each beat, so ANY change -- voice, speed, engine, ref clip --
invalidates the "already rendered" skip even though the
wav/timing/norm files still exist.

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

from capy.beats import load_beats, resolve_voice, NARRATION_FAMILY_KINDS
from capy.voice_pool import slugify

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


def apply_dictionary(text: str, entries: list[dict], *, ipa: bool = True) -> str:
    """Rewrite proper-noun matches as misaki's `[word](/ipa/)` inline
    override syntax. Entries with ipa == "ok-as-is" are left untouched
    (they're documentation, not an override).

    `ipa=False` (Chatterbox beats): still expands D&C -> "Doctrine and
    Covenants" (a plain literal substitution, engine-agnostic) but skips
    the `[word](/ipa/)` wrapping entirely -- Chatterbox's tokenizer is a
    plain grapheme BPE tokenizer with no phoneme-override mechanism of
    any kind (confirmed by reading tools/.venv-chatterbox's installed
    package source, 2026-09-11); feeding it misaki's bracket syntax would
    just be spoken as literal punctuation. This means the pronunciation
    dictionary's actual fixes (mandatory per brand.md sec 6) do NOT
    apply to Chatterbox-voiced beats -- an accepted, known regression
    (user-approved 2026-09-11): spot-check proper-noun pronunciation by
    ear per project instead."""
    out = text
    # Expand D&C -> Doctrine and Covenants first (script-format.md rule).
    out = re.sub(r"\bD&C\b", "Doctrine and Covenants", out)
    if not ipa:
        return out
    for e in sorted(entries, key=lambda e: -len(e["word"])):
        word, ipa_str = e["word"], e.get("ipa")
        if not ipa_str or ipa_str == "ok-as-is":
            continue
        pattern = re.compile(rf"\b{re.escape(word)}\b")
        out = pattern.sub(f"[{word}]({ipa_str})", out)
    return out


def speech_text(beat: dict) -> str:
    """The text actually handed to Kokoro for `beat`. For excerpt beats,
    literal '[...]' ellipsis markers (an on-screen-only omission marker)
    become a sentence pause instead of being spoken as the words "bracket
    dot dot dot bracket" -- delegates to capy.excerpts.speech_text, which
    turns them into a real sentence stop rather than a literal "...".
    Falls back to a plain "..." substitution if capy.excerpts isn't
    importable."""
    if beat.get("kind") == "excerpt":
        try:
            from capy.excerpts import speech_text as _excerpt_speech_text
            return _excerpt_speech_text(beat)
        except ImportError:
            pass
    text = beat.get("text", "")
    if beat.get("kind") == "excerpt":
        text = text.replace("[...]", "...").strip()
        if text.startswith(("\u201c", '"')) and text.endswith(("\u201d", '"')):
            text = text[1:-1]
    return text


def _synthesize_kokoro(text: str, voice: str, speed: float, entries: list[dict], *, print_phonemes: bool = False):
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
    """Kokoro-only quick-test path (unchanged) -- see render_sample_chatterbox
    for the Chatterbox equivalent (`--engine chatterbox`)."""
    import soundfile as sf

    entries = load_pronunciation_dict(None)
    full, timings = _synthesize_kokoro(text, voice, speed, entries, print_phonemes=print_phonemes)
    sf.write(str(out_path), full, SAMPLE_RATE)
    duration = len(full) / SAMPLE_RATE

    timing_path = out_path.with_suffix(".timing.json")
    timing_path.write_text(json.dumps(timings, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} ({duration:.2f}s, {len(timings)} word timings) and {timing_path}")
    return duration


def render_sample_chatterbox(text: str, out_path: Path, ref: Path, *, exaggeration: float = 0.5, cfg_weight: float = 0.5, speed: float = 1.0) -> float:
    """Chatterbox quick-test path: one job through the isolated venv's
    worker subprocess, an ffmpeg atempo/rubberband speed change if
    `speed != 1.0` (BEFORE alignment, same ordering as render_project --
    see apply_speed_change), then whisper-based timing for the
    .timing.json sidecar (same reconciliation logic --project mode
    uses)."""
    from capy.tts_chatterbox import render_batch
    from capy.align import align_timing

    entries = load_pronunciation_dict(None)
    processed = apply_dictionary(text, entries, ipa=False)

    results = render_batch([{"id": "sample", "text": processed, "ref": ref, "out_path": out_path}])
    result = results.get("sample")
    if not result or not result.get("ok"):
        error = result.get("error") if result else "no result returned"
        raise RuntimeError(f"chatterbox render failed: {error}")

    duration = apply_speed_change(out_path, speed)
    timings = align_timing(out_path, processed)
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


# Default pitch-preserving time-stretch method for the Chatterbox path's
# speed:  != 1.0 (Chatterbox's generate() has no native speed param --
# confirmed by reading the installed package source -- so `speed` is
# applied as ffmpeg post-processing instead, unlike Kokoro where it's a
# native KPipeline argument). "atempo" is ffmpeg's built-in filter,
# always available, safe default. "rubberband" (ffmpeg's
# `-af rubberband=tempo=...`) sounded higher-quality in an informal
# comparison at 1.25x but requires an ffmpeg build with
# --enable-librubberband -- not guaranteed on every machine this
# pipeline runs on, so it's not the default. Swap by changing this one
# constant; not worth a full plugin system for two filter names.
CHATTERBOX_SPEED_METHOD = "atempo"


def _wav_duration_seconds(path: Path) -> float:
    import soundfile as sf
    info = sf.info(str(path))
    return info.frames / info.samplerate


def apply_speed_change(wav_path: Path, speed: float, *, method: str = CHATTERBOX_SPEED_METHOD) -> float:
    """Pitch-preserving time-stretch `wav_path` to `speed`x IN PLACE
    (overwrites it) and returns the new duration in seconds. speed==1.0
    is a no-op (just measures and returns the existing duration).
    `atempo`/`rubberband` both take tempo directly for any ratio in
    Chatterbox's practical speed range (~0.5-2.0) without needing to
    chain filter instances (atempo's own single-instance range, 0.5-2.0,
    already covers it)."""
    if speed == 1.0:
        return _wav_duration_seconds(wav_path)
    filt = f"rubberband=tempo={speed}" if method == "rubberband" else f"atempo={speed}"
    tmp_path = wav_path.with_suffix(".speed_tmp.wav")
    cmd = ["ffmpeg", "-y", "-i", str(wav_path), "-af", filt, str(tmp_path)]
    subprocess.run(cmd, capture_output=True, check=True)
    tmp_path.replace(wav_path)
    return _wav_duration_seconds(wav_path)


BEAT_KINDS_WITH_NARRATION = NARRATION_FAMILY_KINDS


def _voice_label(v: dict) -> str:
    """Human-readable id for a resolved voice spec, for skip/progress
    lines -- Kokoro voices are named ('am_michael'), Chatterbox voices
    are a reference-clip filename."""
    engine = v.get("engine", "kokoro")
    if engine == "chatterbox":
        return f"{Path(v['ref']).name}@{v.get('speed', 1.0)} (chatterbox)"
    return f"{v.get('name')}@{v.get('speed', 1.0)} (kokoro)"


def render_project(
    project: Path,
    *,
    voice: str | None,
    speed: float | None,
    only: set[str] | None = None,
    force: bool = False,
    print_phonemes: bool = False,
    timestamps: str = "kokoro",
) -> int:
    """Render real narration for every narration-family beat with `text`
    in `project`'s script/beats.yaml, using each beat's resolved voice
    (capy.beats.resolve_voice) -- Kokoro or Chatterbox, per-beat, decided
    by each voice spec's `engine` field. `voice`/`speed`, if given,
    override only the project's host voice (doc["voice"]) for this run,
    forced onto Kokoro (see main()'s --voice/--speed help) -- they do not
    force every beat onto one voice/engine.

    Chatterbox-engine beats are batched into ONE subprocess call to
    tools/.venv-chatterbox (capy.tts_chatterbox.render_batch) before the
    main per-beat loop, so the model loads once for the whole project
    rather than once per beat.

    Writes audio/<id>.wav (24kHz raw), audio/<id>.timing.json (per-word
    {w,s,e}, relative to the un-padded wav -- Kokoro's own token
    timestamps by default, or capy.align's whisper-based reconciliation
    for Chatterbox beats (mandatory -- Chatterbox exposes no timing of
    its own) or when `timestamps="whisper"` forces it for Kokoro beats
    too), audio/<id>.norm.wav (48kHz stereo, -16 LUFS, head/tail padded),
    and audio/<id>.meta.json (the full resolved voice spec, so ANY
    change -- voice, speed, engine, ref clip -- invalidates the
    "already rendered" skip even though the wav/timing files still
    exist). Returns the count of beats rendered."""
    import soundfile as sf

    from capy.source import load_source_info

    beats_path = project / "script" / "beats.yaml"
    doc = load_beats(beats_path)
    if voice or speed:
        host = doc["voice"]
        doc["voice"] = {
            "engine": "kokoro",
            "name": voice or host.get("name", "am_michael"),
            "speed": speed if speed is not None else host.get("speed", 1.0),
        }
    entries = load_pronunciation_dict(project)
    audio_dir = project / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    source_info = load_source_info(project)
    default_speaker = slugify(source_info.byline) if source_info.byline else None

    # Pass 1: figure out which beats actually need (re-)rendering, and
    # split them by engine -- chatterbox beats get batched below.
    to_render: list[dict] = []
    for beat in doc["beats"]:
        bid, kind = beat["id"], beat["kind"]
        if kind not in BEAT_KINDS_WITH_NARRATION:
            continue
        text = speech_text(beat)
        if not text:
            continue
        if only and bid not in only:
            continue

        v = resolve_voice(doc, beat, default_speaker=default_speaker)
        wav_path = audio_dir / f"{bid}.wav"
        norm_path = audio_dir / f"{bid}.norm.wav"
        timing_path = audio_dir / f"{bid}.timing.json"
        meta_path = audio_dir / f"{bid}.meta.json"
        already_rendered = wav_path.exists() and norm_path.exists() and timing_path.exists()
        if meta_path.exists():
            prior_meta = json.loads(meta_path.read_text(encoding="utf-8"))
            voice_unchanged = prior_meta == v
        else:
            # Legacy beat rendered before audio/<id>.meta.json existed --
            # don't force a re-render just because the file is missing;
            # backfill it so future voice changes are detected correctly.
            voice_unchanged = already_rendered
            if already_rendered:
                meta_path.write_text(json.dumps(v, indent=2), encoding="utf-8")
        if already_rendered and voice_unchanged and not force:
            print(f"skip {bid} (already rendered with {_voice_label(v)}; use --force to re-render)")
            continue

        to_render.append({"beat": beat, "bid": bid, "text": text, "v": v,
                           "wav_path": wav_path, "norm_path": norm_path,
                           "timing_path": timing_path, "meta_path": meta_path})

    # Pass 2: batch-render every Chatterbox job in one worker subprocess
    # call (model loads once for all of them).
    chatterbox_items = [item for item in to_render if item["v"].get("engine") == "chatterbox"]
    if chatterbox_items:
        from capy.tts_chatterbox import render_batch, ChatterboxUnavailable

        jobs = [
            {
                "id": item["bid"],
                "text": apply_dictionary(item["text"], entries, ipa=False),
                "ref": REPO_ROOT / item["v"]["ref"],
                "out_path": item["wav_path"],
                "exaggeration": item["v"].get("exaggeration", 0.5),
                "cfg_weight": item["v"].get("cfg_weight", 0.5),
            }
            for item in chatterbox_items
        ]
        print(f"Rendering {len(jobs)} beat(s) with Chatterbox (batched, one model load)...")
        try:
            results = render_batch(jobs)
        except ChatterboxUnavailable as e:
            print(f"error: {e}", file=sys.stderr)
            results = {}
        for item in chatterbox_items:
            item["chatterbox_result"] = results.get(item["bid"], {"ok": False, "error": "not returned by worker batch"})

    # Pass 3: finalize every beat that has audio now (timing, loudnorm, meta).
    rendered = 0
    for item in to_render:
        bid, text, v = item["bid"], item["text"], item["v"]
        wav_path, norm_path, timing_path, meta_path = item["wav_path"], item["norm_path"], item["timing_path"], item["meta_path"]
        engine = v.get("engine", "kokoro")

        if engine == "chatterbox":
            result = item.get("chatterbox_result", {})
            if not result.get("ok"):
                print(f"{bid}: FAILED ({result.get('error', 'unknown error')}) -- skipped", file=sys.stderr)
                continue
            # Speed change (ffmpeg atempo/rubberband post-process, since
            # Chatterbox has no native speed param) MUST happen before
            # alignment -- timing.json has to describe the final-tempo
            # audio, not the model's natural-cadence raw render, and the
            # reported duration must be the post-stretch one too.
            speed = v.get("speed", 1.0)
            duration = apply_speed_change(wav_path, speed)
            processed = apply_dictionary(text, entries, ipa=False)
            from capy.align import align_timing
            timings = align_timing(wav_path, processed)
        elif engine == "kokoro":
            full, kokoro_timings = _synthesize_kokoro(text, v["name"], v.get("speed", 1.0), entries, print_phonemes=print_phonemes)
            sf.write(str(wav_path), full, SAMPLE_RATE)
            duration = len(full) / SAMPLE_RATE
            if timestamps == "whisper":
                from capy.align import align_timing
                timings = align_timing(wav_path, apply_dictionary(text, entries, ipa=False))
            else:
                timings = kokoro_timings
        else:
            print(f"{bid}: unknown engine {engine!r} -- skipped", file=sys.stderr)
            continue

        timing_path.write_text(json.dumps(timings, indent=2), encoding="utf-8")
        normalize_wav(wav_path, norm_path)
        meta_path.write_text(json.dumps(v, indent=2), encoding="utf-8")
        print(f"{bid}: {duration:.2f}s raw ({_voice_label(v)}), {len(timings)} word timings -> {norm_path.name}")
        rendered += 1

    return rendered


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sample", type=str, default=None, help="render one throwaway sample line, do not touch any project")
    ap.add_argument("--out", type=Path, default=None, help="output wav for --sample")
    ap.add_argument("--engine", choices=["kokoro", "chatterbox"], default="kokoro", help="--sample only: which TTS engine to use (default kokoro, for backward-compatible quick tests). --project mode ignores this -- engine is decided per beat by beats.yaml/capy.beats.resolve_voice, not by a CLI flag.")
    ap.add_argument("--ref", type=Path, default=None, help="--sample --engine chatterbox only: path to a reference voice clip (e.g. assets/saint-capybara/voices/host_andrew_kennedy.wav)")
    ap.add_argument("--exaggeration", type=float, default=0.5, help="--sample --engine chatterbox only (default 0.5)")
    ap.add_argument("--cfg-weight", type=float, default=0.5, help="--sample --engine chatterbox only (default 0.5)")
    ap.add_argument("--voice", type=str, default=None, help="Kokoro voice id. --sample: overrides the default (am_michael). --project: overrides the project's host voice, FORCED to engine=kokoro regardless of what beats.yaml currently has there (see render_project's docstring) -- omit this to let beats.yaml/capy.beats.DEFAULT_VOICE decide per-beat, including Chatterbox.")
    ap.add_argument("--speed", type=float, default=None, help="--project: override the project's host speed, only meaningful alongside --voice (see its help). --sample --engine kokoro: Kokoro's native speed param (default 0.95). --sample --engine chatterbox: ffmpeg atempo/rubberband post-process speed (default 1.0, no stretch) -- Chatterbox has no native speed param.")
    ap.add_argument("--print-phonemes", action="store_true")
    ap.add_argument("--project", type=Path, default=None)
    ap.add_argument("--only", type=str, default=None, help="comma-separated beat ids (project mode)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--timestamps", choices=["kokoro", "whisper"], default="kokoro", help="project mode only: 'kokoro' (default) uses each Kokoro-engine beat's own token timestamps; 'whisper' forces the same whisper-based reconciliation used for Chatterbox beats onto Kokoro beats too (for A/B comparison/debugging -- Chatterbox beats always use whisper regardless of this flag, since Chatterbox exposes no timing of its own).")
    args = ap.parse_args()

    if args.sample:
        out = args.out or Path("sample.wav")
        if args.engine == "chatterbox":
            if not args.ref:
                print("error: --engine chatterbox --sample requires --ref <path to a reference clip>", file=sys.stderr)
                return 3
            render_sample_chatterbox(args.sample, out, args.ref, exaggeration=args.exaggeration, cfg_weight=args.cfg_weight, speed=args.speed if args.speed is not None else 1.0)
        else:
            render_sample(args.sample, out, args.voice or DEFAULT_VOICE, args.speed if args.speed is not None else DEFAULT_SPEED, print_phonemes=args.print_phonemes)
        return 0

    if args.project:
        only = set(args.only.split(",")) if args.only else None
        n = render_project(
            args.project, voice=args.voice, speed=args.speed,
            only=only, force=args.force, print_phonemes=args.print_phonemes,
            timestamps=args.timestamps,
        )
        print(f"\n{n} beat(s) rendered.")
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
