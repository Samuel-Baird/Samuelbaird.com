#!/usr/bin/env python3
"""Renders "What do Mormons believe about Jesus and eternity?" from
docs/datasets/pew-mormon-survey-2011/core-beliefs.json (produced by
core_beliefs.py). Uses the shared magnitude-bar shape in
scripts/flagship-charts/common.py.

Usage:
  python scripts/pew-mormon-survey-2011/render_core_beliefs_chart.py \
    --out public/data-explorer/pew-mormon-survey-2011/core-beliefs.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-mormon-survey-2011"
    / "core-beliefs.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["item_order"]
    values = {r: data["believe_pct"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="What do Mormons believe about Jesus and eternity?",
        subtitle="Share of Mormons who believe each of the following.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 2011 Mormon Survey",
        out_path=args.out,
        fonts=load_fonts(),
        axes_left=0.52,
    )


if __name__ == "__main__":
    main()
