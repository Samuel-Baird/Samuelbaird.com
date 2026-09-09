#!/usr/bin/env python3
"""**TEST / EXPERIMENTAL — hybrid Resolve pipeline, not yet approved for
production use.** See docs/saint-capybara/hybrid-resolve-pipeline.md.

Renders one full-canvas 1080x1920 RGBA "plate" PNG per beat in
script/beats.yaml, for placement as a Resolve timeline still (on the track
directly above the raw source clip). Reuses capy.plates.render_plate,
which already draws the parchment background/vignette, stage content
(card/chart/evidence/freeze-frame), the bottom-left sprite (now sourced
from the finalized AI art, not the retired code-drawn renderer), the
beat-1 hook chip, and the bottom-right wordmark.

For `clip` beats, the stage rectangle is punched fully transparent
(`punch_stage_hole=True`) instead of drawing a placeholder or a
composited frame -- in the Resolve build, the real source clip sits on
its own track underneath this plate and shows through the hole. For
`narration`/`card`/`evidence`/`chart`/`outro` beats needing `stage:
freeze`, a real frame is grabbed from the source video at the timestamp
of the most recently preceding `clip` beat's end (via ffmpeg), matching
the "last clip frame, dimmed 45%" rule in script-format.md.

Usage:
    python capy_beat_plates.py --project D:\\Videos\\<slug> [--only id,id]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image

from capy.beats import load_beats
from capy.layout import Theme
from capy.plates import render_plate


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

    theme = Theme.load()
    sensitive = bool(doc.get("sensitive"))
    hook = doc.get("hook")

    manifest = []
    last_clip_end: float | None = None
    frame_cache: dict[float, Image.Image | None] = {}

    for i, beat in enumerate(beats):
        bid = beat["id"]
        if only and bid not in only:
            if beat.get("kind") == "clip":
                last_clip_end = beat.get("end")
            continue

        kind = beat.get("kind")
        clip_frame = None
        punch_hole = kind == "clip"

        if kind == "clip":
            last_clip_end = beat.get("end")
        elif beat.get("stage") == "freeze" and last_clip_end is not None:
            if last_clip_end not in frame_cache:
                frame_cache[last_clip_end] = grab_frame(source_video, last_clip_end)
            clip_frame = frame_cache[last_clip_end]

        beat_for_render = dict(beat)
        if i == 0 and hook:
            beat_for_render["_is_first"] = True
            beat_for_render["_hook"] = hook

        img = render_plate(
            beat_for_render, theme,
            project_dir=project,
            clip_frame=clip_frame,
            sensitive=sensitive,
            punch_stage_hole=punch_hole,
        )
        out_path = frames_dir / f"plate_{bid}.png"
        img.save(out_path)
        manifest.append({"id": bid, "kind": kind, "path": str(out_path.relative_to(project)), "punch_stage_hole": punch_hole})
        print(f"wrote {out_path.name}" + ("  [transparent stage hole]" if punch_hole else ""))

    import json
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
