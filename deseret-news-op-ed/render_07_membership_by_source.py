"""
Chart 07 - "Membership by source": U.S. Latter-day Saint membership as
reported by four different, unreconciled sources since 1925. Modeled on the
site's own us-membership-growth-2000-2025 "U.S. Church membership,
2000-2025" chart (a single merged line), but this one deliberately does NOT
merge the sources - docs/datasets/lds-usa-membership-source-comparison/'s
whole point is that these four sources disagree by definition, not just by
data-entry error, so collapsing them into one line would misrepresent the
underlying data. Four lines instead, one per source, colored within the
Deseret News brand guide's own five values (no color invented beyond
YELLOW/GRAY1/GRAY2/BLACK). See membership_by_source_common.py for the
shared plotting logic every chart in this family uses.

Usage: python render_07_membership_by_source.py
"""
from __future__ import annotations

from membership_by_source_common import render

render(
    stem="07_membership_by_source",
    title="How many Latter-day Saints live in the U.S.? It depends which source you ask",
    dek=("U.S. membership as reported by four separate sources since 1925: the Church's own "
         "membership rolls (Newsroom and the Almanac), the Yearbook of American and Canadian "
         "Churches' count of “inclusive membership,” and the U.S. Religion Census's "
         "survey-based “adherents” estimate. The definitions are not interchangeable, and "
         "the sources are not reconciled here."),
    source_names=[
        "Church Newsroom",
        "Deseret News Church Almanac",
        "Yearbook of American & Canadian Churches",
        "U.S. Religion Census",
    ],
    min_year=1925,
    x_ticks=range(1925, 2026, 10),
    x_pad=(5, 3),
    footer_sources=("Church Newsroom; Deseret News Church Almanac; Yearbook of American and "
                    "Canadian Churches via ARDA; U.S. Religion Census"),
    zero_baseline=True,
    label_source="Church Newsroom",
)
