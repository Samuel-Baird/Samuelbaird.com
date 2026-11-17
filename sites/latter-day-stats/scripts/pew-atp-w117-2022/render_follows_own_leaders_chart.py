#!/usr/bin/env python3
"""Renders the flagship PNG for the ATP Wave 117 "follows own religious
leaders online" item. Reads only
docs/datasets/pew-atp-w117-2022/follows-own-leaders.json (produced by
follows_own_leaders.py in this folder). Uses the shared magnitude-bar shape
in scripts/flagship-charts/.

Usage:
  python scripts/pew-atp-w117-2022/render_follows_own_leaders_chart.py \
    --out public/data-explorer/pew-atp-w117-2022/follows-own-leaders.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-atp-w117-2022"
    / "follows-own-leaders.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["follows_own_religious_leaders"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="Following their own religious leaders",
        subtitle="Among social media users, share who follow or keep\ntrack of their own religious leaders online or on\nsocial media, by religious tradition, November 2022.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 117 (2022)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
