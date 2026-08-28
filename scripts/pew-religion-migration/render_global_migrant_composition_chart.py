#!/usr/bin/env python3
"""Renders the "Religious composition of the world's migrants" PNG.
Reads only docs/datasets/pew-religion-migration/global-migrant-composition.json
(produced by global_migrant_composition.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-religion-migration/render_global_migrant_composition_chart.py \
    --out public/data-explorer/pew-religion-migration/global-migrant-composition.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-religion-migration"
    / "global-migrant-composition.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["global_composition"][r]["pct"] for r in rows}
    year = data["year"]
    total_m = data["total_migrants"] / 1_000_000

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={"Christian"},
        title="The world's migrants, by religion",
        subtitle=f"Religious composition of the world's ~{total_m:.0f} million\ninternational migrants, {year}.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew, world's migrants 1990-2020",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
