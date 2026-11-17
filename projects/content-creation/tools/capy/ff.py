"""ffmpeg/ffprobe helpers shared by the Saint Capybara tooling.

Kept intentionally small: a subprocess runner that raises with full
stderr on failure, Windows-safe path escaping for ffmpeg filter-graph
string arguments (`subtitles=...`, `drawtext=fontfile=...`), and thin
wrappers around `ffprobe` for duration and container tags.

ffmpeg/ffprobe are assumed to be on PATH (verified: gyan full build
8.1.1, libass/drawtext/loudnorm/xfade/concat/overlay/libx264 present).
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path


class FFError(RuntimeError):
    pass


def run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    """Run an ffmpeg/ffprobe command, returning the CompletedProcess.

    Raises FFError with the full stderr on nonzero exit when check=True.
    """
    proc = subprocess.run(args, capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise FFError(
            f"command failed ({proc.returncode}): {' '.join(args)}\n--- stderr ---\n{proc.stderr}"
        )
    return proc


def ffpath(path: Path | str) -> str:
    """Escape a filesystem path for use inside an ffmpeg filter-graph
    string argument (e.g. `subtitles=<path>`, `drawtext=fontfile=<path>`).

    ffmpeg filter arguments are themselves parsed for `:` (option
    separator) and `\\` (escape char), which collides badly with Windows
    drive letters (`D:\\Videos\\...`) and backslash separators. The
    standard fix: convert backslashes to forward slashes (ffmpeg accepts
    forward slashes on Windows), escape any literal `:` after the drive
    letter as `\\:`, and wrap the whole thing so it can be embedded
    directly after `subtitles=` or `fontfile=`.
    """
    s = str(path).replace("\\", "/")
    # Escape drive-letter colon and any other colon (there normally isn't
    # another one, but be defensive).
    s = s.replace(":", "\\:")
    return s


def probe_duration(path: Path | str) -> float:
    """Return container duration in seconds via ffprobe."""
    proc = run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            str(path),
        ]
    )
    data = json.loads(proc.stdout)
    return float(data["format"]["duration"])


def probe_tags(path: Path | str) -> dict:
    """Return the container-level format tags dict (e.g. {'title': ...}).

    Used by capy_check_brand.py --mp4 to enforce the tag allow-list
    (title, major_brand, minor_version, compatible_brands only -- no
    `encoder`, no leaked metadata).
    """
    proc = run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format_tags",
            "-of", "json",
            str(path),
        ]
    )
    data = json.loads(proc.stdout)
    return data.get("format", {}).get("tags", {}) or {}


def probe_streams(path: Path | str) -> list[dict]:
    proc = run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "stream=index,codec_type,codec_name,width,height,sample_rate,channels",
            "-of", "json",
            str(path),
        ]
    )
    data = json.loads(proc.stdout)
    return data.get("streams", [])


def ebur128_summary(path: Path | str) -> dict | None:
    """Run the ebur128 loudness filter and parse the 'Integrated loudness'
    summary block ffmpeg prints to stderr. Returns None if parsing fails
    (used only as a QC helper, never load-bearing before Gate A)."""
    proc = run(
        ["ffmpeg", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
        check=False,
    )
    text = proc.stderr
    marker = "Integrated loudness:"
    idx = text.rfind(marker)
    if idx == -1:
        return None
    block = text[idx:idx + 300]
    out = {}
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("I:"):
            out["lufs"] = _first_float(line)
        elif line.startswith("LRA:"):
            out["lra"] = _first_float(line)
    return out or None


def _first_float(line: str) -> float | None:
    for tok in line.replace(":", " ").split():
        try:
            return float(tok)
        except ValueError:
            continue
    return None
