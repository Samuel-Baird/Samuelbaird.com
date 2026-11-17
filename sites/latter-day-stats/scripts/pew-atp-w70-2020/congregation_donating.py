"""
Fourth flagship-style chart for ATP Wave 70 (July 2020): does the
respondent donate money to the house of worship they attend most often at
all (CONGDONATE_W70), by religious tradition (F_RELTRAD)? The item asks
whether COVID changed the amount given (more/less/about the same) or
whether the respondent does not donate at all; the reported share here is
everyone NOT selecting "I do not donate" - i.e. any regular congregational
giving, regardless of whether COVID moved the amount. Same population and
threshold conventions as the other w70 flagship charts (groups under 30
valid respondents dropped).

Usage: python scripts/pew-atp-w70-2020/congregation_donating.py
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
DOES_NOT_DONATE = 4.0
VALID_CODES = {1.0, 2.0, 3.0, 4.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELTRAD", "CONGDONATE_W70", "WEIGHT_W70"])
    weight = df["WEIGHT_W70"].to_numpy()
    reltrad = df["F_RELTRAD"].to_numpy()
    donate = df["CONGDONATE_W70"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(donate, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        donates = valid & (donate != DOES_NOT_DONATE)
        results[label] = {
            "pct": round(100 * weight[donates].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(donate, list(VALID_CODES))
    donates_all = valid_all & (donate != DOES_NOT_DONATE)
    results["All U.S. adults"] = {
        "pct": round(100 * weight[donates_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 70, fielded July 13-19, 2020.",
        "method": "Population is respondent's religious tradition (F_RELTRAD). Share NOT "
                  "answering \"I do not donate\" on CONGDONATE_W70 (\"since the start of the "
                  "coronavirus outbreak, how much money have you donated to the house of "
                  "worship you attend most often\") - i.e. any regular congregational giving, "
                  "whether more, less, or about the same as usual; refused excluded from each "
                  "row's denominator. Groups under 30 valid respondents omitted. Weighted by "
                  "the dataset's own WEIGHT_W70 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "donates_to_congregation": results,
    }
    with open("docs/datasets/pew-atp-w70-2020/congregation-donating.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w70-2020/congregation-donating.json")


if __name__ == "__main__":
    main()
