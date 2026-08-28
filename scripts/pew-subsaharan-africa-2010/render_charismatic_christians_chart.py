#!/usr/bin/env python3
"""Renders the "Charismatic Christianity across Sub-Saharan Africa" PNG.
Reads only docs/datasets/pew-subsaharan-africa-2010/charismatic-christians.json
(produced by charismatic_christians.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-subsaharan-africa-2010/render_charismatic_christians_chart.py \
    --out public/data-explorer/pew-subsaharan-africa-2010/charismatic-christians.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-subsaharan-africa-2010"
    / "charismatic-christians.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["charismatic_christian_share"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={"Guinea Bissau"},
        title="Charismatic Christianity across Sub-Saharan Africa",
        subtitle="Share of Christians who describe themselves as a\nCharismatic Christian, by country, top 12 of 18, 2008-09.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew Sub-Saharan Africa (2010)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
