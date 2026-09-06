"""
Seventh chart for ATP Wave 132 (July 31-Aug. 6, 2023): belief the dead can
"be united with other loved ones who have already died" (DTHLKE_f_W132), by
religious tradition.

Same F_RELIG frame variable as this dataset's other charts (beyond_this_
world.py, has_cross.py, religious_community.py, spirituality_important.py,
tattoo_piercing_spiritual.py, dead_aware_living.py) - see beyond_this_
world.py's docstring for why F_RELIG is the right frame here (Wave 132 has
no F_RELTRAD).

DTHLKE_f is the last item in the same six-part "Do you believe people who
have died can..." battery as dead_aware_living.py's DTHLKE_a. Latter-day
Saints say "definitely" or "probably" true at 77.0%, the highest of any
named tradition in the wave by a wide margin - next highest is Orthodox
Christian at 53.9%, with Protestant at 51.4% and Catholic at 40.7%. This is
a distinct construct from DTHLKE_a's "aware of the living" framing: this
item is specifically about being reunited with loved ones after death,
which maps directly onto the LDS doctrine of eternal marriage and family
sealing (temple ordinances that bind spouses and children together beyond
this life, "that whatsoever you seal on earth shall be sealed in heaven",
D&C 132) - a doctrine that makes permanent reunion with family a defining,
distinctive feature of LDS theology rather than a generic afterlife hope.
Shipping this alongside dead_aware_living.py as a tight two-chart cluster
from the same battery: one item about the dead's continued awareness of the
living, one about the living's hope of reunion with the dead - both
distinctive, both doctrinally grounded, neither overlapping the other or
the already-shipped pew-atp-w143-2024 believe-ancestor-spirits.json (a
different wave's help/harm-focused item).

Groups under 30 valid respondents are dropped (MIN_VALID_N, matching every
other chart in this pipeline).

Usage: python scripts/pew-atp-w132-2023/reunited_with_loved_ones.py
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
# DTHLKE_f_W132: 1=Definitely true, 2=Probably true, 3=Probably not true,
# 4=Definitely not true, 5=Not sure, 99=Refused. "True" = definitely/probably.
TRUE_CODES = {1.0, 2.0}
VALID_CODES = {1.0, 2.0, 3.0, 4.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELIG", "DTHLKE_f_W132", "WEIGHT_W132"])
    weight = df["WEIGHT_W132"].to_numpy()
    relig = df["F_RELIG"].to_numpy()
    dthlke = df["DTHLKE_f_W132"].to_numpy()

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
                  "true\" or \"probably true\" to DTHLKE_f_W132 (\"Do you believe people who "
                  "have died can be united with other loved ones who have already died?\", "
                  "one item in a six-part battery asked of all respondents); \"not sure\" "
                  "and refused excluded from each row's denominator. Groups under 30 valid "
                  "respondents omitted. Weighted by the dataset's own WEIGHT_W132 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "reunited_with_loved_ones": results,
    }
    with open("docs/datasets/pew-atp-w132-2023/reunited-with-loved-ones.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w132-2023/reunited-with-loved-ones.json")


if __name__ == "__main__":
    main()
