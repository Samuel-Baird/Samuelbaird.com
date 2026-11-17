#!/usr/bin/env python3
"""Renders the "Do Mormons believe in yoga as a spiritual practice?" PNG.
Reads only docs/datasets/pew-mormon-survey-2011/yoga-by-activity.json
(produced by yoga_by_activity.py in this folder) - no number here is
hand-typed. Uses the shared magnitude-bar shape in
scripts/flagship-charts/common.py.

Usage:
  python scripts/pew-mormon-survey-2011/render_yoga_chart.py \
    --out public/data-explorer/pew-mormon-survey-2011/yoga-by-activity.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-mormon-survey-2011"
    / "yoga-by-activity.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["activity_order"]
    values = {r: data["believes_yoga_spiritual_pct"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="Do Mormons believe in yoga as a spiritual practice?",
        subtitle="Share of Mormons who believe in yoga, not just as exercise but\n"
                 "as a spiritual practice, by how active they are in the Church.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 2011 Mormon Survey",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
