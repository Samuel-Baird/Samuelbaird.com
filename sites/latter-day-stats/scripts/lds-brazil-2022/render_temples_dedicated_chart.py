#!/usr/bin/env python3
"""Renders the Brazil temple-dedication line chart. Reads only
docs/datasets/lds-brazil-2022/temples-dedicated-by-year.json (produced by
build_temples_dedicated_by_year.py in this folder). Uses the shared
line-chart shape (render_timeseries) in scripts/flagship-charts/common.py,
treating the cumulative temple count as the plotted value - every point
is a real, exact dedication-year total (`status: reported`), not
interpolated, so the whole line renders solid.

10 plotted points across 1978-2026, several clustered within a few years
of each other (2000/2002, then 2022/2023/2024/2026) - labeling every real
year (x_tick_step=1) collides those clustered 4-digit labels into an
unreadable run. x_tick_step=10 keeps only round-decade labels plus the
series' own forced first/last year (1978, 2000, 2026 here - same
first/last-forcing logic membership-by-year's chart already relies on),
leaving every real point still plotted as its own marker on the line even
where its year isn't separately labeled. y_step=2/y_label_divisor=1/
y_label_suffix="" because these are whole-number temple counts (1-12),
not the module's membership-scale (hundred-thousands/millions) default.

Usage:
  python scripts/lds-brazil-2022/render_temples_dedicated_chart.py \
    --out public/data-explorer/lds-brazil-2022/temples-dedicated-by-year.png
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_timeseries  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "lds-brazil-2022"
    / "temples-dedicated-by-year.json"
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
    values = {y: series[str(y)]["count"] for y in years}
    statuses = {y: series[str(y)]["status"] for y in years}

    n_construction = len(data["under_construction_or_announced"]["under_construction"])
    n_announced = len(data["under_construction_or_announced"]["announced"])
    n_pending = n_construction + n_announced

    render_timeseries(
        years=years,
        values=values,
        statuses=statuses,
        title="Brazil temples dedicated, 1978-2026",
        subtitle="Cumulative count of dedicated Brazil temples by dedication year. 5 of the 12\n"
                  f"were dedicated in just the last 4 years; {n_pending} more are under construction or announced.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Church chronology + temple list",
        out_path=args.out,
        fonts=load_fonts(),
        y_step=2,
        y_label_divisor=1,
        y_label_suffix="",
        x_tick_step=10,
    )


if __name__ == "__main__":
    main()
