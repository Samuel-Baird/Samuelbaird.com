#!/usr/bin/env python3
"""Renders the U.S. membership 2050 projection RANGE chart. Reads only
docs/datasets/us-membership-growth-2000-2025/membership-projection-2050.json
(produced by build_projection.py in this folder). Uses the shared
render_range_projection shape in scripts/flagship-charts/common.py - a
history line plus a shaded low/high band, not a single projected line
(see that function's and build_projection.py's own docstrings for why).

Usage:
  python scripts/us-membership-growth-2000-2025/render_projection_chart.py \
    --out public/data-explorer/us-membership-growth-2000-2025/membership-projection-2050.png
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_range_projection  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "us-membership-growth-2000-2025"
    / "membership-projection-2050.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    history_years = data["history_year_order"]
    history_values = {y: data["history_series"][str(y)]["members"] for y in history_years}
    range_years = data["range_year_order"]
    range_series = data["range_series"]
    low_values = {y: range_series[str(y)]["low"] for y in range_years}
    high_values = {y: range_series[str(y)]["high"] for y in range_years}

    render_range_projection(
        history_years=history_years,
        history_values=history_values,
        range_years=range_years,
        low_values=low_values,
        high_values=high_values,
        title="U.S. membership, projected to 2050",
        subtitle=f"Reported through {data['anchor_year']}, then a range between\ntwo scenarios (see caption) rather than one guess.",
        caption_paragraphs=[data["method"]],
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
