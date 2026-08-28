#!/usr/bin/env python3
"""Renders the "Where the Christian share of the population fell the most"
PNG for pew-religious-composition-2010-2020. Reads only
docs/datasets/pew-religious-composition-2010-2020/christian-share-decline.json
(produced by christian_share_decline.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/. Bars plot the *decline*
magnitude (a positive percentage-point number, "pp" suffix, not "%") since
render_magnitude_bar's axis assumes non-negative values - the JSON also
carries each country's signed change_pp for anyone reading the data
directly.

Usage:
  python scripts/pew-religious-composition-2010-2020/render_christian_share_decline_chart.py \
    --out public/data-explorer/pew-religious-composition-2010-2020/christian-share-decline.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets"
    / "pew-religious-composition-2010-2020" / "christian-share-decline.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["christian_share_decline_pp"][r]["decline_pp"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={"United States"},
        title="Where the Christian share fell the most",
        subtitle="Percentage-point drop in the Christian share of population,\n2010 to 2020, ten largest declines worldwide.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew religious composition 2010-2020",
        out_path=args.out,
        fonts=load_fonts(),
        value_suffix="pp",
    )


if __name__ == "__main__":
    main()
