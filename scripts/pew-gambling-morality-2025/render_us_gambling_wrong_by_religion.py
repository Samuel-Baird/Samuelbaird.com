#!/usr/bin/env python3
"""Renders "Do religious Americans see gambling as morally wrong?" from
docs/datasets/pew-gambling-morality-2025/us-gambling-wrong-by-religion.json.

Usage:
  python scripts/pew-gambling-morality-2025/render_us_gambling_wrong_by_religion.py \
    --out public/data-explorer/pew-gambling-morality-2025/us-gambling-wrong-by-religion.png
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "flagship-charts"))
sys.path.insert(0, str(HERE.parent))
from common import load_fonts, render_magnitude_bar  # noqa: E402
from chart_style import CONTEXT_GRAY, MUTED, color_for_group, sort_groups  # noqa: E402

DATA_JSON = HERE.parent.parent / "docs" / "datasets" / "pew-gambling-morality-2025" / "us-gambling-wrong-by-religion.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()
    values = json.loads(args.data.read_text(encoding="utf-8"))["wrong_pct"]
    rows = sort_groups(list(values), lambda r: values[r])
    # "Christian" has no locked identity color (it spans several traditions),
    # so it takes the neutral gray; the all-adults baseline takes MUTED.
    colors = {r: (CONTEXT_GRAY if r == "Christian" else color_for_group(r)) for r in rows}
    colors["All U.S. adults"] = MUTED
    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        row_colors=colors,
        title="Do religious Americans see gambling as morally wrong?",
        subtitle="Share of U.S. adults who say gambling is morally wrong, by\nreligion, 2025. Latter-day Saints are not broken out.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew Global Attitudes 2025",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
