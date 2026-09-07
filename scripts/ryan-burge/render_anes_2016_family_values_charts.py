#!/usr/bin/env python3
"""Renders the four ANES 2016 family-values / gender-role magnitude bars from
the JSON written by anes_2016_family_values.py
(docs/datasets/ryan-burge/anes-2016-*.json), using the shared magnitude-bar
shape in scripts/flagship-charts/common.py and chart_style.sort_groups for
row order (highest to lowest; "Other religion" sinks below the substantive
rows, "All U.S. adults" to the very bottom). Same conventions as
render_faith_matters_2011_charts.py.

Usage:
  python scripts/ryan-burge/render_anes_2016_family_values_charts.py \
    --out-dir public/data-explorer/anes-2016
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA_DIR = (Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "ryan-burge").resolve()
HANDLE = "@ithinkisam | data: ANES 2016 via Ryan Burge"

CHARTS = [
    {
        "json": "anes-2016-man-works-woman-home.json", "key": "man_works_woman_home_better",
        "png": "man-works-woman-home.png",
        "title": "Better if the man works and the woman takes care of the home",
        "subtitle": "Share saying much, somewhat, or slightly better (vs. no difference\nor worse), by religious tradition, 2016.",
    },
    {
        "json": "anes-2016-working-mother-bond.json", "key": "working_mother_bond_harder",
        "png": "working-mother-bond.png",
        "title": "Harder for a working mother to bond with her child",
        "subtitle": "Share saying slightly, somewhat, or a great deal harder,\nby religious tradition, 2016.",
    },
    {
        "json": "anes-2016-traditional-family-ties.json", "key": "traditional_family_ties_agree",
        "png": "traditional-family-ties.png",
        "title": "Fewer problems with more emphasis on traditional family ties",
        "subtitle": "Share agreeing strongly or somewhat, by religious tradition, 2016.",
    },
    {
        "json": "anes-2016-newer-lifestyles.json", "key": "newer_lifestyles_breakdown_agree",
        "png": "newer-lifestyles.png",
        "title": "Newer lifestyles are contributing to the breakdown of society",
        "subtitle": "Share agreeing strongly or somewhat, by religious tradition, 2016.",
    },
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    fonts = load_fonts()

    for c in CHARTS:
        with open(DATA_DIR / c["json"], encoding="utf-8") as f:
            data = json.load(f)
        results = data[c["key"]]
        values = {r: results[r]["pct"] for r in data["group_order"]}
        rows = sort_groups(data["group_order"], lambda r: values[r])
        render_magnitude_bar(
            rows=rows,
            values=values,
            highlight_rows=None,
            group_identity=True,
            title=c["title"],
            subtitle=c["subtitle"],
            caption_paragraphs=[],
            handle=HANDLE,
            out_path=args.out_dir / c["png"],
            fonts=fonts,
        )
        print("wrote", args.out_dir / c["png"])


if __name__ == "__main__":
    main()
