#!/usr/bin/env python3
"""Renders the "Opinion of Pope Francis" PNG for ATP Wave 162. Reads only
docs/datasets/pew-atp-w162-2025/pope-francis-favorable.json (produced by
pope_francis_favorable.py in this folder, whose group_order is already
sorted via chart_style.sort_groups). Uses the shared magnitude-bar shape in
scripts/flagship-charts/.

Usage:
  python scripts/pew-atp-w162-2025/render_pope_francis_favorable_chart.py \
    --out public/data-explorer/pew-atp-w162-2025/pope-francis-favorable.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-atp-w162-2025"
    / "pope-francis-favorable.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["pope_francis_favorable"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="Opinion of Pope Francis",
        subtitle="Share with a very or mostly favorable opinion of Pope Francis, among\nthose who had heard of him, by present religion, February 2025.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 162 (2025)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
