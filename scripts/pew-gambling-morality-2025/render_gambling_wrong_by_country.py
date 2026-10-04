#!/usr/bin/env python3
"""Renders "Where is gambling seen as morally wrong?" from
docs/datasets/pew-gambling-morality-2025/gambling-morally-wrong-by-country.json.
Shared magnitude-bar shape; the United States is the highlighted subject (a
country, not a religious identity), with the 27-row-style label override.

Usage:
  python scripts/pew-gambling-morality-2025/render_gambling_wrong_by_country.py \
    --out public/data-explorer/pew-gambling-morality-2025/gambling-morally-wrong-by-country.png
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "flagship-charts"))
sys.path.insert(0, str(HERE.parent))
from common import load_fonts, render_magnitude_bar  # noqa: E402
from chart_style import sort_groups  # noqa: E402

DATA_JSON = HERE.parent.parent / "docs" / "datasets" / "pew-gambling-morality-2025" / "gambling-morally-wrong-by-country.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()
    values = json.loads(args.data.read_text(encoding="utf-8"))["wrong_pct"]
    rows = sort_groups(list(values), lambda r: values[r])
    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={"United States"},
        title="Where is gambling seen as morally wrong?",
        subtitle="Share of adults who say gambling is morally wrong, 25 countries,\n2025. The United States is highlighted.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew Global Attitudes 2025",
        out_path=args.out,
        fonts=load_fonts(),
        axes_left=0.26,
        row_label_fontsize=13,
        value_label_fontsize=12,
    )


if __name__ == "__main__":
    main()
