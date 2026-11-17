#!/usr/bin/env python3
"""Renders the "Who calls themselves 'born-again'?" PNG for the 2014
Religious Landscape Study. Reads only
docs/datasets/pew-rls-2014/born-again-identity.json (produced by
born_again_identity.py in this folder). Uses the shared magnitude-bar shape
in scripts/flagship-charts/.

Usage:
  python scripts/pew-rls-2014/render_born_again_identity_chart.py \
    --out public/data-explorer/pew-rls-2014/born-again-identity.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2014"
    / "born-again-identity.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["born_again_or_evangelical"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="Who calls themselves “born-again”?",
        subtitle="Share of Christians who describe themselves as a\n“born-again” or evangelical Christian, by religious\ntradition, 2014.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 2014 RLS",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
