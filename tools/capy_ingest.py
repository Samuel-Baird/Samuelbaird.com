#!/usr/bin/env python3
"""Ingest a source video into a Saint Capybara project's source\\ folder.

Accepts either a URL (downloaded with yt_dlp) or an existing local file
path (copied in) for the media itself -- and, when a URL is given
(directly, or via --url alongside a local --file), always tries to pull
metadata (title/uploader/canonical url) via yt_dlp so citation/description
text has real attribution even when the media file was already downloaded
by other means.

    python tools/capy_ingest.py URL --project D:\\Videos\\<slug>
    python tools/capy_ingest.py --file "D:\\some\\local.mp4" --url URL --project D:\\Videos\\<slug>
    python tools/capy_ingest.py --file "D:\\some\\local.mp4" --project D:\\Videos\\<slug>  # no URL -- no metadata

Writes source\\source.mp4 (or a copy/link of the local file) and
source\\source_info.json (title, uploader, canonical url, duration, and
`media_from: "downloaded" | "local_file"`), then calls transcribe.py
unchanged (--skip-transcribe to skip).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capy import ff


def fetch_metadata(url: str) -> dict:
    """yt_dlp metadata-only extraction (no download)."""
    import yt_dlp

    opts = {"quiet": True, "skip_download": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {
        "title": info.get("title"),
        "uploader": info.get("uploader"),
        "canonical_url": info.get("webpage_url") or url,
        "upload_date": info.get("upload_date"),
        "duration": info.get("duration"),
        "id": info.get("id"),
    }


def download_media(url: str, dest: Path, max_height: int) -> None:
    import yt_dlp

    opts = {
        "outtmpl": str(dest.with_suffix(".%(ext)s")),
        "format": f"bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]",
        "merge_output_format": "mp4",
        "quiet": False,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    produced = dest.with_suffix(".mp4")
    if produced != dest and produced.exists():
        produced.rename(dest)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("url", nargs="?", default=None, help="source URL (downloaded if --file is not given)")
    ap.add_argument("--url", dest="url_opt", default=None, help="explicit URL for metadata, usable alongside --file")
    ap.add_argument("--file", type=Path, default=None, help="existing local media file to copy into source\\ instead of downloading")
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--max-height", type=int, default=1080)
    ap.add_argument("--model", default="small.en")
    ap.add_argument("--skip-transcribe", action="store_true")
    args = ap.parse_args()

    url = args.url or args.url_opt
    source_dir = args.project / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    dest_media = source_dir / "source.mp4"

    metadata: dict = {}
    media_from = None

    if args.file:
        if not args.file.exists():
            print(f"error: --file not found: {args.file}")
            return 1
        print(f"Copying local file into source\\: {args.file} -> {dest_media}")
        shutil.copy2(args.file, dest_media)
        media_from = "local_file"
    elif url:
        print(f"Downloading via yt_dlp: {url}")
        download_media(url, dest_media, args.max_height)
        media_from = "downloaded"
    else:
        print("error: provide a URL, --file, or both")
        return 1

    if url:
        try:
            print(f"Fetching metadata (no download) for: {url}")
            metadata = fetch_metadata(url)
        except Exception as e:
            print(f"warning: could not fetch metadata for {url}: {e}")
            metadata = {"canonical_url": url}

    if not dest_media.exists():
        print(f"error: expected media at {dest_media} after ingest, not found")
        return 1

    duration = None
    try:
        duration = ff.probe_duration(dest_media)
    except ff.FFError as e:
        print(f"warning: could not probe duration: {e}")

    info = {
        "media_from": media_from,
        "local_file_source": str(args.file) if args.file else None,
        "title": metadata.get("title"),
        "uploader": metadata.get("uploader"),
        "canonical_url": metadata.get("canonical_url") or url,
        "upload_date": metadata.get("upload_date"),
        "source_duration_seconds": duration if duration is not None else metadata.get("duration"),
    }
    info_path = args.project / "source" / "source_info.json"
    info_path.write_text(json.dumps(info, indent=2), encoding="utf-8")
    print(f"Wrote {info_path}:\n{json.dumps(info, indent=2)}")

    if not args.skip_transcribe:
        transcripts_dir = args.project / "transcripts"
        transcribe_script = Path(__file__).resolve().parent / "transcribe.py"
        cmd = [sys.executable, str(transcribe_script), str(dest_media), "--out-dir", str(transcripts_dir), "--model", args.model]
        print("Running:", " ".join(str(c) for c in cmd))
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"error: transcribe.py exited with code {result.returncode}")
            return result.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
