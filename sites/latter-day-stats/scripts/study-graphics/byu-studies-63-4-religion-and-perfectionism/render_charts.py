"""Renders the four study graphics for Goodman's "Religion and
Perfectionism" (BYU Studies Quarterly 63:4, 2024) - high- and low-toxic-
perfectionism-by-religious-group magnitude bars, the same study's full
Low-through-High perfectionism-distribution stack (its Figure 1), and a
high- vs. low-perfectionism introjected-motivation bar.

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

from chart_style import GROUP_COLORS, sort_groups  # noqa: E402
from common import CONTEXT_GRAY, OXBLOOD, load_fonts, render_magnitude_bar, render_ordinal_stack  # noqa: E402

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
    # "Other Christian" and "Other religion" used to share the same
    # CONTEXT_GRAY tier-1 catch-all token, which read as one indistinct
    # gray block next to "Former other religion"'s only-slightly-lighter
    # gray - three near-identical bars in a six-row chart. Each catch-all
    # gets its own locked hue instead, still outside GROUP_COLORS proper
    # since neither is a single named tradition: amber for "Other
    # Christian" (this study's broad non-LDS-Christian category, distinct
    # from but in the same warm family as Protestant's amber) and plum for
    # "Other religion" (this study's broad non-Christian category). Former
    # Latter-day Saint above still sets the pattern every current/former
    # pair here follows: former = a lighter shade of the current group's
    # own family, never CONTEXT_GRAY or --oxblood.
    "Other Christian": "#C9721C",
    "Other religion": "#6B4472",
    "Former other religion": "#B896C4",
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

    low_groups = {r["label"]: r["pct"] for r in DATA["charts"]["low-perfectionism-by-group"]["rows"]}
    render_magnitude_bar(
        # Strict descending by value, not sort_groups's usual "Other X"-
        # pinned-to-bottom tiering - matches the distribution chart's own
        # requested reading, one continuous ranking from Latter-day
        # Saint's 29% down to Former Latter-day Saint's 12%.
        rows=sorted(low_groups, key=lambda label: -low_groups[label]),
        values=low_groups,
        highlight_rows=None,
        row_colors=ROW_COLORS,
        title="Low toxic perfectionism, by religious group",
        subtitle="Share of youth in the low-toxic-perfectionism category,\nFoundations panel (Utah, Arizona, California)",
        caption_paragraphs=[],
        handle=HANDLE,
        out_path=OUT_DIR / "low-perfectionism-by-group.png",
        fonts=fonts,
    )

    # Segment colors for the full Low-through-High distribution stack
    # (Figure 1 in the source article). A caller-chosen ordinal ramp, not
    # religious-group identity colors (segments are perfectionism bands,
    # not groups) - distinct from the source figure's own blue/orange/
    # gray/yellow/navy palette, and cool-to-warm so "High" (toxic
    # perfectionism, the study's own negative outcome) lands on --oxblood,
    # this pipeline's decline/negative token, same as it does elsewhere.
    dist = {r["label"]: r for r in DATA["charts"]["perfectionism-distribution-by-group"]["rows"]}
    segment_order = DATA["charts"]["perfectionism-distribution-by-group"]["segments"]
    SEGMENT_COLORS = {
        "Low": "#3E7CA6",
        "Mid-Low": "#4F8C63",
        "Mid": CONTEXT_GRAY,
        "Mid-High": "#B8860B",
        "High": OXBLOOD,
    }
    SEGMENT_TEXT_COLORS = {seg: "#FFFFFF" for seg in segment_order}
    render_ordinal_stack(
        # Ordered by "Low" descending, not this pipeline's usual
        # sort_groups (which pins "Other X" catch-alls to the bottom
        # regardless of value) - a specific, requested reading of this
        # chart as one continuous ranking from Latter-day Saint's 29% low-
        # perfectionism rate down to Former Latter-day Saint's 12%.
        rows=sorted(dist, key=lambda label: -dist[label]["Low"]),
        segment_order=segment_order,
        segment_colors=SEGMENT_COLORS,
        segment_text_colors=SEGMENT_TEXT_COLORS,
        values=dist,
        title="The full perfectionism spread, by religious identity",
        subtitle="Share of each group in each perfectionism band,\nFoundations panel (Utah, Arizona, California)",
        caption_paragraphs=[],
        handle=HANDLE,
        out_path=OUT_DIR / "perfectionism-distribution-by-group.png",
        fonts=fonts,
        # render_100_stack's 0.30 default is sized for short two-row labels
        # ("U.S. Mormons"); this chart's longest row ("Believe in God, no
        # religion") needs more room.
        axes_left=0.44,
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
