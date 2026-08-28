#!/usr/bin/env python3
"""Renders the "Support for same-sex marriage" PNG for Religion in Latin
America. Reads only docs/datasets/pew-latin-america-2014/samesex-marriage.json
(produced by samesex_marriage.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-latin-america-2014/render_samesex_marriage_chart.py \
    --out public/data-explorer/pew-latin-america-2014/samesex-marriage.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-latin-america-2014"
    / "samesex-marriage.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["favor_samesex_marriage"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="Support for same-sex marriage",
        subtitle="Share across Latin America favoring same-sex\nmarriage, by their own religion.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew Religion in Latin America (2014)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
