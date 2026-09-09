#!/usr/bin/env python3
"""**TEST / EXPERIMENTAL — hybrid Resolve pipeline, not yet approved for
production use.** See docs/saint-capybara/hybrid-resolve-pipeline.md.

Renders one transparent 1080x1920 PNG per caption phrase group, for
placement on their own Resolve video track (topmost, above the plates and
the source clip). Replaces the ffmpeg+libass `subtitles=` burn path with
plain stills, for the same reason capy_render.py already uses PIL stills
instead of Resolve's Text+ API for quote cards/credits (see
docs/resolve-mcp-gotchas.md: `insert_title` is unreliable and there is no
API to import an SRT file).

Word timing sources, per beat kind:
  - `clip` beats with `captions: source`: word timestamps from the
    project's own Whisper transcript (transcripts/source.json), sliced to
    the beat's [start, end) range and shifted to beat-relative time.
  - narration-family beats (`narration`/`card`/`evidence`/`chart`/`outro`):
    real per-word timing from `audio/<id>.timing.json` if capy_tts.py has
    already rendered it (post-Gate-A); otherwise an evenly-spaced DRAFT
    estimate across `capy.beats.estimate_hold_seconds()` for testing this
    tool's rendering before Gate A / before TTS exists. Draft-estimated
    beats are marked `"draft_timing": true` in the manifest and the PNGs
    get a small "(draft timing)" corner mark so they're never mistaken
    for the real, TTS-synced captions.

All output timestamps in captions/manifest.json are **beat-relative**
(seconds since the beat's own start) -- the Resolve-build planner is
responsible for offsetting by each beat's actual record frame.

Usage:
    python capy_caption_cards.py --project D:\\Videos\\<slug> [--only id,id] [--force-draft]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image, ImageDraw, ImageFont

from capy.beats import load_beats, estimate_hold_seconds
from capy.captions import group_phrases
from capy.layout import Theme


def _font(theme: Theme, which: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(theme.font_path(which)), size)
    except Exception:
        return ImageFont.load_default()


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


def _render_phrase_png(theme: Theme, phrase, *, draft: bool) -> Image.Image:
    w, h = theme.canvas_size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    style = theme.caption_style("style_source" if phrase.style == "Source" else "style_capy")
    font = _font(theme, style["font"], style["size"])
    outline_color = theme.color_rgba(style["outline"])
    fill_color = theme.color_rgba(style["primary"])
    highlight_color = theme.color_rgba(theme.data["captions"]["highlight_color"])

    cap_box = theme.caption_box()
    cy = (cap_box[1] + cap_box[3]) // 2
    cx = w // 2

    lines = phrase.text.split("\\N") if "\\N" in phrase.text else [phrase.text]
    if len(lines) == 1 and len(phrase.text) > theme.data["captions"]["max_chars_per_line"]:
        words = phrase.text.split()
        mid = max(1, len(words) // 2)
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]

    line_h = style["size"] + 14
    total_h = line_h * len(lines)
    ty = cy - total_h // 2
    highlight_words = set(phrase.highlight or [])

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=style["outline_px"] // 2)
        tw = bbox[2] - bbox[0]
        tx = cx - tw // 2
        words_in_line = line.split()
        cursor_x = tx
        for word in words_in_line:
            color = highlight_color if word.strip(",.!?\u2019'\"") in highlight_words else fill_color
            draw.text((cursor_x, ty), word, font=font, fill=color, stroke_width=style["outline_px"] // 2, stroke_fill=outline_color)
            word_w = draw.textbbox((0, 0), word + " ", font=font)[2]
            cursor_x += word_w
        ty += line_h

    if draft:
        mark_font = _font(theme, "display", 16)
        draw.text((16, cap_box[3] - 24), "(draft timing)", font=mark_font, fill=theme.color_rgba("highlight_brick", 220))

    return img


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--only", type=str, default=None, help="comma-separated beat ids")
    ap.add_argument("--force-draft", action="store_true", help="use even-spaced draft timing even if real timing.json exists")
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

    manifest = []
    for beat in doc["beats"]:
        bid = beat["id"]
        if only and bid not in only:
            continue
        kind = beat.get("kind")

        if kind == "clip":
            if beat.get("captions") != "source":
                continue
            words = _clip_words(transcript, beat["start"], beat["end"])
            style = "Source"
            draft = False
        elif kind in ("narration", "card", "evidence", "chart", "outro"):
            text = beat.get("text")
            if not text:
                continue
            timing_path = project / "audio" / f"{bid}.timing.json"
            if timing_path.exists() and not args.force_draft:
                words = json.loads(timing_path.read_text(encoding="utf-8"))
                draft = False
            else:
                duration = estimate_hold_seconds(text)
                words = _draft_words(text, duration)
                draft = True
            style = "Capy"
        else:
            continue

        if not words:
            print(f"skip {bid}: no word timings available")
            continue

        highlight = beat.get("highlight")
        phrases = group_phrases(
            words,
            max_chars=theme.data["captions"]["max_chars_per_line"],
            max_words=theme.data["captions"]["max_words_per_phrase"],
            gap_break=theme.data["captions"]["gap_break_seconds"],
            style=style,
            highlight=highlight,
        )

        for idx, phrase in enumerate(phrases):
            img = _render_phrase_png(theme, phrase, draft=draft)
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
