#!/usr/bin/env python3
"""Renders the "Talk about religion with spouse a lot" PNG for the 2014 RLS recontact survey. Reads only
docs/datasets/pew-rls-2014-recontact/spouse-talk-religion.json (produced by spouse_talk_religion.py in
this folder, which already applies chart_style.sort_groups to group_order).
Uses the shared magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-rls-2014-recontact/render_spouse_talk_religion_chart.py \\
    --out public/data-explorer/pew-rls-2014-recontact/spouse-talk-religion.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2014-recontact"
    / "spouse-talk-religion.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["talk_religion_with_spouse_a_lot"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title='Talk about religion with my spouse — a lot',
        subtitle='Share of married or partnered adults who talk about religion with\ntheir spouse or partner "a lot," by current tradition.',
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 2014 RLS Recontact",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
