#!/usr/bin/env python3
"""Renders the flagship PNG for the 2014 Religious Landscape Study.
Reads only docs/datasets/pew-rls-2014/samesex-marriage.json (produced by
samesex_marriage.py in this folder). Uses the shared magnitude-bar shape in
scripts/flagship-charts/.

Usage:
  python scripts/pew-rls-2014/render_samesex_marriage_chart.py \
    --out public/data-explorer/pew-rls-2014/samesex-marriage.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2014"
    / "samesex-marriage.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["favor_samesex_marriage"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={"Mormon"},
        title="Support for same-sex marriage, 2014",
        subtitle="Share who favor or strongly favor allowing gays\nand lesbians to marry legally, by religious tradition.",
        caption_paragraphs=[
            "Population: current religious tradition; top-two-box (strongly favor + favor); "
            "don't know/refused excluded.",
            f"Pew Research Center's 2014 Religious Landscape Study · "
            f"N = {data['total_unweighted_n']:,} U.S. adults",
            data["source"],
        ],
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
