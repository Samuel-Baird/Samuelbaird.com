#!/usr/bin/env python3
"""Renders the "Communion after remarriage, without an annulment" PNG for
the 2015 Survey of U.S. Catholics and Family Life. Reads only
docs/datasets/pew-catholic-family-2015/annulment-communion.json (produced by
annulment_communion.py in this folder). Uses the shared magnitude-bar shape
in scripts/flagship-charts/.

Usage:
  python scripts/pew-catholic-family-2015/render_annulment_communion_chart.py \
    --out public/data-explorer/pew-catholic-family-2015/annulment-communion.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-catholic-family-2015"
    / "annulment-communion.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["should_allow_communion_after_remarriage"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="Communion after remarriage, no annulment",
        subtitle="Share of U.S. Catholics saying the Church should let\ndivorced Catholics who remarry without an annulment take\nCommunion, by Mass attendance, 2015.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 2015 U.S. Catholics & Family Life",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
