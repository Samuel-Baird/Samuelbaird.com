#!/usr/bin/env python3
"""Renders the flagship PNG for the ATP Wave 117 in-person prayer/study
group item. Reads only
docs/datasets/pew-atp-w117-2022/nontech-prayer-groups.json (produced by
nontech_prayer_groups.py in this folder). Uses the shared magnitude-bar
shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-atp-w117-2022/render_nontech_prayer_groups_chart.py \
    --out public/data-explorer/pew-atp-w117-2022/nontech-prayer-groups.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-atp-w117-2022"
    / "nontech-prayer-groups.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["participates_in_person_study_group"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="Prayer groups and scripture study",
        subtitle="Share who participate in in-person prayer groups,\nscripture study groups, or religious education\nprograms, by religious tradition, November 2022.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 117 (2022)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
