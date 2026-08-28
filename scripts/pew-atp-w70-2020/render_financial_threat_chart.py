#!/usr/bin/env python3
"""Renders the "COVID as a financial threat" PNG for ATP Wave 70. Reads
only docs/datasets/pew-atp-w70-2020/financial-threat-covid.json (produced
by financial_threat_covid.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-atp-w70-2020/render_financial_threat_chart.py \
    --out public/data-explorer/pew-atp-w70-2020/financial-threat-covid.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-atp-w70-2020"
    / "financial-threat-covid.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["major_financial_threat"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows={"Mormon"},
        title="COVID as a financial threat",
        subtitle="Share calling the coronavirus outbreak a major threat\nto their personal finances, by religious tradition, July 2020.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 70 (2020)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()
