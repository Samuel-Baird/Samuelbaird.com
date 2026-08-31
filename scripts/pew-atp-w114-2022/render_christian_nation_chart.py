#!/usr/bin/env python3
"""Renders the "Should the U.S. be a Christian nation?" PNG for ATP Wave 114.
Reads only docs/datasets/pew-atp-w114-2022/christian-nation.json (produced
by christian_nation.py in this folder). Uses the shared magnitude-bar shape
in scripts/flagship-charts/. Rows are ordered by sort_groups (site-wide
row-order rule) so "Other" and "All U.S. adults" sink to the bottom
regardless of value.

Usage:
  python scripts/pew-atp-w114-2022/render_christian_nation_chart.py \
    --out public/data-explorer/pew-atp-w114-2022/christian-nation.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-atp-w114-2022"
    / "christian-nation.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    results = data["should_be_christian_nation"]
    values = {r: results[r]["pct"] for r in data["group_order"]}
    rows = sort_groups(data["group_order"], lambda r: values[r])

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="Should the U.S. be a Christian nation?",
        subtitle="Share saying yes, by religious affiliation,\nSeptember 2022.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 114 (2022)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
