"""
Chart 08 - "Membership by source, since 2000": two of chart 07's four
unreconciled sources - Church Newsroom and the Deseret News Church Almanac
- zoomed to 2000-2025. Both the Yearbook of American and Canadian Churches
and U.S. Religion Census are excluded here: Yearbook (a different
"inclusive membership" definition) and Census (three sparse, decade-apart
"adherents" points) both add more noise than signal at this narrower
scale and this reduced two-source set. A companion chart, NOT a
replacement - chart 07's full 1925-2025, four-source view stays as it is.

No dek/subtitle - title only, so the chart reads at a glance.

Usage: python render_08_membership_by_source_2000s.py
"""
from __future__ import annotations

from membership_by_source_common import render

render(
    stem="08_membership_by_source_2000s",
    title="U.S. Church Membership by Source, 2000-2025",
    dek=None,
    source_names=["Church Newsroom", "Deseret News Church Almanac"],
    min_year=2000,
    x_ticks=range(2000, 2026, 5),
    x_pad=(1, 1.6),
    footer_sources="Church Newsroom; Deseret News Church Almanac",
)
