#!/usr/bin/env python3
"""Renders the "Did switching strengthen their faith?" PNG for Faith in
Flux. Reads only
docs/datasets/pew-faith-in-flux-2008/faith-strength-before-after.json
(produced by faith_strength_before_after.py in this folder). Uses the
shared magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-faith-in-flux-2008/render_faith_strength_chart.py \
    --out public/data-explorer/pew-faith-in-flux-2008/faith-strength-before-after.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-faith-in-flux-2008"
    / "faith-strength-before-after.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["time_order"]
    values = {r: data["strong_faith_pct"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={"Now"},
        title="Did switching strengthen their faith?",
        subtitle="Share of religious switchers with strong faith,\nas a teenager vs. now.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew Faith in Flux (2008)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
