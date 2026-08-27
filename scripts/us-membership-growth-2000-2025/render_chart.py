#!/usr/bin/env python3
"""Renders the U.S. membership growth line chart. Reads only
docs/datasets/us-membership-growth-2000-2025/membership-by-year.json
(produced by build_data.py in this folder). Uses the shared line-chart
shape (render_timeseries) in scripts/flagship-charts/common.py.

Usage:
  python scripts/us-membership-growth-2000-2025/render_chart.py \
    --out public/data-explorer/us-membership-growth-2000-2025/membership-by-year.png
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_timeseries  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "us-membership-growth-2000-2025"
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

    n_interpolated = sum(1 for y in years if statuses[y] == "interpolated")
    n_rounded = sum(1 for y in years if statuses[y] == "rounded")

    render_timeseries(
        years=years,
        values=values,
        statuses=statuses,
        title="U.S. Church membership, 2000-2025",
        subtitle="Reported U.S. membership of The Church of Jesus Christ\nof Latter-day Saints, year by year.",
        caption_paragraphs=[
            f"Compiled from multiple Church-reported sources (see full citations in "
            f"docs/datasets/us-membership-growth-2000-2025/); {n_rounded} years are rounded "
            f"to the nearest 10,000 and {n_interpolated} years ({', '.join(str(y) for y in years if statuses[y] == 'interpolated')}) "
            "have no findable source and are linearly interpolated (dashed).",
            "Sources include the 2000 & 2010 U.S. Religion Census, the Deseret News "
            "Church Almanac, and the Church's own newsroom country page.",
        ],
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
