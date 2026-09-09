#!/usr/bin/env python3
"""Ingest a source into a Saint Capybara project's source\\ folder.

Two source kinds (source_info.json `kind`):

VIDEO (default). Accepts either a URL (downloaded with yt_dlp) or an
existing local file path (moved in -- see note below) for the media itself -- and, when a
URL is given (directly, or via --url alongside a local --file), always
tries to pull metadata (title/uploader/canonical url) via yt_dlp so
citation/description text has real attribution even when the media file
was already downloaded by other means.

    python tools/capy_ingest.py URL --project D:\\Videos\\<slug>
    python tools/capy_ingest.py --file "D:\\some\\local.mp4" --url URL --project D:\\Videos\\<slug>
    python tools/capy_ingest.py --file "D:\\some\\local.mp4" --project D:\\Videos\\<slug>  # no URL -- no metadata

Writes source\\source.mp4 (moved from --file's local path, or downloaded) and
source\\source_info.json (kind, title, uploader, canonical url, duration,
and `media_from: "downloaded" | "local_file"`), then calls transcribe.py
unchanged (--skip-transcribe to skip).

ARTICLE (text source; plan Part 4.2). No media, no Whisper. The default
workflow is that the agent fetches the page with its own WebFetch (or the
user pastes the text, for paywalled pieces) into a cleaned .md/.txt file;
this tool normalises it into numbered paragraphs, hashes the text, and
writes source\\source.md + source\\source_info.json:

    python tools/capy_ingest.py --article-file cleaned.md --article-url URL --project D:\\Videos\\<slug> \\
        [--title ...] [--publication ...] [--byline ...] [--date YYYY-MM-DD] [--paywalled]
        [--archive auto|fresh|skip] [--archive-url https://web.archive.org/web/<ts>/<url>]

    python tools/capy_ingest.py --article URL --fetch --project D:\\Videos\\<slug>   # opt-in self-fetch

`--fetch` uses `requests` (generic desktop UA, no cookies) + trafilatura
and EXPOSES THE HOME IP to the publisher; it is opt-in and off by default.
`--archive auto` reuses a Wayback snapshot <= 30 days old or asks
archive.org to save the page (also from the home IP); `--archive-url`
records a capture made from the separate publishing browser profile
instead (preferred for sensitive topics). 429/timeouts -> warning and
`archive_url: null`, never a hard failure.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capy import ff
from capy import source as source_mod

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
WAYBACK_AVAILABLE = "https://archive.org/wayback/available"
WAYBACK_SAVE = "https://web.archive.org/save/"
ARCHIVE_REUSE_DAYS = 30
FETCH_TIMEOUT = 30
SAVE_TIMEOUT = 90


# ---------------------------------------------------------------------------
# Video branch (unchanged behaviour)
# ---------------------------------------------------------------------------

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


def ingest_video(args: argparse.Namespace) -> int:
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
        print(f"Moving local file into source\\: {args.file} -> {dest_media}")
        shutil.move(str(args.file), str(dest_media))
        media_from = "local_file"
    elif url:
        print(f"Downloading via yt_dlp: {url}")
        download_media(url, dest_media, args.max_height)
        media_from = "downloaded"
    else:
        print("error: provide a URL, --file, or both (or --article-file / --article for a text source)")
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
        "kind": "video",
        "media_from": media_from,
        "local_file_source": str(args.file) if args.file else None,
        "title": metadata.get("title"),
        "uploader": metadata.get("uploader"),
        "canonical_url": metadata.get("canonical_url") or url,
        "upload_date": metadata.get("upload_date"),
        "source_duration_seconds": duration if duration is not None else metadata.get("duration"),
        "source_has_captions": {"yes": True, "no": False, "unknown": None}[args.captions_in_source],
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


# ---------------------------------------------------------------------------
# Article branch
# ---------------------------------------------------------------------------

def _session():
    import requests

    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.8"})
    s.cookies.clear()
    return s


def fetch_article(url: str) -> dict:
    """Opt-in self-fetch: requests + trafilatura.bare_extraction. Returns
    {text, title, author, date, sitename, final_url}."""
    import trafilatura

    with _session() as s:
        resp = s.get(url, timeout=FETCH_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
        html = resp.text
        final_url = resp.url
    doc = trafilatura.bare_extraction(
        html, url=final_url, include_comments=False, include_tables=False, favor_precision=True, with_metadata=True,
    )
    if doc is None:
        raise RuntimeError("trafilatura could not extract article text from the page")
    get = (lambda k: doc.get(k)) if isinstance(doc, dict) else (lambda k: getattr(doc, k, None))
    return {
        "text": get("text") or "",
        "title": get("title"),
        "author": get("author"),
        "date": get("date"),
        "sitename": get("sitename"),
        "final_url": final_url,
    }


_WAYBACK_TS_RE = re.compile(r"/web/(\d{14})(?:[a-z_]*)/")


def _wayback_ts_from_url(u: str | None) -> str | None:
    if not u:
        return None
    m = _WAYBACK_TS_RE.search(u)
    return m.group(1) if m else None


def wayback_available(url: str) -> tuple[str | None, str | None]:
    """(archive_url, timestamp) of the closest existing snapshot, or (None, None)."""
    with _session() as s:
        resp = s.get(WAYBACK_AVAILABLE, params={"url": url}, timeout=FETCH_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    closest = (data.get("archived_snapshots") or {}).get("closest") or {}
    if closest.get("available") and closest.get("url"):
        u = closest["url"].replace("http://web.archive.org", "https://web.archive.org")
        return u, closest.get("timestamp") or _wayback_ts_from_url(u)
    return None, None


def wayback_save(url: str) -> tuple[str | None, str | None]:
    """Ask archive.org to capture `url` now. Returns (archive_url, ts)."""
    with _session() as s:
        resp = s.get(WAYBACK_SAVE + url, timeout=SAVE_TIMEOUT, allow_redirects=True)
        if resp.status_code == 429:
            raise RuntimeError("archive.org rate-limited the save request (429); retry later or use --archive-url")
        resp.raise_for_status()
        loc = resp.headers.get("Content-Location") or resp.headers.get("Location")
        candidate = None
        if loc:
            candidate = loc if loc.startswith("http") else "https://web.archive.org" + loc
        elif _wayback_ts_from_url(resp.url):
            candidate = resp.url
    ts = _wayback_ts_from_url(candidate)
    if not ts:
        raise RuntimeError("save request returned no /web/<timestamp>/ location")
    return f"https://web.archive.org/web/{ts}/{url}", ts


def resolve_archive(url: str, mode: str, manual: str | None) -> tuple[str | None, str | None]:
    """-> (archive_url, captured_at ISO) per --archive/--archive-url."""
    if manual:
        ts = _wayback_ts_from_url(manual)
        return manual, source_mod.wayback_timestamp_to_iso(ts) if ts else None
    if mode == "skip":
        return None, None
    try:
        if mode == "auto":
            existing, ts = wayback_available(url)
            if existing and ts:
                captured = datetime.strptime(ts[:14], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) - captured <= timedelta(days=ARCHIVE_REUSE_DAYS):
                    print(f"Reusing Wayback snapshot from {captured.date()}: {existing}")
                    return existing, source_mod.wayback_timestamp_to_iso(ts)
                print(f"Existing Wayback snapshot is older than {ARCHIVE_REUSE_DAYS} days ({captured.date()}); requesting a fresh capture")
        print(f"Requesting Wayback capture of {url} (this contacts archive.org from this machine)")
        saved, ts = wayback_save(url)
        print(f"Archived: {saved}")
        return saved, source_mod.wayback_timestamp_to_iso(ts)
    except Exception as e:  # 429, timeouts, parse failures -> warning only
        print(f"warning: could not archive {url}: {e}")
        print("         archive_url will be null -- pass --archive-url later, or re-run with --archive fresh")
        return None, None


def ingest_article(args: argparse.Namespace) -> int:
    project: Path = args.project
    url = args.article_url or args.article
    text: str
    meta: dict = {}

    if args.article_file:
        if not args.article_file.exists():
            print(f"error: --article-file not found: {args.article_file}")
            return 1
        if not url:
            print("error: --article-file needs --article-url (the article's canonical URL is required for the citation and archive receipt)")
            return 1
        text = args.article_file.read_text(encoding="utf-8")
        text_from = "user_paste" if args.paywalled else "agent_paste"
        print(f"Reading article text from {args.article_file.name} ({text_from})")
    elif args.article:
        if not args.fetch:
            print("error: --article URL needs --fetch to download from this machine (exposes the home IP to the publisher),")
            print("       or fetch the page with the agent's WebFetch / paste the text and pass --article-file cleaned.md --article-url URL")
            return 1
        print(f"Fetching {url} with requests + trafilatura (home IP)")
        try:
            meta = fetch_article(url)
        except Exception as e:
            print(f"error: fetch failed: {e}")
            return 1
        text = meta["text"]
        text_from = "trafilatura"
    else:
        print("error: provide --article-file or --article")
        return 1

    paragraphs = source_mod.number_paragraphs(text)
    if not paragraphs:
        print("error: no paragraphs found in the article text")
        return 1
    if len(paragraphs) < 3:
        print(f"warning: only {len(paragraphs)} paragraph(s) found -- check the cleaned text is blank-line separated")

    archive_url, captured_at = resolve_archive(url, args.archive, args.archive_url)

    info = source_mod.SourceInfo(
        kind="article",
        title=args.title or meta.get("title"),
        byline=args.byline or meta.get("author"),
        publication=args.publication or meta.get("sitename"),
        publish_date=args.date or meta.get("date"),
        url=url,
        canonical_url=meta.get("final_url") or url,
        archive_url=archive_url,
        archive_captured_at=captured_at,
        accessed=source_mod.today_iso(),
        paywalled=bool(args.paywalled),
        text_from=text_from,
        paragraph_count=len(paragraphs),
        text_sha256=source_mod.sha256_text("\n\n".join(paragraphs)),
        present=True,
    )
    missing = [k for k in ("title", "publication", "publish_date") if not getattr(info, k)]
    if missing:
        print(f"warning: missing {', '.join(missing)} -- pass --title/--publication/--date so the attribution line is complete")

    md_path = source_mod.write_source_md(project, info, paragraphs)
    # Round-trip check: what we wrote must hash to what we pinned.
    reread = source_mod.load_article(project)
    if reread.sha256 != info.text_sha256:
        print("error: source.md round-trip hash mismatch (internal bug)")
        return 1

    info_path = source_mod.source_info_path(project)
    info_path.parent.mkdir(parents=True, exist_ok=True)
    info_path.write_text(json.dumps(info.to_json_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {md_path} ({len(paragraphs)} paragraphs)")
    print(f"Wrote {info_path}:\n{json.dumps(info.to_json_dict(), indent=2, ensure_ascii=False)}")
    print("\nNext: research/claims.md (anchors are paragraph numbers), research/sources.yaml (the article is the "
          "type: critic entry with source_kind: article), then excerpt beats in script/beats.yaml and capy_check_sources.py.")
    return 0


# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url", nargs="?", default=None, help="video source URL (downloaded if --file is not given)")
    ap.add_argument("--url", dest="url_opt", default=None, help="explicit video URL for metadata, usable alongside --file")
    ap.add_argument("--file", type=Path, default=None, help="existing local media file to MOVE into source\\ instead of downloading (e.g. from the videos-needing-reactions intake folder -- the original is relocated, not copied)")
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--max-height", type=int, default=1080)
    ap.add_argument("--model", default="small.en")
    ap.add_argument("--skip-transcribe", action="store_true")
    ap.add_argument("--captions-in-source", choices=["yes", "no", "unknown"], default="unknown",
                     help="Does the source video already have captions burned in? The agent must ask "
                          "the user this before ingesting a video source -- see docs/saint-capybara/"
                          "script-format.md's caption rule. Recorded as source_has_captions in "
                          "source_info.json; does not change ingest behavior itself.")

    art = ap.add_argument_group("article (text) source")
    art.add_argument("--article-file", type=Path, default=None, help="cleaned article text (.md/.txt, blank-line separated paragraphs) fetched by the agent or pasted by the user")
    art.add_argument("--article-url", default=None, help="the article's canonical URL (required with --article-file)")
    art.add_argument("--article", default=None, help="article URL to self-fetch (requires --fetch)")
    art.add_argument("--fetch", action="store_true", help="opt in to fetching --article from this machine (requests + trafilatura; exposes the home IP)")
    art.add_argument("--archive", choices=["auto", "fresh", "skip"], default="auto", help="Wayback: reuse a snapshot <= 30 days old else save (auto), always save (fresh), or do nothing (skip)")
    art.add_argument("--archive-url", default=None, help="record this archive URL instead (e.g. a capture made from the publishing browser profile)")
    art.add_argument("--title", default=None)
    art.add_argument("--publication", default=None)
    art.add_argument("--byline", default=None)
    art.add_argument("--date", default=None, help="publish date, YYYY-MM-DD")
    art.add_argument("--paywalled", action="store_true", help="text was pasted by the user from behind a paywall (text_from: user_paste; the archive is an existence receipt only)")
    args = ap.parse_args()

    if args.article_file or args.article:
        if args.file or args.url or args.url_opt:
            print("error: article options cannot be combined with a video URL/--file")
            return 1
        return ingest_article(args)
    return ingest_video(args)


if __name__ == "__main__":
    raise SystemExit(main())
