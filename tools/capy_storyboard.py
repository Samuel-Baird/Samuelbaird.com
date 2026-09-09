#!/usr/bin/env python3
"""Render a Saint Capybara project's storyboard contact sheet and
script.md from script/beats.yaml.

    python tools/capy_storyboard.py --project D:\\Videos\\<slug> [--cols 4] [--with-captions]

Outputs:
    frames/storyboard.png   -- one plate per beat, labeled, on a contact sheet
    script/script.md        -- the Gate A review document (see script-format.md)

--with-captions additionally renders one real ffmpeg+libass frame
(frames/caption_check.png) using theme.yaml's fonts via `subtitles=...
:fontsdir=...` -- this is also the font-discovery smoke test: if libass
can't find Press Start 2P / Pixelify Sans it silently falls back to a
default font, which this flag's output makes visible to the eye.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image

from capy import beats as beats_mod
from capy import ff
from capy.layout import Theme, FONTS_DIR
from capy.plates import render_plate
from capy.compose import contact_sheet


def extract_clip_frame(source_video: Path, at_seconds: float) -> Image.Image | None:
    if not source_video.exists():
        return None
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "frame.png"
        try:
            ff.run([
                "ffmpeg", "-y", "-ss", str(max(0.0, at_seconds)), "-i", str(source_video),
                "-frames:v", "1", str(out),
            ])
        except ff.FFError as e:
            print(f"warning: could not extract clip frame at {at_seconds}s: {e}")
            return None
        if out.exists():
            return Image.open(out).convert("RGBA").copy()
    return None


def render_script_md(doc: dict, per_beat: dict[str, float], total: float) -> str:
    lines = [f"# Script — {doc.get('title', doc.get('slug'))}", ""]
    lines.append(f"**Slug:** `{doc.get('slug')}` | **Hook:** {doc.get('hook','')!r} | **Estimated runtime:** {total:.1f}s "
                  f"(budget {doc['format']['min_seconds']}-{doc['format']['max_seconds']}s)")
    lines.append("")
    lines.append("Edit this file with `DROP` / `SPLIT` / `MOVE AFTER Bxx` directives or plain-language notes "
                  "(see docs/saint-capybara/script-format.md) and return it -- do not edit beats.yaml directly "
                  "unless you're comfortable with the YAML.")
    lines.append("")
    for i, beat in enumerate(doc.get("beats", []), start=1):
        bid = beat["id"]
        kind = beat["kind"]
        dur = per_beat.get(bid, 0.0)
        lines.append(f"## {i:02d}. `{bid}` ({kind}, ~{dur:.1f}s)")
        pose = beats_mod.resolve_pose(beat, sensitive=bool(doc.get("sensitive")))
        if pose:
            lines.append(f"- **Pose:** {pose}")
        if kind == "clip":
            lines.append(f"- **Clip:** {beat.get('speaker','Source video')}, {beat['start']}s–{beat['end']}s @ speed {beat.get('speed',1.0)}")
        if beat.get("text"):
            lines.append(f"- **Narration:** {beat['text']}")
        if kind == "card":
            card = beat.get("card", {})
            lines.append(f"- **Card quote:** “{card.get('quote','')}” — {card.get('attribution','')}")
        if beat.get("evidence", {}).get("image"):
            ev = beat["evidence"]
            lines.append(f"- **Evidence:** `{ev['image']}` — {ev.get('credit','')} (placement: {ev.get('placement','panel')})")
        if beat.get("chart"):
            ch = beat["chart"]
            lines.append(f"- **Chart:** {ch.get('title','')} ({ch.get('type','bar')})")
        if beat.get("sources"):
            lines.append(f"- **Sources:** {', '.join(beat['sources'])}")
        lines.append("- **Notes:** ")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--with-captions", action="store_true")
    args = ap.parse_args()

    project = args.project
    beats_path = project / "script" / "beats.yaml"
    doc = beats_mod.load_beats(beats_path)
    issues = beats_mod.validate(doc)
    errors = [i for i in issues if i.level == "error"]
    for i in issues:
        print(i)
    if errors:
        print(f"\n{len(errors)} error(s) -- fix beats.yaml (or run capy_check_sources.py) before storyboarding.")
        return 1

    theme = Theme.load()
    total, per_beat = beats_mod.resolve_durations(doc)

    source_video = project / "source" / "source.mp4"
    sensitive = bool(doc.get("sensitive"))

    labeled: list[tuple[str, Image.Image]] = []
    beats_list = doc.get("beats", [])
    for i, beat in enumerate(beats_list):
        beat = dict(beat)
        if i == 0:
            beat["_is_first"] = True
            beat["_hook"] = doc.get("hook")
        clip_frame = None
        if beat.get("kind") == "clip":
            clip_frame = extract_clip_frame(source_video, beat.get("start", 0.0))
        elif beat.get("stage") == "freeze":
            # freeze the last clip beat's frame (simple heuristic: previous clip beat's end time)
            for prev in reversed(beats_list[:i]):
                if prev.get("kind") == "clip":
                    clip_frame = extract_clip_frame(source_video, prev.get("end", 0.0) - 0.1)
                    break
        plate = render_plate(beat, theme, project_dir=project, clip_frame=clip_frame, sensitive=sensitive)
        labeled.append((f"{beat['id']} ({beat['kind']}, {per_beat.get(beat['id'],0):.1f}s)", plate))

    sheet = contact_sheet(labeled, cols=args.cols, cell=360, pad=20, label_h=32)
    frames_dir = project / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    sheet_path = frames_dir / "storyboard.png"
    sheet.save(sheet_path, format="PNG")
    print(f"Wrote {sheet_path}")

    script_md = render_script_md(doc, per_beat, total)
    script_path = project / "script" / "script.md"
    script_path.write_text(script_md, encoding="utf-8")
    print(f"Wrote {script_path}")

    if args.with_captions:
        _render_caption_check(project, theme, doc, labeled)

    return 0


def _render_caption_check(project: Path, theme: Theme, doc: dict, labeled: list[tuple[str, Image.Image]]) -> None:
    """Render one real ffmpeg+libass frame to sanity-check that
    Press Start 2P / Pixelify Sans are actually being found by libass on
    this Windows ffmpeg build (fontsdir=), rather than silently falling
    back to a default font."""
    from capy.captions import group_phrases, build_ass

    # Use the first narration-family beat's text as a synthetic caption
    # sample (no real TTS timing exists yet, pre-Gate-A) -- purely a font
    # rendering smoke test, not a real caption sync check.
    sample_text = None
    for beat in doc.get("beats", []):
        if beat.get("text"):
            sample_text = beat["text"]
            break
    if not sample_text:
        print("no narration text found -- skipping caption-check render")
        return

    words = sample_text.split()
    now = 0.0
    fake_words = []
    for w in words:
        fake_words.append({"w": w, "s": now, "e": now + 0.3})
        now += 0.35
    phrases = group_phrases(fake_words, style="Capy")
    ass_text = build_ass(phrases, theme)

    frames_dir = project / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    ass_path = frames_dir / "caption_check.ass"
    ass_path.write_text(ass_text, encoding="utf-8")

    # Base frame: first plate in the storyboard, or a blank parchment frame.
    base_img = labeled[0][1] if labeled else None
    w, h = theme.canvas_size
    if base_img is None:
        base_img = Image.new("RGBA", (w, h), theme.color_rgba("parchment"))
    base_path = frames_dir / "_caption_check_base.png"
    base_img.convert("RGB").save(base_path, format="PNG")

    out_path = frames_dir / "caption_check.png"
    # Windows path escaping for ffmpeg filter args: each path needs its
    # drive-letter colon escaped AND the whole path wrapped in single
    # quotes, or ffmpeg's filtergraph parser misreads the second `:`
    # (between subtitles= and fontsdir=) as part of the first path.
    subtitles_arg = f"subtitles='{ff.ffpath(ass_path)}':fontsdir='{ff.ffpath(FONTS_DIR)}'"
    try:
        ff.run([
            "ffmpeg", "-y", "-i", str(base_path),
            "-vf", subtitles_arg,
            "-frames:v", "1", "-update", "1", str(out_path),
        ])
        print(f"Wrote {out_path} (libass font-discovery check -- inspect by eye for Pixelify Sans, not a fallback font)")
    except ff.FFError as e:
        print(f"warning: caption-check render failed (libass/fontsdir issue?): {e}")


if __name__ == "__main__":
    raise SystemExit(main())
