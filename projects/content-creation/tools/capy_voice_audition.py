#!/usr/bin/env python3
"""Kokoro voice bake-off for Saint Capybara.

Renders, for every voice in --voices (default: all 13 English male voices
plus the female shortlist), a loudness-normalised HOST take (brand-tone
narration at the host speed) and a QUOTE take (first-person "quoted
article" text at the quote speed), plus a spoken slate, and stitches them
into one audition_all.wav so the user can listen straight through.

    python tools/capy_voice_audition.py --out D:\saint-capybara\voice-audition

Voices not yet in the local Hugging Face cache are downloaded by Kokoro on
first use (~520 KB each). Uses the same pronunciation dictionary and
normalisation as capy_tts.py so what you hear is what a video would sound
like.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from capy_tts import apply_dictionary, load_pronunciation_dict, normalize_wav, SAMPLE_RATE

MALE = [
    "am_michael", "am_fenrir", "am_puck", "bm_fable", "bm_george", "am_onyx",
    "bm_lewis", "am_echo", "am_eric", "am_liam", "bm_daniel", "am_adam", "am_santa",
]
FEMALE = ["af_heart", "af_bella", "af_nicole", "bf_emma", "af_sarah"]

GRADES = {
    "am_michael": "C+", "am_fenrir": "C+", "am_puck": "C+", "bm_fable": "C", "bm_george": "C",
    "am_onyx": "D", "bm_lewis": "D+", "am_echo": "D", "am_eric": "D", "am_liam": "D",
    "bm_daniel": "D", "am_adam": "F+", "am_santa": "D-",
    "af_heart": "A", "af_bella": "A-", "af_nicole": "B-", "bf_emma": "B-", "af_sarah": "C+",
}

HOST_TEXT = (
    "That claim sounds strong until you check the premise. Joseph Smith did use a seer stone, "
    "and Oliver Cowdery said so in print. But the Kirtland and Nauvoo accounts were public for decades, "
    "not hidden. Once you apply the same standard consistently, the criticism explains the evidence "
    "poorly, and the Latter-day Saint position explains it better."
)
QUOTE_TEXT = (
    "I grew up in the church and I loved it, but the more I read about the history, the harder it "
    "became to square what I was taught with what the documents actually say. Nobody told me about "
    "the stone in the hat until I was thirty."
)


def spell_voice(voice: str) -> str:
    prefix, name = voice.split("_", 1)
    return f"Voice: {' '.join(prefix.upper())}, {name.capitalize()}."


def synth(pipeline, text: str, voice: str, speed: float, entries):
    import numpy as np
    processed = apply_dictionary(text, entries)
    chunks = []
    for result in pipeline(processed, voice=voice, speed=speed):
        audio = result.audio
        if audio is None:
            continue
        chunks.append(audio.numpy() if hasattr(audio, "numpy") else np.asarray(audio))
    if not chunks:
        raise RuntimeError("kokoro produced no audio")
    return np.concatenate(chunks)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=Path(r"D:\saint-capybara\voice-audition"))
    ap.add_argument("--voices", type=str, default=None, help="comma-separated voice ids (default: MALE + FEMALE)")
    ap.add_argument("--host-speed", type=float, default=0.95)
    ap.add_argument("--quote-speed", type=float, default=1.0)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    import soundfile as sf
    import numpy as np
    from kokoro import KPipeline

    voices = args.voices.split(",") if args.voices else MALE + FEMALE
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    entries = load_pronunciation_dict(None)
    pipeline = KPipeline(lang_code="a")

    rows = []
    failures = {}
    for voice in voices:
        t0 = time.time()
        takes = {}
        try:
            for take, text, speed in (
                ("slate", spell_voice(voice), 1.0),
                ("host", HOST_TEXT, args.host_speed),
                ("quote", QUOTE_TEXT, args.quote_speed),
            ):
                raw = out / f"{voice}_{take}.raw.wav"
                norm = out / f"{voice}_{take}.wav"
                if norm.exists() and not args.force:
                    takes[take] = norm
                    continue
                audio = synth(pipeline, text, voice, speed, entries)
                sf.write(str(raw), audio, SAMPLE_RATE)
                normalize_wav(raw, norm)
                raw.unlink(missing_ok=True)
                takes[take] = norm
            host_dur = sf.info(str(takes["host"])).duration
            quote_dur = sf.info(str(takes["quote"])).duration
            rows.append((voice, GRADES.get(voice, "?"), host_dur, quote_dur))
            print(f"{voice}: host {host_dur:.1f}s, quote {quote_dur:.1f}s ({time.time() - t0:.0f}s)")
        except Exception as e:  # keep going; report at the end
            failures[voice] = repr(e)
            print(f"{voice}: FAILED {e!r}", file=sys.stderr)

    # Stitch: slate + host + quote per voice, 0.7s gaps, 1.5s between voices.
    gap = np.zeros((int(48000 * 0.7), 2), dtype="float32")
    big_gap = np.zeros((int(48000 * 1.5), 2), dtype="float32")
    parts = []
    for voice, *_ in rows:
        for take in ("slate", "host", "quote"):
            data, sr = sf.read(str(out / f"{voice}_{take}.wav"), dtype="float32", always_2d=True)
            assert sr == 48000
            parts += [data, gap]
        parts.append(big_gap)
    if parts:
        sf.write(str(out / "audition_all.wav"), np.concatenate(parts), 48000)

    lines = ["# Kokoro voice audition", "",
             f"Host text ({len(HOST_TEXT.split())} words, speed {args.host_speed}); quote text ({len(QUOTE_TEXT.split())} words, speed {args.quote_speed}). All takes normalised to -16 LUFS.",
             "", "| Voice | Upstream grade | Host take | Quote take |", "|---|---|---|---|"]
    for voice, grade, hd, qd in rows:
        lines.append(f"| {voice} | {grade} | `{voice}_host.wav` ({hd:.1f}s) | `{voice}_quote.wav` ({qd:.1f}s) |")
    if failures:
        lines += ["", "## Failed", ""] + [f"- {v}: {err}" for v, err in failures.items()]
    lines += ["", "`audition_all.wav` plays every voice in the table order: slate, host take, quote take."]
    (out / "audition.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "audition.json").write_text(json.dumps({"rows": rows, "failures": failures}, indent=2), encoding="utf-8")
    print(f"\n{len(rows)} voice(s) rendered, {len(failures)} failed. See {out / 'audition.md'}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
