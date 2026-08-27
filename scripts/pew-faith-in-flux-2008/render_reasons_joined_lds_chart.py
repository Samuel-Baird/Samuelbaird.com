#!/usr/bin/env python3
"""Renders the flagship PNG for Faith in Flux. Reads only
docs/datasets/pew-faith-in-flux-2008/reasons-joined-lds.json (produced by
reasons_joined_lds.py in this folder). Uses the shared magnitude-bar shape
in scripts/flagship-charts/.

Usage:
  python scripts/pew-faith-in-flux-2008/render_reasons_joined_lds_chart.py \
    --out public/data-explorer/pew-faith-in-flux-2008/reasons-joined-lds.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-faith-in-flux-2008"
    / "reasons-joined-lds.json"
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
        title="Why converts say they joined the LDS Church",
        subtitle="Share of LDS converts calling each factor an\nimportant reason they became Mormon.",
        caption_paragraphs=[
            f"Population: respondents who converted to Mormonism (n={data['lds_converts_unweighted_n']}), "
            "a small subgroup of this recontact survey; each reason's own don't know/refused excluded.",
            f"Pew Research Center's Faith in Flux (2008 Conversion Recontact Survey) · "
            f"N = {data['total_unweighted_n']:,} recontacted adults overall",
            data["source"],
        ],
        out_path=args.out,
        fonts=load_fonts(),
        axes_left=0.52,
    )


if __name__ == "__main__":
    main()
