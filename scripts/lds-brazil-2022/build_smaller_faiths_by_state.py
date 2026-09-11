"""
Builds the "Outras religiosidades" (Other religions) share-by-state
dataset from the 2022 Brazilian Census (IBGE), weighted tabulation.

CRITICAL FRAMING: this is NOT an LDS-specific figure. IBGE's public 2022
Census microdata only breaks religious affiliation into 9 broad groups;
"Outras religiosidades" (religion_code 6) is a mixed catch-all bucket that
includes Latter-day Saints alongside Jehovah's Witnesses, Spiritualists,
Jews, Muslims, Buddhists, esoteric traditions, and more. IBGE has not
published a more granular breakout that would isolate LDS specifically
(checked: the public microdata, the SIDRA agregados API, and the official
"Religioes: Resultados preliminares da amostra" PDF report all stop at
these 9 broad groups). Never label this chart, its title, or its caption
as an LDS/Mormon number.

Reads the already-computed, already-verified weighted tabulation at
ibge_religion_by_state_2022.csv (weighted by P0110 sample weight,
restricted to population age 10+, since religion wasn't asked of
under-10s) rather than re-running the ~8GB raw-microdata job. That
tabulation cross-checks against the official report's own state-level
figures: Roraima's 7.78% computed share matches the report's stated
Roraima figure of ~7.8%, the highest of any state.

Usage:
  python scripts/lds-brazil-2022/build_smaller_faiths_by_state.py \
    --csv <path to ibge_religion_by_state_2022.csv>
"""
import argparse
import csv
import json
from pathlib import Path

OTHER_RELIGIONS_CODE = "6"

DEFAULT_CSV = Path(
    r"C:\Users\b13ll\AppData\Local\Temp\claude\C--Users-b13ll-work-latter-day-stats"
    r"\2a291fd8-02ff-4cd3-93b3-663a3876afc6\scratchpad\ibge_religion_by_state_2022.csv"
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    args = ap.parse_args()

    rows = []
    with open(args.csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["religion_code"] == OTHER_RELIGIONS_CODE:
                rows.append({
                    "state": row["uf_name"],
                    "pct": round(float(row["pct_of_state_10plus"]), 2),
                    "weighted_persons": round(float(row["weighted_persons"])),
                })

    if len(rows) != 27:
        raise SystemExit(f"expected 27 states/DF, found {len(rows)} - check the CSV")

    rows.sort(key=lambda r: r["pct"], reverse=True)
    state_order = [r["state"] for r in rows]
    states = {r["state"]: {"pct": r["pct"], "weighted_persons": r["weighted_persons"]} for r in rows}

    out = {
        "national_pct_2022": 4.0,
        "national_pct_2010": 2.7,
        "highest_state": state_order[0],
        "highest_state_pct": states[state_order[0]]["pct"],
        "sources_summary": [
            "2022 Census microdata (Pessoas file), Brazilian Institute of Geography and "
            "Statistics (IBGE) - own weighted tabulation, weighted by the P0110 sample "
            "weight, restricted to population age 10+ (religion was not asked of "
            "under-10s).",
            "Cross-checked against IBGE's own published national and state figures in "
            "\"Censo Demografico 2022 Religioes: Resultados preliminares da amostra\" "
            "(official report), which states a national \"Outras religiosidades\" share "
            "of 2.7% (2010) to 4.0% (2022), and Roraima as the highest state at "
            "approximately 7.8%.",
        ],
        "method": "IBGE's public 2022 Census microdata sorts religious affiliation into "
                  "9 broad groups; \"Outras religiosidades\" (religion code 6) is a mixed "
                  "bucket covering every religion outside the 8 other named categories - "
                  "including Latter-day Saints, Jehovah's Witnesses, Spiritualists, Jews, "
                  "Muslims, Buddhists, and esoteric traditions, among others. IBGE has not "
                  "released a more granular 33-category breakout that would isolate any "
                  "single one of those groups (including LDS) from this bucket, in either "
                  "the public microdata, the SIDRA agregados API, or the official "
                  "preliminary-sample report checked for this chart. This chart is NOT an "
                  "estimate of Latter-day Saint population by state and should never be "
                  "read as one.",
        "state_order": state_order,
        "states": states,
    }

    out_path = (
        Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "lds-brazil-2022"
        / "smaller-faiths-by-state-2022.json"
    ).resolve()
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for r in rows:
        print(f"{r['state']:>20}  {r['pct']:>5.2f}%")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
