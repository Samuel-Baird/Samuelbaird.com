#!/usr/bin/env python3
"""Renders the "The rise of the 'nones'" PNG for the 2014 Religious
Landscape Study. Reads only
docs/datasets/pew-rls-2014/nones-growth-2007-2014.json (produced by
nones_growth_2007_2014.py in this folder). Uses the shared magnitude-bar
shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-rls-2014/render_nones_growth_chart.py \
    --out public/data-explorer/pew-rls-2014/nones-growth-2007-2014.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2014"
    / "nones-growth-2007-2014.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["wave_order"]
    values = {r: data["unaffiliated_pct"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="The rise of the \"nones\"",
        subtitle="Religiously unaffiliated share of U.S. adults,\n2007 vs. 2014.",
        caption_paragraphs=[
            "Population: all U.S. adults, each wave's own RELTRAD variable.",
            "Pew Research Center's 2007 U.S. Religious Landscape Survey and 2014 "
            "Religious Landscape Study",
            data["source"],
        ],
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
