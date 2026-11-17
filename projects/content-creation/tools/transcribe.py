#!/usr/bin/env python3
"""Transcribe a source file with local Whisper and record what was used.

Wraps the ``whisper`` CLI (see ../docs/transcription.md for why this is the
default backend and not Resolve's built-in transcription or a hosted API).
Writes json/srt/txt into the target transcripts directory plus a sidecar
``<name>.meta.json`` recording the model, invocation time, and source
duration, so later pipeline stages know exactly what produced a transcript.

Usage:
    python transcribe.py SOURCE_AUDIO_OR_VIDEO --out-dir D:\\Videos\\<slug>\\transcripts
    python transcribe.py SOURCE_AUDIO_OR_VIDEO --out-dir ... --model small.en
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def probe_duration_seconds(source: Path) -> float | None:
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "csv=p=0",
                str(source),
            ],
            capture_output=True, text=True, check=True,
        )
        return float(result.stdout.strip())
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Audio or video file to transcribe")
    parser.add_argument("--out-dir", type=Path, required=True, help="transcripts/ folder")
    parser.add_argument("--model", default="small.en", help="Whisper model (default: small.en)")
    parser.add_argument(
        "--formats", default="json,srt,txt",
        help=(
            "Comma-separated formats to KEEP (default: json,srt,txt). "
            "The whisper CLI's --output_format only accepts one value at a "
            "time, so this script always runs with --output_format all "
            "(one transcription pass, every format written) and then "
            "deletes any output file whose format isn't in this list."
        ),
    )
    args = parser.parse_args()

    source = args.source.resolve()
    if not source.exists():
        print(f"error: source file not found: {source}", file=sys.stderr)
        return 1

    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    duration = probe_duration_seconds(source)
    started_at = datetime.now(timezone.utc).isoformat()
    wanted_formats = {f.strip() for f in args.formats.split(",") if f.strip()}

    cmd = [
        "whisper", str(source),
        "--model", args.model,
        "--word_timestamps", "True",
        "--output_format", "all",
        "--output_dir", str(out_dir),
    ]

    print("Running:", " ".join(f'"{c}"' if " " in c else c for c in cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"error: whisper exited with code {result.returncode}", file=sys.stderr)
        return result.returncode

    all_formats = {"txt", "vtt", "srt", "tsv", "json"}
    for fmt in all_formats - wanted_formats:
        stale = out_dir / f"{source.stem}.{fmt}"
        if stale.exists():
            stale.unlink()

    finished_at = datetime.now(timezone.utc).isoformat()
    meta = {
        "source": str(source),
        "source_duration_seconds": duration,
        "model": args.model,
        "formats": sorted(wanted_formats),
        "started_at": started_at,
        "finished_at": finished_at,
    }
    meta_path = out_dir / f"{source.stem}.meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Wrote metadata: {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
