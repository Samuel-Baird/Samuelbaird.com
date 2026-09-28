"""Unit tests for capy_fetch_queue.py's pure helper functions.

    python -m pytest tools/tests/test_fetch_queue.py

No network calls are made.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import capy_fetch_queue as fq  # noqa: E402


@pytest.mark.parametrize("url,expected", [
    ("https://www.instagram.com/reel/DAbc123XyZ/", "ig"),
    ("https://instagram.com/p/CxYz9/?igsh=abc", "ig"),
    ("https://www.facebook.com/someuser/videos/1234567890/", "fb"),
    ("https://fb.watch/abcDEF123/", "fb"),
    ("https://www.youtube.com/watch?v=pdm2bsfrm5k", "yt"),
    ("https://youtu.be/pdm2bsfrm5k", "yt"),
    ("https://www.youtube.com/shorts/pdm2bsfrm5k", "yt"),
    ("https://example.com/video/1", None),
])
def test_platform_for(url, expected):
    assert fq.platform_for(url) == expected


@pytest.mark.parametrize("url,prefix,expected", [
    ("https://www.instagram.com/reel/DAbc123XyZ/", "ig", "DAbc123XyZ"),
    ("https://www.instagram.com/someuser/p/CxYz9/", "ig", "CxYz9"),
    ("https://www.facebook.com/someuser/videos/1234567890/", "fb", "1234567890"),
    ("https://www.facebook.com/reel/9876543210", "fb", "9876543210"),
    ("https://www.youtube.com/watch?v=pdm2bsfrm5k", "yt", "pdm2bsfrm5k"),
    ("https://youtu.be/pdm2bsfrm5k", "yt", "pdm2bsfrm5k"),
    ("https://www.youtube.com/shorts/pdm2bsfrm5k", "yt", "pdm2bsfrm5k"),
])
def test_extract_id_by_regex(url, prefix, expected):
    assert fq.extract_id_by_regex(url, prefix) == expected


def test_extract_id_by_regex_no_match_returns_none():
    assert fq.extract_id_by_regex("https://fb.watch/abcDEF123/", "fb") is None


@pytest.mark.parametrize("a,b", [
    ("https://www.youtube.com/watch?v=abc123&t=5s", "https://youtube.com/watch?v=abc123"),
    ("https://youtu.be/abc123", "https://www.youtube.com/watch?v=abc123"),
    ("https://www.instagram.com/reel/DAbc123/?igsh=xyz", "https://instagram.com/reel/DAbc123"),
    ("https://www.facebook.com/x/videos/1234/", "https://facebook.com/x/videos/1234"),
])
def test_normalize_url_dedupes_equivalent_urls(a, b):
    assert fq.normalize_url(a) == fq.normalize_url(b)


def test_normalize_url_distinguishes_different_urls():
    assert fq.normalize_url("https://youtube.com/watch?v=abc") != fq.normalize_url("https://youtube.com/watch?v=xyz")


@pytest.mark.parametrize("url,path_value,expected", [
    ("https://instagram.com/reel/abc/", None, True),
    ("https://instagram.com/reel/abc/", "", True),
    ("https://instagram.com/reel/abc/", "   ", True),
    ("https://instagram.com/reel/abc/", "Download failed 2026-01-01: timeout", True),
    ("https://instagram.com/reel/abc/", r"D:\Videos\slug\source\source.mp4", False),
    ("https://instagram.com/reel/abc/", r"D:\saint-capybara-videos-needing-reactions\ig-abc.mp4", False),
    ("", None, False),
    ("https://example.com/not-a-supported-platform", None, False),
])
def test_is_queueable_row(url, path_value, expected):
    assert fq.is_queueable_row(url, path_value) is expected


def test_find_header_columns(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Link to original", "Path", "Does original video have captions?", "Video Generated", "Notes", "script link"])
    ws.append(["https://youtube.com/watch?v=abc123", None, None, None, None, None])
    xlsx_path = tmp_path / "queue.xlsx"
    wb.save(xlsx_path)

    wb2 = openpyxl.load_workbook(xlsx_path)
    ws2 = wb2.active
    headers = fq.find_header_columns(ws2)
    assert headers["Link to original"] == 1
    assert headers["Path"] == 2


def test_find_header_columns_missing_raises(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Some Other Column"])
    xlsx_path = tmp_path / "bad.xlsx"
    wb.save(xlsx_path)
    wb2 = openpyxl.load_workbook(xlsx_path)
    ws2 = wb2.active
    with pytest.raises(SystemExit):
        fq.find_header_columns(ws2)


def test_dry_run_end_to_end(tmp_path, capsys):
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Link to original", "Path", "Does original video have captions?", "Video Generated", "Notes", "script link"])
    ws.append(["https://www.youtube.com/watch?v=abc123", None, None, None, None, None])
    ws.append(["https://youtu.be/abc123", None, None, None, None, None])  # duplicate of row 2
    ws.append(["https://www.instagram.com/reel/xyz789/", r"D:\Videos\slug\source\source.mp4", None, None, None, None])  # already ingested
    xlsx_path = tmp_path / "queue.xlsx"
    wb.save(xlsx_path)
    out_dir = tmp_path / "out"

    args = fq.argparse.Namespace(
        xlsx=str(xlsx_path), out_dir=str(out_dir), cookies_browser="chrome", dry_run=True,
    )
    rc = fq.run(args)
    assert rc == 0
    captured = capsys.readouterr()
    assert "would download" in captured.out
    assert "duplicate of row 2" in captured.out
    assert "downloaded: 1" in captured.out
    assert "duplicate: 1" in captured.out
    assert "skipped: 1" in captured.out
