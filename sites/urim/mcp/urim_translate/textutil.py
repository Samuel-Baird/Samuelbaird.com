"""Text helpers shared by glossary matching and validation (mirrors pipeline/textutil.py)."""
import re
import unicodedata

_TOK = re.compile(r"\w+")


def fold(s: str) -> str:
    """Lowercase + strip accents, keeping string length so char positions stay valid."""
    out = []
    for c in s:
        n = "".join(x for x in unicodedata.normalize("NFKD", c) if not unicodedata.combining(x)).lower()
        out.append(n if len(n) == 1 else c.lower())
    return "".join(out)


def tokens(s: str):
    return [(m.group(), m.start()) for m in _TOK.finditer(s)]


def en_variants(w: str):
    v = {w, w + "s", w + "es"}
    if w.endswith("y"):
        v.add(w[:-1] + "ies")
    return v


def _word_pat(w: str) -> str:
    e = re.escape
    if w.endswith("ao"):
        return e(w[:-2]) + "(?:ao|oes|aos)"
    if len(w) > 3 and w.endswith(("o", "a")):
        return e(w[:-1]) + "[oa]s?"
    if w.endswith("z"):
        return e(w[:-1]) + "(?:z|ces)"
    if w.endswith(("e", "i", "u")) or len(w) <= 3:
        return e(w) + "s?"
    return e(w) + "(?:es|s)?"


def target_pattern(term: str) -> re.Pattern:
    """Inflection- and accent-tolerant pattern for a pt/es term, to run on fold()ed text."""
    words = [t for t, _ in tokens(fold(term))]
    gap = "[\\s\\-’']+"
    return re.compile(r"(?<!\w)" + gap.join(_word_pat(w) for w in words) + r"(?!\w)")


def norm_key(s: str) -> str:
    """Stable key for translation-memory lookup: NFC, collapsed whitespace."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s)).strip()
