#!/usr/bin/env python3
"""Renders the "Religious duty to convert nonbelievers" PNG for
pew-black-faith-2021. Reads only
docs/datasets/pew-black-faith-2021/convert-duty.json (produced by
convert_duty.py in this folder). Uses the shared magnitude-bar shape in
scripts/flagship-charts/.

Usage:
  python scripts/pew-black-faith-2021/render_convert_duty_chart.py \
    --out public/data-explorer/pew-black-faith-2021/convert-duty.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-black-faith-2021"
    / "convert-duty.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["believes_duty_to_convert"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="A duty to convert nonbelievers?",
        subtitle="Share of Black Americans who believe people of faith have a\nreligious duty to try to convert nonbelievers, by religion.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew Faith Among Black Americans (2021)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
