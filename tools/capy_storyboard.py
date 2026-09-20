#!/usr/bin/env python3
"""Render a Saint Capybara project's storyboard contact sheet and
script.md from script/beats.yaml.

    python tools/capy_storyboard.py --project D:\\Videos\\<slug> [--cols 4]
    python tools/capy_storyboard.py --mock [--out DIR]

Outputs:
    frames/storyboard.png   -- one plate per beat, labeled, on a contact sheet
    script/script.md        -- the Gate A review document (see script-format.md)

For CLIP beats, the contact sheet composites a real extracted frame under
the transparent plate (the same cover-crop/letterbox logic
capy_render_beat_clips.py uses with ffmpeg) so the preview matches the
real full-bleed look.

--mock builds a synthetic beat list covering every frame mode/kind
(clip 9:16, clip 16:9, narration blank/freeze, card, evidence, chart,
excerpt, the non-square `quote` pose) with a worst-case caption on each,
and writes individual PNGs plus a contact sheet under
theme.cache_dir("mock") -- no --project needed. Use this to eyeball a
layout/font change before spending a real render.
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
from capy.layout import Theme
from capy.plates import render_plate
from capy.compose import contact_sheet
from capy.captions import group_phrases
from capy.text import fit_text, draw_lines


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


def _format_timestamp(seconds: float) -> str:
    m, s = divmod(max(0.0, seconds), 60)
    return f"{int(m):02d}:{s:05.2f}"


def _load_transcript_lines(project: Path) -> list[str] | None:
    """Timestamped lines from transcripts/source.json (Whisper segments),
    for the full-transcript appendix in script.md -- lets a reviewer check
    every response beat against exactly what the source video said, not
    just the excerpted clip spans beats.yaml pulls from it."""
    segments = _load_transcript_segments(project)
    if not segments:
        return None
    return [
        f"- `[{_format_timestamp(seg['start'])}–{_format_timestamp(seg['end'])}]` {seg['text'].strip()}"
        for seg in segments
    ]


def _load_transcript_segments(project: Path) -> list[dict] | None:
    import json

    transcript_path = project / "transcripts" / "source.json"
    if not transcript_path.exists():
        return None
    try:
        data = json.loads(transcript_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data.get("segments") or None


def _transcript_span_text(segments: list[dict], start: float, end: float) -> str:
    """Verbatim transcript text for segments overlapping [start, end]."""
    words = [seg["text"].strip() for seg in segments if seg["start"] < end and seg["end"] > start]
    return " ".join(words)


def render_script_md(doc: dict, per_beat: dict[str, float], total: float, project: Path | None = None) -> str:
    source_time = beats_mod.source_time_seconds(doc, per_beat)
    pct = (source_time / total * 100) if total else 0.0
    lines = [f"# Script — {doc.get('title', doc.get('slug'))}", ""]
    lines.append(f"**Slug:** `{doc.get('slug')}` | **Estimated runtime:** {total:.1f}s "
                  f"(budget {doc['format']['min_seconds']}-{doc['format']['max_seconds']}s) | "
                  f"**Source time:** {source_time:.1f}s ({pct:.0f}%)")
    source_info = None
    if project is not None:
        try:
            from capy.source import load_source_info
            source_info = load_source_info(project)
        except Exception:
            source_info = None
    if source_info is not None and source_info.kind == "article":
        try:
            from capy.source import source_header_lines
            lines.extend(source_header_lines(source_info))
        except Exception:
            pass
    lines.append("")
    lines.append(f"**Hook (title/description only, not shown on screen):** {doc.get('hook','')!r}")
    exemplars = doc.get("exemplars") or []
    lines.append(f"**Exemplars modeled:** {', '.join(exemplars) if exemplars else 'none'}")
    lines.append("")
    lines.append("Edit this file with `DROP` / `SPLIT` / `MOVE AFTER Bxx` directives or plain-language notes "
                  "(see docs/saint-capybara/script-format.md) and return it -- do not edit beats.yaml directly "
                  "unless you're comfortable with the YAML.")
    lines.append("")

    video_segments = None
    if project is not None and (source_info is None or source_info.kind != "article"):
        video_segments = _load_transcript_segments(project)
    last_clip_transcript = "(none yet)"

    for i, beat in enumerate(doc.get("beats", []), start=1):
        bid = beat["id"]
        kind = beat["kind"]
        dur = per_beat.get(bid, 0.0)
        lines.append(f"## {i:02d}. `{bid}` ({kind}, ~{dur:.1f}s)")
        if video_segments is not None:
            if kind == "clip":
                last_clip_transcript = _transcript_span_text(video_segments, beat["start"], beat["end"]) or "(no transcript in this span)"
            lines.append(f"- **Original Video Transcript:** {last_clip_transcript}")
        pose = beats_mod.resolve_pose(beat, sensitive=bool(doc.get("sensitive")))
        if pose:
            lines.append(f"- **Pose:** {pose}")
        if kind == "clip":
            lines.append(f"- **Clip:** {beat.get('speaker','Source video')}, {beat['start']}s–{beat['end']}s @ speed {beat.get('speed',1.0)}")
        if kind == "excerpt":
            if source_info is not None:
                try:
                    from capy.source import excerpt_script_line
                    voice_role = beats_mod.resolve_voice(doc, beat).get("role", "quote_default")
                    lines.append(excerpt_script_line(beat, source_info, voice=voice_role))
                except Exception as e:
                    lines.append(f"- **Excerpt (¶{beat.get('para')}):** “{beat.get('text','')}” (attribution unavailable: {e})")
            else:
                lines.append(f"- **Excerpt (¶{beat.get('para')}):** “{beat.get('text','')}” (no source/source_info.json found)")
        elif beat.get("text"):
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

    if project is not None and (source_info is None or source_info.kind != "article"):
        transcript_lines = _load_transcript_lines(project)
        if transcript_lines:
            lines.append("## Full source transcript")
            lines.append("")
            lines.append("Every line of the source video, timestamped, for checking each response "
                          "beat above against the full context -- not just the clip spans quoted from it.")
            lines.append("")
            lines.extend(transcript_lines)
            lines.append("")

    return "\n".join(lines)


def _mock_beats(mock_dir: Path) -> tuple[list[dict], Path, Path]:
    """Synthetic beats covering every mode/kind. Returns (beats, portrait_frame_path, landscape_frame_path)."""
    portrait = mock_dir / "mock_source_916.png"
    landscape = mock_dir / "mock_source_169.png"
    if not portrait.exists():
        Image.new("RGB", (1080, 1920), (90, 60, 140)).save(portrait)
    if not landscape.exists():
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc2=size=1920x1080",
            "-frames:v", "1", str(landscape),
        ], capture_output=True, check=True)

    beats = [
        {"id": "c01", "kind": "clip", "pose": "listening", "_mock_frame": portrait},
        {"id": "c02", "kind": "clip", "pose": "listening", "_mock_frame": landscape},
        {"id": "n01", "kind": "narration", "pose": "reading", "stage": "blank"},
        {"id": "n02", "kind": "narration", "pose": "concerned", "stage": "freeze", "_mock_frame": portrait},
        {"id": "q01", "kind": "card", "pose": "quote", "card": {
            "quote": "Brother Joseph would read off the English to Oliver Cowdery, who was his principal scribe... "
                     "Thus the Book of Mormon was translated by the gift and power of God, and not by any power of man.",
            "attribution": "David Whitmer, An Address to All Believers in Christ (1887)",
        }},
        {"id": "e01", "kind": "evidence", "pose": "source", "evidence": {"credit": "Missing-image smoke test"}},
        {"id": "ch01", "kind": "chart", "pose": "teaching", "chart": {
            "title": "Public accounts by decade", "data": [["1830s", 2], ["1850s", 4], ["1880s", 9]],
            "credit": "Illustrative mock data",
        }},
        {"id": "x01", "kind": "excerpt", "pose": "reading", "para": 4,
         "text": "I grew up in the church and I loved it, but [...] nobody told me about the stone in the hat until I was thirty.",
         "_excerpt_attribution": "The Capybara Gazette · \u201cA Reporter's Story\u201d · Sep 1, 2026"},
    ]
    return beats, portrait, landscape


def _mock_caption(theme: Theme, img: Image.Image, mode: str, style_name: str) -> None:
    from PIL import ImageFont
    text = "some former-member creators lead with something"
    style = theme.caption_style(style_name)
    zone = theme.caption_zone(mode)
    font_path = theme.font_path(style["font"])
    measure_font = ImageFont.truetype(str(font_path), style["size"])
    words = text.split()
    fake_words = [{"w": w, "s": i * 0.3, "e": i * 0.3 + 0.25} for i, w in enumerate(words)]
    phrases = group_phrases(fake_words, style="Capy", highlight=[words[2]],
                             measure=measure_font.getlength, max_width=zone.max_width)
    if not phrases:
        return
    phrase = phrases[0]
    font, lines = fit_text(phrase.text, font_path, size=style["size"], min_size=style["min_size"],
                            step=theme.data["captions"]["shrink_step"], max_w=zone.max_width,
                            max_lines=theme.data["captions"]["max_lines"], stroke=style["stroke_px"])
    pill = style.get("pill")
    pill_color = theme.color_rgba(pill["color"], pill["alpha"]) if pill else None
    draw_lines(img, lines, font, zone, fill=theme.color_rgba(style["primary"]), stroke_px=style["stroke_px"],
               stroke_fill=theme.color_rgba(style["outline"]), line_height_mult=theme.data["captions"]["line_height"],
               highlight_words={words[2]}, highlight_color=theme.color_rgba(theme.data["captions"]["highlight_color"]),
               pill=pill, pill_color=pill_color)


def run_mock(out_dir: Path | None) -> int:
    theme = Theme.load()
    mock_dir = out_dir or theme.cache_dir("mock")
    mock_dir.mkdir(parents=True, exist_ok=True)
    beats, portrait, landscape = _mock_beats(mock_dir)

    labeled: list[tuple[str, Image.Image]] = []
    variants: list[tuple[str, Image.Image]] = []
    for beat in beats:
        frame_path = beat.pop("_mock_frame", None)
        preview_frame = Image.open(frame_path).convert("RGBA") if frame_path else None
        img = render_plate(beat, theme, project_dir=mock_dir, freeze_frame=preview_frame, preview_video_frame=preview_frame)
        mode = theme.mode_for(beat)
        style_name = "style_source" if mode == "clip" else ("style_card" if mode == "card" else "style_capy")
        _mock_caption(theme, img, mode, style_name)
        name = f"mock_{beat['id']}.png"
        img.save(mock_dir / name)
        labeled.append((f"{beat['id']} ({beat['kind']}, {mode})", img))
        print(f"wrote {name}  [{mode}]")

    # LANCZOS/NEAREST/BOX sprite resampling comparison triptych: crop the
    # neutral pose to its alpha bbox and scale it the same way
    # capy.sprites.render_sprite does, once per resample filter, so the
    # cache/outline/shadow logic isn't duplicated here -- just the resize.
    from capy.sprites import _alpha_bbox_crop
    src = Image.open(theme.finalized_sprite_path("neutral")).convert("RGBA")
    cropped = _alpha_bbox_crop(src)
    spec = theme.sprite_spec("host")
    box_size = spec.box[2] - spec.box[0]
    ratio = box_size / max(cropped.width, cropped.height)
    new_size = (max(1, round(cropped.width * ratio)), max(1, round(cropped.height * ratio)))
    for resample_name, resample in (("LANCZOS", Image.LANCZOS), ("NEAREST", Image.NEAREST), ("BOX", Image.BOX)):
        variants.append((resample_name, cropped.resize(new_size, resample)))
    triptych = contact_sheet(variants, cols=3, cell=400, pad=20, label_h=32)
    triptych.save(mock_dir / "mock_sprite_resample.png")
    print("wrote mock_sprite_resample.png (LANCZOS/NEAREST/BOX comparison)")

    sheet = contact_sheet(labeled, cols=3, cell=360, pad=20, label_h=32)
    sheet_path = mock_dir / "storyboard.png"
    sheet.save(sheet_path)
    print(f"\nWrote {sheet_path} and {len(labeled)} individual mock_<id>.png files under {mock_dir}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", type=Path, default=None)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--out", type=Path, default=None, help="--mock only: output directory")
    args = ap.parse_args()

    if args.mock:
        return run_mock(args.out)

    if not args.project:
        ap.error("--project is required unless --mock is given")

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

    excerpt_attribution = None
    if any(b.get("kind") == "excerpt" for b in doc.get("beats", [])):
        try:
            from capy.source import load_source_info, attribution_line
            _info = load_source_info(project)
            excerpt_attribution = lambda beat: attribution_line(_info, cite_byline=bool(beat.get("cite_byline")))
        except Exception:
            excerpt_attribution = None

    labeled: list[tuple[str, Image.Image]] = []
    beats_list = doc.get("beats", [])
    for beat in beats_list:
        preview_frame = None
        freeze_frame = None
        if beat.get("kind") == "clip":
            preview_frame = extract_clip_frame(source_video, beat.get("start", 0.0))
        elif beat.get("stage") == "freeze":
            for prev in reversed(beats_list[:beats_list.index(beat)]):
                if prev.get("kind") == "clip":
                    freeze_frame = extract_clip_frame(source_video, prev.get("end", 0.0) - 0.1)
                    break
        beat_for_render = beat
        if beat.get("kind") == "excerpt" and excerpt_attribution is not None:
            beat_for_render = dict(beat)
            beat_for_render["_excerpt_attribution"] = excerpt_attribution(beat)
        plate = render_plate(beat_for_render, theme, project_dir=project, freeze_frame=freeze_frame,
                              sensitive=sensitive, preview_video_frame=preview_frame)
        labeled.append((f"{beat['id']} ({beat['kind']}, {per_beat.get(beat['id'],0):.1f}s)", plate))

    sheet = contact_sheet(labeled, cols=args.cols, cell=360, pad=20, label_h=32)
    frames_dir = project / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    sheet_path = frames_dir / "storyboard.png"
    sheet.save(sheet_path, format="PNG")
    print(f"Wrote {sheet_path}")

    script_md = render_script_md(doc, per_beat, total, project)
    script_path = project / "script" / "script.md"
    script_path.write_text(script_md, encoding="utf-8")
    print(f"Wrote {script_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
