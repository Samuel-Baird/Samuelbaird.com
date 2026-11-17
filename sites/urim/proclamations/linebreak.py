"""Break opportunities inside a token, for scripts written without spaces between words.

Each function takes one token (text between spaces) and returns the indices at which a line may break.
layout.set_breaker(name) selects the function for the edition being typeset. The Church's Khmer and Lao
texts already carry U+200B (zero width space) between words, which is used where present.
"""
import regex

ZWSP = "​"
NO_START = set("、。，．・：；！？）］｝〕〉》」』】〙〗〟’”ゝゞー々ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮヵヶ…‥—"
                ",.:;!?)]}%、。")
NO_END = set("（［｛〔〈《「『【〘〖〝‘“([{")


def _zwsp(text):
    return [i + 1 for i, ch in enumerate(text[:-1]) if ch == ZWSP]


def cjk(text):
    """Chinese and Japanese: a line may break between any two characters except where kinsoku forbids it
    (no closing punctuation or small kana at the start of a line, no opening bracket at its end, and not
    inside a run of Latin letters or digits, or between the two halves of a dash or ellipsis)."""
    out = []
    for i in range(1, len(text)):
        a, b = text[i - 1], text[i]
        if b in NO_START or a in NO_END:
            continue
        if a.isascii() and b.isascii() and a.isalnum() and b.isalnum():
            continue
        if a == b and a in "—…‥":
            continue
        out.append(i)
    return out


_thai = None


def thai(text):
    global _thai
    if _thai is None:
        import budoux
        _thai = budoux.load_default_thai_parser()
    out, pos = [], 0
    for chunk in _thai.parse(text)[:-1]:
        pos += len(chunk)
        out.append(pos)
    return out


def _between(text, pattern):
    return [m.start() for m in pattern.finditer(text) if 0 < m.start()]


_KHMER_SYLLABLE = regex.compile(r"(?<![្​‌‍])[ក-អ](?!្)")
_LAO_SYLLABLE = regex.compile(r"(?<=[ະ-ຽ່-ໍຯ])(?=[ກ-ຮເ-ໄ])")
_MYANMAR = regex.compile(r"(?<![္])[က-အ](?![်္])")


def khmer(text):
    z = _zwsp(text)
    return z if z else _between(text, _KHMER_SYLLABLE)


def lao(text):
    z = _zwsp(text)
    return z if z else _between(text, _LAO_SYLLABLE)


def myanmar(text):
    z = _zwsp(text)
    return z if z else _between(text, _MYANMAR)


BREAKERS = {"cjk": cjk, "thai": thai, "khmer": khmer, "lao": lao, "myanmar": myanmar}


def get(name):
    if name is None:
        return None
    if name not in BREAKERS:
        raise KeyError(f"unknown line breaker '{name}'; choose from {', '.join(BREAKERS)}")
    return BREAKERS[name]
