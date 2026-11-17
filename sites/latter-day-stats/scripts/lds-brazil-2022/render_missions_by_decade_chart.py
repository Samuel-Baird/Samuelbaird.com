#!/usr/bin/env python3
"""Renders the Brazil LDS-mission-count line chart. Reads only
docs/datasets/lds-brazil-2022/missions-by-decade.json (produced by
build_missions_by_decade.py in this folder). Uses the shared line-chart
shape (render_timeseries) in scripts/flagship-charts/common.py, same
pattern as render_membership_by_year_chart.py in this same folder - 8
real, sparse decade-by-decade points, every one `status: reported`, no
interpolation.

x_tick_step=10 matches membership-by-year's own choice: it labels every
real decade point (1950-2010) and the code's own "force first/last year
into x_ticks" logic pulls in the odd final 2025 point too, exactly as it
does for that chart's own 2025 endpoint.

Usage:
  python scripts/lds-brazil-2022/render_missions_by_decade_chart.py \
    --out public/data-explorer/lds-brazil-2022/missions-by-decade.png
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_timeseries  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "lds-brazil-2022"
    / "missions-by-decade.json"
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
    values = {y: series[str(y)]["missions"] for y in years}
    statuses = {y: series[str(y)]["status"] for y in years}

    render_timeseries(
        years=years,
        values=values,
        statuses=statuses,
        title="Brazil LDS missions, 1950-2025",
        subtitle="Number of Church missions organized in Brazil. Counts roughly doubled\n"
                  "each decade through 1990, then grew far more slowly after 2000.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Reaching the Nations (cumorah.com)",
        out_path=args.out,
        fonts=load_fonts(),
        y_step=5,
        y_label_divisor=1,
        y_label_suffix="",
        x_tick_step=10,
    )


if __name__ == "__main__":
    main()
