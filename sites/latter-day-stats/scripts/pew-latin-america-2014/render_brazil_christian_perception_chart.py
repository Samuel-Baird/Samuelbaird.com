#!/usr/bin/env python3
"""Renders the Brazil-themed PNG for brazil_christian_perception.py. Reads
only docs/datasets/pew-latin-america-2014/brazil-christian-perception.json.
Uses brazil_theme.render_brazil_bar - a deliberate one-off flag-colored
exception to this pipeline's locked palette (see that module's own docstring).

Usage:
  python scripts/pew-latin-america-2014/render_brazil_christian_perception_chart.py \
    --out public/data-explorer/pew-latin-america-2014/brazil-christian-perception.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brazil_theme import load_fonts, render_brazil_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-latin-america-2014"
    / "brazil-christian-perception.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["consider_christian_brazil"][r]["pct"] for r in rows}

    render_brazil_bar(
        rows=rows,
        values=values,
        highlight_rows={data["highlight"]},
        title="Do you consider them to be Christian?",
        subtitle="Share of Brazilians answering yes, asked individually about\neach group.",
        handle="@ithinkisam | data: Pew Religion in Latin America (2014)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
