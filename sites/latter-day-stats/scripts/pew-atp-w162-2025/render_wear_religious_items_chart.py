#!/usr/bin/env python3
"""Renders the "Wearing your faith" PNG for ATP Wave 162. Reads only
docs/datasets/pew-atp-w162-2025/wear-religious-items.json (produced by
wear_religious_items.py in this folder). Uses the shared magnitude-bar shape
in scripts/flagship-charts/.

Usage:
  python scripts/pew-atp-w162-2025/render_wear_religious_items_chart.py \
    --out public/data-explorer/pew-atp-w162-2025/wear-religious-items.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-atp-w162-2025"
    / "wear-religious-items.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["wear_religious_items_weekly_plus"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="Wearing your faith",
        subtitle="Share who wear religious items or symbols, or carry them\nwith them, daily or weekly, by present religion, Feb. 2025.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 162 (2025)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
