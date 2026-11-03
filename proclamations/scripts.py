"""Editions, built from the registry (languages.yaml). A Script says which published text to start from,
how to convert it, and how to typeset it (Latin font family, hyphenation dictionary, credit line, hints).

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
        self.credit = entry.get("credit", DEFAULT_CREDIT)
        self.hints = entry.get("hints") or {}

    def convert(self, strings):
        return list(strings)

    def caps(self, text):
        return text.upper()

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
