"""
Sixth chart for ATP Wave 132 (July 31-Aug. 6, 2023): belief the dead can "be
aware of things going on among those who are still living" (DTHLKE_a_W132),
by religious tradition.

Same F_RELIG frame variable as this dataset's other charts (beyond_this_
world.py, has_cross.py, religious_community.py, spirituality_important.py,
tattoo_piercing_spiritual.py) - see beyond_this_world.py's docstring for why
F_RELIG is the right frame here (Wave 132 has no F_RELTRAD).

DTHLKE_a is one item in a six-part "Do you believe people who have died
can..." battery asked of all respondents. Latter-day Saints say "definitely"
or "probably" true at 43.1%, the highest of any NAMED tradition in the wave
by a wide margin - next highest named tradition is Orthodox Christian at
27.6%, with Protestant/Catholic both around 18-21% and most non-Christian
traditions lower still. Ties to LDS doctrine of an active spirit world
(D&C 138) where the dead continue to take an interest in the living, and to
the Church's emphasis on temple/family-history work performed on behalf of
deceased ancestors - a practice that only makes sense if the dead remain
aware of and invested in what their living descendants do.

Distinct from this dataset's existing has-cross.json/tattoo-piercing-
spiritual.json (physical objects, not beliefs) and from pew-atp-w143-2024's
already-shipped believe-ancestor-spirits.json (a merged "can ancestors'
spirits help OR harm you" framing, PRACTICE_ANCSTR-style item) - this item
is specifically about awareness/attentiveness, not about ancestors exerting
active help/harm, and comes from a different wave/battery entirely. Also
distinct from this same battery's DTHLKE_c ("provide assistance, protection
or guidance"), which prior exploration-log passes flagged as the item that
overlaps the W143 ancestor-spirits chart and should be skipped - DTHLKE_a's
"aware of" framing was deliberately picked instead to avoid that overlap.

Groups under 30 valid respondents are dropped (MIN_VALID_N, matching every
other chart in this pipeline).

Usage: python scripts/pew-atp-w132-2023/dead_aware_living.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-atp-w132-2023/ATP W132.sav"

RELIG_CODES = {
    1.0: "Protestant",
    2.0: "Catholic",
    3.0: "Mormon",
    4.0: "Orthodox Christian",
    5.0: "Jewish",
    6.0: "Muslim",
    7.0: "Buddhist",
    8.0: "Hindu",
    9.0: "Atheist",
    10.0: "Agnostic",
    11.0: "Other",
    12.0: "Nothing in particular",
}
# DTHLKE_a_W132: 1=Definitely true, 2=Probably true, 3=Probably not true,
# 4=Definitely not true, 5=Not sure, 99=Refused. "True" = definitely/probably.
TRUE_CODES = {1.0, 2.0}
VALID_CODES = {1.0, 2.0, 3.0, 4.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELIG", "DTHLKE_a_W132", "WEIGHT_W132"])
    weight = df["WEIGHT_W132"].to_numpy()
    relig = df["F_RELIG"].to_numpy()
    dthlke = df["DTHLKE_a_W132"].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(dthlke, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & np.isin(dthlke, list(TRUE_CODES))
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(dthlke, list(VALID_CODES))
    yes_all = valid_all & np.isin(dthlke, list(TRUE_CODES))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 132, fielded July 31-Aug. 6, 2023.",
        "method": "Population is respondent's religion (F_RELIG; this wave has no F_RELTRAD "
                  "frame variable, see this dataset's README). Share answering \"definitely "
                  "true\" or \"probably true\" to DTHLKE_a_W132 (\"Do you believe people who "
                  "have died can be aware of things going on among those who are still "
                  "living?\", one item in a six-part battery asked of all respondents); "
                  "\"not sure\" and refused excluded from each row's denominator. Groups "
                  "under 30 valid respondents omitted. Weighted by the dataset's own "
                  "WEIGHT_W132 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "dead_aware_of_living": results,
    }
    with open("docs/datasets/pew-atp-w132-2023/dead-aware-living.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w132-2023/dead-aware-living.json")


if __name__ == "__main__":
    main()
