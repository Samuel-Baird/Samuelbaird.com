#!/usr/bin/env python3
"""Renders the "Whose decision was it to leave?" PNG for Faith in Flux.
Reads only docs/datasets/pew-faith-in-flux-2008/leaving-decision-maker.json
(produced by leaving_decision_maker.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-faith-in-flux-2008/render_leaving_decision_chart.py \
    --out public/data-explorer/pew-faith-in-flux-2008/leaving-decision-maker.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-faith-in-flux-2008"
    / "leaving-decision-maker.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["decision_order"]
    values = {r: data["decision_pct"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="Whose decision was it to leave?",
        subtitle="Among people who left their childhood religion,\nwho mainly made that decision?",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew Faith in Flux (2008)",
        out_path=args.out,
        fonts=load_fonts(),
        axes_left=0.46,
    )


if __name__ == "__main__":
    main()
