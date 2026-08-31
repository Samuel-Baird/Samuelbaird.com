"""Renders the two study graphics for Goodman's "Religion and
Perfectionism" (BYU Studies Quarterly 63:4, 2024) - a high-toxic-
perfectionism-by-religious-group magnitude bar and a high- vs.
low-perfectionism introjected-motivation bar.

Every number comes from docs/study-data/<study-slug>/data.json (see that
file's `sources` for the transcription provenance); nothing is typed here.
Regenerate with:

    python3 scripts/study-graphics/byu-studies-63-4-religion-and-perfectionism/render_charts.py

Row colors for the by-group chart: this study compares religious-status
groups (current vs. former members) that chart_style.GROUP_COLORS doesn't
cover, so the explicit `row_colors` map below extends it the same way the
Protestant sub-traditions extended amber - a "former" group takes a lighter
shade of its current counterpart's family. See
scripts/study-graphics/STYLE.md's "Current-vs-former group colors" section.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(SCRIPTS_DIR / "flagship-charts"))

from chart_style import CONTEXT_GRAY, GROUP_COLORS, sort_groups  # noqa: E402
from common import load_fonts, render_magnitude_bar  # noqa: E402

STUDY_SLUG = "byu-studies-63-4-religion-and-perfectionism"
REPO = SCRIPTS_DIR.parent
DATA = json.loads((REPO / "docs" / "study-data" / STUDY_SLUG / "data.json").read_text())
OUT_DIR = REPO / "public" / "study-graphics" / STUDY_SLUG
HANDLE = f"@ithinkisam | data: {DATA['source_short_title']}"

ROW_COLORS = {
    "Latter-day Saint": GROUP_COLORS["Latter-day Saint"],
    # Lighter shade of the Latter-day Saint blue family - "former" reads as
    # a shade of the tradition it left, not its own new hue.
    "Former Latter-day Saint": "#7FA3C8",
    # The combined category takes the Atheist anchor of the atheist/agnostic
    # pair (the darker, more distinguishable of the two tokens).
    "Atheist/agnostic": GROUP_COLORS["Atheist"],
    # Named catch-alls take the shared bar-safe gray, per the site-wide
    # tier-1 rule; "Former other religion" is a lighter shade of that same
    # family, mirroring the former-LDS treatment above.
    "Other Christian": CONTEXT_GRAY,
    "Other religion": CONTEXT_GRAY,
    "Former other religion": "#B3AFA5",
}


def main() -> None:
    fonts = load_fonts()

    groups = {r["label"]: r["pct"] for r in DATA["charts"]["high-perfectionism-by-group"]["rows"]}
    render_magnitude_bar(
        rows=sort_groups(list(groups), lambda label: groups[label]),
        values=groups,
        highlight_rows=None,
        row_colors=ROW_COLORS,
        title="High toxic perfectionism, by religious group",
        subtitle="Share of youth in the high-toxic-perfectionism category,\nFoundations panel (Utah, Arizona, California)",
        caption_paragraphs=[],
        handle=HANDLE,
        out_path=OUT_DIR / "high-perfectionism-by-group.png",
        fonts=fonts,
    )

    motivation = {r["label"]: r["pct"] for r in DATA["charts"]["introjected-motivation"]["rows"]}
    render_magnitude_bar(
        rows=sorted(motivation, key=lambda label: -motivation[label]),
        values=motivation,
        highlight_rows=None,
        title="Guilt-driven religion and perfectionism",
        subtitle="Share in the high-introjected-motivation group\n(religiosity driven by guilt or shame)",
        caption_paragraphs=[],
        handle=HANDLE,
        out_path=OUT_DIR / "introjected-motivation.png",
        fonts=fonts,
    )


if __name__ == "__main__":
    main()
