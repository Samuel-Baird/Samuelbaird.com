"""
Flagship chart for the Pew "Being Christian in Western Europe" church-tax
add-on: what share of adults currently pay the church tax (Q13), by
country? Church tax - a tax collected by the state and remitted to
registered churches, historically tied to baptismal registration - only
exists in a subset of the survey's 15 countries, so Q13 was fielded only
in the 9 where it applies (confirmed against the codebook's own skip
instruction: "ASK ALL IN AUSTRIA, DENMARK, FINLAND, GERMANY, ITALY,
PORTUGAL, SPAIN, SWEDEN, SWITZERLAND" - six with mandatory church taxes,
three (Italy, Portugal, Spain) with voluntary opt-in programs per Pew's
2019 report). The other 7 countries in the base survey (Belgium, France,
Ireland, Netherlands, Norway, Slovak Republic, UK) never had Q13 asked and
are excluded entirely rather than shown as 0%/blank.

Denominator is Q13's three substantive codes (1 Yes / 2 No / 3 "I do not
pay any taxes"), i.e. everyone who gave a real answer about their current
church-tax status; only don't-know (98) and refused (99) are dropped from
the denominator. Numerator is code 1 (Yes).

Usage: python scripts/pew-church-tax-western-europe/pays_church_tax.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-church-tax-western-europe/Western Europe Public Data_Church Tax Added.sav"

# Countries where Q13 ("Do you currently pay the church tax, or not?") was
# asked at all - the codebook's own ASK instruction, not an inference from
# missingness alone (confirmed against it below).
COUNTRY_CODES = {
    1.0: "Austria",
    3.0: "Denmark",
    4.0: "Finland",
    6.0: "Germany",
    8.0: "Italy",
    11.0: "Portugal",
    13.0: "Spain",
    14.0: "Sweden",
    15.0: "Switzerland",
}
YES = 1.0
VALID_CODES = {1.0, 2.0, 3.0}  # Yes / No / "I do not pay any taxes" - excludes DK(98), refused(99)
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["country", "Q13", "weight"])
    weight = df["weight"].to_numpy()
    country = df["country"].to_numpy()
    q13 = df["Q13"].to_numpy()

    # Sanity-check the codebook's ASK list against the raw missingness
    # pattern: every respondent outside COUNTRY_CODES should have Q13
    # missing, and every respondent inside it should have Q13 answered
    # (valid or not-DK/refused) at a normal survey non-response rate.
    asked_mask = np.isin(country, list(COUNTRY_CODES))
    assert np.all(np.isnan(q13[~asked_mask])), "Q13 answered outside the codebook's ASK list"
    assert np.isnan(q13[asked_mask]).sum() == 0, "Q13 missing for a respondent it should've been asked"

    results = {}
    for code, label in COUNTRY_CODES.items():
        group_mask = country == code
        valid = group_mask & np.isin(q13, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (q13 == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = asked_mask & np.isin(q13, list(VALID_CODES))
    yes_all = valid_all & (q13 == YES)
    results["9-country average"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(asked_mask.sum()),
    }

    order = [label for label in results if label != "9-country average"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("9-country average")

    out = {
        "source": "Pew Research Center. Being Christian in Western Europe survey, church-tax "
                   "add-on, fielded April-August 2017.",
        "method": "Population is respondents in the 9 countries where the church tax exists "
                  "and Q13 was asked (Austria, Denmark, Finland, Germany, Italy, Portugal, "
                  "Spain, Sweden, Switzerland - the codebook's own ASK list). Share answering "
                  "\"yes\" to Q13 (\"Do you currently pay the church tax, or not?\"); "
                  "denominator is Q13's three substantive codes (yes / no / \"I do not pay "
                  "any taxes\"), don't-know and refused excluded. Weighted by the dataset's "
                  "own weight variable.",
        "total_weighted_n": float(weight[asked_mask].sum()),
        "total_unweighted_n": int(asked_mask.sum()),
        "group_order": order,
        "pays_church_tax": results,
    }
    with open("docs/datasets/pew-church-tax-western-europe/pays-church-tax.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:20} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-church-tax-western-europe/pays-church-tax.json")


if __name__ == "__main__":
    main()
