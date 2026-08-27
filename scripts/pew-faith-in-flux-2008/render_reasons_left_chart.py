#!/usr/bin/env python3
"""Renders the "Why do people leave their childhood religion?" PNG for
Faith in Flux. Reads only
docs/datasets/pew-faith-in-flux-2008/reasons-left-religion.json (produced
by reasons_left_religion.py in this folder). Uses the shared magnitude-bar
shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-faith-in-flux-2008/render_reasons_left_chart.py \
    --out public/data-explorer/pew-faith-in-flux-2008/reasons-left-religion.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-faith-in-flux-2008"
    / "reasons-left-religion.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["reason_order"]
    values = {r: data["important_reason_pct"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="Why do people leave their childhood religion?",
        subtitle="Share of religious switchers calling each factor an\nimportant reason they left the religion they grew up in.",
        caption_paragraphs=[
            "Population: all recontacted respondents who left the religion they were "
            "raised in; each reason's own don't know/refused excluded.",
            f"Pew Research Center's Faith in Flux (2008 Conversion Recontact Survey) · "
            f"N = {data['total_unweighted_n']:,} recontacted adults",
            data["source"],
        ],
        out_path=args.out,
        fonts=load_fonts(),
        axes_left=0.52,
    )


if __name__ == "__main__":
    main()
