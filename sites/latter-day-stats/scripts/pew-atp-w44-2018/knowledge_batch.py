"""
Five religious-knowledge quiz items from ATP Wave 44, broken out by
F_RELTRAD (the standard RLS-coded tradition variable this wave carries) -
same by-group construction and MIN_VALID_N floor as
pew-religious-knowledge-2010/mormon_founding_knowledge.py. Each item's own
"not sure"/refused excluded from its own denominator. F_RELTRAD's three
Protestant sub-traditions (Evangelical/Mainline/Historically Black) are
collapsed into one "Protestant" row here, matching the coarser 13-group
set every other ATP-wave chart on this site uses (e.g.
pew-atp-w143-2024's holiday batches) - keeping all three separate pushed
these charts to 15 rows, which overlapped at this pipeline's row-label
wrap width.

- CONREL: what the Constitution says about religious tests for federal
  officeholders. Hook: Constitution Day, Sep 17 2026.
- EASTER: what's commemorated on Easter Sunday. Hook: Easter, Mar 28 2027
  (second post alongside the 2011 Mormon Survey's belief chart).
- RMDN: what Ramadan is. Hook: Ramadan begins, Feb 8 2027 (second post
  alongside ATP W143's fasting-behavior chart).
- JNEWYR: what Rosh Hashana is. Hook: Rosh Hashana, Sep 2026.
- PLGRMG: which city Muslims make a pilgrimage to (Mecca/Hajj). Hook: Eid
  al-Adha, May 2027.
- KFAITHMOD: which tradition traditionally teaches salvation through faith
  alone (correct answer: Protestantism - sola fide). Hook: Reformation
  Day, Oct 31 2026 - a knowledge-quiz companion to the State of Theology
  belief chart on the same doctrine.

Usage: python scripts/pew-atp-w44-2018/knowledge_batch.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-atp-w44-2018/ATP W44.sav"

RELTRAD_CODES = {
    (1100.0, 1200.0, 1300.0): "Protestant",
    (10000.0,): "Catholic",
    (20000.0,): "Latter-day Saint",
    (30000.0,): "Orthodox Christian",
    (40001.0,): "Jehovah's Witness",
    (40002.0,): "Other Christian",
    (50000.0,): "Jewish",
    (60000.0,): "Muslim",
    (70000.0,): "Buddhist",
    (80000.0,): "Hindu",
    (90001.0,): "Other world religions",
    (90002.0,): "Other faiths",
    (100000.0,): "Religiously unaffiliated",
}
MIN_VALID_N = 30


def knowledge_by_group(col, weight, reltrad, correct_code, valid_codes):
    results = {}
    for codes, label in RELTRAD_CODES.items():
        group_mask = np.isin(reltrad, codes)
        valid = group_mask & np.isin(col, list(valid_codes))
        if valid.sum() < MIN_VALID_N:
            continue
        correct = valid & (col == correct_code)
        results[label] = {
            "pct": round(100 * weight[correct].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }
    valid_all = np.isin(col, list(valid_codes))
    correct_all = valid_all & (col == correct_code)
    results["U.S. adults"] = {
        "pct": round(100 * weight[correct_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(col)),
    }
    return results


def main():
    cols = ["F_RELTRAD", "CONREL_W44", "EASTER_W44", "RMDN_W44", "JNEWYR_W44",
            "PLGRMG_W44", "KFAITHMOD_W44", "WEIGHT_W44"]
    df, _ = pyreadstat.read_sav(SAV, usecols=cols)
    weight = df["WEIGHT_W44"].to_numpy()
    reltrad = df["F_RELTRAD"].to_numpy()
    substantive = {1.0, 2.0, 3.0, 4.0}

    conrel = knowledge_by_group(df["CONREL_W44"].to_numpy(), weight, reltrad, 1.0, substantive)
    easter = knowledge_by_group(df["EASTER_W44"].to_numpy(), weight, reltrad, 1.0, substantive)
    ramadan = knowledge_by_group(df["RMDN_W44"].to_numpy(), weight, reltrad, 3.0, substantive)
    rosh_hashana = knowledge_by_group(df["JNEWYR_W44"].to_numpy(), weight, reltrad, 2.0, substantive)
    hajj = knowledge_by_group(df["PLGRMG_W44"].to_numpy(), weight, reltrad, 4.0, substantive)
    faith_alone = knowledge_by_group(df["KFAITHMOD_W44"].to_numpy(), weight, reltrad, 1.0, substantive)

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 44, fielded Feb. 4-19, 2019.",
        "method": "Population is all respondents, grouped by religious tradition (F_RELTRAD). "
                  "Each item's own 'not sure'/refused excluded from its own denominator. Groups "
                  "under 30 valid respondents omitted. Weighted by WEIGHT_W44.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "knows_constitution_no_religious_test": conrel,
        "knows_easter_is_resurrection": easter,
        "knows_ramadan_is_islamic": ramadan,
        "knows_rosh_hashana_is_new_year": rosh_hashana,
        "knows_mecca_is_pilgrimage_city": hajj,
        "knows_protestantism_teaches_faith_alone": faith_alone,
    }
    with open("docs/datasets/pew-atp-w44-2018/knowledge-batch.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Wrote docs/datasets/pew-atp-w44-2018/knowledge-batch.json")


if __name__ == "__main__":
    main()
