#!/usr/bin/env python3
"""Renders the "Churches should endorse candidates" PNG for ATP Wave 114. Reads only
docs/datasets/pew-atp-w114-2022/churches-endorse-candidates.json (produced by churches_endorse_candidates.py in this
folder). Uses the shared magnitude-bar shape in scripts/flagship-charts/;
rows are ordered by sort_groups (site-wide row-order rule) so the "U.S.
adults" row sinks to the bottom regardless of its value.

Usage:
  python scripts/pew-atp-w114-2022/render_churches_endorse_candidates_chart.py \\
    --out public/data-explorer/pew-atp-w114-2022/churches-endorse-candidates.png
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
    / "churches-endorse-candidates.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    results = data["churches_should_endorse_candidates"]
    values = {r: results[r]["pct"] for r in data["group_order"]}
    rows = sort_groups(data["group_order"], lambda r: values[r])

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title='Should churches endorse candidates?',
        subtitle='Share saying churches and houses of worship should come out in favor\nof one candidate over another during elections, by religion, September 2022.',
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 114 (2022)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
