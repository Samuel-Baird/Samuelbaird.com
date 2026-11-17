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

    render_timeseries(
        years=years,
        values=values,
        statuses=statuses,
        title="U.S. Church membership, 2000-2025",
        subtitle="Reported U.S. membership of The Church of Jesus Christ\nof Latter-day Saints, year by year.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Church membership compilation",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
