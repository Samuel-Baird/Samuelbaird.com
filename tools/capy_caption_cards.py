#!/usr/bin/env python3
"""Renders one transparent 1080x1920 PNG per caption phrase group
(captions/<id>_<n>.png), for compositing into each beat's clip by
capy_render_beat_clips.py.

Word timing sources, per beat kind:
  - `clip` beats with `captions: source`: word timestamps from the
    project's own Whisper transcript (transcripts/source.json), sliced to
    the beat's [start, end) range and shifted to beat-relative time.
  - `excerpt` beats: real per-word timing from audio/<id>.timing.json
    (Kokoro's own token timestamps for that beat's quote-voice reading).
  - narration-family beats (`narration`/`card`/`evidence`/`chart`/`outro`):
    real per-word timing from audio/<id>.timing.json if capy_tts.py has
    already rendered it (post-Gate-A); otherwise an evenly-spaced DRAFT
    estimate across capy.beats.estimate_hold_seconds() for testing this
    tool's rendering before Gate A / before TTS exists. Draft-estimated
    beats are marked "draft_timing": true in the manifest (no on-screen
    corner mark -- that was itself on-screen text outside the
    caption/quote rule; check the manifest flag instead).

Every caption PNG is laid out by tools/capy/text.py (measured-width wrap,
shrink-to-fit) using the style and zone for the beat's frame mode
(CLIP -> style_source with a pill, CARD -> style_card, HOST -> style_capy)
-- see tools/capy/layout.py and assets/saint-capybara/theme.yaml.

Usage:
    python capy_caption_cards.py --project D:\\Videos\\<slug> [--only id,id] [--force-draft] [--render-fixed-outro]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image, ImageDraw, ImageFont

from capy.beats import load_beats, estimate_hold_seconds, is_fixed_outro
from capy.captions import group_phrases, attach_punctuation
from capy.layout import Theme
from capy.text import fit_text, draw_lines


def _style_name_for(theme: Theme, beat: dict) -> str:
    mode = theme.mode_for(beat)
    if mode == "clip":
        return "style_source"
    if mode == "card":
        return "style_card"
    return "style_capy"


def _clip_words(transcript: dict, start: float, end: float) -> list[dict]:
    words = []
    for seg in transcript.get("segments", []):
        for w in seg.get("words", []):
            ws, we = w.get("start"), w.get("end")
            if ws is None or we is None or ws < start or we > end + 0.05:
                continue
            words.append({"w": w["word"].strip(), "s": ws - start, "e": we - start})
    return words


def _draft_words(text: str, duration: float) -> list[dict]:
    """Evenly-spaced pseudo-timing across `duration` -- for testing the
    caption renderer before real TTS timing exists. Never used once
    audio/<id>.timing.json is present."""
    words = text.split()
    if not words:
        return []
    per = duration / len(words)
    return [{"w": w, "s": i * per, "e": (i + 1) * per} for i, w in enumerate(words)]


def _render_phrase_png(theme: Theme, phrase, mode: str, style_name: str) -> Image.Image:
    w, h = theme.canvas_size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    style = theme.caption_style(style_name)
    font_path = theme.font_path(style["font"])
    zone = theme.caption_zone(mode)

    fill_color = theme.color_rgba(style["primary"])
    outline_color = theme.color_rgba(style["outline"])
    highlight_color = theme.color_rgba(theme.data["captions"]["highlight_color"])
    highlight_words = set(phrase.highlight or [])

    max_lines = theme.data["captions"]["max_lines"]
    font, lines = fit_text(
        phrase.text, font_path,
        size=style["size"], min_size=style["min_size"],
        step=theme.data["captions"]["shrink_step"],
        max_w=zone.max_width, max_lines=max_lines, stroke=style["stroke_px"],
    )

    pill = style.get("pill")
    pill_color = theme.color_rgba(pill["color"], pill["alpha"]) if pill else None

    draw_lines(
        img, lines, font, zone,
        fill=fill_color, stroke_px=style["stroke_px"], stroke_fill=outline_color,
        line_height_mult=theme.data["captions"]["line_height"],
        highlight_words=highlight_words, highlight_color=highlight_color if highlight_words else None,
        pill=pill, pill_color=pill_color,
    )
    return img


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--only", type=str, default=None, help="comma-separated beat ids")
    ap.add_argument("--force-draft", action="store_true", help="use even-spaced draft timing even if real timing.json exists")
    ap.add_argument("--render-fixed-outro", action="store_true", help="render outro-01..05 too (used by capy_outro.py)")
    args = ap.parse_args()

    project = args.project.resolve()
    beats_path = project / "script" / "beats.yaml"
    if not beats_path.exists():
        print(f"error: {beats_path} not found", file=sys.stderr)
        return 1

    doc = load_beats(beats_path)
    only = set(args.only.split(",")) if args.only else None
    theme = Theme.load()

    captions_dir = project / "captions"
    captions_dir.mkdir(parents=True, exist_ok=True)

    transcript_path = project / "transcripts" / "source.json"
    transcript = json.loads(transcript_path.read_text(encoding="utf-8")) if transcript_path.exists() else {}

    font_path_by_style: dict[str, Path] = {}

    def measurer(style_name: str):
        style = theme.caption_style(style_name)
        if style_name not in font_path_by_style:
            font_path_by_style[style_name] = theme.font_path(style["font"])
        font = ImageFont.truetype(str(font_path_by_style[style_name]), style["size"])
        return font.getlength

    manifest = []
    for beat in doc["beats"]:
        bid = beat["id"]
        kind = beat.get("kind")

        if is_fixed_outro(beat) and not args.render_fixed_outro:
            continue
        if only and bid not in only:
            continue

        mode = theme.mode_for(beat)
        style_name = _style_name_for(theme, beat)

        if kind == "clip":
            if beat.get("captions") != "source":
                continue
            words = attach_punctuation(_clip_words(transcript, beat["start"], beat["end"]))
            style_key = "Source"
            draft = False
        elif kind in ("narration", "card", "evidence", "chart", "excerpt", "outro"):
            text = beat.get("text")
            if not text:
                continue
            timing_path = project / "audio" / f"{bid}.timing.json"
            if timing_path.exists() and not args.force_draft:
                words = attach_punctuation(json.loads(timing_path.read_text(encoding="utf-8")))
                draft = False
            else:
                # Draft (pre-TTS) captions for an excerpt must never show
                # a literal '[...]' token -- real timing.json never
                # contains one (capy.excerpts.speech_text strips it
                # before synthesis), so the draft preview shouldn't either.
                draft_text = text
                if kind == "excerpt":
                    try:
                        from capy.excerpts import caption_text
                        draft_text = caption_text(beat)
                    except ImportError:
                        draft_text = text.replace("[...]", "...")
                duration = estimate_hold_seconds(draft_text)
                words = _draft_words(draft_text, duration)
                draft = True
            style_key = "Card" if mode == "card" else "Capy"
        else:
            continue

        if not words:
            print(f"skip {bid}: no word timings available")
            continue

        highlight = beat.get("highlight") if kind != "excerpt" else None
        cap_style = theme.caption_style(style_name)
        phrases = group_phrases(
            words,
            max_chars=theme.data["captions"]["max_chars_per_line"],
            max_words=theme.data["captions"]["max_words_per_phrase"],
            gap_break=theme.data["captions"]["gap_break_seconds"],
            style=style_key,
            highlight=highlight,
            measure=measurer(style_name),
            max_width=theme.caption_zone(mode).max_width,
        )

        for idx, phrase in enumerate(phrases):
            img = _render_phrase_png(theme, phrase, mode, style_name)
            out_path = captions_dir / f"{bid}_{idx:02d}.png"
            img.save(out_path)
            manifest.append({
                "beat_id": bid, "index": idx,
                "path": str(out_path.relative_to(project)),
                "start": round(phrase.start, 3), "end": round(phrase.end, 3),
                "text": phrase.text, "draft_timing": draft,
            })
        tag = " (DRAFT TIMING)" if draft else ""
        print(f"{bid}: {len(phrases)} caption card(s){tag}")

    manifest_path = captions_dir / "manifest.json"
    if only and manifest_path.exists():
        existing = [m for m in json.loads(manifest_path.read_text(encoding="utf-8")) if m["beat_id"] not in only]
        manifest = existing + manifest
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    n_draft = sum(1 for m in manifest if m["draft_timing"])
    print(f"\n{len(manifest)} caption card(s) written ({n_draft} on draft timing). Manifest: {captions_dir / 'manifest.json'}")
    if n_draft:
        print("NOTE: draft-timed cards will NOT match the final narration once real TTS runs -- re-run this tool after capy_tts.py (post-Gate-A) before building the Resolve timeline for real.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
