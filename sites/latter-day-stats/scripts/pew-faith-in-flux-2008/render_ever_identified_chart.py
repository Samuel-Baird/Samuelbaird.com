#!/usr/bin/env python3
"""Renders the "Have you ever identified as..." PNG for Faith in Flux.
Reads only docs/datasets/pew-faith-in-flux-2008/ever-identified-with.json
(produced by ever_identified_with.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/, highlighting the Mormon
row (the only row this chart singles out - a battery of named identities,
not a group-identity chart, so `group_identity` stays False/default and
`highlight_rows` does the highlighting instead).

Usage:
  python scripts/pew-faith-in-flux-2008/render_ever_identified_chart.py \
    --out public/data-explorer/pew-faith-in-flux-2008/ever-identified-with.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-faith-in-flux-2008"
    / "ever-identified-with.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["identity_order"]
    values = {r: data["ever_identified_pct"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={"Mormon"},
        title="Have you ever identified as...?",
        subtitle="Share of religious switchers who have EVER identified\nwith each religion, not just as their current or\nchildhood faith.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew Faith in Flux (2008)",
        out_path=args.out,
        fonts=load_fonts(),
        axes_left=0.50,
    )


if __name__ == "__main__":
    main()
