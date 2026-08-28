#!/usr/bin/env python3
"""Renders the flagship PNG for ATP Wave 70. Reads only
docs/datasets/pew-atp-w70-2020/online-worship-covid.json (produced by
online_worship_covid.py in this folder). Uses the shared magnitude-bar
shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-atp-w70-2020/render_online_worship_chart.py \
    --out public/data-explorer/pew-atp-w70-2020/online-worship-covid.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-atp-w70-2020"
    / "online-worship-covid.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["watched_online_worship"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={"Mormon"},
        title="Worship online during COVID lockdowns",
        subtitle="Share who watched religious services online or on\nTV in the past month, by religious tradition, July 2020.",
        caption_paragraphs=["@ithinkisam | data: Pew ATP Wave 70 (2020)"],
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
