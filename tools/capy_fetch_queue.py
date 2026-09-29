#!/usr/bin/env python3
"""Batch-download the Saint Capybara reaction queue's URL-only rows.

Reads `need reaction.xlsx` (columns `Link to original` / `Path` / ...,
see `docs/types/saint-capybara.md` "Source intake"), downloads every
Instagram/Facebook/YouTube row whose `Path` is empty or a previous
failure note, and writes the resulting local file path (or a failure
note) back into that row's `Path` cell. Run this when instructed --
it is not part of the per-project `capy_ingest.py` flow, which still
does the actual project ingest afterwards.

    python tools/capy_fetch_queue.py --dry-run
    python tools/capy_fetch_queue.py

Files are named `<prefix>-<id>.mp4` (prefix: ig/fb/yt) in --out-dir,
matching the existing `yt-<id>` slug convention documented in
`docs/types/saint-capybara.md`. A file already on disk is not
re-downloaded, and a duplicate URL (after normalizing the query string
away) is not downloaded twice.

Cookies: Instagram/Facebook require a logged-in session for most posts.
The first attempt is cookie-less; a login/rate-limit/private failure is
retried once with --cookies-browser (yt_dlp's BROWSER[:PROFILE] syntax,
default "chrome"). Chrome must be closed while its cookie DB is read (a
yt_dlp/Windows limitation). See docs/types/saint-capybara.md's batch
download section for anonymity/account-hygiene notes before using a
personal Chrome profile against this brand's content.

One failed row never stops the run -- it is caught, noted in `Path`, and
the script continues to the next row. The workbook is copied to
`need reaction.backup.xlsx` before any writes, and saved after every 5
rows so a crash doesn't lose progress.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DEFAULT_XLSX = r"D:\saint-capybara-videos-needing-reactions\need reaction.xlsx"
DEFAULT_OUT_DIR = r"D:\saint-capybara-videos-needing-reactions"

LINK_HEADER = "Link to original"
PATH_HEADER = "Path"

FAIL_PREFIX = "Download failed"
DUP_PREFIX = "Duplicate of row"

# host -> (platform prefix, id-extraction regexes tried in order)
PLATFORM_PATTERNS = {
    "instagram.com": ("ig", [
        r"instagram\.com/(?:[^/]+/)?(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)",
    ]),
    "facebook.com": ("fb", [
        r"facebook\.com/(?:[^/]+/)?videos/(\d+)",
        r"facebook\.com/reel/(\d+)",
        r"[?&]v=(\d+)",
    ]),
    "fb.watch": ("fb", []),  # short link -- id resolved via yt_dlp only
    "youtube.com": ("yt", [
        r"[?&]v=([A-Za-z0-9_-]{6,})",
        r"youtube\.com/shorts/([A-Za-z0-9_-]{6,})",
    ]),
    "youtu.be": ("yt", [
        r"youtu\.be/([A-Za-z0-9_-]{6,})",
    ]),
}


def host_of(url: str) -> str:
    try:
        netloc = urlsplit(url).netloc.lower()
    except Exception:
        return ""
    if netloc.startswith("www."):
        netloc = netloc[4:]
    if netloc.startswith("m."):
        netloc = netloc[2:]
    return netloc


def platform_for(url: str) -> str | None:
    host = host_of(url)
    for known_host, (prefix, _patterns) in PLATFORM_PATTERNS.items():
        if host == known_host or host.endswith("." + known_host):
            return prefix
    return None


def normalize_url(url: str) -> str:
    """Normalize a URL for duplicate detection: map youtu.be -> a
    youtube.com/watch?v= URL, then drop everything but scheme/host/path
    and, for a youtube watch URL, the `v` query param (so tracking
    params like &t=5s or &igsh=... don't defeat dedup, but two different
    videos never collapse into one)."""
    url = url.strip()
    parts = urlsplit(url)
    netloc = parts.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = parts.path.rstrip("/")
    if netloc == "youtu.be":
        vid = path.lstrip("/")
        return urlunsplit(("https", "youtube.com", "/watch", f"v={vid}", ""))
    if netloc == "youtube.com" and path == "/watch":
        m = re.search(r"(?:^|&)v=([^&]+)", parts.query)
        vid = m.group(1) if m else ""
        return urlunsplit(("https", netloc, path, f"v={vid}", ""))
    return urlunsplit(("https", netloc, path, "", ""))


def extract_id_by_regex(url: str, prefix: str) -> str | None:
    host = host_of(url)
    for known_host, (known_prefix, patterns) in PLATFORM_PATTERNS.items():
        if known_prefix != prefix:
            continue
        if not (host == known_host or host.endswith("." + known_host)):
            continue
        for pat in patterns:
            m = re.search(pat, url)
            if m:
                return m.group(1)
    return None


def is_queueable_row(url: str, path_value: str | None) -> bool:
    """Should this row be considered for download?"""
    if not url or not url.strip():
        return False
    if platform_for(url) is None:
        return False
    path_value = (path_value or "").strip()
    if not path_value:
        return True
    if path_value.startswith(FAIL_PREFIX):
        return True
    return False


def find_header_columns(ws) -> dict:
    headers = {}
    for cell in ws[1]:
        if cell.value:
            headers[str(cell.value).strip()] = cell.column
    missing = [h for h in (LINK_HEADER, PATH_HEADER) if h not in headers]
    if missing:
        raise SystemExit(
            f"error: '{ws.title}' header row is missing column(s): {', '.join(missing)}"
        )
    return headers


def load_yt_dlp():
    try:
        import yt_dlp  # noqa: F401
    except ImportError:
        raise SystemExit(
            "error: yt-dlp is not installed -- pip install -r tools/requirements.txt"
        )
    return yt_dlp


def build_opts(out_dir: Path, prefix: str, cookies_browser: str | None) -> dict:
    opts = {
        "outtmpl": str(out_dir / f"{prefix}-%(id)s.%(ext)s"),
        "format": "bestvideo*+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "retries": 3,
        "quiet": False,
    }
    if cookies_browser:
        # yt_dlp wants a tuple: (browser, profile, keyring, container)
        if ":" in cookies_browser:
            browser, profile = cookies_browser.split(":", 1)
            opts["cookiesfrombrowser"] = (browser, profile, None, None)
        else:
            opts["cookiesfrombrowser"] = (cookies_browser, None, None, None)
    return opts


NEEDS_COOKIES_MARKERS = (
    "login", "log in", "cookies", "rate-limit", "rate limit",
    "private", "restricted", "sign in",
)


def download_one(url: str, prefix: str, out_dir: Path, cookies_browser: str) -> tuple[bool, str]:
    """Returns (ok, path_or_error). Tries cookie-less first, then retries
    once with browser cookies if the failure looks auth/rate-limit related."""
    yt_dlp = load_yt_dlp()

    def _try(use_cookies: bool) -> tuple[bool, str]:
        opts = build_opts(out_dir, prefix, cookies_browser if use_cookies else None)
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
            vid = info.get("id") or "unknown"
            produced = out_dir / f"{prefix}-{vid}.mp4"
            if produced.exists():
                return True, str(produced)
            # yt_dlp may have merged to a different extension in edge cases
            for f in out_dir.glob(f"{prefix}-{vid}.*"):
                return True, str(f)
            return False, "downloaded but output file not found"
        except Exception as e:  # yt_dlp.DownloadError and friends
            return False, str(e)

    ok, result = _try(use_cookies=False)
    if ok:
        return ok, result
    if any(marker in result.lower() for marker in NEEDS_COOKIES_MARKERS):
        print(f"  retrying with browser cookies ({cookies_browser}): {result[:200]}")
        return _try(use_cookies=True)
    return ok, result


def existing_file_for(url: str, prefix: str, out_dir: Path) -> Path | None:
    guessed_id = extract_id_by_regex(url, prefix)
    if guessed_id:
        candidate = out_dir / f"{prefix}-{guessed_id}.mp4"
        if candidate.exists():
            return candidate
        return None
    # No regex match (e.g. fb.watch short link) -- fall back to a glob
    # scan only if there's exactly one file for this prefix that we can't
    # otherwise disambiguate; safer to just attempt the download and let
    # yt_dlp's own id resolve it, then check again post-hoc.
    return None


def run(args: argparse.Namespace) -> int:
    import openpyxl

    xlsx_path = Path(args.xlsx)
    out_dir = Path(args.out_dir)
    if not xlsx_path.exists():
        raise SystemExit(f"error: not found: {xlsx_path}")
    out_dir.mkdir(parents=True, exist_ok=True)

    if not args.dry_run:
        backup = xlsx_path.with_name(xlsx_path.stem + ".backup.xlsx")
        shutil.copy2(xlsx_path, backup)
        print(f"Backed up queue to: {backup}")
        try:
            with open(xlsx_path, "ab"):
                pass
        except PermissionError:
            raise SystemExit(
                f"error: {xlsx_path} is open in another program (Excel?) -- close it and re-run"
            )

    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active
    headers = find_header_columns(ws)
    link_col = headers[LINK_HEADER]
    path_col = headers[PATH_HEADER]

    seen_normalized: dict[str, int] = {}  # normalized url -> first row number
    stats = {"downloaded": 0, "already_present": 0, "duplicate": 0, "failed": 0, "skipped": 0}
    failures: list[tuple[int, str, str]] = []

    for row_idx, row in enumerate(ws.iter_rows(min_row=2), start=2):
        url_cell = row[link_col - 1]
        path_cell = row[path_col - 1]
        url = (url_cell.value or "").strip() if isinstance(url_cell.value, str) else ""
        path_value = path_cell.value

        if not is_queueable_row(url, path_value):
            stats["skipped"] += 1
            continue

        norm = normalize_url(url)
        if norm in seen_normalized:
            first_row = seen_normalized[norm]
            print(f"Row {row_idx}: duplicate of row {first_row} -- {url}")
            if not args.dry_run:
                path_cell.value = f"{DUP_PREFIX} {first_row}"
            stats["duplicate"] += 1
            continue
        seen_normalized[norm] = row_idx

        prefix = platform_for(url)
        existing = existing_file_for(url, prefix, out_dir)
        if existing:
            print(f"Row {row_idx}: already downloaded -- {existing}")
            if not args.dry_run:
                path_cell.value = str(existing)
            stats["already_present"] += 1
            continue

        if args.dry_run:
            print(f"Row {row_idx}: would download ({prefix}) -- {url}")
            stats["downloaded"] += 1
            continue

        print(f"Row {row_idx}: downloading ({prefix}) -- {url}")
        ok, result = download_one(url, prefix, out_dir, args.cookies_browser)
        if ok:
            print(f"  saved: {result}")
            path_cell.value = result
            stats["downloaded"] += 1
        else:
            note = f"{FAIL_PREFIX} {date.today().isoformat()}: {result[:180]}"
            print(f"  FAILED: {result}")
            path_cell.value = note
            stats["failed"] += 1
            failures.append((row_idx, url, result))

        if row_idx % 5 == 0:
            wb.save(xlsx_path)

    if not args.dry_run:
        wb.save(xlsx_path)

    print("\n--- Summary ---")
    for key in ("downloaded", "already_present", "duplicate", "failed", "skipped"):
        print(f"{key}: {stats[key]}")
    if failures:
        print("\nFailed rows:")
        for row_idx, url, err in failures:
            print(f"  row {row_idx}: {url}\n    {err[:200]}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--xlsx", default=DEFAULT_XLSX, help="path to need reaction.xlsx")
    ap.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="folder to download into")
    ap.add_argument("--cookies-browser", default="chrome",
                     help="yt_dlp --cookies-from-browser value, BROWSER or BROWSER:PROFILE (default: chrome)")
    ap.add_argument("--dry-run", action="store_true", help="print the plan without downloading or writing the sheet")
    args = ap.parse_args()
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
