#!/usr/bin/env python3
"""Renders the "Where does the Book of Mormon say Jesus appeared?" PNG for
the 2010 U.S. Religious Knowledge Survey. Reads only
docs/datasets/pew-religious-knowledge-2010/book-of-mormon-knowledge.json
(produced by book_of_mormon_knowledge.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-religious-knowledge-2010/render_book_of_mormon_chart.py \
    --out public/data-explorer/pew-religious-knowledge-2010/book-of-mormon-knowledge.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-religious-knowledge-2010"
    / "book-of-mormon-knowledge.json"
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
        title="Where does the Book of Mormon say Jesus appeared?",
        subtitle="Share correctly saying the Americas, by the\nrespondent's own religion.",
        caption_paragraphs=[
            "Population: all U.S. adults, by present religion (qn20); don't know/refused "
            "excluded. Groups under 30 valid respondents omitted.",
            f"Pew Research Center's 2010 U.S. Religious Knowledge Survey · "
            f"N = {data['total_unweighted_n']:,} U.S. adults",
            data["source"],
        ],
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
