from pipeline.attest import EnglishIndex
from pipeline.textutil import fold, target_pattern, window


def idx():
    return EnglishIndex({
        "priesthood": {"en": {"match": ["priesthood"]}},
        "priesthood-keys": {"en": {"match": ["priesthood keys"]}},
        "ministering": {"en": {"match": ["ministering"]}},
    })


def test_longest_match_consumes_shorter():
    hits = idx().scan("He holds the priesthood keys. The priesthood is great.")
    assert set(hits) == {"priesthood-keys", "priesthood"}
    s, e = hits["priesthood"]
    assert "He holds the priesthood keys. The priesthood is great."[s:e] == "priesthood"


def test_plural_and_case():
    assert "priesthood" in idx().scan("Priesthoods differ.")


def test_target_pattern_inflection_and_accents():
    p = target_pattern("sacerdócio")
    assert p.search(fold("O Sacerdócio é")) and p.search(fold("dos sacerdocios"))
    assert not p.search(fold("sacerdotes"))
    q = target_pattern("exaltação")
    assert q.search(fold("exaltações"))
    r = target_pattern("llaves del sacerdocio")
    assert r.search(fold("las Llaves del Sacerdocio"))


def test_window_slices_original_without_stray_spacing():
    t = "He is a God, one of the three in the Godhead. He is the Savior and Redeemer of the human race. More."
    s = t.index("Godhead")
    w = window(t, s, s + 7, 12)
    assert "Godhead." in w and " ." not in w
