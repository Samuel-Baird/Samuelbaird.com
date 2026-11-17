#!/usr/bin/env python3
"""Renders the "Weekly prayer or Scripture study groups" PNG for the 2007
U.S. Religious Landscape Survey. Reads only
docs/datasets/pew-rls-2007/prayer-scripture-groups.json (produced by
prayer_scripture_groups.py in this folder). Uses the shared magnitude-bar
shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-rls-2007/render_prayer_scripture_groups_chart.py \
    --out public/data-explorer/pew-rls-2007/prayer-scripture-groups.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2007"
    / "prayer-scripture-groups.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["weekly_prayer_or_scripture_group"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="Weekly prayer or Scripture study groups",
        subtitle="Share who participate in a prayer group, Scripture study\ngroup, or religious education program at least weekly,\nby religious tradition, 2007.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 2007 RLS",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
