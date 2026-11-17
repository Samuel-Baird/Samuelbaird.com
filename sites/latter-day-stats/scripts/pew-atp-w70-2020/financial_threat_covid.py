"""
Fourth flagship chart for ATP Wave 70 (July 2020): how many people saw
the coronavirus outbreak as a major threat to their personal financial
situation (COVIDTHREAT_d_W70), by religious tradition (F_RELTRAD)?
Companion to online_worship_covid.py in this folder - same population and
threshold conventions (groups under 30 valid respondents dropped).

Usage: python scripts/pew-atp-w70-2020/financial_threat_covid.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-atp-w70-2020/ATP W70.sav"

RELTRAD_CODES = {
    1100.0: "Evangelical Protestant",
    1200.0: "Mainline Protestant",
    1300.0: "Historically Black Protestant",
    10000.0: "Catholic",
    20000.0: "Mormon",
    50000.0: "Jewish",
    100000.0: "Unaffiliated",
}
MAJOR_THREAT = 1.0
VALID_CODES = {1.0, 2.0, 3.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELTRAD", "COVIDTHREAT_d_W70", "WEIGHT_W70"])
    weight = df["WEIGHT_W70"].to_numpy()
    reltrad = df["F_RELTRAD"].to_numpy()
    threat = df["COVIDTHREAT_d_W70"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(threat, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        major = valid & (threat == MAJOR_THREAT)
        results[label] = {
            "pct": round(100 * weight[major].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(threat, list(VALID_CODES))
    major_all = valid_all & (threat == MAJOR_THREAT)
    results["All U.S. adults"] = {
        "pct": round(100 * weight[major_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 70, fielded July 13-19, 2020.",
        "method": "Population is respondent's religious tradition (F_RELTRAD). Share "
                  "answering \"a major threat\" to COVIDTHREAT_d_W70 (\"how much of a "
                  "threat is the coronavirus outbreak for your personal financial "
                  "situation\"); refused excluded from each row's denominator. Groups "
                  "under 30 valid respondents omitted. Weighted by the dataset's own "
                  "WEIGHT_W70 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "major_financial_threat": results,
    }
    with open("docs/datasets/pew-atp-w70-2020/financial-threat-covid.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w70-2020/financial-threat-covid.json")


if __name__ == "__main__":
    main()
