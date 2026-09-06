#!/usr/bin/env python3
"""Renders the "Churches too concerned with money and power" PNG for the
2014 Religious Landscape Study. Reads only
docs/datasets/pew-rls-2014/church-too-much-money-power.json (produced by
church_too_much_money_power.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-rls-2014/render_church_too_much_money_power_chart.py \
    --out public/data-explorer/pew-rls-2014/church-too-much-money-power.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2014"
    / "church-too-much-money-power.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["agrees_church_too_much_money_power"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="“Churches are too concerned with money and power”",
        subtitle="Share who agree churches and other religious\norganizations are too concerned with money and power,\nby religious tradition, 2014.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 2014 RLS",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
