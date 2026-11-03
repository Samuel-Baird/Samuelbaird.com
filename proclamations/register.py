"""Build languages.generated.yaml: registry entries for every language the engine can typeset today.

    python -m proclamations.register

A language qualifies when the survey found at least one proclamation for it (language-survey.json) and the
font chain has a glyph for every character of its texts (after compatibility normalization). Scripts that need shaping,
right-to-left layout or special line breaking get their settings from RULES below (docs/scripts.md).
Hand-written entries in languages.yaml take precedence over generated ones.
"""
import glob
import json
import unicodedata
from pathlib import Path

import yaml

from . import fonts

HERE = Path(__file__).resolve().parent
OUT = HERE / "languages.generated.yaml"

# Church ?lang= code -> pyphen dictionary. Languages not listed are typeset ragged-right.
HYPHENATION = {
    "afr": "af", "alb": "sq", "bul": "bg", "cat": "ca", "ces": "cs", "dan": "da", "deu": "de", "ell": "el",
    "eng": "en_US", "est": "et", "fra": "fr", "hrv": "hr", "hun": "hu", "ind": "id", "isl": "is", "ita": "it",
    "lav": "lv", "lit": "lt", "mon": "mn", "nld": "nl", "nor": "nb", "pol": "pl", "por": "pt_BR", "ept": "pt_PT",
    "ron": "ro", "rus": "ru", "slk": "sk", "slv": "sl", "spa": "es", "srp": "sr", "swe": "sv", "ukr": "uk", "zul": "zu",
}
CASELESS = {"kat"}          # Georgian (Mkhedruli) has no capitals; upper-casing would pick Mtavruli forms the font may lack
SLUG_OVERRIDES = {"ept": "portugueseuropeu"}

# Scripts that need more than plain left-to-right text. Joined and combining scripts are never letter-spaced
# (tracked: false); scripts written without spaces break lines by linebreak.py and spread the slack between
# characters; tall scripts get extra line spacing (lead). See docs/scripts.md.
_JOINED = {"caps": "none", "tracked": False, "justify": True}
_UNSPACED = {**_JOINED, "spaced": False, "char_justify": True}
RULES = {
    "ara": {**_JOINED, "font": "serif-arabic", "rtl": True, "dc_scale": 0.7, "dc_scale": 0.7, "dc_scale": 0.7, "dc_scale": 0.7, "lead": 1.25},
    "urd": {**_JOINED, "font": "serif-arabic", "rtl": True, "dc_scale": 0.7, "dc_scale": 0.7, "dc_scale": 0.7, "dc_scale": 0.7, "lead": 1.3},
    "pes": {**_JOINED, "font": "serif-arabic", "rtl": True, "dc_scale": 0.7, "dc_scale": 0.7, "dc_scale": 0.7, "dc_scale": 0.7, "lead": 1.25},
    "ckb": {**_JOINED, "font": "serif-arabic", "rtl": True, "dc_scale": 0.7, "dc_scale": 0.7, "dc_scale": 0.7, "dc_scale": 0.7, "lead": 1.25},
    "hin": {**_JOINED, "font": "serif-devanagari", "lead": 1.3},
    "mar": {**_JOINED, "font": "serif-devanagari", "lead": 1.3},
    "nep": {**_JOINED, "font": "serif-devanagari", "lead": 1.3},
    "ben": {**_JOINED, "font": "serif-bengali", "lead": 1.25},
    "guj": {**_JOINED, "font": "serif-gujarati", "lead": 1.25},
    "tam": {**_JOINED, "font": "serif-tamil", "lead": 1.3},
    "tel": {**_JOINED, "font": "serif-telugu", "lead": 1.35},
    "kan": {**_JOINED, "font": "serif-kannada", "lead": 1.35},
    "mal": {**_JOINED, "font": "serif-malayalam", "lead": 1.35},
    "sin": {**_JOINED, "font": "serif-sinhala", "lead": 1.3},
    "tha": {**_UNSPACED, "font": "serif-thai", "breaks": "thai", "lead": 1.3},
    "lao": {**_UNSPACED, "font": "serif-lao", "breaks": "lao", "lead": 1.3},
    "khm": {**_UNSPACED, "font": "serif-khmer", "breaks": "khmer", "lead": 1.4},
    "mya": {**_UNSPACED, "font": "serif-myanmar", "breaks": "myanmar", "lead": 1.5, "dc_scale": 0.32},
    "ksw": {**_UNSPACED, "font": "serif-myanmar", "breaks": "myanmar", "lead": 1.5, "dc_scale": 0.32},
    "zhs": {**_UNSPACED, "font": "serif-sc", "breaks": "cjk", "lead": 1.3, "tracked": True},
    "zho": {**_UNSPACED, "font": "serif-tc", "breaks": "cjk", "lead": 1.3, "tracked": True},
    "yue": {**_UNSPACED, "font": "serif-tc", "breaks": "cjk", "lead": 1.3, "tracked": True},
    "jpn": {**_UNSPACED, "font": "serif-jp", "breaks": "cjk", "lead": 1.3, "tracked": True},
    "kor": {**_JOINED, "font": "serif-kr", "lead": 1.25, "tracked": True},
}


def ascii_slug(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text) if c.isascii() and c.isalnum()).lower()


def make_slug(native, english, taken):
    letters = [c for c in native if c.isalpha()]
    folded = [c for c in unicodedata.normalize("NFKD", native) if c.isascii() and c.isalpha()]
    slug = ascii_slug(native) if letters and len(folded) >= len(letters) else ""
    for candidate in (slug, ascii_slug(english)):
        if candidate and candidate not in taken:
            return candidate
    raise ValueError(f"no free slug for {native!r}/{english!r}")


def texts_of(code):
    parts = []
    for f in glob.glob(str(HERE / "texts" / code / "*.yaml")):
        d = yaml.safe_load(open(f, encoding="utf-8"))
        for v in d.values():
            if isinstance(v, str):
                parts.append(v)
            elif isinstance(v, list):
                parts += [x if isinstance(x, str) else " ".join(str(y) for y in x.values()) for x in v]
    return unicodedata.normalize("NFC", " ".join(parts))


def main():
    from . import languages
    survey = json.loads((HERE / "language-survey.json").read_text(encoding="utf-8"))
    names = yaml.safe_load((HERE.parent.parent / "pulpit-vault" / "schema" / "language-names.yaml").read_text(encoding="utf-8")) \
        if (HERE.parent.parent / "pulpit-vault" / "schema" / "language-names.yaml").exists() else {}
    hand = yaml.safe_load(languages.REGISTRY.read_text(encoding="utf-8"))
    taken = set(hand)
    handled = {e["code"] for e in hand.values()}
    out, skipped = {}, []
    for e in sorted(survey, key=lambda e: e["name"].lower()):
        code = e["code"]
        if not e["documents"] or code in handled:
            continue
        rules = RULES.get(code, {})
        family = rules.get("font", "serif")
        txt = texts_of(code)
        txt = fonts.sanitize(txt, family)
        missing = fonts.missing_chars(txt, family)
        if missing:
            skipped.append((code, e["script"], "".join(missing)[:12]))
            continue
        english = names.get(code, e["name"])
        slug = SLUG_OVERRIDES.get(code) or make_slug(e["name"], english, taken)
        taken.add(slug)
        entry = {"kind": "language", "code": code, "native": e["name"], "english": english,
                 "hyphenation": HYPHENATION.get(code), "font": "serif"}
        entry.update(rules)
        if code in CASELESS:
            entry["caps"] = "none"
        out[slug] = entry
    header = ("# GENERATED by `python -m proclamations.register`; do not edit. Hand-written entries in languages.yaml win.\n"
              "# One entry per language the survey found and the font chain can typeset.\n")
    OUT.write_text(header + yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8", newline="\n")
    print(f"{len(out)} generated entries; {len(skipped)} languages need a script handler first:")
    for code, script, miss in skipped:
        print(f"  {code:9} {script:11} e.g. {miss}")


if __name__ == "__main__":
    main()
