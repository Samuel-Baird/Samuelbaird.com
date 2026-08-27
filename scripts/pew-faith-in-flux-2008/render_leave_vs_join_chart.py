#!/usr/bin/env python3
"""Renders the "Leaving, or joining?" PNG for Faith in Flux. Reads only
docs/datasets/pew-faith-in-flux-2008/leave-vs-join.json (produced by
leave_vs_join.py in this folder). Uses the shared magnitude-bar shape in
scripts/flagship-charts/.

Usage:
  python scripts/pew-faith-in-flux-2008/render_leave_vs_join_chart.py \
    --out public/data-explorer/pew-faith-in-flux-2008/leave-vs-join.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-faith-in-flux-2008"
    / "leave-vs-join.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["motive_order"]
    values = {r: data["motive_pct"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="Leaving, or joining?",
        subtitle="When people changed religion, was it driven more by\nwanting to leave the old one, or join the new one?",
        caption_paragraphs=[
            "Population: all recontacted respondents who left the religion they were "
            "raised in; don't know/refused excluded.",
            f"Pew Research Center's Faith in Flux (2008 Conversion Recontact Survey) · "
            f"N = {data['valid_unweighted_n']:,} recontacted adults",
            data["source"],
        ],
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
