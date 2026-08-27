#!/usr/bin/env python3
"""Renders the "Where do Mormons live?" PNG for the 2007 U.S. Religious
Landscape Survey. Reads only
docs/datasets/pew-rls-2007/lds-share-by-region.json (produced by
lds_share_by_region.py in this folder). Uses the shared magnitude-bar
shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-rls-2007/render_lds_share_by_region_chart.py \
    --out public/data-explorer/pew-rls-2007/lds-share-by-region.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2007"
    / "lds-share-by-region.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["region_order"]
    values = {r: data["share_of_mormons"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="Where do Mormons live?",
        subtitle="Share of U.S. Mormons living in each\nCensus region, 2007.",
        caption_paragraphs=[
            "Population: respondents whose current tradition (RELTRAD) is Mormon, "
            "continental U.S., by Census region (cregion).",
            f"Pew Research Center's 2007 U.S. Religious Landscape Survey · "
            f"N = {data['mormon_unweighted_n']:,} Mormon adults",
            data["source"],
        ],
        out_path=args.out,
        fonts=load_fonts(),
        value_suffix="%",
    )


if __name__ == "__main__":
    main()
