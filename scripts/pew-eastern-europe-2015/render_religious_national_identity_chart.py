#!/usr/bin/env python3
"""Renders the "Being [Orthodox/Catholic] and belonging" PNG for Pew's
2015-2016 Central and Eastern Europe survey. Reads only
docs/datasets/pew-eastern-europe-2015/religious-national-identity.json
(produced by religious_national_identity.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-eastern-europe-2015/render_religious_national_identity_chart.py \
    --out public/data-explorer/pew-eastern-europe-2015/religious-national-identity.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import load_fonts, render_magnitude_bar  # noqa: E402
from chart_style import sort_groups  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-eastern-europe-2015"
    / "religious-national-identity.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    results = data["important_to_share_dominant_faith"]
    values = {r: results[r]["pct"] for r in data["group_order"]}
    rows = sort_groups(data["group_order"], lambda r: values[r])
    # Highlight the top 6 (the "belief and belonging are fused" half of the
    # story) in --accent; the bottom 6 stay gray as the contrasting context.
    top_six = set(sorted(rows, key=lambda r: -values[r])[:6])

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=top_six,
        title="Being Orthodox (or Catholic) and belonging",
        subtitle="Share saying it's \"very important\" to belong to their\ncountry's dominant church to be truly a citizen, by\ncountry (6 highest, 6 lowest of 18 surveyed), 2015-16.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew Central & Eastern Europe (2017)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
