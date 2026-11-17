#!/usr/bin/env python3
"""Renders the Brazil membership-growth line chart. Reads only
docs/datasets/lds-brazil-2022/membership-by-year.json (produced by
build_membership_by_year.py in this folder). Uses the shared line-chart
shape (render_timeseries) in scripts/flagship-charts/common.py.

This series is a sparse historical timeline (1940-2025, irregularly
spaced - see build_membership_by_year.py's docstring), not an annual
grid. Two pairs of points sit only a year apart (1999/2000, 2009/2010);
labeling every point (x_tick_step=1) crowds those pairs illegibly, so
this uses x_tick_step=10 - close enough to label most real points
(1940, 1950, 1960, 1970, 2000, 2010, plus 2025 forced in as the series'
own last year) while every point still gets its own plotted marker.

Usage:
  python scripts/lds-brazil-2022/render_membership_by_year_chart.py \
    --out public/data-explorer/lds-brazil-2022/membership-by-year.png
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_timeseries  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "lds-brazil-2022"
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
        title="Brazil Church membership, 1940-2025",
        subtitle="Reported Brazilian membership of The Church of Jesus Christ\n"
                  "of Latter-day Saints, 1940 to 2025.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Brazil membership compilation",
        out_path=args.out,
        fonts=load_fonts(),
        x_tick_step=10,
    )


if __name__ == "__main__":
    main()
