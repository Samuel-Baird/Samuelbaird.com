#!/usr/bin/env python3
"""Renders the U.S. membership 2050 projection chart. Reads only
docs/datasets/us-membership-growth-2000-2025/membership-projection-2050.json
(produced by build_projection.py in this folder). Uses the shared
render_timeseries shape in scripts/flagship-charts/common.py, with its
"projected" status (gray dashed) for 2026-2050.

Usage:
  python scripts/us-membership-growth-2000-2025/render_projection_chart.py \
    --out public/data-explorer/us-membership-growth-2000-2025/membership-projection-2050.png
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_timeseries  # noqa: E402

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

    years = data["year_order"]
    series = data["series"]
    values = {y: series[str(y)]["members"] for y in years}
    statuses = {y: series[str(y)]["status"] for y in years}
    anchor_year = data["anchor_year"]

    render_timeseries(
        years=years,
        values=values,
        statuses=statuses,
        title="U.S. membership, projected to 2050",
        subtitle=f"Reported through {anchor_year}, then a linear extrapolation\nof the {data['trend_fit_years'][0]}-{data['trend_fit_years'][1]} reported trend.",
        caption_paragraphs=[
            data["method"],
            "This is a trend extrapolation, not a demographic forecast - it assumes the "
            f"~{data['trend_slope_per_year']:,}/year average increase of {data['trend_fit_years'][0]}-"
            f"{data['trend_fit_years'][1]} continues unchanged through 2050.",
        ],
        out_path=args.out,
        fonts=load_fonts(),
        label_years=[years[0], anchor_year, years[-1]],
        y_step=1_000_000,
    )


if __name__ == "__main__":
    main()
