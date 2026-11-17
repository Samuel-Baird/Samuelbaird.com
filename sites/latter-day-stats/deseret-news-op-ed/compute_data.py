"""
Computes every number the Deseret News op-ed graphics use, from the three Pew
Religious Landscape Study public-use files, and writes data/oped_data.json.

Microdata (gitignored, see docs/datasets/pew-rls-*/README.md):
  data/pew-rls-2007/Religious Landscape Survey Data - Continental US.sav   (N=35,556)
  data/pew-rls-2014/Dataset - ... 2014 Religious Landscape Study ... .sav    (N=35,071)
  data/pew-rls-2023-24/2023-24 RLS Public Use File Feb 19.csv                (N=36,908)

Conventions (all match Pew's published practice unless noted):
- Every wave weighted by its own full-sample weight (weight / WEIGHT / WEIGHT).
- Population shares (Christian, unaffiliated, LDS, denominations) are % of ALL
  adults, don't-know/refused kept in the denominator - that is how Pew reports
  "62% of U.S. adults are Christian".
- Parents' practices (KIDACT_A/B/C) are % of parents/guardians of children
  under 18 at home (CHILDREN=1). The headline "at least one" uses all such
  parents as the base (a respondent who refused all three items counts as not
  doing any); an `excl_dk` variant drops respondents who refused all three.
  The three component items use that same all-parents base (item-level
  don't-know/refused counted as not doing it), matching Pew's published
  figures for Christian parents (58% pray/read scripture, 48% religious
  education).
- Completed fertility uses FERTREC, which the PUF caps at "4 or more", and
  BIRTHDECADE, the PUF's only age proxy. Pew's published averages (Christians
  2.2, unaffiliated 1.8, ages 40-59) come from the restricted file's exact age
  and uncapped counts, so they cannot be reproduced exactly here. We report the
  full 0/1/2/3/4+ distribution for adults born in the 1960s and 1970s (roughly
  ages 44-64 at fielding, the nearest "finished childbearing" cohort) plus a
  floor mean that counts "4 or more" as 4.
- Transmission uses Pew's own definitions from the 2023-24 overview report:
  "highly religious upbringing" = attended weekly or more (CHATTEND 1-2) AND
  religion very important to the family (CHIMPREL_B=1); "highly religious
  now" = attends weekly or more (ATTNDPERRLS 1-2) AND religion very important
  (RELIMP=1). Age groups are BIRTHDECADE buckets: born 1940s or earlier ~ ages
  74+, born 2000s ~ ages 18-24, which is exactly how Pew's 51% / 28% is cut.
- 2023-24 denominational shares (Southern Baptist Convention, United
  Methodist Church) are NOT computable from the PUF (DENOM/FAMILY are
  restricted-use and blank), so those two 2023-24 values are Pew's published
  figures and flagged as such in the JSON.

Usage (from the repo root):  python deseret-news-op-ed/compute_data.py
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "data" / "oped_data.json"

SAV_2007 = ROOT / "data/pew-rls-2007/Religious Landscape Survey Data - Continental US.sav"
SAV_2014 = ROOT / ("data/pew-rls-2014/Dataset - Pew Research Center 2014 Religious Landscape Study "
                   "National Telephone Survey - Version 1.1 - December 1 2016.sav")
CSV_2324 = ROOT / "data/pew-rls-2023-24/2023-24 RLS Public Use File Feb 19.csv"

CHRISTIAN_RELTRAD = ["1100", "1200", "1300", "10000", "20000", "30000", "40001", "40002"]
UNAFF, LDS, DK = "100000", "20000", "900000"

# Pew's published figures we cannot (or should not) recompute from the PUF.
PUBLISHED = {
    "source_overview": "Pew Research Center, 'Decline of Christianity in the U.S. Has Slowed, May Have "
                       "Leveled Off' (Feb. 26, 2025), https://www.pewresearch.org/religion/2025/02/26/"
                       "decline-of-christianity-in-the-us-has-slowed-may-have-leveled-off/",
    "source_fertility": "Pew Research Center, 2023-24 RLS chapter 'Religion, fertility and child-rearing', "
                        "https://www.pewresearch.org/religion/2025/02/26/religion-fertility-and-child-rearing/",
    "shares_rounded": {
        "Christian": {"2007": 78, "2014": 71, "2023-24": 62},
        "Religiously unaffiliated": {"2007": 16, "2014": 23, "2023-24": 29},
        "Latter-day Saints": {"2007": 2, "2014": 2, "2023-24": 2},
        "Southern Baptist Convention": {"2007": 6.7, "2014": 5.3, "2023-24": 4.4},
        "United Methodist Church": {"2007": 5.1, "2014": 3.6, "2023-24": 2.7},
        "Mainline Protestant": {"2007": 18, "2023-24": 11},
        "Evangelical Protestant": {"2007": 26, "2023-24": 23},
    },
    "fertility_ages_40_59_mean_children": {"Christians": 2.2, "Religiously unaffiliated": 1.8,
                                           "Non-Christian religions": 1.8, "Jewish": 2.0},
    "parents_at_least_one_practice": {"Latter-day Saints": 84, "Christians": 70, "Evangelical Protestants": 82},
    "parents_unaffiliated_religious_education_only": 9,
    "transmission_still_highly_religious": {"ages 74+": 51, "ages 18-24": 28},
    "transmission_definition": "Raised: attended religious services weekly in a family in which religion "
                               "was very important. Now: attends weekly and says religion is very important.",
}


def wshare(w, mask, base=None):
    base = np.ones_like(mask, dtype=bool) if base is None else base
    return round(float(100 * w[mask & base].sum() / w[base].sum()), 2)


def wave_shares(reltrad, denom, w, sbc_code, umc_code):
    r = reltrad.astype(str)
    out = {
        "Christian": wshare(w, np.isin(r, CHRISTIAN_RELTRAD)),
        "Religiously unaffiliated": wshare(w, r == UNAFF),
        "Latter-day Saints": wshare(w, r == LDS),
        "Evangelical Protestant": wshare(w, r == "1100"),
        "Mainline Protestant": wshare(w, r == "1200"),
        "Historically Black Protestant": wshare(w, r == "1300"),
        "Catholic": wshare(w, r == "10000"),
        "Don't know/refused": wshare(w, r == DK),
        "n": int(len(r)),
        "n_lds": int((r == LDS).sum()),
    }
    if denom is not None:
        d = denom.astype(str)
        out["Southern Baptist Convention"] = wshare(w, d == sbc_code)
        out["United Methodist Church"] = wshare(w, d == umc_code)
        out["n_sbc"] = int((d == sbc_code).sum())
        out["n_umc"] = int((d == umc_code).sum())
    return out


def codes_as_str(series: pd.Series) -> np.ndarray:
    """SPSS numeric codes (1100.0) -> '1100'; NaN -> 'nan'."""
    return np.array([str(int(v)) if pd.notna(v) else "nan" for v in series.to_numpy()])


def main():
    print("2007 ...")
    df07, _ = pyreadstat.read_sav(str(SAV_2007), usecols=["reltrad", "denom", "weight"])
    w07 = df07["weight"].to_numpy()
    waves = {"2007": wave_shares(codes_as_str(df07["reltrad"]), codes_as_str(df07["denom"]), w07, "101", "234")}

    print("2014 ...")
    df14, _ = pyreadstat.read_sav(str(SAV_2014), usecols=["RELTRAD", "DENOM", "WEIGHT"])
    w14 = df14["WEIGHT"].to_numpy()
    waves["2014"] = wave_shares(codes_as_str(df14["RELTRAD"]), codes_as_str(df14["DENOM"]), w14, "101", "234")

    print("2023-24 ...")
    cols = ["RELTRAD", "CHILDREN", "KIDACT_A", "KIDACT_B", "KIDACT_C", "FERTREC", "MARITAL", "BIRTHDECADE",
            "CHATTEND", "CHIMPREL_B", "ATTNDPERRLS", "RELIMP", "WEIGHT"]
    df = pd.read_csv(CSV_2324, usecols=cols, dtype={c: str for c in cols if c != "WEIGHT"})
    w = df["WEIGHT"].to_numpy()
    R = df["RELTRAD"].to_numpy()
    waves["2023-24"] = wave_shares(R, None, w, None, None)
    waves["2023-24"]["Southern Baptist Convention"] = None
    waves["2023-24"]["United Methodist Church"] = None
    waves["2023-24"]["denomination_note"] = ("DENOM/FAMILY are restricted-use and blank in the PUF; use "
                                            "PUBLISHED.shares_rounded for SBC/UMC 2023-24.")

    is_chr = np.isin(R, CHRISTIAN_RELTRAD)
    is_lds = R == LDS
    is_un = R == UNAFF
    is_aff = ~is_un & (R != DK)
    groups = {
        "Latter-day Saints": is_lds,
        "All Christians": is_chr,
        "Religiously unaffiliated": is_un,
        "Religiously affiliated": is_aff,
        "Evangelical Protestant": R == "1100",
        "Mainline Protestant": R == "1200",
        "Catholic": R == "10000",
        "All U.S. adults": np.ones(len(df), bool),
    }

    # --- Parents' religious practices with children (KIDACT_A/B/C) ---------
    par = df["CHILDREN"].to_numpy() == "1"
    A, B, C = (df[k].to_numpy() for k in ("KIDACT_A", "KIDACT_B", "KIDACT_C"))
    any_yes = (A == "1") | (B == "1") | (C == "1")
    all_dk = (A == "99") & (B == "99") & (C == "99")
    parents = {}
    for name, g in groups.items():
        base = g & par
        parents[name] = {
            "at_least_one_pct": wshare(w, any_yes, base),
            "at_least_one_excl_dk_pct": wshare(w, any_yes, base & ~all_dk),
            # Same all-parents base as the headline (item-level don't-know/refused
            # counted as not doing it) so the components match Pew's published
            # 58% / 48% for Christian parents.
            "pray_or_read_scripture_pct": wshare(w, A == "1", base),
            "religious_education_pct": wshare(w, B == "1", base),
            "religious_school_or_homeschool_pct": wshare(w, C == "1", base),
            "parents_unweighted_n": int(base.sum()),
        }

    # --- Completed fertility (FERTREC x BIRTHDECADE) ------------------------
    F = df["FERTREC"].to_numpy()
    BD = df["BIRTHDECADE"].to_numpy()
    fert_codes = ["0", "1", "2", "3", "4"]
    fert_labels = {"0": "None", "1": "1", "2": "2", "3": "3", "4": "4 or more"}
    cohorts = {
        "born_1960s_1970s": (np.isin(BD, ["3", "4"]), "Born 1960s-1970s (about ages 44-64 when surveyed)"),
        "born_1950s_1970s": (np.isin(BD, ["2", "3", "4"]), "Born 1950s-1970s (about ages 44-74)"),
        "born_1970s": (BD == "4", "Born 1970s (about ages 44-54)"),
    }
    fertility = {}
    for ckey, (cmask, clabel) in cohorts.items():
        fertility[ckey] = {"label": clabel, "groups": {}}
        for name in ("Religiously affiliated", "Religiously unaffiliated", "All Christians", "Latter-day Saints",
                     "All U.S. adults"):
            base = groups[name] & cmask & np.isin(F, fert_codes)
            bw = w[base]
            dist = {fert_labels[c]: round(float(100 * bw[F[base] == c].sum() / bw.sum()), 2) for c in fert_codes}
            vals = F[base].astype(int)
            fertility[ckey]["groups"][name] = {
                "distribution_pct": dist,
                "mean_children_floor_4plus_as_4": round(float((bw * vals).sum() / bw.sum()), 2),
                "share_3_or_more_pct": round(float(100 * bw[vals >= 3].sum() / bw.sum()), 2),
                "share_none_pct": dist["None"],
                "unweighted_n": int(base.sum()),
            }

    # --- Marital status ------------------------------------------------------
    M = df["MARITAL"].to_numpy()
    marital = {}
    for name in ("Latter-day Saints", "All Christians", "Religiously unaffiliated", "All U.S. adults"):
        base = groups[name] & (M != "99")
        marital[name] = {
            "married_pct": wshare(w, M == "1", base),
            "living_with_partner_pct": wshare(w, M == "2", base),
            "divorced_or_separated_pct": wshare(w, np.isin(M, ["3", "4"]), base),
            "widowed_pct": wshare(w, M == "5", base),
            "never_married_pct": wshare(w, M == "6", base),
            "unweighted_n": int(base.sum()),
        }

    # --- Transmission: raised highly religious -> highly religious now ------
    CA, CIB = df["CHATTEND"].to_numpy(), df["CHIMPREL_B"].to_numpy()
    AT, RI = df["ATTNDPERRLS"].to_numpy(), df["RELIMP"].to_numpy()
    raised_hr = np.isin(CA, ["1", "2"]) & (CIB == "1")
    now_hr = np.isin(AT, ["1", "2"]) & (RI == "1")
    decades = [
        ("1", "1940s or earlier", "74+"),
        ("2", "1950s", "64-74"),
        ("3", "1960s", "54-64"),
        ("4", "1970s", "44-54"),
        ("5", "1980s", "34-44"),
        ("6", "1990s", "24-34"),
        ("7", "2000s", "18-24"),
    ]
    transmission = {"definition": PUBLISHED["transmission_definition"], "by_birth_decade": []}
    for code, label, ages in decades:
        base = raised_hr & (BD == code)
        transmission["by_birth_decade"].append({
            "birth_decade": label,
            "approx_age_at_survey": ages,
            "still_highly_religious_pct": wshare(w, now_hr, base),
            "raised_highly_religious_unweighted_n": int(base.sum()),
            "share_of_cohort_raised_highly_religious_pct": wshare(w, raised_hr, BD == code),
            "share_of_cohort_highly_religious_now_pct": wshare(w, now_hr, BD == code),
        })
    transmission["all_adults_pct"] = wshare(w, now_hr, raised_hr)
    transmission["latter_day_saints_pct"] = wshare(w, now_hr, raised_hr & is_lds)
    transmission["latter_day_saints_raised_hr_unweighted_n"] = int((raised_hr & is_lds).sum())

    out = {
        "generated": date.today().isoformat(),
        "sources": {
            "2007": 'Pew Research Center. 2008. "U.S. Religious Landscape Survey." Continental-US file, N=35,556.',
            "2014": 'Pew Research Center. 2015. "2014 Religious Landscape Study." N=35,071.',
            "2023-24": 'Pew Research Center. 2025. "2023-24 Religious Landscape Study (RLS) Dataset." '
                       'doi: 10.58094/3kwb-bf52. Public-use file, N=36,908.',
        },
        "methods": __doc__.strip(),
        "published": PUBLISHED,
        "waves": waves,
        "parents_practice_2023_24": parents,
        "fertility_2023_24": fertility,
        "marital_2023_24": marital,
        "transmission_2023_24": transmission,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("\nShares of all adults")
    for wv, d in waves.items():
        print(f"  {wv:8} Christian {d['Christian']:5.2f}  Unaff {d['Religiously unaffiliated']:5.2f}  "
              f"LDS {d['Latter-day Saints']:4.2f}  Mainline {d['Mainline Protestant']:5.2f}  "
              f"SBC {d.get('Southern Baptist Convention')}  UMC {d.get('United Methodist Church')}")
    print("\nParents, at least one practice (base: all parents)")
    for name in ("Latter-day Saints", "All Christians", "Religiously unaffiliated"):
        p = parents[name]
        print(f"  {name:26} {p['at_least_one_pct']:5.2f}  (excl DK {p['at_least_one_excl_dk_pct']:5.2f})  n={p['parents_unweighted_n']}")
    print("\nTransmission by birth decade")
    for row in transmission["by_birth_decade"]:
        print(f"  {row['birth_decade']:18} {row['still_highly_religious_pct']:5.2f}  n={row['raised_highly_religious_unweighted_n']}")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
