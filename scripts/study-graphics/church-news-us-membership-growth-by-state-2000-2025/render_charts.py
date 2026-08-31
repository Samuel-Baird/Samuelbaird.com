"""Renders the two study graphics for the Church News "membership growth by
U.S. state, 2000-2025" analysis - a percent-growth magnitude bar (fastest
growers + the U.S. overall baseline) and a headcount-gains magnitude bar.

Every number comes from docs/study-data/<study-slug>/data.json (see that
file's `sources` for the transcription provenance); nothing is typed here.
Regenerate with:

    python3 scripts/study-graphics/church-news-us-membership-growth-by-state-2000-2025/render_charts.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(SCRIPTS_DIR / "flagship-charts"))

from common import load_fonts, render_magnitude_bar  # noqa: E402

STUDY_SLUG = "church-news-us-membership-growth-by-state-2000-2025"
REPO = SCRIPTS_DIR.parent
DATA = json.loads((REPO / "docs" / "study-data" / STUDY_SLUG / "data.json").read_text())
OUT_DIR = REPO / "public" / "study-graphics" / STUDY_SLUG
HANDLE = f"@ithinkisam | data: {DATA['source_short_title']}"


def main() -> None:
    fonts = load_fonts()

    pct_rows = DATA["charts"]["pct-growth-by-state"]["rows"]
    pct_values = {r["label"]: r["pct"] for r in pct_rows}
    # States sorted by their own value; the U.S. overall baseline sinks to
    # the bottom (it's an aggregate over the whole chart, not a state) and
    # stays gray via the highlight set, per the site-wide row-order rule.
    states = sorted(
        (label for label in pct_values if label != "U.S. overall"),
        key=lambda label: -pct_values[label],
    )
    render_magnitude_bar(
        rows=states + ["U.S. overall"],
        values=pct_values,
        highlight_rows=set(states),
        title="Membership growth by percent, 2000–2025",
        subtitle="Change in reported Latter-day Saint membership,\nfastest-growing U.S. states and D.C.",
        caption_paragraphs=[],
        handle=HANDLE,
        out_path=OUT_DIR / "pct-growth-by-state.png",
        fonts=fonts,
    )

    gain_rows = DATA["charts"]["gains-by-state"]["rows"]
    gain_values = {r["label"]: r["added"] / 1_000 for r in gain_rows}
    render_magnitude_bar(
        rows=sorted(gain_values, key=lambda label: -gain_values[label]),
        values=gain_values,
        highlight_rows=None,
        title="Membership growth by headcount, 2000–2025",
        subtitle="Reported Latter-day Saint members added,\nfour largest state gains (thousands)",
        caption_paragraphs=[],
        handle=HANDLE,
        value_suffix="K",
        out_path=OUT_DIR / "gains-by-state.png",
        fonts=fonts,
    )


if __name__ == "__main__":
    main()
