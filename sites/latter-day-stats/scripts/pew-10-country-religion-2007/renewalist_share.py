"""
Flagship chart for Pew Forum's "Spirit and Power: A 10-Country Survey of
Pentecostals" (fielded May-Sept 2006, published Oct 5, 2006): what share of
each country's population is "renewalist" - the survey's own umbrella term
for Pentecostal plus Charismatic Christians (RENEWALIST derived variable,
values 1=Pentecostal, 2=Charismatic, 0=Non-renewalist)?

Population is each country's GENERAL PUBLIC sample only (SAMPLE==1),
excluding the renewalist oversample rows (SAMPLE==2) that exist purely to
get enough Pentecostal/Charismatic respondents for within-group analysis -
including them would inflate every country's renewalist share above its
true population rate. Weighted by GPWGT, the file's own general-public
weight. Checked the value labels for "mormon"/"latter" first (per the task
brief): q3<country> ("do you consider yourself as belonging to a particular
religion") does carry a "Mormon" code in five of the ten countries, but
counts are 1-21 respondents per country - far under this pipeline's
MIN_VALID_N=30 floor - so, as expected for a Pentecostal-focused survey,
there's no usable Latter-day Saint breakout here.

Usage: python scripts/pew-10-country-religion-2007/renewalist_share.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-10-country-religion-2007/pew forum 10-country religion survey data.sav"

COUNTRY_CODES = {
    1.0: "Brazil",
    2.0: "Chile",
    3.0: "Guatemala",
    4.0: "India",
    5.0: "Kenya",
    6.0: "Nigeria",
    7.0: "Philippines",
    8.0: "South Africa",
    9.0: "South Korea",
    10.0: "United States",
}
GENERAL_PUBLIC_SAMPLE = 1.0
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["country", "sample", "renewalist", "GPWGT"])
    gp = df[df["sample"] == GENERAL_PUBLIC_SAMPLE]
    weight = gp["GPWGT"].to_numpy()
    country = gp["country"].to_numpy()
    renewalist = gp["renewalist"].to_numpy()

    results = {}
    for code, label in COUNTRY_CODES.items():
        mask = country == code
        valid = mask & ~np.isnan(renewalist) & ~np.isnan(weight)
        if valid.sum() < MIN_VALID_N:
            continue
        is_renewalist = valid & (renewalist > 0.0)
        results[label] = {
            "pct": round(100 * weight[is_renewalist].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(mask.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": 'Pew Research Center, Forum on Religion & Public Life. 2006. "Spirit and '
                  'Power: A 10-Country Survey of Pentecostals."',
        "method": "Population is each country's general public sample (SAMPLE==1), excluding "
                  "the renewalist oversample rows added to boost within-group analysis. Share "
                  "coded \"Pentecostal\" or \"Charismatic\" on the survey's own RENEWALIST "
                  "derived variable (vs. \"Non-renewalist\"); no missing values on this "
                  "derived field within the general public sample. Weighted by the dataset's "
                  "own GPWGT (general-public weight). Fielded May-September 2006 (see each "
                  "country's own field dates in the topline); India's sample covers "
                  "disproportionately Christian districts of three states and is not "
                  "representative of India as a whole, per Pew's own note in the topline.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(gp)),
        "group_order": order,
        "renewalist_share": results,
    }
    with open(
        "docs/datasets/pew-10-country-religion-2007/renewalist-share.json",
        "w", encoding="utf-8",
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:16} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-10-country-religion-2007/renewalist-share.json")


if __name__ == "__main__":
    main()
