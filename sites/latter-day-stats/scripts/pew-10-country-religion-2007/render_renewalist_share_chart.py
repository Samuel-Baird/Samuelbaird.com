#!/usr/bin/env python3
"""Renders the "How renewalist is each country?" PNG for Pew's 10-Country
Survey of Pentecostals. Reads only
docs/datasets/pew-10-country-religion-2007/renewalist-share.json (produced
by renewalist_share.py in this folder). Uses the shared magnitude-bar shape
in scripts/flagship-charts/.

Usage:
  python scripts/pew-10-country-religion-2007/render_renewalist_share_chart.py \
    --out public/data-explorer/pew-10-country-religion-2007/renewalist-share.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-10-country-religion-2007"
    / "renewalist-share.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["renewalist_share"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="How renewalist is each country?",
        subtitle="Share of the general public who are Pentecostal or\nCharismatic Christians, by country, 2006.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 10-Country Survey of Pentecostals (2006)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
