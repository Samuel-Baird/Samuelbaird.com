#!/usr/bin/env python3
"""Renders the flagship PNG for the 2011 National Survey of Mormons.
Reads only docs/datasets/pew-mormon-survey-2011/ordination-by-activity.json
(produced by ordination_by_activity.py in this folder) - no number here is
hand-typed. Uses the shared magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-mormon-survey-2011/render_ordination_chart.py \
    --out public/data-explorer/pew-mormon-survey-2011/ordination-by-activity.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-mormon-survey-2011"
    / "ordination-by-activity.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["activity_order"]
    values = {r: data["ordain_women_yes"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="Should women be ordained to the priesthood?",
        subtitle="Share of Mormons who believe dedicated women members\nshould be ordained, by how active they are in the Church.",
        caption_paragraphs=[
            "Population: all respondents (self-identified Mormons by the survey's own "
            "design); don't know/refused excluded from each row.",
            f"Pew Research Center's 2011 National Survey of Mormons · "
            f"N = {data['total_unweighted_n']:,} Mormon adults",
            data["source"],
        ],
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
