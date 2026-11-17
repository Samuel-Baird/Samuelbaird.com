#!/usr/bin/env python3
"""Renders "Where is gambling seen as morally acceptable?" from
docs/datasets/pew-gambling-morality-2025/gambling-morally-wrong-by-country.json
(its `acceptable_pct` block). Same flag-colored bars and flag icons as
render_gambling_wrong_by_country.py.

Usage:
  python scripts/pew-gambling-morality-2025/render_gambling_acceptable_by_country.py \
    --out public/data-explorer/pew-gambling-morality-2025/gambling-morally-acceptable-by-country.png
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "flagship-charts"))
sys.path.insert(0, str(HERE.parent))
from common import load_fonts, render_magnitude_bar  # noqa: E402
from chart_style import sort_groups  # noqa: E402
from render_gambling_wrong_by_country import DATA_JSON, FLAG_COLORS, FLAG_DIR, ISO2  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()
    values = json.loads(args.data.read_text(encoding="utf-8"))["acceptable_pct"]
    rows = sort_groups(list(values), lambda r: values[r])
    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        row_colors=FLAG_COLORS,
        bar_images={r: FLAG_DIR / f"{ISO2[r]}.png" for r in rows},
        title="Where is gambling seen as morally acceptable?",
        subtitle="Share of adults who say gambling is morally acceptable,\nby country, 2025.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew Global Attitudes 2025",
        out_path=args.out,
        fonts=load_fonts(),
        axes_left=0.30,
        row_label_fontsize=13,
        value_label_fontsize=12,
    )


if __name__ == "__main__":
    main()
