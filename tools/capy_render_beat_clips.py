#!/usr/bin/env python3
"""Renders one self-contained MP4 per beat (frames/beat_<id>.mp4) by
compositing, with ffmpeg: the beat's plate (chrome: background/vignette,
sprite, card/chart/evidence/excerpt -- from capy_beat_plates.py), its
caption phrase stills (from capy_caption_cards.py) timed with `enable=`
windows, and its audio (the trimmed source clip's own audio, two-pass
loudness-matched to the same target as narration -- see
measure_loudnorm() -- for `clip` beats; audio/<id>.norm.wav for
narration-family beats).

CLIP-mode beats: the source video fills the whole 1080x1920 canvas. A
9:16-or-narrower source is cover-scaled + center-cropped; a
16:9-or-wider source is letterboxed inside theme.layout.clip.letterbox_band
over a blurred, darkened cover copy of the same footage (never plain
black bars). The plate (transparent except the sprite) is overlaid on
top. See docs/saint-capybara/hybrid-resolve-pipeline.md.

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

from capy.banner import BANNER_FILENAME, banner_beat_ids, render_banner
from capy.beats import load_beats
from capy.layout import Theme

HEAD_PAD_SECONDS = 0.25


def measure_loudnorm(source: Path, start: float, end: float, target_lufs: float) -> dict:
    """First pass of a two-pass loudnorm on a trimmed audio span -- returns
    ffmpeg's measured_* stats for measure_loudnorm_filter() to apply on the
    real render. Mirrors capy_tts.py's two-pass narration normalization
    (2026-09-09: clip-beat audio was previously left raw/un-normalized,
    which made the reacted-to source noticeably quieter than the
    loudness-matched narration -- see hybrid-resolve-pipeline.md "Audio
    consistency")."""
    cmd = [
        "ffmpeg", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(source),
        "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11:print_format=json",
        "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    stderr = result.stderr
    start_i = stderr.rfind("{")
    end_i = stderr.rfind("}")
    if start_i == -1 or end_i == -1:
        raise RuntimeError(f"loudnorm measurement pass produced no stats for {source} [{start}, {end}]")
    return json.loads(stderr[start_i:end_i + 1])


def loudnorm_apply_filter(stats: dict, target_lufs: float) -> str:
    """Second-pass loudnorm filter string using measure_loudnorm()'s stats."""
    return (
        f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11:"
        f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
        f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']}:linear=true:print_format=summary"
    )


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


def render_beat_clip(beat: dict, project: Path, plate_path: Path, captions: list[dict], theme: Theme, out_path: Path, *, video_bg_start: float | None = None, banner_path: Path | None = None) -> float:
    kind = beat["kind"]
    w, h = theme.canvas_size
    fps = theme.fps

    inputs: list[str] = []
    filter_parts: list[str] = []
    audio_map: list[str] = []

    if theme.mode_for(beat) == "host" and beat.get("stage") == "video":
        # "Capybara in front of the reacted video" -- the source video
        # keeps playing (not a frozen frame) behind the big HOST-mode
        # sprite, same blur/dim treatment as stage:freeze. bg_start is
        # `beat.background_start` if given, else the caller passes the
        # most recent preceding clip beat's end (video_bg_start) so this
        # naturally continues where the last clip left off. Loops if the
        # narration runs longer than the remaining source video.
        bg_start = beat.get("background_start")
        if bg_start is None:
            bg_start = video_bg_start
        wav = project / "audio" / f"{beat['id']}.norm.wav"
        padded_duration = ffprobe_duration(wav)
        duration = padded_duration - 2 * HEAD_PAD_SECONDS
        source = project / "source" / "source.mp4"
        sw, sh = ffprobe_size(source)
        inputs += ["-ss", f"{bg_start:.3f}", "-stream_loop", "-1", "-i", str(source)]
        inputs += ["-loop", "1", "-t", f"{duration:.3f}", "-i", str(plate_path)]
        inputs += ["-i", str(wav)]
        spec = theme.freeze_spec()
        filter_parts.append(
            f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps={fps},"
            f"gblur=sigma={spec['blur_sigma']},drawbox=c=black@{spec['dim']}:t=fill[vidbg]"
        )
        filter_parts.append("[1:v]format=rgba[plate0]")
        filter_parts.append("[vidbg][plate0]overlay=0:0:format=auto[capbase0]")
        filter_parts.append(
            f"[2:a]atrim=start={HEAD_PAD_SECONDS}:end={padded_duration - HEAD_PAD_SECONDS},asetpts=PTS-STARTPTS[aout]"
        )
        audio_map = ["-map", "[aout]"]
    elif kind == "clip":
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

        # Loudness-match the reacted-to clip's own audio to the same
        # target as narration (theme.yaml: audio.target_lufs) -- see
        # measure_loudnorm()'s docstring. Two-pass: measure the trimmed
        # span first, then apply as a real filter_complex stage (not a
        # bare -filter:a) so it composes with atempo when speed != 1.0.
        target_lufs = theme.data.get("audio", {}).get("target_lufs", -16)
        stats = measure_loudnorm(source, start, end, target_lufs)
        audio_chain = f"[0:a]{loudnorm_apply_filter(stats, target_lufs)}"
        if speed != 1.0:
            audio_chain += f",atempo={speed:.6f}"
        filter_parts.append(f"{audio_chain}[aout]")
        audio_map = ["-map", "[aout]"]
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

    # Chain caption overlays, each windowed with enable=. The clip and
    # narration-family branches each declare exactly 2 media inputs
    # (source+plate, or plate+wav); the stage:video branch declares 3
    # (source+plate+wav) -- caption PNGs start right after however many
    # -i flags the branch above actually used (NOT len(inputs): -ss/-to/
    # -loop/-t tokens share the list with -i and would over-count it).
    cap_first_index = inputs.count("-i")
    label = "capbase0"
    if banner_path is not None:
        # "RESPONSE INCOMING" -- whole beat (the caller only passes it for
        # the leading run of clip beats), under the captions.
        inputs += ["-loop", "1", "-t", f"{duration:.3f}", "-i", str(banner_path)]
        filter_parts.append(
            f"[{cap_first_index}:v]format=rgba[banner]; [{label}][banner]overlay=0:0[capbanner]"
        )
        label = "capbanner"
        cap_first_index += 1
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
    banner_ids = banner_beat_ids(doc)
    banner_path = render_banner(theme, out_dir / BANNER_FILENAME) if banner_ids else None
    manifest = []
    last_clip_end: float | None = None
    for beat in doc["beats"]:
        bid = beat["id"]
        if beat.get("kind") == "clip":
            last_clip_end = beat.get("end")

        if only and bid not in only:
            continue
        plate = plates_manifest.get(bid)
        if not plate:
            print(f"skip {bid}: no plate rendered", file=sys.stderr)
            continue
        plate_path = project / plate["path"]
        captions = captions_by_beat.get(bid, [])
        out_path = out_dir / f"beat_{bid}.mp4"
        duration = render_beat_clip(beat, project, plate_path, captions, theme, out_path, video_bg_start=last_clip_end,
                                   banner_path=banner_path if bid in banner_ids else None)
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
