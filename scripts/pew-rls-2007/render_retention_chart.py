#!/usr/bin/env python3
"""Renders the "Who stays in the religion they were raised in?" PNG for
the 2007 U.S. Religious Landscape Survey. Reads only
docs/datasets/pew-rls-2007/retention-rate.json (produced by
retention_rate.py in this folder). Uses the shared magnitude-bar shape in
scripts/flagship-charts/.

Usage:
  python scripts/pew-rls-2007/render_retention_chart.py \
    --out public/data-explorer/pew-rls-2007/retention-rate.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2007"
    / "retention-rate.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["retained_pct"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="Who stays in the religion they were raised in?",
        subtitle="Share raised in each tradition who still identify\nwith that same tradition as adults.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 2007 RLS",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
