#!/usr/bin/env python3
"""Renders the "President who stands up for your religious beliefs" PNG for ATP Wave 143. Reads only
docs/datasets/pew-atp-w143-2024/president-stands-up.json (produced by president_stands_up.py in this
folder). Uses the shared magnitude-bar shape in scripts/flagship-charts/;
rows ordered by chart_style.sort_groups (site-wide row-order rule) so the
"U.S. adults" row sinks to the bottom regardless of its value.

Usage:
  python scripts/pew-atp-w143-2024/render_president_stands_up_chart.py \\
    --out public/data-explorer/pew-atp-w143-2024/president-stands-up.png
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
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-atp-w143-2024"
    / "president-stands-up.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    results = data["president_stands_up_very_important"]
    values = {r: results[r]["pct"] for r in data["group_order"]}
    rows = sort_groups(data["group_order"], lambda r: values[r])

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title='A president who stands up for people with my religious beliefs',
        subtitle='Share saying this is very important to them in a president,\nby religion, February 2024.',
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 143 (2024)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
