"""
Flagship chart for Pew's 2015-2016 Central and Eastern Europe survey: how
important is it, to be truly a citizen of your country, to belong to that
country's dominant Christian tradition (Q66c)? The item text is generic
across countries - "How important do you think each of the following is
for being truly [SURVEY COUNTRY CITIZENSHIP]? To be a [DOMINANT DENOMINATION
OF SURVEY COUNTRY, e.g. Russian Orthodox, Greek Orthodox, Polish Catholic,
etc.]" (confirmed against the questionnaire docx, which shows the item as a
single generic Q66 stem with a country-specific denomination insert) - so
every country's own respondents are being asked about their own country's
own dominant church, making the percentages directly comparable across
Orthodox-majority and Catholic-majority countries.

Population is all respondents in each of the 18 countries covered by Pew's
2017 report "Religious Belief and National Belonging in Central and Eastern
Europe" - Armenia, Belarus, Bosnia, Bulgaria, Croatia, Czech Republic,
Estonia, Georgia, Greece, Hungary, Latvia, Lithuania, Moldova, Poland,
Romania, Russia, Serbia, Ukraine. The raw .sav also carries a 19th country,
Kazakhstan (a majority-Muslim country used in Pew's related Central Asia
work, not part of the 18-country CEE report), which is excluded here since
it falls outside both the cited report and this site's Christianity focus.

19 countries is well past this pipeline's ~12-row guideline for one clean
chart (scripts/flagship-charts/common.py's render_magnitude_bar), so this
narrows to the 6 highest and 6 lowest countries by "very important" share -
the story here is the *range* (near-universal in some Orthodox-majority
countries, marginal in the most secularized ones), which a top/bottom cut
shows more clearly than an unreadable 18-row wall would. See this dataset's
README for the full 18-country table.

Usage: python scripts/pew-eastern-europe-2015/religious_national_identity.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-eastern-europe-2015/Eastern Europe Public Data_12.5 CHECKED.sav"

# COUNTRY codes for the 18 countries in Pew's report; excludes Kazakhstan
# (code 12, present in the raw file but not part of the cited report).
COUNTRY_CODES = {
    1.0: "Armenia", 2.0: "Belarus", 3.0: "Bosnia", 4.0: "Bulgaria",
    5.0: "Croatia", 6.0: "Czech Republic", 7.0: "Estonia", 9.0: "Georgia",
    10.0: "Greece", 11.0: "Hungary", 13.0: "Latvia", 14.0: "Lithuania",
    15.0: "Moldova", 16.0: "Poland", 17.0: "Romania", 18.0: "Russia",
    19.0: "Serbia", 20.0: "Ukraine",
}
VERY_IMPORTANT = 1.0
VALID_CODES = {1.0, 2.0, 3.0, 4.0}  # very/somewhat/not very/not at all important
MIN_VALID_N = 30
N_PER_SIDE = 6  # top 6 + bottom 6 countries shown on the chart


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["COUNTRY", "Q66c", "final_weight"])
    weight = df["final_weight"].to_numpy()
    country = df["COUNTRY"].to_numpy()
    important = df["Q66c"].to_numpy()

    results = {}
    for code, label in COUNTRY_CODES.items():
        group_mask = country == code
        valid = group_mask & np.isin(important, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        very = valid & (important == VERY_IMPORTANT)
        results[label] = {
            "pct": round(100 * weight[very].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    full_order = sorted(results, key=lambda label: -results[label]["pct"])
    chart_order = full_order[:N_PER_SIDE] + full_order[-N_PER_SIDE:]
    # De-dupe in case the 18-country list is ever short enough that the two
    # slices overlap (not the case today at 18 countries / 6-and-6, but
    # keeps this safe if COUNTRY_CODES ever shrinks).
    seen = set()
    chart_order = [c for c in chart_order if not (c in seen or seen.add(c))]

    valid_18 = np.isin(country, list(COUNTRY_CODES.keys())) & np.isin(important, list(VALID_CODES))
    very_18 = valid_18 & (important == VERY_IMPORTANT)

    out = {
        "source": 'Pew Research Center. 2017. "Religious Belief and National Belonging in '
                  'Central and Eastern Europe."',
        "method": "Population is all respondents in each of the 18 countries covered by the "
                  "cited report (the raw file's 19th country, Kazakhstan, is excluded - see "
                  "this script's own docstring). Share answering \"very important\" to Q66c "
                  "(\"How important do you think each of the following is for being truly "
                  "[survey country citizenship]? To be a [survey country's dominant "
                  "denomination, e.g. Russian Orthodox, Greek Orthodox, Polish Catholic]\"); "
                  "don't know/refused excluded from each row's denominator. Chart shows the 6 "
                  "highest- and 6 lowest-ranked of the 18 countries; see the dataset README "
                  "for the full country table. Weighted by the dataset's own final_weight "
                  "variable.",
        "total_weighted_n": float(weight[np.isin(country, list(COUNTRY_CODES.keys()))].sum()),
        "total_unweighted_n": int(np.isin(country, list(COUNTRY_CODES.keys())).sum()),
        "region_weighted_n": float(weight[valid_18].sum()),
        "region_pct_very_important": round(100 * weight[very_18].sum() / weight[valid_18].sum(), 2),
        "group_order": chart_order,
        "full_country_order": full_order,
        "important_to_share_dominant_faith": results,
    }
    with open(
        "docs/datasets/pew-eastern-europe-2015/religious-national-identity.json",
        "w", encoding="utf-8",
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in full_order:
        r = results[label]
        marker = " *" if label in chart_order else ""
        print(f"{label:16} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5}){marker}")
    print(f"\nRegion-wide (18 countries, pooled): {out['region_pct_very_important']:.1f}%")
    print("\nWrote docs/datasets/pew-eastern-europe-2015/religious-national-identity.json")


if __name__ == "__main__":
    main()
