"""Shared text helpers: 1:1 accent folding, tokenizing, inflection-tolerant patterns."""
import re
import unicodedata

_TOK = re.compile(r"\w+")


def fold(s: str) -> str:
    """Lowercase + strip accents, keeping string length (char positions stay valid)."""
    out = []
    for c in s:
        n = "".join(x for x in unicodedata.normalize("NFKD", c) if not unicodedata.combining(x)).lower()
        out.append(n if len(n) == 1 else c.lower())
    return "".join(out)


def tokens(s: str):
    """[(token, start)] over folded text."""
    return [(m.group(), m.start()) for m in _TOK.finditer(s)]


def en_variants(w: str):
    v = {w, w + "s", w + "es"}
    if w.endswith("y"):
        v.add(w[:-1] + "ies")
    return v


def _word_pat(w: str) -> str:
    """Folded pt/es word -> regex allowing gender/number inflection."""
    e = re.escape
    if len(w) > 3 and w.endswith(("o", "a")):
        return e(w[:-1]) + "[oa]s?"
    if w.endswith("ao"):
        return e(w[:-2]) + "(?:ao|oes|aos)"
    if w.endswith("z"):
        return e(w[:-1]) + "(?:z|ces)"
    if w.endswith(("e", "i", "u")) or len(w) <= 3:
        return e(w) + "s?"
    return e(w) + "(?:es|s)?"


def target_pattern(term: str) -> re.Pattern:
    words = [t for t, _ in tokens(fold(term))]
    gap = "[\\s\\-’']+"
    return re.compile(r"(?<!\w)" + gap.join(_word_pat(w) for w in words) + r"(?!\w)")


def window(text: str, start: int, end: int, words: int = 20) -> str:
    """~`words` words of original text around [start,end), ellipsized; slices the original text."""
    left = [m.start() for m in re.finditer(r"\S+", text[:start])]
    right = [m.end() for m in re.finditer(r"\S+", text[end:])]
    used = max(1, len(text[start:end].split()))
    nb = max(0, (words - used) // 2)
    na = max(0, words - used - nb)
    a = left[-nb] if nb and len(left) >= nb else (left[0] if nb and left else start)
    b = end + right[na - 1] if na and len(right) >= na else (end + right[-1] if right and na else end)
    return ("… " if a > (left[0] if left else start) else "") + text[a:b] + (" …" if b < len(text.rstrip()) else "")
