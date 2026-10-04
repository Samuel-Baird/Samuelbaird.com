#!/usr/bin/env python3
"""Renders the two Gallup 2018 gambling-by-attendance charts (morally
acceptable, morally wrong) from
docs/datasets/gallup-values-beliefs-gambling/acceptable-by-attendance.json.
Bars are a three-step ramp by attendance (lighter = attends less): green for
"acceptable", oxblood-red for "wrong", matching the Latter-day Saint
Next Mormons chart's colors.

Usage:
  python scripts/gallup-values-beliefs-gambling/render_acceptable_by_attendance.py \
    --out-dir public/data-explorer/gallup-values-beliefs-gambling
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = HERE.parent.parent / "docs" / "datasets" / "gallup-values-beliefs-gambling" / "acceptable-by-attendance.json"

# Seldom/never -> At least weekly, light to dark.
GREEN_RAMP = ["#6FAE9C", "#3F8A77", "#1F6E5E"]
RED_RAMP = ["#C98585", "#A65252", "#7C2D2D"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    order = data["attendance_order"]
    fonts = load_fonts()
    for key, word, ramp, fname in (
        ("acceptable_pct", "acceptable", GREEN_RAMP, "acceptable-by-attendance.png"),
        ("wrong_pct", "wrong", RED_RAMP, "wrong-by-attendance.png"),
    ):
        values = data[key]
        rows = sorted(order, key=lambda r: -values[r])
        render_magnitude_bar(
            rows=rows,
            values=values,
            highlight_rows=None,
            row_colors=dict(zip(order, ramp)),
            title=f"Share who view gambling as morally {word}, by church attendance",
            subtitle=f"Share of U.S. adults who say gambling is morally {word}, by\nhow often they attend religious services, 2018.",
            caption_paragraphs=[],
            handle="@ithinkisam | data: Gallup Values & Beliefs 2018",
            out_path=args.out_dir / fname,
            fonts=fonts,
        )


if __name__ == "__main__":
    main()
