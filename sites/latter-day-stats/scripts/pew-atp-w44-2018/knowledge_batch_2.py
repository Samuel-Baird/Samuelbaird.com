"""
Second religious-knowledge batch from ATP Wave 44 (Feb. 2019), broken out by
F_RELTRAD with the same collapsed 13-group set, MIN_VALID_N floor, and
by-group construction as knowledge_batch.py (whose knowledge_by_group()
this file imports rather than copies). Chosen after a full sweep of the
wave's 32 knowledge items against every live chart: Latter-day Saints score
above the national average on Bible and Christian-teaching items and well
below it on other traditions' doctrines, so this batch shows both sides.

- SERMON: who delivered the Sermon on the Mount (correct: Jesus, code 3).
  Latter-day Saints 84.7% vs 72.3% of all adults.
- COMMAND: which is NOT one of the Ten Commandments (correct: "Do unto
  others as you would have them do unto you," code 4). LDS 76.7% vs 63.5%.
- PRGTRY: what purgatory is in Catholic teaching (correct: where souls
  undergo purification before entering heaven, code 3). LDS 32.2% vs 66%;
  61% of Latter-day Saints instead chose "where the souls of evildoers go
  for eternal punishment" - a doctrine the Church does not teach, and the
  lowest correct share of any tradition.
- PROSGOSP: what the prosperity gospel teaches (correct: the faithful will
  be blessed with financial success, code 1). LDS 26.5% vs 44.7%.
- RELTEACHc: "How much do you personally know about Mormonism?" - share
  saying a lot or some (codes 1-2), the one non-quiz item here: how much
  the rest of the country says it knows about the Church, by tradition.
  Latter-day Saints' own row (95%) is kept for honesty rather than dropped.

Usage: python scripts/pew-atp-w44-2018/knowledge_batch_2.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pyreadstat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from knowledge_batch import MIN_VALID_N, RELTRAD_CODES, SAV, knowledge_by_group  # noqa: E402


def share_by_group(col, weight, reltrad, yes_codes, valid_codes):
    """Like knowledge_by_group but with a set of 'yes' codes (top-two-box)."""
    results = {}
    for codes, label in RELTRAD_CODES.items():
        group_mask = np.isin(reltrad, codes)
        valid = group_mask & np.isin(col, list(valid_codes))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & np.isin(col, list(yes_codes))
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }
    valid_all = np.isin(col, list(valid_codes))
    yes_all = valid_all & np.isin(col, list(yes_codes))
    results["U.S. adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(col)),
    }
    return results


def main():
    cols = ["F_RELTRAD", "SERMON_W44", "COMMAND_W44", "PRGTRY_W44", "PROSGOSP_W44",
            "RELTEACHc_W44", "WEIGHT_W44"]
    df, _ = pyreadstat.read_sav(SAV, usecols=cols)
    weight = df["WEIGHT_W44"].to_numpy()
    reltrad = df["F_RELTRAD"].to_numpy()
    substantive = {1.0, 2.0, 3.0, 4.0}

    sermon = knowledge_by_group(df["SERMON_W44"].to_numpy(), weight, reltrad, 3.0, substantive)
    command = knowledge_by_group(df["COMMAND_W44"].to_numpy(), weight, reltrad, 4.0, substantive)
    purgatory = knowledge_by_group(df["PRGTRY_W44"].to_numpy(), weight, reltrad, 3.0, substantive)
    prosperity = knowledge_by_group(df["PROSGOSP_W44"].to_numpy(), weight, reltrad, 1.0, substantive)
    knows_mormonism = share_by_group(df["RELTEACHc_W44"].to_numpy(), weight, reltrad, {1.0, 2.0}, substantive)

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 44, fielded Feb. 4-19, 2019.",
        "method": "Population is all respondents, grouped by religious tradition (F_RELTRAD). "
                  "Each item's own 'not sure'/refused excluded from its own denominator. Groups "
                  "under 30 valid respondents omitted. Weighted by WEIGHT_W44. Knowledge items "
                  "read the share choosing the correct answer; RELTEACHc reads the share saying "
                  "they know 'a lot' or 'some' about Mormonism.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "knows_sermon_on_mount_jesus": sermon,
        "knows_golden_rule_not_commandment": command,
        "knows_purgatory_purification": purgatory,
        "knows_prosperity_gospel": prosperity,
        "knows_about_mormonism_a_lot_or_some": knows_mormonism,
    }
    with open("docs/datasets/pew-atp-w44-2018/knowledge-batch-2.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    for key in list(out)[5:]:
        print(f"\n=== {key} ===")
        for label, r in out[key].items():
            print(f"{label:28} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w44-2018/knowledge-batch-2.json")


if __name__ == "__main__":
    main()
