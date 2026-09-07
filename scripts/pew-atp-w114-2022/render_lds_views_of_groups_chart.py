#!/usr/bin/env python3
"""Renders the "How Latter-day Saints view other religious groups" PNG for
ATP Wave 114. Reads only docs/datasets/pew-atp-w114-2022/lds-views-of-groups.json
(produced by lds_views_of_groups.py in this folder). Rows are the rated
groups, so each takes its own identity color from chart_style.color_for_group
via render_magnitude_bar's group_identity mode; ordered by sort_groups.

Usage:
  python scripts/pew-atp-w114-2022/render_lds_views_of_groups_chart.py \
    --out public/data-explorer/pew-atp-w114-2022/lds-views-of-groups.png
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
    / "lds-views-of-groups.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    results = data["lds_favorable_view_of_group"]
    values = {r: results[r]["pct"] for r in data["group_order"]}
    rows = sort_groups(data["group_order"], lambda r: values[r])

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="How Latter-day Saints view other religious groups",
        subtitle="Share of Latter-day Saints with a very or somewhat favorable view of\neach group, among those who gave a rating, September 2022.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 114 (2022)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
