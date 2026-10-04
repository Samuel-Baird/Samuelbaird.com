#!/usr/bin/env python3
"""Renders "Does attending church change views on gambling?" from
docs/datasets/gallup-values-beliefs-gambling/acceptable-by-attendance.json.

Usage:
  python scripts/gallup-values-beliefs-gambling/render_acceptable_by_attendance.py \
    --out public/data-explorer/gallup-values-beliefs-gambling/acceptable-by-attendance.png
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = HERE.parent.parent / "docs" / "datasets" / "gallup-values-beliefs-gambling" / "acceptable-by-attendance.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    rows = sorted(data["attendance_order"], key=lambda r: -data["acceptable_pct"][r])
    render_magnitude_bar(
        rows=rows,
        values=data["acceptable_pct"],
        highlight_rows=None,
        title="Does attending church change views on gambling?",
        subtitle="Share of U.S. adults who say gambling is morally acceptable, by\nhow often they attend religious services, 2018.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Gallup Values & Beliefs 2018",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
