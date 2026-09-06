#!/usr/bin/env python3
"""Renders "Do Mormons see polygamy as morally acceptable?" from
docs/datasets/pew-mormon-survey-2011/polygamy-morality.json (produced by
polygamy_morality.py). Uses the shared magnitude-bar shape in
scripts/flagship-charts/common.py.

Usage:
  python scripts/pew-mormon-survey-2011/render_polygamy_chart.py \
    --out public/data-explorer/pew-mormon-survey-2011/polygamy-morality.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import OXBLOOD, CONTEXT_GRAY, load_fonts, render_magnitude_bar  # noqa: E402
from chart_style import DIV_POS_GREEN  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-mormon-survey-2011"
    / "polygamy-morality.json"
).resolve()

# --honey, the site's one reserved "highlight" hex - used here as the 4th
# color in this chart's own moral-judgment scale (wrong/gray/acceptable/
# depends), not as a highlight-vs-everyone-else contrast.
HONEY = "#8a5a06"

# Two-line row labels, forced via a literal newline (render_magnitude_bar
# respects one verbatim instead of re-wrapping by width) - shortens the
# widest rendered line per row, which lets the auto-measured left margin
# shrink and hands that freed width to the bars.
LABELS = {
    "Morally wrong": "Morally\nwrong",
    "Not a moral issue": "Not a\nmoral issue",
    "Morally acceptable": "Morally\nacceptable",
    "Depends on the situation": "Depends on\nthe situation",
}

# This item's own 4-point moral-judgment scale, not a religious-group
# comparison, so each answer gets a semantic color traceable to an
# existing site token rather than the group-identity palette:
# oxblood/negative, gray/neutral, teal-green/positive (chart_style.py's
# diverging-chart green), honey/the 4th categorical color.
COLORS = {
    "Morally wrong": OXBLOOD,
    "Not a moral issue": CONTEXT_GRAY,
    "Morally acceptable": DIV_POS_GREEN,
    "Depends on the situation": HONEY,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    item_order = data["item_order"]
    rows = [LABELS[r] for r in item_order]
    values = {LABELS[r]: data["polygamy_view_pct"][r]["pct"] for r in item_order}
    row_colors = {LABELS[r]: COLORS[r] for r in item_order}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        title="Do Mormons see polygamy as moral?",
        subtitle="Mormons' own view of polygamy - having more than one wife.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 2011 Mormon Survey",
        out_path=args.out,
        fonts=load_fonts(),
        # Only 4 rows - the standard low-row scaling in render_magnitude_bar
        # still left this one visibly sparse, so pack it tighter than any
        # other <7-row chart currently asks for.
        bar_h_override=0.88,
        margin_frac_override=0.03,
        # Two-line labels no longer need the ~50% left margin a full-width
        # single line did - let the auto-measure step size this from the
        # labels' own (now much narrower) rendered width.
        axes_left=0.2,
        row_colors=row_colors,
    )


if __name__ == "__main__":
    main()
