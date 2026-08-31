#!/usr/bin/env python3
"""Renders the "Who attends weekly?" PNG for the 2014 Religious Landscape
Study. Reads only docs/datasets/pew-rls-2014/weekly-attendance.json
(produced by weekly_attendance.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-rls-2014/render_weekly_attendance_chart.py \
    --out public/data-explorer/pew-rls-2014/weekly-attendance.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2014"
    / "weekly-attendance.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["attend_weekly"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="Who attends religious services weekly?",
        subtitle="Share attending religious services once a week\nor more, by religious tradition, 2014.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 2014 RLS",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
