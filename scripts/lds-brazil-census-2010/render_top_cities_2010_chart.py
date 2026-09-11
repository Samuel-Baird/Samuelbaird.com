#!/usr/bin/env python3
"""Renders "Cities with the highest concentration of Latter-day Saints" -
a ranked horizontal bar of the top municipalities (population >= 50,000)
by LDS self-identification share, 2010 Census. Reads only
docs/datasets/lds-brazil-census-2010/top-cities-2010.json (produced by
build_top_cities_2010.py in this folder, which already applies the
50,000-population floor and truncates to the top N before writing the
JSON - this script does no further filtering). Uses the shared
magnitude-bar shape (render_magnitude_bar) in
scripts/flagship-charts/common.py.

Usage:
  python scripts/lds-brazil-census-2010/render_top_cities_2010_chart.py \
    --out public/data-explorer/lds-brazil-census-2010/top-cities-2010.png
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "lds-brazil-census-2010"
    / "top-cities-2010.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["city_order"]
    values = {r: data["cities"][r]["pct"] for r in rows}
    top_city = data["top_city"]

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={top_city},
        title="Where Latter-day Saints concentrate, city by city",
        subtitle=f"Share of population self-identifying as Latter-day Saint,\n"
                 f"2010 Census - municipalities with population {data['population_floor']:,}+\n"
                 "only, to avoid small-town noise. Half of the top 10 are in Rio\n"
                 "Grande do Sul, including border cities with Uruguay/Argentina.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: 2010 Census (IBGE)",
        out_path=args.out,
        fonts=load_fonts(),
        value_suffix="%",
        value_decimals=2,
        axes_left=0.34,
        row_label_fontsize=15,
        value_label_fontsize=13,
    )


if __name__ == "__main__":
    main()
