#!/usr/bin/env python3
"""Renders the "Uses a scripture app or website" PNG for ATP Wave 117. Reads only
docs/datasets/pew-atp-w117-2022/scripture-app.json (produced by scripture_app.py in this
folder, whose group_order is already sorted via chart_style.sort_groups).
Uses the shared magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-atp-w117-2022/render_scripture_app_chart.py \\
    --out public/data-explorer/pew-atp-w117-2022/scripture-app.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-atp-w117-2022"
    / "scripture-app.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["uses_scripture_app"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title='Use an app or website to read scripture',
        subtitle='Share who ever use apps or websites that remind them or help\nthem to read scripture, by religious tradition, November 2022.',
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 117 (2022)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
