#!/usr/bin/env python3
"""Renders the "Is Mormonism a Christian religion?" PNG for the 2011
National Survey of Mormons. Reads only
docs/datasets/pew-mormon-survey-2011/mormonism-christian.json (produced by
mormonism_christian.py in this folder - see that script's docstring for
where the "U.S. general public" row comes from). Uses the shared
100%-stack shape in scripts/flagship-charts/common.py.

Usage:
  python scripts/pew-mormon-survey-2011/render_mormonism_christian_chart.py \
    --out public/data-explorer/pew-mormon-survey-2011/mormonism-christian.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_100_stack  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-mormon-survey-2011"
    / "mormonism-christian.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    render_100_stack(
        rows=data["row_order"],
        segment_order=data["segment_order"],
        values=data["results"],
        title="Is Mormonism a Christian religion?",
        subtitle="Mormons themselves vs. the U.S. general public.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 2011 Mormon Survey",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
