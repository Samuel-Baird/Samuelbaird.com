"""
2014 Religious Landscape Study: do you describe yourself as a "born-again"
or evangelical Christian, or not (born), by current religious tradition
(RELTRAD)? Like qh2, this item was asked only of respondents the survey's
skip logic had already classified as Christian - Jewish/Muslim/Buddhist/
Hindu/Unaffiliated respondents have zero valid cases, confirmed against the
.sav. "Born-again" is a specifically Evangelical/Protestant self-label;
Latter-day Saints have their own conversion language (baptism, confirmation,
personal testimony) but rarely reach for this particular term, even though
LDS theology has its own strong doctrine of spiritual rebirth - this item
checks how far that labeling gap actually runs against real data, alongside
every other Christian tradition. Jehovah's Witness clears the sample
(n=245) but falls under the 30-valid floor on this skip-gated item and is
dropped, same convention as certainty_of_god.py in this folder.

Usage: python scripts/pew-rls-2014/born_again_identity.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-rls-2014/"
       "Dataset - Pew Research Center 2014 Religious Landscape Study National Telephone "
       "Survey - Version 1.1 - December 1 2016.sav")

RELTRAD_CODES = {
    1100.0: "Evangelical Protestant Tradition",
    1200.0: "Mainline Protestant Tradition",
    1300.0: "Historically Black Protestant Tradition",
    10000.0: "Catholic",
    20000.0: "Mormon",
    30000.0: "Orthodox Christian",
    40001.0: "Jehovah's Witness",
}
BORN_AGAIN_CODE = {1.0}
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELTRAD", "born", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    reltrad = df["RELTRAD"].to_numpy()
    born = df["born"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(born, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & np.isin(born, list(BORN_AGAIN_CODE))
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(born, list(VALID_CODES))
    yes_all = valid_all & np.isin(born, list(BORN_AGAIN_CODE))
    results["All Christian traditions"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(valid_all.sum()),
    }

    order = [label for label in results if label != "All Christian traditions"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All Christian traditions")

    out = {
        "source": 'Pew Research Center. 2015. "2014 Religious Landscape Study."',
        "method": "Population is current religious tradition (RELTRAD), restricted to "
                  "Christian traditions - born was asked only of respondents the survey's "
                  "skip logic had already classified as Christian; non-Christian and "
                  "unaffiliated respondents have no valid cases on this item. Share shown "
                  "self-describes as a \"born-again\" or evangelical Christian; don't know/"
                  "refused/undesignated are excluded from each row's denominator. Groups "
                  "with fewer than 30 valid respondents are omitted. Weighted by the "
                  "dataset's own national WEIGHT variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "born_again_or_evangelical": results,
    }
    with open(
        "docs/datasets/pew-rls-2014/born-again-identity.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2014/born-again-identity.json")


if __name__ == "__main__":
    main()
