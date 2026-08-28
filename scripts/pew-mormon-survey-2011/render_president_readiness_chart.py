#!/usr/bin/env python3
"""Renders the "Ready for a Mormon president?" PNG for the 2011 National
Survey of Mormons. Reads only
docs/datasets/pew-mormon-survey-2011/president-readiness-by-party.json
(produced by president_readiness_by_party.py in this folder). Uses the
shared magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-mormon-survey-2011/render_president_readiness_chart.py \
    --out public/data-explorer/pew-mormon-survey-2011/president-readiness-by-party.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-mormon-survey-2011"
    / "president-readiness-by-party.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["ready_for_mormon_president"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="Ready for a Mormon president?",
        subtitle="Share of Mormons saying Americans are ready to elect a\nMormon president, by the Mormon respondent's own party.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 2011 Mormon Survey",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
