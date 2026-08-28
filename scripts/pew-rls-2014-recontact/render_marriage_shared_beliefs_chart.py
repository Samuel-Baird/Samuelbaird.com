#!/usr/bin/env python3
"""Renders the flagship PNG for the 2014 RLS recontact survey. Reads only
docs/datasets/pew-rls-2014-recontact/marriage-shared-beliefs.json (produced
by marriage_shared_beliefs.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-rls-2014-recontact/render_marriage_shared_beliefs_chart.py \
    --out public/data-explorer/pew-rls-2014-recontact/marriage-shared-beliefs.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2014-recontact"
    / "marriage-shared-beliefs.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["shared_beliefs_very_important"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={"Mormon"},
        title="Sharing faith with a spouse",
        subtitle="Share who say shared religious beliefs are very\nimportant for a successful marriage, by tradition.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 2014 RLS Recontact",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
