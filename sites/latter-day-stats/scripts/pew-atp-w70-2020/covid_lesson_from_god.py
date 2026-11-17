"""
Among those who believe there's a lesson for humankind to learn from the
coronavirus outbreak (COVIDLESSON1_W70), do they believe that lesson was
sent by God (COVIDLESSON2_W70), by religious tradition (F_RELTRAD)? A
providence-attribution item distinct from this folder's already-shipped
`covid-lesson-belief.json` (COVIDLESSON1_W70): that chart measures belief
that a lesson exists at all; this one asks the subset who say a lesson
exists whether God specifically sent it. Ties to LDS providential
theology — a personal, active God who intervenes in human affairs (D&C
1:17, "I the Lord... have sent mine angels to prepare the way before me").
Same population and threshold conventions as the rest of this folder's
scripts (groups under 30 valid respondents dropped).

Usage: python scripts/pew-atp-w70-2020/covid_lesson_from_god.py
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
SENT_BY_GOD = 1.0
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELTRAD", "COVIDLESSON2_W70", "WEIGHT_W70"])
    weight = df["WEIGHT_W70"].to_numpy()
    reltrad = df["F_RELTRAD"].to_numpy()
    sentbygod = df["COVIDLESSON2_W70"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(sentbygod, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        believes = valid & (sentbygod == SENT_BY_GOD)
        results[label] = {
            "pct": round(100 * weight[believes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(sentbygod, list(VALID_CODES))
    believes_all = valid_all & (sentbygod == SENT_BY_GOD)
    results["All U.S. adults"] = {
        "pct": round(100 * weight[believes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 70, fielded July 13-19, 2020.",
        "method": "Population is respondents who believe there is a lesson or set of "
                  "lessons for humankind to learn from the coronavirus outbreak "
                  "(COVIDLESSON1_W70 = yes), broken out by religious tradition "
                  "(F_RELTRAD). Share of that subgroup who believe the lesson(s) were "
                  "sent by God (COVIDLESSON2_W70); refused and 'I do not believe in "
                  "God' excluded from each row's denominator. Groups under 30 valid "
                  "respondents omitted. Weighted by the dataset's own WEIGHT_W70 "
                  "variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "believes_lesson_from_god": results,
    }
    with open("docs/datasets/pew-atp-w70-2020/covid-lesson-from-god.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w70-2020/covid-lesson-from-god.json")


if __name__ == "__main__":
    main()
