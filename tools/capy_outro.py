#!/usr/bin/env python3
"""Render the mandatory sign-of-the-cross outro (docs/saint-capybara/brand.md
sec 5a) ONCE and cache it, so per-project builds copy a shared
frames/beat_outro.mp4 instead of re-running TTS + compositing for four
beats that are byte-identical (apart from Kokoro's non-deterministic
waveform) across every video.

    python tools/capy_outro.py --build [--force] [--voice am_michael] [--speed 0.95]
    python tools/capy_outro.py --verify
    python tools/capy_outro.py --print-key
    python tools/capy_outro.py --gc

Cache location: theme.cache_dir("outro") / <key16> / (outro.mp4,
manifest.json, inputs.json, and a mini "project/" with the intermediate
wav/timing/plate/caption files, kept for debugging).

`key` is a sha256 of every input that could change the rendered pixels or
audio: voice+speed, the five beats' text/pose, the full layout/captions/
card_text theme blocks, font+sprite file hashes, the audio block, and
this tool's own RENDERER_VERSION (bump when the outro-affecting code
changes in a way theme.layout.version doesn't already capture).

Consumers: capy_render_beat_clips.py calls ensure_cached_outro() and
copies the result into frames/beat_outro.mp4 -- see that module's
_handle_fixed_outro(). capy_tts.py / capy_beat_plates.py /
capy_caption_cards.py skip the five fixed beats by default (matched via
capy.beats.is_fixed_outro) and only render them when THIS tool invokes
them with --render-fixed-outro, against the mini project below.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from capy.beats import OUTRO_BEATS, DEFAULT_VOICE, dump_beats
from capy.layout import Theme

REPO_ROOT = Path(__file__).resolve().parent.parent
RENDERER_VERSION = 1

ENCODE_PARAMS = {"crf": 18, "preset": "medium", "audio_bitrate": "192k"}


@dataclass
class OutroEntry:
    key: str
    mp4: Path
    duration: float
    beats: list[str]


def _cache_inputs(theme: Theme, voice: str, speed: float, beats: list[dict]) -> dict:
    return {
        "schema": 1,
        "tool_version": RENDERER_VERSION,
        "layout_version": theme.layout_version,
        "voice": voice,
        "speed": speed,
        "beats": [{"id": b["id"], "pose": b["pose"], "text": b["text"]} for b in beats],
        "canvas": theme.layout["canvas"],
        "layout_host": theme.layout["host"],
        "layout_platform_safe": theme.layout["platform_safe"],
        "layout_sprite_bottom": theme.layout["sprite_bottom"],
        "captions": theme.data["captions"],
        "card_text": theme.data["card_text"],
        "palette": {k: v for k, v in theme.data["palette"].items() if isinstance(v, str)},
        "fonts": {"display": theme.font_hash("display"), "body": theme.font_hash("body")},
        "sprites": {pose: theme.sprite_hash(pose) for pose in [b["pose"] for b in beats]},
        "audio": theme.data["audio"],
        "encode": ENCODE_PARAMS,
    }


def outro_key(doc: dict | None, theme: Theme, *, voice: str | None = None, speed: float | None = None) -> tuple[str, str, float, list[dict]]:
    """Returns (key16, voice, speed, beats) for either a project's doc
    (its trailing 4 fixed beats + doc['voice']) or the global defaults
    when doc is None."""
    if doc is not None:
        tail = doc["beats"][-4:]
        v = voice or doc.get("voice", DEFAULT_VOICE)["name"]
        s = speed if speed is not None else doc.get("voice", DEFAULT_VOICE)["speed"]
        beats = tail
    else:
        v = voice or DEFAULT_VOICE["name"]
        s = speed if speed is not None else DEFAULT_VOICE["speed"]
        beats = OUTRO_BEATS
    inputs = _cache_inputs(theme, v, s, beats)
    digest = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    return digest, v, s, beats


def _run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(" ".join(cmd), file=sys.stderr)
        print(result.stderr[-4000:], file=sys.stderr)
        raise RuntimeError(f"command failed: {cmd[1]}")


def build(theme: Theme, *, voice: str | None, speed: float | None, force: bool = False) -> OutroEntry:
    key, v, s, beats = outro_key(None, theme, voice=voice, speed=speed)
    cache_dir = theme.cache_dir("outro") / key
    mp4_path = cache_dir / "outro.mp4"
    manifest_path = cache_dir / "manifest.json"
    if mp4_path.exists() and manifest_path.exists() and not force:
        m = json.loads(manifest_path.read_text(encoding="utf-8"))
        print(f"outro cache already built at key {key}, skipping (--force to rebuild)")
        return OutroEntry(key=key, mp4=mp4_path, duration=m["total_duration"], beats=[b["id"] for b in beats])

    mini = cache_dir / "project"
    for sub in ("script", "audio", "captions", "frames"):
        (mini / sub).mkdir(parents=True, exist_ok=True)

    doc = {
        "version": 1, "slug": f"outro-cache-{key}", "title": "Sign-of-the-cross outro (cached)",
        "hook": None, "summary": None,
        "format": {"width": 1080, "height": 1920, "fps": 30, "min_seconds": 0, "max_seconds": 3600},
        "voice": {"name": v, "speed": s},
        "voices": {}, "sensitive": False, "music": None, "tags": [],
        "beats": [dict(b) for b in beats],
    }
    dump_beats(doc, mini / "script" / "beats.yaml")

    tools_dir = REPO_ROOT / "tools"
    py = sys.executable
    _run([py, str(tools_dir / "capy_tts.py"), "--project", str(mini), "--render-fixed-outro"])
    _run([py, str(tools_dir / "capy_beat_plates.py"), "--project", str(mini), "--render-fixed-outro"])
    _run([py, str(tools_dir / "capy_caption_cards.py"), "--project", str(mini), "--render-fixed-outro"])
    _run([py, str(tools_dir / "capy_render_beat_clips.py"), "--project", str(mini), "--render-fixed-outro"])

    clip_manifest = json.loads((mini / "frames" / "beat_clips_manifest.json").read_text(encoding="utf-8"))
    by_id = {m["id"]: m for m in clip_manifest}
    ordered_paths = [mini / by_id[b["id"]]["path"] for b in beats]
    for p in ordered_paths:
        if not p.exists():
            raise RuntimeError(f"expected beat clip missing: {p}")

    concat_list = cache_dir / "concat.txt"
    concat_list.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in ordered_paths) + "\n", encoding="utf-8")
    _run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c:v", "libx264", "-crf", str(ENCODE_PARAMS["crf"]), "-preset", ENCODE_PARAMS["preset"],
        "-c:a", "aac", "-b:a", ENCODE_PARAMS["audio_bitrate"],
        "-map_metadata", "-1", "-fflags", "+bitexact", "-flags:v", "+bitexact", "-flags:a", "+bitexact",
        str(mp4_path),
    ])

    total = sum(by_id[b["id"]]["duration"] for b in beats)
    manifest = {
        "key": key, "voice": v, "speed": s,
        "beats": [{"id": b["id"], "duration": by_id[b["id"]]["duration"]} for b in beats],
        "total_duration": round(total, 3),
        "renderer_version": RENDERER_VERSION,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (cache_dir / "inputs.json").write_text(json.dumps(_cache_inputs(theme, v, s, beats), indent=2), encoding="utf-8")

    _run([py, str(tools_dir / "capy_storyboard.py"), "--project", str(mini)])

    print(f"built outro cache at key {key}: {mp4_path} ({total:.2f}s)")
    return OutroEntry(key=key, mp4=mp4_path, duration=round(total, 3), beats=[b["id"] for b in beats])


def ensure_cached_outro(doc: dict, theme: Theme, *, auto_build: bool = True) -> OutroEntry:
    key, v, s, beats = outro_key(doc, theme)
    cache_dir = theme.cache_dir("outro") / key
    mp4_path = cache_dir / "outro.mp4"
    manifest_path = cache_dir / "manifest.json"
    if not (mp4_path.exists() and manifest_path.exists()):
        if not auto_build:
            raise RuntimeError(
                f"outro cache missing for key {key} (voice={v}@{s}) and --no-auto-build was set -- "
                f"run: python tools/capy_outro.py --build --voice {v} --speed {s}"
            )
        return build(theme, voice=v, speed=s, force=False)
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    return OutroEntry(key=key, mp4=mp4_path, duration=m["total_duration"], beats=[b["id"] for b in beats])


def verify(theme: Theme, key: str) -> bool:
    import subprocess as sp
    cache_dir = theme.cache_dir("outro") / key
    mp4_path = cache_dir / "outro.mp4"
    manifest_path = cache_dir / "manifest.json"
    ok = True
    if not mp4_path.exists():
        print(f"FAIL: {mp4_path} missing")
        return False
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = sp.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4_path)],
                     capture_output=True, text=True, check=True)
    actual = float(result.stdout.strip())
    if abs(actual - manifest["total_duration"]) > 0.1:
        print(f"FAIL: duration mismatch: manifest {manifest['total_duration']:.3f}s vs ffprobe {actual:.3f}s")
        ok = False
    else:
        print(f"OK: duration {actual:.3f}s matches manifest")

    tags = sp.run(["ffprobe", "-v", "error", "-show_entries", "format_tags", "-of", "json", str(mp4_path)],
                   capture_output=True, text=True, check=True)
    tag_data = json.loads(tags.stdout).get("format", {}).get("tags", {}) or {}
    allowed = {"title", "major_brand", "minor_version", "compatible_brands"}
    bad_tags = set(tag_data) - allowed
    if bad_tags:
        print(f"FAIL: unexpected mp4 tags: {bad_tags}")
        ok = False
    else:
        print("OK: mp4 tags within allow-list")

    try:
        from PIL import Image
        for png in cache_dir.rglob("*.png"):
            info = Image.open(png).info
            if info:
                print(f"FAIL: {png} carries metadata: {list(info.keys())}")
                ok = False
        print("OK: no PNG metadata found under the cache dir")
    except Exception as e:
        print(f"warning: PNG metadata scan skipped: {e}")

    recomputed_key, *_ = outro_key(None, theme, voice=manifest["voice"], speed=manifest["speed"])
    if recomputed_key != key:
        print(f"note: key recomputes to {recomputed_key} against current theme.yaml (was built at {key}) -- "
              "expected if layout/theme changed since this build; rebuild to pick it up.")
    else:
        print("OK: key recomputes identically against the current theme.yaml")

    return ok


def gc(theme: Theme, *, keep: set[str]) -> None:
    root = theme.cache_dir("outro")
    for child in root.iterdir():
        if child.is_dir() and child.name not in keep:
            shutil.rmtree(child)
            print(f"removed stale outro cache {child.name}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--verify", action="store_true", help="verify the cache for --key (or the current default voice/speed's key)")
    ap.add_argument("--print-key", action="store_true")
    ap.add_argument("--gc", action="store_true", help="delete every cached outro key except the current default's")
    ap.add_argument("--project", type=Path, default=None, help="compute the key from this project's voice/wording instead of the global default")
    ap.add_argument("--voice", type=str, default=None)
    ap.add_argument("--speed", type=float, default=None)
    ap.add_argument("--key", type=str, default=None)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    theme = Theme.load()
    doc = None
    if args.project:
        from capy.beats import load_beats
        doc = load_beats(args.project / "script" / "beats.yaml")

    if args.print_key:
        key, v, s, _ = outro_key(doc, theme, voice=args.voice, speed=args.speed)
        print(f"{key}  voice={v}@{s}")
        return 0

    if args.build:
        key, v, s, _ = outro_key(doc, theme, voice=args.voice, speed=args.speed)
        build(theme, voice=v, speed=s, force=args.force)
        return 0

    if args.verify:
        key = args.key
        if not key:
            key, *_ = outro_key(doc, theme, voice=args.voice, speed=args.speed)
        ok = verify(theme, key)
        return 0 if ok else 1

    if args.gc:
        key, *_ = outro_key(doc, theme, voice=args.voice, speed=args.speed)
        gc(theme, keep={key})
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
