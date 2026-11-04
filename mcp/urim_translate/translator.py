"""Glossary access and validation shared by the pipeline and the glossary tools. The translation itself is written by the
calling agent (see workflow.py); nothing here calls a model."""
from dataclasses import dataclass, field

from . import segment
from .glossary import Glossary
from .store import Store


@dataclass
class Seg:
    text: str
    masked: str = ""
    ph: dict = field(default_factory=dict)
    matches: list = field(default_factory=list)


def length_ok(src: str, tgt: str) -> bool:
    if len(src) < 40:
        return True
    return 0.45 <= len(tgt) / max(1, len(src)) <= 2.6


class Translator:
    def __init__(self, store: Store = None):
        self.store = store or Store()
        self._gloss = {}

    def glossary(self, lang):
        g = self._gloss.get(lang)
        if g is None:
            g = self._gloss[lang] = Glossary(lang, self.store)
        return g

    def reload_glossary(self, lang):
        self._gloss.pop(lang, None)

    def problems(self, seg: Seg, target: str, g: Glossary):
        probs = []
        if not target.strip():
            return ["empty output"]
        if not segment.placeholders_ok(target, seg.ph):
            probs.append("a placeholder was lost, duplicated or altered; keep each one exactly once")
        if segment.numbers(seg.masked) != segment.numbers(target):
            probs.append("numbers differ from the source")
        if not length_ok(seg.masked, target):
            probs.append("length is implausible compared with the source (omission or addition)")
        for e in g.missing(seg.matches, target):
            probs.append(f'"{e.en[0]}" must be rendered as "{e.preferred}"'
                         + (f' (or: {", ".join(v["term"] for v in e.variants)})' if e.variants else ""))
        return probs
