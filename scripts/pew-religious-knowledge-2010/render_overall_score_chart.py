#!/usr/bin/env python3
"""Renders the "Who scored best on the religious knowledge quiz?" PNG for
the 2010 U.S. Religious Knowledge Survey - Pew's own headline finding.
Reads only docs/datasets/pew-religious-knowledge-2010/overall-score.json
(produced by overall_score.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/, with value_suffix=""
since this is an average-number-correct score (out of 32), not a percent.

Usage:
  python scripts/pew-religious-knowledge-2010/render_overall_score_chart.py \
    --out public/data-explorer/pew-religious-knowledge-2010/overall-score.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-religious-knowledge-2010"
    / "overall-score.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["results"][r]["mean_correct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={"Mormon"},
        title="Who scored best on the religious knowledge quiz?",
        subtitle=f"Average number correct out of {data['n_items']} questions,\nby the respondent's own religion.",
        caption_paragraphs=[
            "Population: all U.S. adults, by present religion (qn20). Don't know/refused "
            "scores as incorrect, matching Pew's own published scoring. Groups under 30 "
            "respondents omitted.",
            f"Pew Research Center's 2010 U.S. Religious Knowledge Survey · "
            f"N = {data['total_unweighted_n']:,} U.S. adults",
            data["source"],
        ],
        out_path=args.out,
        fonts=load_fonts(),
        value_suffix="",
    )


if __name__ == "__main__":
    main()
