#!/usr/bin/env python3
"""Renders "Is equality really about special favors?" from
docs/datasets/ryan-burge/sexism-special-favors.json (produced by
sexism_special_favors.py). Uses the shared magnitude-bar shape in
scripts/flagship-charts/common.py.

Usage:
  python scripts/ryan-burge/render_sexism_special_favors_chart.py \
    --out public/data-explorer/voter-survey-panel/sexism-special-favors.png
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
    / "sexism-special-favors.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    results = data["special_favors_agree"]
    values = {r: results[r]["pct"] for r in data["group_order"]}
    rows = sort_groups(data["group_order"], lambda r: values[r])

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="Is equality really about special favors?",
        subtitle="Share who strongly or somewhat agree equality demands\nare really about special favors, by religion, 2016.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Ryan Burge, VOTER Panel 2016",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
