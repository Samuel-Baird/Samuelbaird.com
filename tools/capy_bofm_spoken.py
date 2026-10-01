#!/usr/bin/env python3
"""Derive a Chatterbox `spoken:` respelling for every entry in
assets/saint-capybara/templates/bofm-pronunciations.yaml from its `respelling:`
(the Church guide's own notation) and write it back into that file, plus
into the same-named entries of the general seed pronunciations.yaml.

    python tools/capy_bofm_spoken.py [--check]

Chatterbox only sees graphemes (no phoneme override), so `spoken` is a plain
English spelling that a grapheme model reads the way the Church guide says
(ī -> "eye", ō -> "oh", ē -> "ee" ...). Stress can't be expressed; the vowel
spellings carry the pronunciation. Only the first of an "X or Y" pair is used.
Names in COMMON_OK are left alone: the model already reads them correctly and
a respelling could only make them worse.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BOFM = ROOT / "assets" / "saint-capybara" / "templates" / "bofm-pronunciations.yaml"
SEED = ROOT / "assets" / "saint-capybara" / "templates" / "pronunciations.yaml"

# Familiar names the model already reads correctly; leave them unrespelled.
COMMON_OK = {
    "Aaron", "Abel", "Abraham", "Adam", "Babylon", "Benjamin", "Cain", "Egypt", "Egyptian",
    "Elijah", "Ephraim", "Eve", "Isaac", "Isaiah", "Ishmael", "Israel", "Israelite", "Jacob",
    "Jeremiah", "Jerusalem", "Jesse", "Jew", "John", "Jordan", "Joseph", "Joshua", "Judah",
    "Judea", "Lebanon", "Levi", "Malachi", "Manasseh", "Mary", "Moses", "Mormon", "Nazareth",
    "Noah", "Salem", "Samuel", "Sarah", "Saul", "Seth", "Sinai", "Syria", "Timothy", "Zion",
    "Jehovah", "Gideon", "Bountiful", "Zechariah", "Zedekiah", "Uriah", "Uzziah", "Pharaoh",
    "Philistine", "Amos", "Ammon", "Enos", "Ether", "Alpha", "Omega", "Cherubim", "Seraphim",
    "Gomorrah", "Immanuel", "Alma", "Laban", "Lehi", "Sam", "Shem", "Gad",
}

# Hand-tuned where the mechanical rule reads wrong on Chatterbox (checked by
# transcribing a render: "mohrohnye" came out as "Mahronye"; the user then specified "more-oh-nigh").
OVERRIDES = {"Moroni": "moreohnigh", "Moronihah": "moreohnighhah", "Mosiah": "mozeyeyah"}

# Church key -> plain-English grapheme spelling.
VOWELS = {
    "ă": "a", "ā": "ay", "ä": "ah", "ĕ": "e", "ē": "ee", "ĭ": "i", "ī": "eye",
    "ō": "oh", "ū": "oo", "a": "uh", "u": "uh",
}
STRESS = "ʹˊʹʹ"  # the guide's stress mark (modifier prime) and lookalikes


def spoken_from_respelling(resp: str) -> str:
    first = re.split(r"\s+or\s+", resp.strip())[0]
    out = []
    i = 0
    while i < len(first):
        ch = first[i]
        two = first[i:i + 2]
        if ch in STRESS or ch == "-":
            i += 1
            continue
        if ch == "–":  # separator between the parts of a hyphenated name
            out.append("-")
            i += 1
            continue
        if two == "ou":
            out.append("ow")
            i += 2
            continue
        if two == "er":
            out.append("er")
            i += 2
            continue
        if ch == "ī":
            prev = first[:i].rstrip("-" + STRESS)
            nxt = first[i + 1:].lstrip("-" + STRESS)
            if not prev or prev[-1] in "aeiouăāäĕēĭīōūy":
                out.append("eye")          # standalone / after a vowel
            elif nxt and nxt[0] in "aeiouăāäĕēĭīōū":
                out.append("y")            # "sī-a" -> "sya"
            else:
                out.append("ye")           # "fī", "nī", "dī" -> "fye"
            i += 1
            continue
        out.append(VOWELS.get(ch, ch))
        i += 1
    return "".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    args = ap.parse_args()

    data = yaml.safe_load(BOFM.read_text(encoding="utf-8"))
    spoken: dict[str, str] = {}
    for e in data["entries"]:
        if e["word"] in COMMON_OK or not e.get("respelling"):
            continue
        s = OVERRIDES.get(e["word"]) or spoken_from_respelling(e["respelling"])
        if s.lower() != e["word"].lower().replace("-", ""):
            spoken[e["word"]] = s
    print(f"{len(data['entries'])} entries, {len(spoken)} get a spoken respelling")
    for w in ("Moroni", "Nephi", "Mosiah", "Moronihah", "Zarahemla", "Cumorah", "Anti-Nephi-Lehi"):
        print(f"  {w:16} -> {spoken.get(w, '(left as spelled)')}")
    if args.check:
        return 0

    def rewrite(path: Path, lookup: dict[str, str]) -> int:
        text = path.read_text(encoding="utf-8")
        nl = "\r\n" if "\r\n" in text else "\n"
        lines = text.split(nl)
        out, n, i = [], 0, 0
        while i < len(lines):
            out.append(lines[i])
            m = re.match(r"\s*- word: (\S+)\s*$", lines[i])
            if m and m.group(1) in lookup:
                # drop any existing spoken: line in this entry, then add ours
                j = i + 1
                block = []
                while j < len(lines) and not re.match(r"\s*- word:", lines[j]) and lines[j].strip():
                    block.append(lines[j])
                    j += 1
                block = [b for b in block if not b.strip().startswith("spoken:")]
                indent = re.match(r"\s*", block[0]).group(0) if block else "    "
                for k, b in enumerate(block):
                    out.append(b)
                    if b.strip().startswith(("ipa:", "respelling:")) and not any(
                        x.strip().startswith(("ipa:", "respelling:")) for x in block[k + 1:]
                    ):
                        out.append(f'{indent}spoken: "{lookup[m.group(1)]}"')
                        n += 1
                i = j
                continue
            i += 1
        path.write_text(nl.join(out), encoding="utf-8", newline="")
        return n

    print("bofm file:", rewrite(BOFM, spoken), "entries updated")
    print("seed file:", rewrite(SEED, spoken), "entries updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
