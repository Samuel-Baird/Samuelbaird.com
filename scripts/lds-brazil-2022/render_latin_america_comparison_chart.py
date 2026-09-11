#!/usr/bin/env python3
"""Renders the "Brazil vs. other Latin American countries, 2025" magnitude
bar chart. Reads only
docs/datasets/lds-brazil-2022/latin-america-comparison-2025.json (produced
by build_latin_america_comparison.py in this folder). Uses the shared
magnitude-bar shape (render_magnitude_bar) in scripts/flagship-charts/common.py.

Countries aren't a religious-identity axis, so this uses the default
`group_identity=False` mode with `highlight_rows={"Brazil"}` - the chart's
own subject (Brazil, now the largest of the five) drawn in --accent, the
other four countries in bar-safe gray.

Usage:
  python scripts/lds-brazil-2022/render_latin_america_comparison_chart.py \
    --out public/data-explorer/lds-brazil-2022/latin-america-comparison-2025.png
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "lds-brazil-2022"
    / "latin-america-comparison-2025.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["country_order"]
    values = {r: data["countries"][r]["members"] / 1000 for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={"Brazil"},
        title="Brazil overtakes Mexico",
        subtitle="Total Church membership, the five largest Latter-day Saint\n"
                  "populations in Latin America, as of Dec. 31, 2025.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Church facts-and-statistics pages (2025)",
        out_path=args.out,
        fonts=load_fonts(),
        value_suffix="K",
    )


if __name__ == "__main__":
    main()
