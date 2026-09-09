#!/usr/bin/env python3
"""Renders one self-contained MP4 per beat (frames/beat_<id>.mp4) by
compositing, with ffmpeg: the beat's plate (chrome: background/vignette,
sprite, card/chart/evidence/excerpt -- from capy_beat_plates.py), its
caption phrase stills (from capy_caption_cards.py) timed with `enable=`
windows, and its audio (the trimmed source clip's own audio for `clip`
beats, audio/<id>.norm.wav for narration-family beats).

CLIP-mode beats: the source video fills the whole 1080x1920 canvas. A
9:16-or-narrower source is cover-scaled + center-cropped; a
16:9-or-wider source is letterboxed inside theme.layout.clip.letterbox_band
over a blurred, darkened cover copy of the same footage (never plain
black bars). The plate (transparent except the sprite) is overlaid on
top. See docs/saint-capybara/hybrid-resolve-pipeline.md.

The five fixed sign-of-the-cross outro beats (outro-01..05) are rendered
once and cached -- see tools/capy_outro.py. This tool copies the cached
frames/beat_outro.mp4 into the project and writes one merged manifest
entry instead of re-rendering them, unless --render-fixed-outro is set
(used by capy_outro.py itself when building the cache) or --no-auto-build
is set (a missing cache then errors instead of silently re-rendering).

Usage:
    python capy_render_beat_clips.py --project D:\\Videos\\<slug> [--only id,id]
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from capy.beats import load_beats, is_fixed_outro
from capy.layout import Theme

HEAD_PAD_SECONDS = 0.25


def ffprobe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def ffprobe_size(path: Path) -> tuple[int, int]:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", str(path)],
        capture_output=True, text=True, check=True,
    )
    w, h = result.stdout.strip().split("x")
    return int(w), int(h)


def _fit(sw: int, sh: int, max_w: int, max_h: int) -> tuple[int, int]:
    ratio = min(max_w / sw, max_h / sh)
    fw = max(2, int(sw * ratio) // 2 * 2)
    fh = max(2, int(sh * ratio) // 2 * 2)
    return fw, fh


def render_beat_clip(beat: dict, project: Path, plate_path: Path, captions: list[dict], theme: Theme, out_path: Path) -> float:
    kind = beat["kind"]
    w, h = theme.canvas_size
    fps = theme.fps

    inputs: list[str] = []
    filter_parts: list[str] = []
    audio_map: list[str] = []

    if kind == "clip":
        start, end = beat["start"], beat["end"]
        speed = beat.get("speed", 1.0) or 1.0
        duration = (end - start) / speed
        source = project / "source" / "source.mp4"
        sw, sh = ffprobe_size(source)
        inputs += ["-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(source)]
        inputs += ["-loop", "1", "-t", f"{duration:.3f}", "-i", str(plate_path)]

        speed_vf = f",setpts=PTS/{speed:.6f}" if speed != 1.0 else ""
        if sw <= sh:
            # 9:16-or-narrower source: cover-crop the whole canvas.
            filter_parts.append(
                f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1{speed_vf},fps={fps}[vid]"
            )
        else:
            # 16:9-or-wider source: fit inside the letterbox band over a
            # blurred, darkened cover copy of the same footage (never
            # plain black bars) -- downscale/boxblur/upscale is far
            # cheaper than a full-resolution gblur.
            band_y0, band_y1 = theme.letterbox_band()
            band_h = band_y1 - band_y0
            fw, fh = _fit(sw, sh, w, band_h)
            fx, fy = (w - fw) // 2, band_y0 + (band_h - fh) // 2
            bg = theme.letterbox_bg()
            filter_parts.append(
                f"[0:v]fps={fps},setsar=1{speed_vf},split=2[bgsrc][fgsrc]"
            )
            filter_parts.append(
                f"[bgsrc]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
                f"scale={w//bg['blur_scale']}:{h//bg['blur_scale']},boxblur={bg['boxblur']},"
                f"scale={w}:{h}:flags=bicubic,drawbox=c=black@{bg['dim']}:t=fill[bg]"
            )
            filter_parts.append(f"[fgsrc]scale={fw}:{fh}:flags=lanczos[fg]")
            filter_parts.append(f"[bg][fg]overlay={fx}:{fy}[vid]")

        filter_parts.append("[1:v]format=rgba[plate0]")
        filter_parts.append("[vid][plate0]overlay=0:0:format=auto[capbase0]")
        if speed != 1.0:
            audio_map = ["-filter:a", f"atempo={speed:.6f}", "-map", "0:a"]
        else:
            audio_map = ["-map", "0:a"]
    else:
        # Use the loudness-normalized wav but trim back the head/tail pad
        # for assembly -- in a single hard-cut track, that padding is just
        # ~0.5s of dead air per beat. The standalone audio/<id>.norm.wav
        # file (with its pad) is left alone for anyone who wants it
        # standalone; only the beat-clip copy is trimmed.
        wav = project / "audio" / f"{beat['id']}.norm.wav"
        padded_duration = ffprobe_duration(wav)
        duration = padded_duration - 2 * HEAD_PAD_SECONDS
        inputs += ["-loop", "1", "-t", f"{duration:.3f}", "-i", str(plate_path)]
        inputs += ["-i", str(wav)]
        filter_parts.append(f"[0:v]format=rgba,fps={fps}[capbase0]")
        filter_parts.append(
            f"[1:a]atrim=start={HEAD_PAD_SECONDS}:end={padded_duration - HEAD_PAD_SECONDS},asetpts=PTS-STARTPTS[aout]"
        )
        audio_map = ["-map", "[aout]"]

    # Chain caption overlays, each windowed with enable=. Both branches
    # above declare exactly 2 media inputs (source+plate, or plate+wav),
    # so caption PNGs start at ffmpeg -i index 2 regardless of branch.
    cap_first_index = 2
    label = "capbase0"
    for i, cap in enumerate(captions):
        idx = cap_first_index + i
        inputs += ["-loop", "1", "-t", f"{duration:.3f}", "-i", str(project / cap["path"])]
        cs, ce = cap["start"], cap["end"]
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


def _handle_fixed_outro(doc: dict, project: Path, theme: Theme, *, auto_build: bool) -> dict:
    """Resolve (building if needed) the cached shared outro.mp4, copy it
    into frames/, and return the manifest entry for it."""
    from capy_outro import ensure_cached_outro  # local import: avoid a hard dependency for callers that never hit this path

    entry = ensure_cached_outro(doc, theme, auto_build=auto_build)
    out_dir = project / "frames"
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "beat_outro.mp4"
    shutil.copy2(entry.mp4, dest)
    return {
        "id": "outro", "kind": "outro",
        "beats": entry.beats,
        "path": str(dest.relative_to(project)),
        "duration": entry.duration,
        "cache_key": entry.key,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--only", type=str, default=None)
    ap.add_argument("--render-fixed-outro", action="store_true", help="render outro-01..05 individually instead of using the cache (used by capy_outro.py)")
    ap.add_argument("--no-auto-build", action="store_true", help="error instead of building the outro cache if it's missing")
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
    outro_handled = False
    for beat in doc["beats"]:
        bid = beat["id"]

        if is_fixed_outro(beat) and not args.render_fixed_outro:
            if only and "outro" not in only and bid not in only:
                continue
            if not outro_handled:
                entry = _handle_fixed_outro(doc, project, theme, auto_build=not args.no_auto_build)
                manifest.append(entry)
                print(f"outro: {entry['duration']:.2f}s -> {Path(entry['path']).name} (cached, key {entry['cache_key']})")
                outro_handled = True
            continue

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
