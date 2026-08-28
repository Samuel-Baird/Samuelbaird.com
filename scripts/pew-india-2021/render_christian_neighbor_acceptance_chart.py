#!/usr/bin/env python3
"""Renders the "Would you accept a Christian neighbor?" PNG for Pew's 2019-2020
India Religion Survey. Reads only
docs/datasets/pew-india-2021/christian-neighbor-acceptance.json (produced by
christian_neighbor_acceptance.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-india-2021/render_christian_neighbor_acceptance_chart.py \
    --out public/data-explorer/pew-india-2021/christian-neighbor-acceptance.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-india-2021"
    / "christian-neighbor-acceptance.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["accept_christian_neighbor"][r]["pct"] for r in rows}
    # Highlight every real religious group in --accent; leave the
    # "All non-Christian adults" aggregate row in the neutral gray, same
    # convention as the ATP Wave 70 charts muting their "All attenders" row.
    highlight_rows = {r for r in rows if r != "All non-Christian adults"}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=highlight_rows,
        title="Would you accept a Christian neighbor?",
        subtitle="Share of India's other major religious communities willing to\naccept a Christian as a neighbor, by the respondent's own religion.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew India Religion Survey (2021)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
