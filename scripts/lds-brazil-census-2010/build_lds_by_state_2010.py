"""
Builds "Self-identified Latter-day Saints by state, 2010 Census" - all
27 Brazilian states/DF ranked by LDS self-identification as a % of each
state's own total population.

Unlike scripts/lds-brazil-2022/build_smaller_faiths_by_state.py (which uses
IBGE's mixed "Outras religiosidades" bucket because the 2022 Census never
published an LDS-specific category), this dataset uses the **2010** Census
religion table, which DOES break out "Igreja de Jesus Cristo dos Santos dos
Ultimos Dias" (category 100423 under classification 133) as its own row -
real, government-tabulated, LDS-specific counts. Verified this session
against IBGE's public SIDRA aggregate-table API (table 137):

  National, all census years (1991/2000/2010), LDS-specific category:
    https://apisidra.ibge.gov.br/values/t/137/n1/all/v/93/p/all/c133/100423
  -> 1991 and 2000 both return "..." (suppressed/not disclosed) at this
     category; only 2010 has a real, non-suppressed national figure
     (226,509). This is why no 1991/2000/2010 LDS-specific time series is
     built anywhere in this dataset - the earlier two points don't exist.

  State level (n3), LDS counts and total population, 2010:
    https://apisidra.ibge.gov.br/values/t/137/n3/all/v/93/p/2010/c133/100423
    https://apisidra.ibge.gov.br/values/t/137/n3/all/v/93/p/2010/c133/0
  -> all 27 states/DF returned real (non-suppressed) values for both
     queries - no confidentiality gaps to work around.

Reads the raw SIDRA API JSON responses saved at ibge_2010/{lds_state_2010,
pop_state_2010}.json in the scratchpad (re-fetch with the two state-level
URLs above if missing/stale).

Usage:
  python scripts/lds-brazil-census-2010/build_lds_by_state_2010.py
"""
import argparse
import json
from pathlib import Path

DEFAULT_DIR = Path(
    r"C:\Users\b13ll\AppData\Local\Temp\claude\C--Users-b13ll-work-latter-day-stats"
    r"\2a291fd8-02ff-4cd3-93b3-663a3876afc6\scratchpad\ibge_2010"
)

SUPPRESSED = {"...", "-", "X", ".."}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, default=DEFAULT_DIR)
    args = ap.parse_args()

    with open(args.dir / "lds_state_2010.json", encoding="utf-8") as f:
        lds_rows = json.load(f)[1:]
    with open(args.dir / "pop_state_2010.json", encoding="utf-8") as f:
        pop_rows = json.load(f)[1:]

    lds_by_uf = {r["D1N"]: r["V"] for r in lds_rows}
    pop_by_uf = {r["D1N"]: r["V"] for r in pop_rows}

    if len(lds_by_uf) != 27 or len(pop_by_uf) != 27:
        raise SystemExit(
            f"expected 27 states/DF in both queries, got {len(lds_by_uf)} "
            f"LDS rows / {len(pop_by_uf)} population rows - check the source JSON"
        )

    rows = []
    for uf, lds_v in lds_by_uf.items():
        pop_v = pop_by_uf[uf]
        if lds_v in SUPPRESSED or pop_v in SUPPRESSED:
            raise SystemExit(f"unexpected suppressed value for {uf}: lds={lds_v} pop={pop_v}")
        lds = int(lds_v)
        pop = int(pop_v)
        rows.append({"state": uf, "lds": lds, "population": pop, "pct": round(lds / pop * 100, 3)})

    rows.sort(key=lambda r: r["pct"], reverse=True)
    state_order = [r["state"] for r in rows]
    states = {r["state"]: {"lds": r["lds"], "population": r["population"], "pct": r["pct"]} for r in rows}

    # National total from the direct national-level query (226,509) is used
    # as the headline figure; it differs by 1 from summing the 27 state
    # values here (226,508) - a normal rounding/independent-tabulation
    # artifact between SIDRA's national and state aggregation levels, not a
    # data error.
    national_total = 226509

    out = {
        "national_total_2010": national_total,
        "highest_state": state_order[0],
        "highest_state_pct": states[state_order[0]]["pct"],
        "lowest_state": state_order[-1],
        "lowest_state_pct": states[state_order[-1]]["pct"],
        "sources_summary": [
            "2010 Brazilian Census (IBGE), SIDRA aggregate table 137 (\"Populacao "
            "residente, por religiao\"), classification 133 (Religiao), category "
            "100423 (\"Igreja de Jesus Cristo dos Santos dos Ultimos Dias\") - a "
            "real, government-tabulated LDS-specific category, unlike the 2022 "
            "Census (see lds-brazil-2022/smaller-faiths-by-state-2022.json for why "
            "that year can't isolate LDS).",
            "Percentage is each state's LDS count divided by that state's own "
            "total resident population (SIDRA table 137, category 0/Total), both "
            "queried at the state level (n3) for 2010 - ranked by share, not raw "
            "count, since state population varies hugely (Sao Paulo has far more "
            "members in absolute terms but a lower share than several smaller "
            "states).",
        ],
        "method": "Public SIDRA API queries: "
                  "https://apisidra.ibge.gov.br/values/t/137/n3/all/v/93/p/2010/c133/100423 "
                  "(LDS counts by state) and "
                  "https://apisidra.ibge.gov.br/values/t/137/n3/all/v/93/p/2010/c133/0 "
                  "(total population by state), joined on state, all 27 states/DF "
                  "non-suppressed for both queries.",
        "state_order": state_order,
        "states": states,
    }

    out_path = (
        Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "lds-brazil-census-2010"
        / "lds-by-state-2010.json"
    ).resolve()
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for r in rows:
        print(f"{r['state']:>20}  {r['pct']:>6.3f}%  ({r['lds']:,} / {r['population']:,})")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
