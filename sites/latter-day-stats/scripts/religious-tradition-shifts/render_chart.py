"""
Renders the religious-tradition-shifts-2007-2023 dataset's one chart: every
RELTRAD religious tradition's share of U.S. adults, 2007 vs. 2023-24. See
scripts/flagship-charts/common.py's render_dumbbell_identity docstring for
the chart shape.

Usage:
    python scripts/religious-tradition-shifts/compute_shifts.py
    python scripts/religious-tradition-shifts/render_chart.py \
        --out public/data-explorer/religious-tradition-shifts/shifts-2007-2023.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_dumbbell_identity  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA_PATH = (Path(__file__).resolve().parent.parent.parent /
             "docs/datasets/religious-tradition-shifts/shifts-2007-2023.json")

# Groups under this unweighted n, in EITHER wave, get the low-confidence
# asterisk - matches this site's other small-group caveats (e.g. the Deseret
# News op-ed set's LDS-cohort notes).
LOW_CONFIDENCE_FLOOR = 300


def pct_fmt(v: float) -> str:
    if v < 1:
        return f"{v:.2f}%"
    if v < 10:
        return f"{v:.1f}%"
    return f"{v:.0f}%"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    groups = {g["name"]: g for g in data["groups"]}

    rows = sort_groups(list(groups.keys()), value_of=lambda name: groups[name]["pct_2023_24"])
    row_labels = {name: name for name in rows}
    start_values = {name: groups[name]["pct_2007"] for name in rows}
    end_values = {name: groups[name]["pct_2023_24"] for name in rows}
    low_confidence_rows = {
        name for name in rows
        if groups[name]["unweighted_n_2007"] < LOW_CONFIDENCE_FLOOR
        or groups[name]["unweighted_n_2023_24"] < LOW_CONFIDENCE_FLOOR
    }

    render_dumbbell_identity(
        rows=rows,
        row_labels=row_labels,
        start_values=start_values,
        end_values=end_values,
        start_label="2007",
        end_label="2023-24",
        low_confidence_rows=low_confidence_rows,
        value_fmt=pct_fmt,
        title="Every Religious Tradition's Share of U.S. Adults, 2007 vs. 2023-24",
        subtitle="Pew Research Center's Religious Landscape Study, all traditions, not just Christian ones",
        caption_paragraphs=[
            "Share of all U.S. adults, weighted. 2007 was phone-only; 2023-24 was mostly "
            "online/mail, a mode change Pew flags for cross-wave comparisons. *Fewer than "
            "300 unweighted respondents in a wave - treat as approximate.",
        ],
        handle="@ithinkisam | data: Pew RLS 2007 & 2023-24",
        out_path=args.out,
        fonts=load_fonts(),
        log_scale=True,
    )


if __name__ == "__main__":
    main()
