#!/usr/bin/env python3
"""Renders the flagship PNG for the 2010 U.S. Religious Knowledge Survey.
Reads only docs/datasets/pew-religious-knowledge-2010/mormon-founding-knowledge.json
(produced by mormon_founding_knowledge.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-religious-knowledge-2010/render_mormon_founding_chart.py \
    --out public/data-explorer/pew-religious-knowledge-2010/mormon-founding-knowledge.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-religious-knowledge-2010"
    / "mormon-founding-knowledge.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["correct_pct"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={"Mormon"},
        title="Who knows when Mormonism was founded?",
        subtitle="Share correctly saying the Mormon religion was founded\nsometime after 1800, by the respondent's own religion.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 2010 Religious Knowledge Survey",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
