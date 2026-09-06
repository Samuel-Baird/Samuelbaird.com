#!/usr/bin/env python3
"""Renders "Have opportunities for women improved quality of life?" from
docs/datasets/ryan-burge/sexism-opportunities-improved.json (produced by
sexism_opportunities_improved.py). Uses the shared magnitude-bar shape in
scripts/flagship-charts/common.py.

Usage:
  python scripts/ryan-burge/render_sexism_opportunities_improved_chart.py \
    --out public/data-explorer/voter-survey-panel/sexism-opportunities-improved.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "ryan-burge"
    / "sexism-opportunities-improved.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    results = data["opportunities_improved_agree"]
    values = {r: results[r]["pct"] for r in data["group_order"]}
    rows = sort_groups(data["group_order"], lambda r: values[r])

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="Have opportunities for women improved quality of life?",
        subtitle="Share who strongly or somewhat agree opportunities for\nwomen have improved their quality of life, by religion, 2016.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Ryan Burge, VOTER Panel 2016",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
