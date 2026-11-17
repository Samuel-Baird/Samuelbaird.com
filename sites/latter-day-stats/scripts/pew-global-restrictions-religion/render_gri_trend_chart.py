#!/usr/bin/env python3
"""Renders the global median Government Restrictions Index (GRI) line
chart, 2007-2022. Reads only
docs/datasets/pew-global-restrictions-religion/gri-trend.json (produced by
build_gri_trend.py in this folder). Uses the shared line-chart shape
(render_timeseries) in scripts/flagship-charts/common.py.

Usage:
  python scripts/pew-global-restrictions-religion/render_gri_trend_chart.py \
    --out public/data-explorer/pew-global-restrictions-religion/gri-trend.png
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_timeseries  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-global-restrictions-religion"
    / "gri-trend.json"
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
    values = {y: series[str(y)]["median_gri"] for y in years}
    statuses = {y: series[str(y)]["status"] for y in years}

    render_timeseries(
        years=years,
        values=values,
        statuses=statuses,
        title="Government restrictions on religion, worldwide",
        subtitle="Global median score on Pew's 0-10 Government\nRestrictions Index (GRI), by year.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew global restrictions on religion",
        out_path=args.out,
        fonts=load_fonts(),
        y_step=0.5,
        y_label_divisor=1,
        y_label_suffix="",
        x_tick_step=3,
    )


if __name__ == "__main__":
    main()
