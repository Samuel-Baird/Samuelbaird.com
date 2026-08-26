#!/usr/bin/env python3
"""Turn Pew's RLS codebook spreadsheet into a machine-readable JSON codebook.

The published codebook is an .xlsx with one row per (variable, value) pair
and the variable name/label only on the first row of each block. This
flattens that into one object per variable, so the taxonomy in
src/lib/evangelical-quiz/demographics.ts can be checked against the source
rather than retyped from memory.

Standard library only (an .xlsx is a zip of XML) - no pip install needed.

    python scripts/pew-rls/extract_codebook.py \
        docs/datasets/pew-rls-2023-24/source/codebook.xlsx \
        docs/datasets/pew-rls-2023-24/codebook.json
"""

import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def cell_text(cell, shared):
    """The displayed text of one <c>, resolving shared-string references."""
    v = cell.find(NS + "v")
    if v is None:
        inline = cell.find(NS + "is")
        if inline is None:
            return ""
        return "".join(t.text or "" for t in inline.iter(NS + "t"))
    if cell.get("t") == "s":
        return shared[int(v.text)]
    return v.text or ""


def read_rows(path):
    """Every row of the first worksheet, as {column letter: text}."""
    with zipfile.ZipFile(path) as z:
        shared = [
            "".join(t.text or "" for t in si.iter(NS + "t"))
            for si in ET.fromstring(z.read("xl/sharedStrings.xml"))
        ]
        sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))

    rows = []
    for row in sheet.find(NS + "sheetData"):
        cells = {}
        for c in row:
            col = re.match(r"[A-Z]+", c.get("r")).group()
            cells[col] = cell_text(c, shared)
        rows.append(cells)
    return rows


def to_codebook(rows):
    """Fold the (variable, value) rows into one entry per variable.

    Column A repeats the variable name on every row of a block, so a new
    variable starts only where the name changes; the human-readable label
    is carried on the block's first row only. Rows whose "value label" is
    Min./Max. Val. describe a numeric range rather than a category, so
    they become `range` instead of `values`.
    """
    codebook = []
    current = None
    for row in rows[1:]:  # row 0 is the header
        name = row.get("A", "").strip()
        if not name:
            name = current["variable"] if current else ""
        if current is None or name != current["variable"]:
            label = row.get("B", "").strip()
            current = {
                "variable": name,
                "label": label,
                "restricted_use_only": "only available in restricted use file" in label,
                "values": [],
            }
            codebook.append(current)

        value, label = row.get("C", "").strip(), row.get("D", "").strip()
        if not value and not label:
            continue
        if label in ("Min. Val.", "Max. Val", "Max. Val."):
            bound = "min" if label.startswith("Min") else "max"
            current.setdefault("range", {})[bound] = value
        else:
            current["values"].append({"value": value, "label": label})

    for entry in codebook:
        if not entry["values"]:
            del entry["values"]
    return codebook


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    codebook = to_codebook(read_rows(sys.argv[1]))
    with open(sys.argv[2], "w", encoding="utf-8", newline="\n") as f:
        json.dump(
            {
                "source": "Pew Research Center. 2025. “2023-24 Religious "
                "Landscape Study (RLS) Dataset.” doi: 10.58094/3kwb-bf52.",
                "generated_by": "scripts/pew-rls/extract_codebook.py",
                "variable_count": len(codebook),
                "variables": codebook,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
        f.write("\n")
    print(f"{len(codebook)} variables -> {sys.argv[2]}")


if __name__ == "__main__":
    main()
