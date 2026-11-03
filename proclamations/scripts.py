"""Output scripts / languages. Each takes the English source strings and returns the same strings
in the target script. Only Deseret exists so far; a translation backend (for example the Urim
translation MCP) can be added as another Script without touching the layout code."""
import json
import subprocess
from pathlib import Path

from .fonts import to_caps

ROOT = Path(__file__).resolve().parents[1]
SEP = "\n§\n"     # a section sign on its own line survives transliteration untouched


class Script:
    name = "base"
    label = ""

    def convert(self, strings):
        raise NotImplementedError

    def caps(self, text):
        return text.upper()

    def report(self):
        return {}


class Latin(Script):
    """Identity. Used only for the format check against the English originals."""
    name = "latin"
    label = "English"

    def convert(self, strings):
        return list(strings)


class Deseret(Script):
    name = "deseret"
    label = "Deseret Alphabet"

    def __init__(self):
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


SCRIPTS = {"latin": Latin, "deseret": Deseret}


def get(name):
    try:
        return SCRIPTS[name]()
    except KeyError:
        raise KeyError(f"unknown script '{name}'; choose from {', '.join(SCRIPTS)}")
