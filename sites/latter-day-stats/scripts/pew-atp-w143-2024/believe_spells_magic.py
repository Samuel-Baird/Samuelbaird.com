"""
Fifth batch item for ATP Wave 143 (Feb. 2024): belief that spells, curses,
or other magic can influence people's lives (BELIEVE_SPEL_W143). Same
F_RELIG group set and by-group construction as holiday_batch.py/
holiday_batch_4.py in this folder - see religious_minority.py's own
docstring for why F_RELIG (not F_RELTRAD) is this wave's group variable.

Latter-day Saints land at 25.5% - the lowest of the wave's four named
Christian traditions (Protestant 30.0%, Catholic 31.4%, Orthodox Christian
58.5%), though still above several non-Christian/secular groups (Atheist
7.3%, Jewish 15.0%, Agnostic 20.2%). Ties to Book of Mormon/Doctrine and
Covenants counsel against sorcery, divination, and "curious workmanship"
(e.g. Alma 1:32, D&C 63:17 numbers sorcerers among "the wicked and
adulterous"): among Christian traditions, Latter-day Saints are the least
likely to say spells/curses/magic can influence people's lives.

Checked for overlap first against pew-latin-america-2014's existing
"magic, sorcery, or witchcraft" chart - similar wording, but that dataset
folds Mormons into an undifferentiated "Other religion" bucket with no
Mormon-specific data point, so this is not a duplicate; it's the first
chart on the site with an actual Latter-day Saint belief-in-magic figure.

Usage: python scripts/pew-atp-w143-2024/believe_spells_magic.py
"""
import json

import pyreadstat

from holiday_batch import binary_by_group

SAV = "data/pew-atp-w143-2024/ATP W143.sav"


def main():
    cols = ["F_RELIG", "BELIEVE_SPEL_W143", "WEIGHT_W143"]
    df, _ = pyreadstat.read_sav(SAV, usecols=cols)
    weight = df["WEIGHT_W143"].to_numpy()
    relig = df["F_RELIG"].to_numpy()

    believe_spells_magic = binary_by_group(
        df["BELIEVE_SPEL_W143"].to_numpy(), weight, relig, {1.0}, {1.0, 2.0}
    )

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 143, fielded Feb. 13-25, 2024.",
        "method": "Population is all respondents, grouped by religious affiliation (F_RELIG). "
                  "Share answering 'yes, I believe' that spells, curses, or other magic can "
                  "influence people's lives; refused excluded from each row's denominator. "
                  "Groups under 30 valid respondents omitted. Weighted by WEIGHT_W143.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "believes_in_spells_magic": believe_spells_magic,
    }
    with open("docs/datasets/pew-atp-w143-2024/believe-spells-magic.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label, r in sorted(believe_spells_magic.items(), key=lambda kv: -kv[1]["pct"]):
        print(f"{label:24} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w143-2024/believe-spells-magic.json")


if __name__ == "__main__":
    main()
