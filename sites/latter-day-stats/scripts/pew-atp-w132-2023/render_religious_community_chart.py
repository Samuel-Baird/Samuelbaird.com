#!/usr/bin/env python3
"""Renders the "Involved in a religious community" PNG for ATP Wave 132.
Reads only docs/datasets/pew-atp-w132-2023/religious-community.json
(produced by religious_community.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-atp-w132-2023/render_religious_community_chart.py \
    --out public/data-explorer/pew-atp-w132-2023/religious-community.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-atp-w132-2023"
    / "religious-community.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["involved_in_religious_community"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="Involved in a religious community",
        subtitle="Share involved in “a religious community, such as a church or\nreligious congregation,” by religion, 2023.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 132 (2023)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
