#!/usr/bin/env python3
"""Renders the four Faith Matters 2006 magnitude bars from the JSON written
by faith_matters_2006.py (docs/datasets/ryan-burge/faith-matters-*.json),
using the shared magnitude-bar shape in scripts/flagship-charts/common.py
and chart_style.sort_groups for row order (highest to lowest; "Other
non-Christian" sinks below the substantive rows, "All U.S. adults" to the
very bottom).

Usage:
  python scripts/ryan-burge/render_faith_matters_2006_charts.py \
    --out-dir public/data-explorer/faith-matters-2006
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA_DIR = (Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "ryan-burge").resolve()
HANDLE = "@ithinkisam | data: Faith Matters 2006 via Ryan Burge"

CHARTS = [
    {
        "json": "faith-matters-convert-ok.json", "key": "convert_ok",
        "png": "convert-ok.png",
        "title": "Okay for religious people to try to convert others",
        "subtitle": "Share choosing that over “everyone should leave everyone\nelse alone,” by religious tradition, 2006.",
    },
    {
        "json": "faith-matters-religious-giving.json", "key": "gave_1000_plus_religious",
        "png": "religious-giving-1000-plus.png",
        "title": "Gave $1,000 or more to religious causes last year",
        "subtitle": "Share of households giving $1,000+ to religious causes in the\npast 12 months, by religious tradition, 2006.",
    },
    {
        "json": "faith-matters-marry-within-faith.json", "key": "marry_within_faith_very_important",
        "png": "marry-within-faith.png",
        "title": "Very important that my children marry within my faith",
        "subtitle": "Share of parents saying it is very important that their children\nmarry someone of their own faith, by tradition, 2006.",
    },
    {
        "json": "faith-matters-talk-religion.json", "key": "talk_religion_daily",
        "png": "talk-religion-daily.png",
        "title": "Talk about religion with family and friends daily",
        "subtitle": "Share saying they discuss religion roughly daily,\nby religious tradition, 2006.",
    },
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    fonts = load_fonts()

    for c in CHARTS:
        with open(DATA_DIR / c["json"], encoding="utf-8") as f:
            data = json.load(f)
        results = data[c["key"]]
        values = {r: results[r]["pct"] for r in data["group_order"]}
        rows = sort_groups(data["group_order"], lambda r: values[r])
        render_magnitude_bar(
            rows=rows,
            values=values,
            highlight_rows=None,
            group_identity=True,
            title=c["title"],
            subtitle=c["subtitle"],
            caption_paragraphs=[],
            handle=HANDLE,
            out_path=args.out_dir / c["png"],
            fonts=fonts,
        )
        print("wrote", args.out_dir / c["png"])


if __name__ == "__main__":
    main()
