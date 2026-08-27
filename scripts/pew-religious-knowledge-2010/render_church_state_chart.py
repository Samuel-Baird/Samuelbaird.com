#!/usr/bin/env python3
"""Renders the "What can public school teachers do?" PNG for the 2010
U.S. Religious Knowledge Survey. Reads only
docs/datasets/pew-religious-knowledge-2010/church-state-law.json (produced
by church_state_law.py in this folder). Uses the shared magnitude-bar
shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-religious-knowledge-2010/render_church_state_chart.py \
    --out public/data-explorer/pew-religious-knowledge-2010/church-state-law.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-religious-knowledge-2010"
    / "church-state-law.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["item_order"]
    values = {r: data["correct_pct"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="What can public school teachers do?",
        subtitle="Share correctly identifying whether the Constitution\npermits each action in a public school classroom.",
        caption_paragraphs=[
            "Population: all U.S. adults; don't know/refused excluded from each item's own "
            "base.",
            f"Pew Research Center's 2010 U.S. Religious Knowledge Survey · "
            f"N = {data['total_unweighted_n']:,} U.S. adults",
            data["source"],
        ],
        out_path=args.out,
        fonts=load_fonts(),
        axes_left=0.5,
    )


if __name__ == "__main__":
    main()
