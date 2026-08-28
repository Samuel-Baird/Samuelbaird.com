#!/usr/bin/env python3
"""Renders the "A feeling of connection with something beyond this world" PNG
for ATP Wave 132. Reads only
docs/datasets/pew-atp-w132-2023/beyond-this-world.json (produced by
beyond_this_world.py in this folder). Uses the shared magnitude-bar shape in
scripts/flagship-charts/.

Usage:
  python scripts/pew-atp-w132-2023/render_beyond_this_world_chart.py \
    --out public/data-explorer/pew-atp-w132-2023/beyond-this-world.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-atp-w132-2023"
    / "beyond-this-world.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["felt_beyond_this_world_connection"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={"Mormon"},
        title="A feeling of connection beyond this world",
        subtitle="Share who have ever had a sudden or unexpected feeling of\nconnection with something from beyond this world, by religion, 2023.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 132 (2023)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
