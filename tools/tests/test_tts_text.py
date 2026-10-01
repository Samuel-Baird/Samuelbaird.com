"""Chatterbox synthesis-text helpers in tools/capy_tts.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from capy_tts import apply_spoken_respellings, spoken_scripture_refs


def test_scripture_refs_spoken_as_words():
    assert spoken_scripture_refs("Second Corinthians 11:14 says") == "Second Corinthians eleven fourteen says"
    assert spoken_scripture_refs("Galatians 1:8.") == "Galatians one eight."
    assert spoken_scripture_refs("Romans 3:23-25") == "Romans three twenty-three through twenty-five"


def test_non_reference_numbers_untouched():
    assert spoken_scripture_refs("In 1838, at 10:30 sharp") == "In 1838, at ten thirty sharp"  # times read the same way
    assert spoken_scripture_refs("four hundred pages") == "four hundred pages"


def test_spoken_respelling_whole_word_only():
    e = [{"word": "Moroni", "spoken": "moreohnigh"}]
    assert apply_spoken_respellings("Moroni, not Moronic", e) == "moreohnigh, not Moronic"
