#!/usr/bin/env python3
"""Renders "Who says gambling is morally acceptable?" from
docs/datasets/gallup-values-beliefs-gambling/gallup-acceptable-by-religion.json (transcribed from
Gallup's published table). Shared magnitude-bar shape, per-group identity colors.

Usage:
  python scripts/gallup-values-beliefs-gambling/render_gallup_acceptable_by_religion.py \
    --out public/data-explorer/gallup-values-beliefs-gambling/gallup-acceptable-by-religion.png
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

DATA_JSON = HERE.parent.parent / "docs" / "datasets" / "gallup-values-beliefs-gambling" / "gallup-acceptable-by-religion.json"


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
        group_identity=True,
        title="Who says gambling is morally acceptable?",
        subtitle="Share of U.S. adults who say gambling is morally acceptable, by\nreligion, 2001-2016 combined. Latter-day Saints are the lowest.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Gallup Values & Beliefs 2001-16",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
