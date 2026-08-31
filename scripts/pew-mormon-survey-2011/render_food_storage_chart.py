#!/usr/bin/env python3
"""Renders "Who keeps a supply of food in storage?" from
docs/datasets/pew-mormon-survey-2011/food-storage-by-activity.json
(produced by food_storage_by_activity.py). Uses the shared magnitude-bar
shape in scripts/flagship-charts/common.py.

Usage:
  python scripts/pew-mormon-survey-2011/render_food_storage_chart.py \
    --out public/data-explorer/pew-mormon-survey-2011/food-storage-by-activity.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-mormon-survey-2011"
    / "food-storage-by-activity.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["activity_order"]
    values = {r: data["keeps_food_storage_yes"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="Who keeps a food storage supply?",
        subtitle="Share of Mormons who keep a supply of food in storage\nfor emergencies, by activity level in the Church.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 2011 Mormon Survey",
        out_path=args.out,
        fonts=load_fonts(),
        axes_left=0.52,
    )


if __name__ == "__main__":
    main()
