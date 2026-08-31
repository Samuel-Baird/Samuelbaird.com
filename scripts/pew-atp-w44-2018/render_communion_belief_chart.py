#!/usr/bin/env python3
"""Renders "Do Catholics believe in transubstantiation?" from
docs/datasets/pew-atp-w44-2018/communion-belief.json (produced by
communion_belief.py). Uses the shared magnitude-bar shape in
scripts/flagship-charts/common.py.

Usage:
  python scripts/pew-atp-w44-2018/render_communion_belief_chart.py \
    --out public/data-explorer/pew-atp-w44-2018/communion-belief.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-atp-w44-2018"
    / "communion-belief.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["item_order"]
    values = {r: data["belief_pct"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="Do Catholics believe in transubstantiation?",
        subtitle="What U.S. Catholics personally believe about the bread\nand wine used for Communion, February 2019.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 44 (2019)",
        out_path=args.out,
        fonts=load_fonts(),
        axes_left=0.48,
    )


if __name__ == "__main__":
    main()
