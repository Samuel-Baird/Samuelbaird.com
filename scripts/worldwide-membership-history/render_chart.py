#!/usr/bin/env python3
"""Renders the worldwide membership history chart, 1830-2025. Reads only
docs/datasets/worldwide-membership-history/membership-by-year.json
(produced by build_data.py in this folder). Uses the shared
render_timeseries shape in scripts/flagship-charts/common.py, with sparser
x-axis ticks and no per-year marker (196 points is dense enough that a dot
every year is noise, not signal - see that function's own docstring).

Usage:
  python scripts/worldwide-membership-history/render_chart.py \
    --out public/data-explorer/worldwide-membership-history/membership-by-year.png
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_timeseries  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "worldwide-membership-history"
    / "membership-by-year.json"
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

    render_timeseries(
        years=years,
        values=values,
        statuses=statuses,
        title=f"Worldwide Church membership, {years[0]}-{years[-1]}",
        subtitle="From six founding members to nearly 18 million,\nyear by year.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Church membership history",
        out_path=args.out,
        fonts=load_fonts(),
        y_step=2_000_000,
        x_tick_step=25,
        show_markers=False,
        label_years=[years[0], 1947, years[-1]],
    )


if __name__ == "__main__":
    main()
