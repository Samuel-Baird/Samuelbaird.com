#!/usr/bin/env python3
"""Renders "Self-identification vs. Church membership records, 2010" - a
two-row magnitude-bar comparison. Reads only
docs/datasets/lds-brazil-census-2010/self-id-vs-membership-2010.json
(produced by build_self_id_vs_membership_2010.py in this folder). Reuses
render_magnitude_bar (scripts/flagship-charts/common.py) rather than
building a new two-row shape - it already handles an arbitrary row count,
including two, and the existing latin-america-comparison-2025.png chart
already established the value_suffix="K"/divide-by-1000 convention this
script follows for the same reason (raw six-figure counts read cleaner as
"227K"/"1139K" than unformatted five-to-seven-digit numbers, since this
shape has no built-in thousands-separator support).

FRAMING: these two bars measure different things (who told a census taker
one thing vs. who is on the Church's own rolls) - not a before/after or a
correction of one by the other. `highlight_rows=None` (both bars in
--accent) deliberately avoids implying one number is the "right" one and
the other a shortfall from it; see build_self_id_vs_membership_2010.py's
docstring for the full framing rationale, mirrored in this chart's own
subtitle.

Usage:
  python scripts/lds-brazil-census-2010/render_self_id_vs_membership_2010_chart.py \
    --out public/data-explorer/lds-brazil-census-2010/self-id-vs-membership-2010.png
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "lds-brazil-census-2010"
    / "self-id-vs-membership-2010.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["row_order"]
    values = {r: data["rows"][r]["value"] / 1000 for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="Two ways to count Latter-day Saints, 2010",
        subtitle="Brazil, 2010: how many people told the Census taker they\n"
                  "were Latter-day Saint, versus how many were on the\n"
                  "Church's own membership rolls that year. Different\n"
                  "measures, not a correction of one by the other - see the\n"
                  "dataset README for why the gap isn't attributed to one cause.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: 2010 Census (IBGE); Church membership records",
        out_path=args.out,
        fonts=load_fonts(),
        value_suffix="K",
        axes_left=0.42,
        row_label_fontsize=17,
        value_label_fontsize=15,
    )


if __name__ == "__main__":
    main()
