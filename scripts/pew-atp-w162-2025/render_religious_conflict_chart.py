#!/usr/bin/env python3
"""Renders the "Feeling out of step with mainstream culture" PNG for ATP
Wave 162. Reads only docs/datasets/pew-atp-w162-2025/religious-conflict.json
(produced by religious_conflict.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-atp-w162-2025/render_religious_conflict_chart.py \
    --out public/data-explorer/pew-atp-w162-2025/religious-conflict.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-atp-w162-2025"
    / "religious-conflict.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["religious_belief_conflict"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={"Mormon"},
        title="Feeling out of step with mainstream culture",
        subtitle="Share who feel at least some conflict between their own\nreligious beliefs and mainstream American culture, Feb. 2025.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 162 (2025)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
