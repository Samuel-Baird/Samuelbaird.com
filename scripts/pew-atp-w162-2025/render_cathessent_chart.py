#!/usr/bin/env python3
"""Renders "What's essential to being Catholic?" from
docs/datasets/pew-atp-w162-2025/cathessent.json (produced by cathessent.py).
Uses the shared magnitude-bar shape in scripts/flagship-charts/common.py -
same pattern as pew-mormon-survey-2011/render_essential_chart.py.

Usage:
  python scripts/pew-atp-w162-2025/render_cathessent_chart.py \
    --out public/data-explorer/pew-atp-w162-2025/cathessent.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-atp-w162-2025"
    / "cathessent.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["item_order"]
    values = {r: data["essential_pct"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="What's essential to being Catholic?",
        subtitle="Share of Catholics calling each item essential to what\nbeing Catholic means to them, February 2025.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 162 (2025)",
        out_path=args.out,
        fonts=load_fonts(),
        axes_left=0.52,
    )


if __name__ == "__main__":
    main()
