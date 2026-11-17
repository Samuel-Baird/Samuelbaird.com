"""Editions, built from the registry (languages.yaml). A Script says which published text to start from,
how to convert it, and how to typeset it (font family, hyphenation, direction, line breaking, credit line, hints).

- kind "language": the Church's own published text for that language (nothing is translated here).
- kind "script": the English text converted into another alphabet (Deseret).

Adding a language is a registry entry plus fetching its text; the layout code does not change."""
import json
import subprocess
from pathlib import Path

from . import languages
from .fonts import to_caps

ROOT = Path(__file__).resolve().parents[1]
SEP = "\n§\n"     # a section sign on its own line survives transliteration untouched
DEFAULT_CREDIT = languages.load()["english"]["credit"]


class Script:
    def __init__(self, entry):
        self.entry = entry
        self.name = entry["slug"]                      # also the folder name
        self.label = entry["english"]
        self.native = entry["native"]
        self.source = entry.get("source", entry["code"])    # which texts/<code>/ file to start from
        self.latin_family = entry.get("font", "serif")
        self.hyphenation = entry.get("hyphenation")
        self.justify = entry.get("justify", self.hyphenation is not None)   # ragged-right without a dictionary
        self.cased = entry.get("caps", "upper") != "none"
        self.rtl = entry.get("rtl", False)                  # right-to-left: the whole design is mirrored
        self.breaker = entry.get("breaks")                  # linebreak.py function for scripts without spaces
        self.spaced = entry.get("spaced", True)             # words are separated by spaces (lead-ins make sense)
        self.lead = entry.get("lead", 1.0)                  # line spacing multiplier for tall scripts
        self.tracked = entry.get("tracked", True)           # letter-spacing is fine (not for joined scripts)
        self.char_justify = entry.get("char_justify", False)
        self.dc_scale = entry.get("dc_scale", 1.0)          # drop-cap size factor
        self.credit = entry.get("credit", DEFAULT_CREDIT)
        self.hints = entry.get("hints") or {}

    def convert(self, strings):
        return list(strings)

    def caps(self, text):
        return text.upper() if self.cased else text

    def report(self):
        return {}


class Deseret(Script):
    def __init__(self, entry):
        super().__init__(entry)
        self.left_in_latin = set()

    def convert(self, strings):
        text = SEP.join(strings)
        node = ROOT / "deseret" / "bin" / "deseret.mjs"
        r = subprocess.run(["node", str(node)], input=text, capture_output=True, text=True, encoding="utf-8", check=True)
        out = r.stdout.split(SEP)
        if len(out) != len(strings):
            raise RuntimeError("Deseret conversion changed the number of strings")
        cov = subprocess.run(["node", str(node), "--coverage"], input=text, capture_output=True, text=True,
                             encoding="utf-8", check=True)
        self.left_in_latin |= set(json.loads(cov.stdout)["left_latin"])
        return out

    def caps(self, text):
        return to_caps(text)

    def report(self):
        return {"left_in_latin": sorted(self.left_in_latin)}


CLASSES = {"deseret": Deseret}
EDITIONS = languages.slugs()
ALIASES = {"latin": "english"}      # the format check renders the English edition


def get(name):
    name = ALIASES.get(name, name)
    entry = languages.get(name)
    return CLASSES.get(name, Script)(entry)
