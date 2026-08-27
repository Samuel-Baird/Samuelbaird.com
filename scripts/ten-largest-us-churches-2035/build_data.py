"""
Builds the comparative dataset for the "Ten Largest U.S.-Rooted Church
Bodies, Projected to 2035" Data Explorer entry - a second kind of "mixed
data" entry alongside us-membership-growth-2000-2025 and
worldwide-membership-history, except this one compares ACROSS ten
denominations rather than tracking one body over time. In the spirit of
Ryan Burge's "if these lines just keep going" religion projections
(https://gist.github.com/ryanburge/e785275206cd12584b73eb4ec9b3ad52), but
applied to individual denominations' own reported membership rather than
GSS tradition shares.

Every body's REPORTED points are its own denomination's self-reported (or,
for Orthodox/COGIC, independently surveyed) membership figures at
whatever years a real source was found - never invented, never
interpolated. A simple ordinary-least-squares line through those points is
then extended to 2035. This is a blunt method: it cannot see an inflection
that hasn't happened yet in the data (a schism, a policy vote, an
accelerating or decelerating rate), so `note` on every entry below says
plainly where that matters. Catholic Church is a special case - see its
own comment - fit through only its most recent two points rather than the
full noisy 1990-2020 series.

Usage: python scripts/ten-largest-us-churches-2035/build_data.py
"""
import json
from pathlib import Path

# Each denomination: (slug, name, population_note, points, trend, confidence, note)
# points: list of (year, members, source)
# confidence: "high" (clean multi-point series), "medium" (usable but sparse
#   or a known one-time shock complicates the fit), "low" (sparse and/or
#   internally inconsistent sourcing - shown, but flagged everywhere)
DENOMINATIONS = [
    (
        "catholic-church", "Catholic Church",
        "US, official diocesan counts (Official Catholic Directory)",
        [
            (1990, 62_400_000, "ARDA / Official Catholic Directory, via CARA sourcing summary (cara.georgetown.edu/faqs)."),
            (2000, 62_000_000, "CARA (Georgetown), cara.georgetown.edu/faqs."),
            (2010, 68_500_000, "CARA (Georgetown), cara.georgetown.edu/faqs."),
            (2020, 67_600_000, "Official Catholic Directory diocesan total, via Wikipedia \"Catholic Church in the United States.\""),
        ],
        "flat", "low",
        "Sources disagree by 5-15M in the same year depending on methodology "
        "(registered vs. self-identified counts) - the weakest series in this set. "
        "The projection below uses only the 2010-2020 slope (roughly flat), not the "
        "noisy full 1990-2020 fit, which is dominated by a 2000-2010 jump that looks "
        "like a reporting-convention change rather than real growth.",
    ),
    (
        "united-methodist-church", "United Methodist Church",
        "US, General Commission on Archives & History / GCFA statistics",
        [
            (1990, 8_853_455, "General Commission on Archives & History, gcah.org/history/timelines/membership-statistics."),
            (2000, 8_411_503, "General Commission on Archives & History."),
            (2010, 7_679_850, "General Commission on Archives & History."),
            (2020, 6_268_310, "General Commission on Archives & History."),
            (2022, 5_424_175, "UMC.org, \"United Methodists at a Glance.\""),
            (2023, 4_238_097, "General Council on Finance and Administration, via juicyecumenism.com (Nov. 2024)."),
        ],
        "down", "medium",
        "Includes the 2019-2023 disaffiliation schism (~7,600 churches left in one "
        "wave). A straight-line fit through this whole span likely overstates future "
        "decline, since that one-time shock is unlikely to repeat at the same rate.",
    ),
    (
        "lds-church", "The Church of Jesus Christ of Latter-day Saints",
        "Worldwide membership - no clean U.S.-only annual series exists (see this "
        "site's own us-membership-growth-2000-2025 dataset for why)",
        [
            (1990, 7_761_179, "Wikipedia, \"Membership history of the Church of Jesus Christ of Latter-day Saints.\""),
            (1995, 9_338_859, "Wikipedia, \"Membership history of the Church of Jesus Christ of Latter-day Saints.\""),
            (2000, 11_068_861, "Wikipedia, \"Membership history of the Church of Jesus Christ of Latter-day Saints.\""),
            (2005, 12_560_869, "Wikipedia, \"Membership history of the Church of Jesus Christ of Latter-day Saints.\""),
            (2010, 14_131_467, "Wikipedia, \"Membership history of the Church of Jesus Christ of Latter-day Saints.\""),
            (2015, 15_634_199, "Wikipedia, \"Membership history of the Church of Jesus Christ of Latter-day Saints.\""),
            (2020, 16_663_663, "Wikipedia, \"Membership history of the Church of Jesus Christ of Latter-day Saints.\""),
            (2024, 17_509_781, "Wikipedia, \"Membership history of the Church of Jesus Christ of Latter-day Saints.\""),
        ],
        "up", "medium",
        "Worldwide, not U.S.-only - the other nine bodies here are U.S. totals. A true "
        "U.S.-only projection would show slower growth, since most of the Church's "
        "current growth is international (see us-membership-growth-2000-2025).",
    ),
    (
        "elca", "Evangelical Lutheran Church in America",
        "US, baptized membership",
        [
            (1988, 5_251_534, "So What Faith, \"ELCA Membership Cut in Half\" (2024), sowhatfaith.com."),
            (1993, 5_212_785, "So What Faith."),
            (1998, 5_178_225, "So What Faith."),
            (2003, 4_984_925, "So What Faith."),
            (2008, 4_633_887, "So What Faith."),
            (2013, 3_863_133, "So What Faith."),
            (2020, 3_142_777, "So What Faith."),
            (2023, 2_690_000, "ELCA, \"Summary of Congregational Statistics as of 12/31/2023,\" resources.elca.org."),
        ],
        "down", "high",
        "The steepest sustained decline in this set. A 2009 denomination-wide vote on "
        "sexuality policy accelerated losses roughly 2009-2013.",
    ),
    (
        "lcms", "Lutheran Church-Missouri Synod",
        "US, baptized membership",
        [
            (1993, 2_615_567, "LCMS statistical yearbook, as cited via secondary compilation."),
            (2010, 2_280_000, "Mighty Fortress Substack, \"The Brisk Decline of the LCMS.\""),
            (2020, 1_860_000, "Mighty Fortress Substack."),
            (2024, 1_674_315, "LCMS Inc. Annual Report 2024."),
        ],
        "down", "medium",
        "Only 4 usable data points - no reliable 1990 or 2000 figure was found - so "
        "this trend line is less precise than the other Lutheran/mainline bodies here.",
    ),
    (
        "orthodox-christian", "Orthodox Christian (combined estimate)",
        "US, Eastern + Oriental Orthodox, aggregate estimates",
        [
            (2000, 1_200_000, "Association of Statisticians of American Religious Bodies (ASARB) 2000 study, via orthodoxhistory.org."),
            (2010, 900_000, "Average of two conflicting 2010 estimates (799,400-1,044,000) - see orthodoxhistory.org and usreligioncensus.org."),
            (2020, 1_170_000, "2020 U.S. Religion Census, Appendix F (Orthodox Christian Groups): ~675,675 Eastern + ~491,413 Oriental Orthodox."),
        ],
        "flat", "low",
        "Sparse, self-reported/estimated, and internally inconsistent between sources "
        "for the same year (two 2010 estimates differ by 30%). Treat as roughly flat, "
        "not a real trend - the three points barely outnumber the free parameters in "
        "a line.",
    ),
    (
        "episcopal-church", "Episcopal Church",
        "US, baptized membership",
        [
            (1995, 2_500_000, "The Living Church, \"Facing Episcopal Church Decline.\""),
            (2010, 1_960_000, "The Living Church, livingchurch.org/covenant/facing-episcopal-church-decline-the-latest-numbers."),
            (2023, 1_547_000, "The Living Church, \"TEC's Latest Numbers: The Good News and the Bad News,\" livingchurch.org."),
        ],
        "down", "medium",
        "Only 3 data points. Child-baptism counts (a decline proxy tracked by the "
        "same source: 1990 ~56,862 to 2023 ~14,735) confirm the same steady downward "
        "shape. The Church did not report a 2024 baptized-membership topline at all, "
        "citing \"parochial report confusion.\"",
    ),
    (
        "pcusa", "Presbyterian Church (USA)",
        "US, active membership",
        [
            (1990, 3_788_009, "So What Faith, \"PCUSA Membership: 30 Years of Decline\" (2023)."),
            (2000, 2_525_330, "So What Faith / Protestia compilation."),
            (2010, 2_016_091, "So What Faith / Protestia compilation."),
            (2019, 1_300_000, "So What Faith, \"The PCUSA Is Missing 2.6 Million People.\""),
            (2020, 1_245_097, "So What Faith / Protestia compilation."),
            (2022, 1_100_000, "Presbyterian Outlook, \"PCUSA 2022 Statistical Report,\" pres-outlook.org."),
            (2023, 1_094_733, "So What Faith / Protestia compilation."),
        ],
        "down", "high",
        "The steepest relative decline of any body here. The straight-line fit "
        "implies near-zero membership by the late 2030s - a widely-discussed (if "
        "mechanically extreme) implication of this exact trend continuing unchanged; "
        "real decline curves usually decelerate as the steepest-declining "
        "congregations close first, so treat the 2035 figure as a lower bound on "
        "plausibility, not a real forecast.",
    ),
    (
        "cogic", "Church of God in Christ",
        "US, self-reported (the denomination's own figures)",
        [
            (1997, 5_200_000, "Denominational self-report."),
            (2003, 5_400_000, "Denominational self-report."),
            (2016, 5_500_000, "Denominational self-report."),
        ],
        "flat", "low",
        "Self-reported figures (~5.2-5.5M) diverge roughly 5-6x from the independent "
        "U.S. Religion Census, which counted ~624,000 in 2010 and ~920,000 in 2020 "
        "(itself a rising count on the independent measure). This is the "
        "lowest-confidence series in the whole set, shown here per the "
        "denomination's own reporting rather than the census figures - a genuinely "
        "unresolved discrepancy, not a rounding difference.",
    ),
    (
        "pca", "Presbyterian Church in America",
        "US, communicant + non-communicant members",
        [
            (1988, 211_154, "PCA Historical Center, pcahistory.org/main/pcastats.html."),
            (1993, 250_551, "PCA Historical Center."),
            (1998, 287_091, "PCA Historical Center."),
            (2003, 320_400, "PCA Historical Center."),
            (2008, 340_852, "PCA Historical Center."),
            (2016, 374_161, "PCA Historical Center."),
            (2025, 405_634, "Graphs About Religion, \"A Deep Dive into the Presbyterian Church in America\" (2025)."),
        ],
        "up", "high",
        "The one denomination in this set that has grown steadily throughout the "
        "period (roughly 1.5-2%/year).",
    ),
]

OUT_PATH = Path(__file__).resolve().parent.parent.parent / "docs/datasets/ten-largest-us-churches-2035/denominations.json"


def fit_line(points):
    n = len(points)
    sx = sum(p[0] for p in points)
    sy = sum(p[1] for p in points)
    sxx = sum(p[0] * p[0] for p in points)
    sxy = sum(p[0] * p[1] for p in points)
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    intercept = (sy - slope * sx) / n
    return slope, intercept


def main():
    order = []
    denominations = {}
    for slug, name, population_note, points, trend, confidence, note in DENOMINATIONS:
        if slug == "catholic-church":
            # See this entry's own note: the full 1990-2020 series is dominated
            # by a 2000-2010 jump that reads as a reporting-convention change,
            # not real growth - fit only the most recent two points instead.
            p1, p2 = points[-2], points[-1]
            slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
            intercept = p2[1] - slope * p2[0]
            fit_method = "linear (2010-2020 only, see note)"
        else:
            slope, intercept = fit_line(points)
            fit_method = "linear (ordinary least squares, all reported points)"

        last_year, last_members, _ = points[-1]
        projected_2035 = round(slope * 2035 + intercept)
        pct_change = round((projected_2035 - last_members) / last_members * 100, 1)

        order.append(slug)
        denominations[slug] = {
            "name": name,
            "population_note": population_note,
            "points": [
                {"year": y, "members": m, "source": s} for y, m, s in points
            ],
            "last_reported_year": last_year,
            "last_reported_members": last_members,
            "fit_method": fit_method,
            "projected_2035_members": projected_2035,
            "projected_pct_change": pct_change,
            "trend": trend,
            "confidence": confidence,
            "note": note,
        }

    payload = {
        "method": (
            "For each denomination, an ordinary-least-squares line is fit through its "
            "own reported membership points, then extended to 2035 (Catholic Church is "
            "fit through only its 2010 and 2020 points - see its own note). This is a "
            "simple straight-line extrapolation, not a demographic model: it cannot see "
            "an inflection - a schism, a policy vote, an accelerating or decelerating "
            "rate - that hasn't happened yet in the data. `confidence` on every entry "
            "reflects how clean and consistent that entry's own sourcing is, from "
            "\"high\" (a clean multi-point single-source series) to \"low\" (sparse "
            "and/or internally inconsistent). Modeled after Ryan Burge's GSS-based "
            "American-religion projections "
            "(https://gist.github.com/ryanburge/e785275206cd12584b73eb4ec9b3ad52), "
            "applied here to individual denominations' own reported membership rather "
            "than survey-tradition shares."
        ),
        "denomination_order": order,
        "denominations": denominations,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {OUT_PATH}")
    for slug in order:
        d = denominations[slug]
        print(f"  {d['name']}: {d['last_reported_year']}={d['last_reported_members']:,} "
              f"-> 2035={d['projected_2035_members']:,} ({d['projected_pct_change']:+.1f}%)")


if __name__ == "__main__":
    main()
