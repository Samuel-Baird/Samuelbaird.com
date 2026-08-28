#!/usr/bin/env python3
"""Renders the flagship PNG for Religion in Latin America. Reads only
docs/datasets/pew-latin-america-2014/mormons-as-christian.json (produced by
mormons_as_christian.py in this folder). Uses the shared magnitude-bar
shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-latin-america-2014/render_mormons_as_christian_chart.py \
    --out public/data-explorer/pew-latin-america-2014/mormons-as-christian.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-latin-america-2014"
    / "mormons-as-christian.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["consider_mormons_christian"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="Are Mormons seen as Christian?",
        subtitle="Share across Latin America who consider Mormons to\nbe followers of the Christian faith, by their own religion.",
        caption_paragraphs=["@ithinkisam | data: Pew Religion in Latin America (2014)"],
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
