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

    render_timeseries_by_direction(
        years=years,
        values=values,
        title="Where did membership ever decrease?",
        subtitle="Worldwide Church membership, 1830-2025, colored\nby whether it grew or shrank from the year before.",
        caption_paragraphs=[
            "Four years saw a net decrease: 1839 (following the 1838 Missouri Extermination "
            "Order), and 1855-1857 (the difficult early Utah years). Every other year grew.",
            data["source"],
        ],
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
