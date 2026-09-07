#!/usr/bin/env python3
"""Renders the "Houses of worship should get more flexibility on COVID rules" PNG for ATP Wave 70. Reads only
docs/datasets/pew-atp-w70-2020/worship-rules-flexibility.json (produced by worship_rules_flexibility.py in this
folder, whose group_order is already sorted via chart_style.sort_groups).
Uses the shared magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-atp-w70-2020/render_worship_rules_flexibility_chart.py \\
    --out public/data-explorer/pew-atp-w70-2020/worship-rules-flexibility.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-atp-w70-2020"
    / "worship-rules-flexibility.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["worship_more_flexibility"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title='Should houses of worship get more flexibility on COVID rules?',
        subtitle='Share saying houses of worship should be allowed more flexibility with\nsocial-distancing rules than other organizations (vs. the same rules),\nby religious tradition, July 2020.',
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 70 (2020)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
