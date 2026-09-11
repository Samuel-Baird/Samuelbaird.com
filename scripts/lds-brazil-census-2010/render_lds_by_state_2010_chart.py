#!/usr/bin/env python3
"""Renders "Self-identified Latter-day Saints by state" - a ranked
horizontal bar of all 27 Brazilian states/DF by LDS self-identification as
a share of each state's own population, 2010 Census (the LDS-specific
category IBGE published that year - see
build_lds_by_state_2010.py's docstring). Reads only
docs/datasets/lds-brazil-census-2010/lds-by-state-2010.json. Uses the
shared magnitude-bar shape (render_magnitude_bar) in
scripts/flagship-charts/common.py, with the same `row_label_fontsize`
override the 27-state lds-brazil-2022/smaller-faiths-by-state-2022.png
chart uses (the pipeline's normal 24pt floor overlaps at this row count).

Usage:
  python scripts/lds-brazil-census-2010/render_lds_by_state_2010_chart.py \
    --out public/data-explorer/lds-brazil-census-2010/lds-by-state-2010.png
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "lds-brazil-census-2010"
    / "lds-by-state-2010.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["state_order"]
    values = {r: data["states"][r]["pct"] for r in rows}
    highest = data["highest_state"]

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={highest},
        title="Where self-identified Latter-day Saints concentrate",
        subtitle="Share of each state's total population that told the 2010\n"
                  "Census taker they were Latter-day Saints - a real,\n"
                  "government-tabulated LDS-specific category IBGE published\n"
                  "only that year. Ranked by share, not raw count.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: 2010 Census (IBGE)",
        out_path=args.out,
        fonts=load_fonts(),
        value_suffix="%",
        value_decimals=2,
        axes_left=0.30,
        row_label_fontsize=13,
        value_label_fontsize=12,
    )


if __name__ == "__main__":
    main()
