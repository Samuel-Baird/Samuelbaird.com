"""
Builds "Self-identification vs. Church membership records, 2010" - a
two-bar comparison, same census year (2010):

  - 226,509: people who told the census taker they were Latter-day Saints
    (IBGE 2010 Census, SIDRA table 137, category 100423 - see
    build_lds_by_state_2010.py's docstring for the source and how it was
    verified).
  - 1,138,740: the Church's own reported membership total for Brazil in
    2010 (cumorah.com LDS Growth Case Studies, Matt Martinich,
    "Expanding LDS Outreach in Brazil" - the same figure already cited for
    2010 in docs/datasets/lds-brazil-2022/membership-by-year.json).

Framing note (do not change without re-reading this): the ~5:1 gap between
these two numbers is real and worth showing, but this dataset does NOT
assert a single cause for it. Membership records can include people who
are inactive, moved away, never really engaged after baptism, or simply
did not tell a census taker their religious affiliation truthfully; record
lag/duplication is also possible. The title/subtitle/caption describe what
each bar measures ("told the census taker" vs. "on Church membership
rolls") rather than picking one explanation.

No inline hard-coded figures beyond the two cited above - both are already
independently verified (SIDRA API for the census figure, cross-referenced
against the existing membership-by-year.json entry for the Church figure).

Usage:
  python scripts/lds-brazil-census-2010/build_self_id_vs_membership_2010.py
"""
import json
from pathlib import Path

CENSUS_SELF_ID_2010 = 226509
CHURCH_MEMBERSHIP_2010 = 1138740


def main():
    ratio = CHURCH_MEMBERSHIP_2010 / CENSUS_SELF_ID_2010

    out = {
        "year": 2010,
        "row_order": ["Self-identified to census taker", "On Church membership rolls"],
        "rows": {
            "Self-identified to census taker": {
                "value": CENSUS_SELF_ID_2010,
                "source": "2010 Brazilian Census (IBGE), SIDRA table 137, category 100423",
            },
            "On Church membership rolls": {
                "value": CHURCH_MEMBERSHIP_2010,
                "source": "cumorah.com LDS Growth Case Studies (Matt Martinich), "
                          "\"Expanding LDS Outreach in Brazil\"",
            },
        },
        "ratio_membership_to_selfid": round(ratio, 2),
        "sources_summary": [
            "2010 Brazilian Census (IBGE), SIDRA aggregate table 137, classification "
            "133 (Religiao), category 100423 (\"Igreja de Jesus Cristo dos Santos dos "
            "Ultimos Dias\") - verified against "
            "https://apisidra.ibge.gov.br/values/t/137/n1/all/v/93/p/all/c133/100423.",
            "cumorah.com LDS Growth Case Studies (Matt Martinich), \"Expanding LDS "
            "Outreach in Brazil\" - same 2010 figure already cited in "
            "docs/datasets/lds-brazil-2022/membership-by-year.json.",
        ],
        "method": "A direct same-year (2010) comparison of two differently-defined "
                  "counts: how many people told an IBGE census taker they were "
                  "Latter-day Saints, versus how many people the Church itself counted "
                  "as members on its own rolls. This chart does not attribute the gap "
                  "to any single cause (inactivity, moving away, declining to state a "
                  "religion, record lag) - see this script's own docstring.",
    }

    out_path = (
        Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "lds-brazil-census-2010"
        / "self-id-vs-membership-2010.json"
    ).resolve()
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Self-identified: {CENSUS_SELF_ID_2010:,}")
    print(f"Church rolls:     {CHURCH_MEMBERSHIP_2010:,}")
    print(f"Ratio: {ratio:.2f}x")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
