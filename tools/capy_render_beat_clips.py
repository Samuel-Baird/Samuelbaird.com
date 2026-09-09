#!/usr/bin/env python3
"""**TEST / EXPERIMENTAL — hybrid Resolve pipeline, revised approach
(2026-09-09).** See docs/saint-capybara/hybrid-resolve-pipeline.md.

Renders one self-contained MP4 per beat (`frames/beat_<id>.mp4`) by
compositing, with ffmpeg: the beat's plate (chrome: background, sprite,
card/chart/evidence, wordmark -- from capy_beat_plates.py), its caption
phrase stills (from capy_caption_cards.py) timed with `enable=` windows,
and its audio (the trimmed source clip's own audio for `clip` beats,
`audio/<id>.norm.wav` for narration-family beats).

**Why this replaces the original per-still-track Resolve plan:** placing
each of a project's ~70-90 individual caption stills (plus ~15-18 plates)
as separate Media Pool imports and timeline placements turned out to be
extremely call-heavy through the davinci-resolve MCP (Resolve also
auto-detects sequentially-numbered same-prefix PNGs as an image
*sequence* rather than individual stills -- worth adding to
docs/resolve-mcp-gotchas.md -- so even importing them needed one MCP call
per file). Pre-compositing each beat into one flattened clip collapses
the Resolve side back down to one import + one timeline placement per
*beat* (matching the plate count, not the caption count), while the
actual Resolve timeline still holds real, reorderable/trimmable clips a
human editor can adjust afterward -- it just means the source clip's
region and the caption overlay are pre-baked per beat instead of kept as
separate live Resolve layers.

Usage:
    python capy_render_beat_clips.py --project D:\\Videos\\<slug> [--only id,id]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from capy.beats import load_beats
from capy.layout import Theme

HEAD_PAD_SECONDS = 0.25


def ffprobe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def render_beat_clip(beat: dict, project: Path, plate_path: Path, captions: list[dict], theme: Theme, out_path: Path) -> float:
    kind = beat["kind"]
    w, h = theme.canvas_size
    fps = theme.fps
    stage_box = theme.stage_box()
    sx0, sy0, sx1, sy1 = stage_box
    sw, sh = sx1 - sx0, sy1 - sy0

    inputs: list[str] = []
    filter_parts: list[str] = []
    audio_map: list[str] = []

    if kind == "clip":
        start, end = beat["start"], beat["end"]
        duration = (end - start) / (beat.get("speed", 1.0) or 1.0)
        audio_offset = 0.0
        source = project / "source" / "source.mp4"
        inputs += ["-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(source)]
        inputs += ["-loop", "1", "-t", f"{duration:.3f}", "-i", str(plate_path)]
        # Background canvas + scaled/cropped source video positioned into the stage box, plate on top (its stage region is a transparent hole).
        filter_parts.append(f"color=c=black:s={w}x{h}:d={duration:.3f}[bg]")
        filter_parts.append(
            f"[0:v]scale={sw}:{sh}:force_original_aspect_ratio=increase,crop={sw}:{sh},setsar=1,fps={fps}[vid]"
        )
        filter_parts.append(f"[bg][vid]overlay={sx0}:{sy0}[base0]")
        filter_parts.append("[1:v]format=rgba[plate0]")
        filter_parts.append("[base0][plate0]overlay=0:0:format=auto[capbase0]")
        audio_map = ["-map", "0:a"]
    else:
        # Use the loudness-normalized wav but trim back the head/tail pad
        # for assembly -- in a single hard-cut track, that padding is just
        # ~0.5s of dead air per beat that pushed the whole video over the
        # 180s ceiling budgeted without it (capy_resolve_build_plan.py's
        # estimate uses the un-padded duration). The standalone
        # audio/<id>.norm.wav file (with its pad) is left alone for anyone
        # who wants it standalone; only the beat-clip copy is trimmed.
        wav = project / "audio" / f"{beat['id']}.norm.wav"
        padded_duration = ffprobe_duration(wav)
        duration = padded_duration - 2 * HEAD_PAD_SECONDS
        audio_offset = 0.0
        inputs += ["-loop", "1", "-t", f"{duration:.3f}", "-i", str(plate_path)]
        inputs += ["-i", str(wav)]
        filter_parts.append(f"[0:v]format=rgba,fps={fps}[capbase0]")
        filter_parts.append(
            f"[1:a]atrim=start={HEAD_PAD_SECONDS}:end={padded_duration - HEAD_PAD_SECONDS},asetpts=PTS-STARTPTS[aout]"
        )
        audio_map = ["-map", "[aout]"]

    # Chain caption overlays, each windowed with enable=.
    cap_input_start = len(inputs) // 2 if False else None  # placeholder, computed below
    n_media_inputs = 2 if kind == "clip" else 2
    cap_first_index = 2  # inputs[0]=source or plate, inputs[1]=plate or audio -- see below per-branch indices
    if kind == "clip":
        cap_first_index = 2  # 0=source video(+audio), 1=plate
    else:
        cap_first_index = 2  # 0=plate, 1=audio(no video stream)

    label = "capbase0"
    for i, cap in enumerate(captions):
        idx = cap_first_index + i
        inputs += ["-loop", "1", "-t", f"{duration:.3f}", "-i", str(project / cap["path"])]
        cs, ce = cap["start"] + audio_offset, cap["end"] + audio_offset
        next_label = f"capbase{i + 1}"
        filter_parts.append(
            f"[{idx}:v]format=rgba[cap{i}]; "
            f"[{label}][cap{i}]overlay=0:0:enable='between(t,{cs:.3f},{ce:.3f})'[{next_label}]"
        )
        label = next_label

    filter_complex = ";".join(filter_parts)
    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filter_complex,
        "-map", f"[{label}]", *audio_map,
        "-t", f"{duration:.3f}",
        "-r", str(fps), "-pix_fmt", "yuv420p",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k",
        "-map_metadata", "-1",
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ffmpeg command:\n{' '.join(cmd)}\n", file=sys.stderr)
        print(result.stderr[-4000:], file=sys.stderr)
        raise RuntimeError(f"ffmpeg failed for beat {beat['id']}")
    return duration


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--only", type=str, default=None)
    args = ap.parse_args()

    project = args.project.resolve()
    doc = load_beats(project / "script" / "beats.yaml")
    only = set(args.only.split(",")) if args.only else None
    theme = Theme.load()

    plates_manifest = {m["id"]: m for m in json.loads((project / "frames" / "plates_manifest.json").read_text(encoding="utf-8"))}
    captions_manifest = json.loads((project / "captions" / "manifest.json").read_text(encoding="utf-8"))
    captions_by_beat: dict[str, list] = {}
    for c in captions_manifest:
        captions_by_beat.setdefault(c["beat_id"], []).append(c)
    for lst in captions_by_beat.values():
        lst.sort(key=lambda c: c["start"])

    out_dir = project / "frames"
    manifest = []
    for beat in doc["beats"]:
        bid = beat["id"]
        if only and bid not in only:
            continue
        plate = plates_manifest.get(bid)
        if not plate:
            print(f"skip {bid}: no plate rendered", file=sys.stderr)
            continue
        plate_path = project / plate["path"]
        captions = captions_by_beat.get(bid, [])
        out_path = out_dir / f"beat_{bid}.mp4"
        duration = render_beat_clip(beat, project, plate_path, captions, theme, out_path)
        manifest.append({"id": bid, "kind": beat["kind"], "path": str(out_path.relative_to(project)), "duration": round(duration, 3)})
        print(f"{bid}: {duration:.2f}s -> {out_path.name} ({len(captions)} caption windows)")

    manifest_path = out_dir / "beat_clips_manifest.json"
    if only and manifest_path.exists():
        existing = {m["id"]: m for m in json.loads(manifest_path.read_text(encoding="utf-8"))}
        for m in manifest:
            existing[m["id"]] = m
        manifest = list(existing.values())
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\n{len(manifest)} beat clip(s) written. Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
