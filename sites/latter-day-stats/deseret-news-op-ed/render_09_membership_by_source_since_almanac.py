"""
Chart 09 - "Membership by source, since the Almanac begins": Church
Newsroom and the Deseret News Church Almanac, starting in 1973 - the
earliest year docs/datasets/lds-usa-membership-source-comparison/'s
Almanac file has a figure for. A third variant in the same family as
charts 07 (full 1925-2025, four sources) and 08 (2000-2025, two sources) -
none of them replace each other.

No dek/subtitle - title only, so the chart reads at a glance.

Usage: python render_09_membership_by_source_since_almanac.py
"""
from __future__ import annotations

from membership_by_source_common import render

render(
    stem="09_membership_by_source_since_almanac",
    title="U.S. Church Membership by Source, 1973-2025",
    dek=None,
    source_names=["Church Newsroom", "Deseret News Church Almanac"],
    min_year=1973,
    x_ticks=range(1975, 2026, 10),
    x_pad=(4, 3),
    footer_sources="Church Newsroom; Deseret News Church Almanac",
)
