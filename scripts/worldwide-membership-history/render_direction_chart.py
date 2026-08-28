#!/usr/bin/env python3
"""Renders a second worldwide-membership-history chart: the same
1830-2025 series, but colored per-segment by direction (blue = grew from
the prior year, red = shrank) rather than by data status - highlighting
the handful of historical years the Church's membership actually
decreased (1839, 1855-1857 - see this dataset's own README for the likely
historical causes: the 1838 Missouri Extermination Order and the
difficult early Utah years). Reads only
docs/datasets/worldwide-membership-history/membership-by-year.json
(produced by build_data.py - no new data file needed, this is a different
view of the same series). Uses render_timeseries_by_direction in
scripts/flagship-charts/common.py.

Usage:
  python scripts/worldwide-membership-history/render_direction_chart.py \
    --out public/data-explorer/worldwide-membership-history/membership-by-direction.png
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_timeseries_by_direction  # noqa: E402

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
    values = {y: data["series"][str(y)]["members"] for y in years}

    # Value callouts every 25 years from the series' own start, plus the
    # final year (2025 is only 20 years past 2005, an uneven last gap, but
    # leaving off the endpoint would be a stranger omission than one
    # shorter interval).
    label_years = list(range(years[0], years[-1], 25))
    if label_years[-1] != years[-1]:
        label_years.append(years[-1])

    render_timeseries_by_direction(
        years=years,
        values=values,
        title="Worldwide Church membership, 1830-2025",
        subtitle="Colored by whether it grew or shrank from the year\nbefore, with the total every 25 years.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Church membership history",
        out_path=args.out,
        fonts=load_fonts(),
        label_years=label_years,
    )


if __name__ == "__main__":
    main()
