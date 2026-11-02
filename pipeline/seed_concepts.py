"""One-off seeder: Pulpit glossary-master + pt/es glossaries + es approved terms -> concepts/*.yaml.

Candidates are *hints* only. attest.py must confirm each against Church text
before the atlas shows it as a translation. Pulpit `Unverified` rows are skipped.
Existing concept files are never overwritten (they are hand-curated).
"""
import re
import sys
import yaml

from .config import CONCEPTS, MASTER, GLOSSARY, APPROVED, LANGS

# Terms from the project brief that are not in Pulpit's master list.
EXTRA = [
    {"term": "intelligence", "category": "Plan of Salvation",
     "note": "D&C 93:29 'intelligence, or the light of truth'; no Pulpit glossary entry. "
             "Renderings are discovered from aligned Church text."},
]

CELL = re.compile(r"\s*\|\s*")


def slugify(s: str) -> str:
    s = s.lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def table_rows(path):
    """Yield (section, [cells]) for every data row in a markdown table file."""
    section = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        elif line.startswith("|") and not line.startswith("|---"):
            cells = [c.strip() for c in CELL.split(line.strip().strip("|"))]
            yield section, cells


def parse_sources(cell: str):
    out = {}
    for part in cell.split("·"):
        part = part.strip()
        m = re.match(r"(GS|Topics|TtF|GH|CFM|TG|BD):\s*(\S+)", part)
        if m and m.group(1) in ("GS", "Topics", "TtF", "GH"):
            out.setdefault(m.group(1), []).append(m.group(2))
    return out


def english_forms(term: str):
    base = re.sub(r"\(s\)$", "", term).strip()
    alts = [a.strip() for a in re.split(r"\s/\s", base) if a.strip()]
    forms = []
    for a in alts:
        if a not in forms:
            forms.append(a)
    return forms


def main():
    master = []
    for section, cells in table_rows(MASTER):
        if len(cells) >= 4 and cells[0] not in ("English term",):
            master.append((section, cells))

    gloss = {}
    for lang, path in GLOSSARY.items():
        d = {}
        for _, c in table_rows(path):
            if len(c) >= 3 and c[0] != "English" and c[1] and c[2] in ("Verified", "Standard"):
                d[c[0].lower()] = (c[1], c[2])
        gloss[lang] = d

    approved = {}
    for lang, path in APPROVED.items():
        d = {}
        for _, c in table_rows(path):
            if len(c) >= 2 and c[0] != "English" and c[1]:
                d.setdefault(c[0].lower(), c[1])
        approved[lang] = d

    CONCEPTS.mkdir(exist_ok=True)
    made = skipped = 0
    entries = [(s, c[0], c[2] if len(c) > 2 else "", c[3] if len(c) > 3 else "", None) for s, c in master]
    entries += [(e["category"], e["term"], "", "", e["note"]) for e in EXTRA]
    for section, term, srcs, note, extra_note in entries:
        slug = slugify(term)
        out = CONCEPTS / f"{slug}.yaml"
        if out.exists():
            skipped += 1
            continue
        cands = {}
        for lang in LANGS:
            lst = []
            seen = set()
            a = approved.get(lang, {}).get(term.lower())
            if a:
                for r in re.split(r"\s*/\s*|,\s+", a):
                    if len(r) >= 4 and r.lower() not in seen:
                        seen.add(r.lower())
                        lst.append({"term": r, "hint": "approved-terms"})
            g = gloss[lang].get(term.lower())
            if g:
                for r in re.split(r"\s+/\s+", g[0]):
                    if r and r.lower() not in seen:
                        seen.add(r.lower())
                        lst.append({"term": r, "hint": f"pulpit-glossary:{g[1].lower()}"})
            cands[lang] = lst
        doc = {
            "id": f"concept.{slug}",
            "category": section,
            "en": {"term": term, "match": english_forms(term)},
            "sources": parse_sources(srcs),
            "candidates": cands,
            "related": [],
        }
        n = extra_note or note
        if n:
            doc["note"] = n
        out.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
        made += 1
    print(f"concepts written: {made}, existing kept: {skipped}")


if __name__ == "__main__":
    sys.exit(main())
