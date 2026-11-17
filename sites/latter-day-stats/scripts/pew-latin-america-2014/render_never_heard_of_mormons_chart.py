#!/usr/bin/env python3
"""Renders the Brazil-themed PNG for never_heard_of_mormons.py. Reads only
docs/datasets/pew-latin-america-2014/never-heard-of-mormons.json. Uses
brazil_theme.render_brazil_bar - a deliberate one-off flag-colored exception
to this pipeline's locked palette (see that module's own docstring).

Usage:
  python scripts/pew-latin-america-2014/render_never_heard_of_mormons_chart.py \
    --out public/data-explorer/pew-latin-america-2014/never-heard-of-mormons.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brazil_theme import load_fonts, render_brazil_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-latin-america-2014"
    / "never-heard-of-mormons.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["country_order"]
    values = {r: data["never_heard_of_mormons"][r]["pct"] for r in rows}

    render_brazil_bar(
        rows=rows,
        values=values,
        highlight_rows={data["highlight"]},
        title="“Never heard of” the Mormons?",
        subtitle="Asked “Do you personally consider Mormons to be followers\nof the Christian faith, or not?” — share who volunteered\nthey'd never heard of the group, by country.",
        handle="@ithinkisam | data: Pew Religion in Latin America (2014)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
