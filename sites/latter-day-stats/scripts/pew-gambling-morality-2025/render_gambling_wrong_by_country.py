#!/usr/bin/env python3
"""Renders "Where is gambling seen as morally wrong?" from
docs/datasets/pew-gambling-morality-2025/gambling-morally-wrong-by-country.json.
Shared magnitude-bar shape; each bar is a solid color taken from its country's
flag (FLAG_COLORS) and a small flag (flags/<iso2>.png, from flagcdn.com) sits
beside the label.

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

FLAG_DIR = HERE / "flags"
ISO2 = {
    "Indonesia": "id", "India": "in", "Turkey": "tr", "South Korea": "kr", "Nigeria": "ng",
    "Italy": "it", "Greece": "gr", "Brazil": "br", "Kenya": "ke", "Israel": "il",
    "South Africa": "za", "Argentina": "ar", "Mexico": "mx", "Netherlands": "nl",
    "Poland": "pl", "Spain": "es", "Japan": "jp", "United Kingdom": "gb",
    "Australia": "au", "Sweden": "se", "France": "fr", "Germany": "de",
    "Hungary": "hu", "United States": "us", "Canada": "ca",
}
# One characteristic color from each flag, chosen to stay readable on white.
FLAG_COLORS = {
    "Indonesia": "#CE1126", "India": "#138808", "Turkey": "#E30A17", "South Korea": "#003478",
    "Nigeria": "#008751", "Italy": "#009246", "Greece": "#0D5EAF", "Brazil": "#009C3B",
    "Kenya": "#BB0000", "Israel": "#0038B8", "South Africa": "#007749", "Argentina": "#74ACDF",
    "Mexico": "#006847", "Netherlands": "#21468B", "Poland": "#DC143C", "Spain": "#AA151B",
    "Japan": "#BC002D", "United Kingdom": "#012169", "Australia": "#00247D", "Sweden": "#006AA7",
    "France": "#0055A4", "Germany": "#DD0000", "Hungary": "#477050", "United States": "#B22234",
    "Canada": "#D52B1E",
}
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
        highlight_rows=None,
        row_colors=FLAG_COLORS,
        bar_images={r: FLAG_DIR / f"{ISO2[r]}.png" for r in rows},
        title="Where is gambling seen as morally wrong?",
        subtitle="Share of adults who say gambling is morally wrong, 25 countries,\n2025.",
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
