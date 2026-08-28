#!/usr/bin/env python3
"""Renders the "Who prays daily?" PNG for the 2007 U.S. Religious
Landscape Survey. Reads only docs/datasets/pew-rls-2007/daily-prayer.json
(produced by daily_prayer.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-rls-2007/render_daily_prayer_chart.py \
    --out public/data-explorer/pew-rls-2007/daily-prayer.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2007"
    / "daily-prayer.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["pray_daily"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={"Mormon"},
        title="Who prays daily?",
        subtitle="Share who pray at least once a day outside of\nreligious services, by religious tradition.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 2007 RLS",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
