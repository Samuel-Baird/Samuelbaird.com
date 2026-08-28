#!/usr/bin/env python3
"""Renders the "Who still pays the church tax" PNG for the Pew Western
Europe church-tax add-on. Reads only
docs/datasets/pew-church-tax-western-europe/pays-church-tax.json (produced
by pays_church_tax.py in this folder). Uses the shared magnitude-bar shape
in scripts/flagship-charts/. Rows are ordered by sort_groups (site-wide
row-order rule) so the "9-country average" row sinks to the bottom
regardless of its value, rather than sorting into the middle of the pack.

Usage:
  python scripts/pew-church-tax-western-europe/render_pays_church_tax_chart.py \
    --out public/data-explorer/pew-church-tax-western-europe/pays-church-tax.png
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
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-church-tax-western-europe"
    / "pays-church-tax.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    results = data["pays_church_tax"]
    values = {r: results[r]["pct"] for r in data["group_order"]}
    rows = sort_groups(data["group_order"], lambda r: values[r])

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="Who still pays the church tax",
        subtitle="Share of adults who currently pay their country's church tax,\namong the 9 Western European countries where it exists, 2017.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew church tax in Western Europe (2019)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
