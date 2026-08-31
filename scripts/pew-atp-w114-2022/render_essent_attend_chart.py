#!/usr/bin/env python3
"""Renders the "attending religious services regularly" essentiality PNG
for ATP Wave 114. Reads only
docs/datasets/pew-atp-w114-2022/essent-attend.json (produced by
essent_attend.py in this folder). Uses the shared magnitude-bar shape in
scripts/flagship-charts/. Rows are ordered by sort_groups (site-wide
row-order rule).

Usage:
  python scripts/pew-atp-w114-2022/render_essent_attend_chart.py \
    --out public/data-explorer/pew-atp-w114-2022/essent-attend.png
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
    / "essent-attend.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    results = data["attend_services_essential"]
    values = {r: results[r]["pct"] for r in data["group_order"]}
    rows = sort_groups(data["group_order"], lambda r: values[r])

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="Is attending services essential to your faith?",
        subtitle="Share saying regular religious attendance is essential\nto what being faithful to their tradition means, September 2022.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 114 (2022)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
