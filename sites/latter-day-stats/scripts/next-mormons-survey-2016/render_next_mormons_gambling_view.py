#!/usr/bin/env python3
"""Renders "How do Latter-day Saints view gambling?" from
docs/datasets/next-mormons-survey-2016/next-mormons-gambling-view.json (transcribed from
published reporting on the 2016 Next Mormons Survey).

Usage:
  python scripts/next-mormons-survey-2016/render_next_mormons_gambling_view.py \
    --out public/data-explorer/next-mormons-survey-2016/next-mormons-gambling-view.png
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "flagship-charts"))
sys.path.insert(0, str(HERE.parent))
from common import load_fonts, render_magnitude_bar  # noqa: E402
from chart_style import CONTEXT_GRAY, DIV_NEG_RED, DIV_POS_GREEN  # noqa: E402

DATA_JSON = HERE.parent.parent / "docs" / "datasets" / "next-mormons-survey-2016" / "next-mormons-gambling-view.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    rows = data["item_order"]
    render_magnitude_bar(
        rows=rows,
        values=data["view_pct"],
        highlight_rows=None,
        row_colors={
            "Morally wrong": DIV_NEG_RED,
            "Not a moral issue": CONTEXT_GRAY,
            "Morally acceptable": DIV_POS_GREEN,
        },
        title="How do Latter-day Saints view gambling?",
        subtitle="Share of self-identified Latter-day Saints who say gambling is\nmorally wrong, not a moral issue, or morally acceptable.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Next Mormons Survey 2016",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
