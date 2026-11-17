#!/usr/bin/env python3
"""Renders "How warmly do Americans feel toward feminists?" from
docs/datasets/ryan-burge/ft-feminists.json (produced by ft_feminists.py).
Uses the shared magnitude-bar shape in scripts/flagship-charts/common.py,
with value_suffix="/100" since the plotted value is a feeling-thermometer
mean, not a percentage.

Usage:
  python scripts/ryan-burge/render_ft_feminists_chart.py \
    --out public/data-explorer/voter-survey-panel/ft-feminists.png
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
    / "ft-feminists.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    results = data["ft_feminists"]
    values = {r: results[r]["mean"] for r in data["group_order"]}
    rows = sort_groups(data["group_order"], lambda r: values[r])

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        value_suffix="/100",
        title="How warmly do Americans feel toward feminists?",
        subtitle="Mean feeling-thermometer rating toward feminists\n(0=coldest, 100=warmest), by religion, 2017.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Ryan Burge, VOTER Panel 2017",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
