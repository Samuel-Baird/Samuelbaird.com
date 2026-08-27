#!/usr/bin/env python3
"""Renders the "Converts vs. lifelong Mormons" PNG for the 2011 National
Survey of Mormons. Reads only
docs/datasets/pew-mormon-survey-2011/mission-and-tithe-by-convert.json
(produced by mission_and_tithe_by_convert.py in this folder). Uses the
shared magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-mormon-survey-2011/render_mission_tithe_chart.py \
    --out public/data-explorer/pew-mormon-survey-2011/mission-and-tithe-by-convert.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-mormon-survey-2011"
    / "mission-and-tithe-by-convert.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["row_order"]
    values = {r: data["results"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="Converts vs. lifelong Mormons",
        subtitle="Share serving a full-time mission and paying a full\ntithe, by whether they converted or were raised Mormon.",
        caption_paragraphs=[
            f"Population: all respondents; \"Convert\" (n={data['convert_unweighted_n']}) "
            f"was not raised Mormon, \"Lifelong\" (n={data['lifelong_unweighted_n']}) was; "
            "don't know/refused excluded from each item's own base.",
            f"Pew Research Center's 2011 National Survey of Mormons · "
            f"N = {data['total_unweighted_n']:,} Mormon adults",
            data["source"],
        ],
        out_path=args.out,
        fonts=load_fonts(),
        axes_left=0.5,
    )


if __name__ == "__main__":
    main()
