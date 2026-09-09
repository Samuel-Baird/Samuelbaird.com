#!/usr/bin/env python3
"""Renders one full-canvas 1080x1920 RGBA "plate" PNG per beat in
script/beats.yaml (frames/plate_<id>.png), via capy.plates.render_plate.

CLIP-mode plates are transparent except the sprite layer -- the real
source clip is composited underneath by ffmpeg in
capy_render_beat_clips.py. HOST/CARD-mode plates are fully opaque
(parchment or full-bleed dimmed freeze-frame background, sprite, and any
card/chart/evidence/excerpt content).

For HOST beats with `stage: freeze`, a real frame is grabbed from the
source video at the timestamp of the most recently preceding `clip`
beat's end. Fixed sign-of-the-cross outro beats (outro-01..05) are
skipped by default -- see tools/capy_outro.py -- pass
--render-fixed-outro to render them anyway (used by capy_outro.py itself
when building the shared cache).

Usage:
    python capy_beat_plates.py --project D:\\Videos\\<slug> [--only id,id] [--clean]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image

from capy.beats import load_beats, is_fixed_outro
from capy.layout import Theme
from capy.plates import render_plate


def _excerpt_attribution(project: Path, beat: dict) -> str:
    try:
        from capy.source import load_source_info, attribution_line
        info = load_source_info(project)
        return attribution_line(info, cite_byline=bool(beat.get("cite_byline")))
    except Exception as e:
        print(f"warning: could not resolve excerpt attribution for {beat.get('id')}: {e}", file=sys.stderr)
        return ""


def grab_frame(source: Path, timestamp: float) -> Image.Image | None:
    """One PNG frame at `timestamp` seconds into `source`, via ffmpeg."""
    if not source.exists():
        return None
    import io
    cmd = [
        "ffmpeg", "-y", "-ss", f"{max(timestamp, 0.0):.3f}", "-i", str(source),
        "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"warning: frame grab failed at {timestamp:.2f}s: {e}", file=sys.stderr)
        return None
    return Image.open(io.BytesIO(result.stdout)).convert("RGBA")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--only", type=str, default=None, help="comma-separated beat ids")
    ap.add_argument("--clean", action="store_true", help="delete existing frames/plate_*.png and frames/beat_*.mp4 first")
    ap.add_argument("--render-fixed-outro", action="store_true", help="render outro-01..05 too (used by capy_outro.py)")
    args = ap.parse_args()

    project = args.project.resolve()
    beats_path = project / "script" / "beats.yaml"
    if not beats_path.exists():
        print(f"error: {beats_path} not found", file=sys.stderr)
        return 1

    doc = load_beats(beats_path)
    beats = doc["beats"]
    only = set(args.only.split(",")) if args.only else None

    source_video = project / "source" / "source.mp4"
    frames_dir = project / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    if args.clean:
        removed = 0
        for pattern in ("plate_*.png", "beat_*.mp4"):
            for p in frames_dir.glob(pattern):
                p.unlink()
                removed += 1
        print(f"--clean: removed {removed} stale file(s) from {frames_dir}")

    theme = Theme.load()
    sensitive = bool(doc.get("sensitive"))

    manifest = []
    last_clip_end: float | None = None
    frame_cache: dict[float, Image.Image | None] = {}

    for beat in beats:
        bid = beat["id"]
        kind = beat.get("kind")

        if kind == "clip":
            last_clip_end = beat.get("end")
            if only and bid not in only:
                continue
        else:
            if is_fixed_outro(beat) and not args.render_fixed_outro:
                continue
            if only and bid not in only:
                continue

        freeze_frame = None
        if beat.get("stage") == "freeze":
            if last_clip_end is None:
                print(f"warning: {bid} requests stage: freeze but no clip beat precedes it -- rendering blank "
                      "(this should have been caught by capy.beats.validate())", file=sys.stderr)
            else:
                if last_clip_end not in frame_cache:
                    frame_cache[last_clip_end] = grab_frame(source_video, last_clip_end)
                freeze_frame = frame_cache[last_clip_end]

        beat_for_render = beat
        if kind == "excerpt":
            beat_for_render = dict(beat)
            beat_for_render["_excerpt_attribution"] = _excerpt_attribution(project, beat)

        img = render_plate(
            beat_for_render, theme,
            project_dir=project,
            freeze_frame=freeze_frame,
            sensitive=sensitive,
        )
        out_path = frames_dir / f"plate_{bid}.png"
        img.save(out_path)
        manifest.append({"id": bid, "kind": kind, "path": str(out_path.relative_to(project)), "mode": theme.mode_for(beat)})
        print(f"wrote {out_path.name}  [{theme.mode_for(beat)}]")

    manifest_path = frames_dir / "plates_manifest.json"
    if only and manifest_path.exists():
        existing = {m["id"]: m for m in json.loads(manifest_path.read_text(encoding="utf-8"))}
        for m in manifest:
            existing[m["id"]] = m
        manifest = list(existing.values())
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\n{len(manifest)} plate(s) written. Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
