"""
Builds "Cities with the highest concentration of Latter-day Saints, 2010
Census" - municipality-level (IBGE n6), same LDS-specific category
(100423) as build_lds_by_state_2010.py, restricted to municipalities with
total 2010 population >= 50,000 to avoid small-town noise (a single family
in a town of a few hundred people can otherwise produce a spuriously huge
percentage - this floor is a statistical-significance requirement, not a
style choice).

Source queries (municipality level, n6, 2010):
  https://apisidra.ibge.gov.br/values/t/137/n6/all/v/93/p/2010/c133/100423
  https://apisidra.ibge.gov.br/values/t/137/n6/all/v/93/p/2010/c133/0

Of Brazil's 5,565 municipalities, most (~4,548) come back suppressed
("...") at this LDS-specific category - normal for a small population in a
small town, and exactly why this chart restricts to population >= 50,000:
470 municipalities clear that floor with a real, non-suppressed LDS count.
Only the top N (see --top-n) are shown - this is a top-cities chart, not
an attempt to show all 470.

Reads the raw SIDRA API JSON responses saved at ibge_2010/{lds_muni_2010,
pop_muni_2010}.json in the scratchpad (re-fetch with the two URLs above if
missing/stale).

Usage:
  python scripts/lds-brazil-census-2010/build_top_cities_2010.py
"""
import argparse
import json
import re
from pathlib import Path

DEFAULT_DIR = Path(
    r"C:\Users\b13ll\AppData\Local\Temp\claude\C--Users-b13ll-work-latter-day-stats"
    r"\2a291fd8-02ff-4cd3-93b3-663a3876afc6\scratchpad\ibge_2010"
)

SUPPRESSED = {"...", "-", "X", ".."}
POP_FLOOR = 50_000


def clean_name(raw: str) -> str:
    """SIDRA's D1N for a municipality is "City Name - UF" (e.g.
    "Sant'Ana do Livramento - RS"). Keep that shape - it's exactly the
    "city, state" framing the chart needs - but only normalize the FINAL
    " - UF" separator's spacing, not every hyphen in the string: several
    city names are themselves hyphenated (e.g. "Embu-Guacu"), and blindly
    re-spacing every "-" would incorrectly split those into two words."""
    m = re.match(r"^(.*)-\s*([A-Z]{2})$", raw.strip())
    if not m:
        return raw.strip()
    return f"{m.group(1).strip()} - {m.group(2)}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, default=DEFAULT_DIR)
    ap.add_argument("--top-n", type=int, default=12)
    args = ap.parse_args()

    with open(args.dir / "lds_muni_2010.json", encoding="utf-8") as f:
        lds_rows = json.load(f)[1:]
    with open(args.dir / "pop_muni_2010.json", encoding="utf-8") as f:
        pop_rows = json.load(f)[1:]

    lds_by_code = {r["D1C"]: r for r in lds_rows}
    pop_by_code = {r["D1C"]: r for r in pop_rows}

    eligible = []
    suppressed_count = 0
    for code, r in lds_by_code.items():
        p = pop_by_code.get(code)
        if p is None:
            continue
        lds_v, pop_v = r["V"], p["V"]
        if lds_v in SUPPRESSED or pop_v in SUPPRESSED:
            suppressed_count += 1
            continue
        lds, pop = int(lds_v), int(pop_v)
        if pop < POP_FLOOR:
            continue
        eligible.append({
            "city": clean_name(r["D1N"]),
            "lds": lds,
            "population": pop,
            "pct": round(lds / pop * 100, 3),
        })

    eligible.sort(key=lambda r: r["pct"], reverse=True)
    top = eligible[: args.top_n]

    rs_in_top10 = sum(1 for r in top[:10] if r["city"].endswith("- RS"))

    city_order = [r["city"] for r in top]
    cities = {r["city"]: {"lds": r["lds"], "population": r["population"], "pct": r["pct"]} for r in top}

    out = {
        "population_floor": POP_FLOOR,
        "n_eligible_municipalities": len(eligible),
        "n_total_municipalities_queried": len(lds_by_code),
        "top_city": city_order[0],
        "top_city_pct": cities[city_order[0]]["pct"],
        "rs_in_top10": rs_in_top10,
        "sources_summary": [
            "2010 Brazilian Census (IBGE), SIDRA aggregate table 137, classification "
            "133 (Religiao), category 100423 (\"Igreja de Jesus Cristo dos Santos dos "
            "Ultimos Dias\") at the municipality level (n6), restricted to "
            f"municipalities with total 2010 population >= {POP_FLOOR:,} to avoid "
            "small-town statistical noise.",
        ],
        "method": f"Of {len(lds_by_code):,} Brazilian municipalities queried, "
                  f"{len(eligible):,} had both a non-suppressed LDS-specific count "
                  f"and total population >= {POP_FLOOR:,}; the chart shows only the "
                  f"top {args.top_n} of those by share of population. Several of the "
                  "highest-concentration cities are in Rio Grande do Sul, including "
                  "border cities with Uruguay/Argentina, consistent with the "
                  "Church's history of early missionary concentration in southern "
                  "Brazil.",
        "city_order": city_order,
        "cities": cities,
    }

    out_path = (
        Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "lds-brazil-census-2010"
        / "top-cities-2010.json"
    ).resolve()
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"{suppressed_count:,} municipalities suppressed at this category")
    print(f"{len(eligible):,} eligible (pop >= {POP_FLOOR:,}); showing top {args.top_n}")
    for r in top:
        print(f"{r['city']:40} {r['pct']:>6.3f}%  ({r['lds']:,} / {r['population']:,})")
    print(f"RS cities in top 10: {rs_in_top10}")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
