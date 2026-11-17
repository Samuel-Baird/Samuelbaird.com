#!/usr/bin/env python3
"""Renders "Where Brazil's smaller faiths are concentrated" - a ranked
horizontal bar of all 27 Brazilian states/DF by IBGE's "Outras
religiosidades" ("Other religions") share of the population 10+, 2022
Census. Reads only
docs/datasets/lds-brazil-2022/smaller-faiths-by-state-2022.json (produced
by build_smaller_faiths_by_state.py in this folder). Uses the shared
magnitude-bar shape (render_magnitude_bar) in scripts/flagship-charts/common.py.

CRITICAL FRAMING: this is NOT an LDS-specific number - see
build_smaller_faiths_by_state.py's docstring and this dataset's README for
why. The title, subtitle, and caption below spell out the bucket's mixed
composition (Latter-day Saints, Jehovah's Witnesses, Spiritualists, Jews,
Muslims, Buddhists, and more) and must never be edited to imply an
LDS-specific estimate.

Usage:
  python scripts/lds-brazil-2022/render_smaller_faiths_by_state_chart.py \
    --out public/data-explorer/lds-brazil-2022/smaller-faiths-by-state-2022.png
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "lds-brazil-2022"
    / "smaller-faiths-by-state-2022.json"
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
        title="Where Brazil's smaller faiths are concentrated",
        subtitle="Share of each state's population (age 10+) in IBGE's \"Other\n"
                  "religions\" bucket - a mixed group including Latter-day Saints,\n"
                  "Jehovah's Witnesses, Spiritualists, Jews, Muslims, Buddhists,\n"
                  "and more. Not an LDS-specific figure. 2022 Census.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: 2022 Census (IBGE), own weighted tabulation",
        out_path=args.out,
        fonts=load_fonts(),
        value_suffix="%",
        axes_left=0.30,
        row_label_fontsize=13,
        value_label_fontsize=12,
    )


if __name__ == "__main__":
    main()
