"""Whisper-based word-timing reconciliation for TTS engines (Chatterbox)
that don't expose their own token/word timestamps the way Kokoro does.

    from capy.align import align_timing

    timings = align_timing(wav_path, script_text)   # -> [{w, s, e}, ...]

Chatterbox's generate() (and the whole T3/S3Gen architecture underneath
it) exposes no duration/alignment information at all -- confirmed by
reading the installed package source directly (2026-09-11). The
approach here: run `openai-whisper` (already installed + pinned in
tools/requirements.txt for tools/transcribe.py's clip-beat captions;
reused here in-process rather than via its CLI, so the model loads once
per capy_tts.py run instead of once per beat) with word_timestamps=True
on the rendered wav, then reconcile its recognized words against the
KNOWN script text via difflib -- so timing.json always contains the
real script's words (never Whisper's own mis-hearing) with the
best-matched timestamps. Never crashes: falls back to evenly-spaced
timing (scoped to the wav's real measured duration) on a poor match,
logging a warning so a human knows to double-check that beat's captions
by ear during QA -- this fallback is deliberately the same shape/quality
as capy_caption_cards.py's own pre-TTS draft timing, not a new failure
mode.

Empirically validated on 2026-09-11 against a real Chatterbox render
(Line C, ~10s, ~30 words): Whisper's recognized text matched the
original script word-for-word, in order, correct count (only trivial
casing differences on a mid-sentence "he"/"He").
"""
from __future__ import annotations

import difflib
import re
import sys
from pathlib import Path

_WHISPER_MODEL = None  # process-wide cache: load once, reuse for every beat
WHISPER_MODEL_NAME = "small.en"  # matches tools/transcribe.py's default


def _get_whisper_model():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        import whisper
        print(f"[align] loading whisper model {WHISPER_MODEL_NAME!r} (once per run)...", file=sys.stderr)
        _WHISPER_MODEL = whisper.load_model(WHISPER_MODEL_NAME)
    return _WHISPER_MODEL


def _wav_duration_seconds(wav_path: Path) -> float:
    import soundfile as sf
    info = sf.info(str(wav_path))
    return info.frames / info.samplerate


_WORD_RE = re.compile(r"[A-Za-z0-9']+")


def _normalize(word: str) -> str:
    """Lowercase, strip surrounding punctuation/whitespace -- used only
    for MATCHING script words against Whisper's recognized words, never
    for what ends up in timing.json (that always keeps the script's own
    original word text)."""
    m = _WORD_RE.findall(word.lower())
    return "".join(m)


def _evenly_spaced(script_words: list[str], duration: float) -> list[dict]:
    if not script_words:
        return []
    per = duration / len(script_words)
    return [{"w": w, "s": round(i * per, 3), "e": round((i + 1) * per, 3)} for i, w in enumerate(script_words)]


def align_timing(wav_path: Path, script_text: str, *, min_match_ratio: float = 0.6) -> list[dict]:
    """Per-word {w, s, e} timing (seconds) for `script_text` as actually
    spoken in `wav_path`, via Whisper ASR + sequence-matching
    reconciliation against the known script words. `w` is always the
    original script word (with its own punctuation attached, same
    convention as Kokoro's timing.json); `s`/`e` come from the
    best-matching Whisper word, or are linearly interpolated between the
    nearest matched neighbours when a script word has no match at all.
    Falls back to evenly-spaced timing across the wav's real measured
    duration (never crashes) if fewer than `min_match_ratio` of the
    script words could be matched -- logs a warning either way so a
    human knows to double-check that beat's captions by ear."""
    script_words = script_text.split()
    duration = _wav_duration_seconds(wav_path)
    if not script_words:
        return []

    try:
        model = _get_whisper_model()
        result = model.transcribe(str(wav_path), word_timestamps=True)
    except Exception as e:
        print(f"[align] WARNING: whisper transcription failed ({e}); falling back to evenly-spaced timing for {wav_path.name}", file=sys.stderr)
        return _evenly_spaced(script_words, duration)

    whisper_words: list[dict] = []
    for seg in result.get("segments", []):
        for w in seg.get("words", []):
            if w.get("start") is None or w.get("end") is None:
                continue
            whisper_words.append({"text": w["word"], "start": w["start"], "end": w["end"]})

    if not whisper_words:
        print(f"[align] WARNING: whisper produced no word timestamps for {wav_path.name}; falling back to evenly-spaced timing", file=sys.stderr)
        return _evenly_spaced(script_words, duration)

    script_norm = [_normalize(w) for w in script_words]
    whisper_norm = [_normalize(w["text"]) for w in whisper_words]

    matcher = difflib.SequenceMatcher(a=script_norm, b=whisper_norm, autojunk=False)
    matched_pairs: dict[int, int] = {}  # script index -> whisper index
    n_matched_words = 0
    for tag, a0, a1, b0, b1 in matcher.get_opcodes():
        if tag == "equal":
            for off in range(a1 - a0):
                matched_pairs[a0 + off] = b0 + off
            n_matched_words += (a1 - a0)

    match_ratio = n_matched_words / len(script_words)
    if match_ratio < min_match_ratio:
        print(
            f"[align] WARNING: only {n_matched_words}/{len(script_words)} script words "
            f"({match_ratio:.0%}) matched whisper's transcription of {wav_path.name} "
            f"(recognized: {result.get('text', '')!r}); falling back to evenly-spaced timing",
            file=sys.stderr,
        )
        return _evenly_spaced(script_words, duration)

    if match_ratio < 1.0:
        print(
            f"[align] NOTE: {n_matched_words}/{len(script_words)} script words "
            f"({match_ratio:.0%}) matched for {wav_path.name}; unmatched words got "
            f"interpolated timing -- worth a caption spot-check on this beat",
            file=sys.stderr,
        )

    # Fill in unmatched script words by linear interpolation between the
    # nearest matched neighbours (or the clip boundaries if a run of
    # unmatched words is at the very start/end).
    out: list[dict] = [None] * len(script_words)  # type: ignore[list-item]
    for si, wi in matched_pairs.items():
        out[si] = {"w": script_words[si], "s": round(whisper_words[wi]["start"], 3), "e": round(whisper_words[wi]["end"], 3)}

    i = 0
    while i < len(out):
        if out[i] is not None:
            i += 1
            continue
        j = i
        while j < len(out) and out[j] is None:
            j += 1
        prev_end = out[i - 1]["e"] if i > 0 else 0.0
        next_start = out[j]["s"] if j < len(out) else duration
        span = max(next_start - prev_end, 0.0)
        n = j - i
        per = span / n if n else 0.0
        for k in range(i, j):
            s = prev_end + per * (k - i)
            e = prev_end + per * (k - i + 1)
            out[k] = {"w": script_words[k], "s": round(s, 3), "e": round(e, 3)}
        i = j

    return out
