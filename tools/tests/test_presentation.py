"""Unit tests for the presentation pipeline's pure helpers (no media needed).

    python -m pytest tools/tests/test_presentation.py
"""
from __future__ import annotations

import sys
from pathlib import Path

PRES = Path(__file__).resolve().parents[1] / 'presentation'
if str(PRES) not in sys.path:
    sys.path.insert(0, str(PRES))

from shorts import apply_fixes, ass_t  # noqa: E402


def _w(*words):
    return [[i * 0.5, i * 0.5 + 0.4, w] for i, w in enumerate(words)]


def test_word_fix_keeps_punctuation_once():
    out = apply_fixes(_w('Aryans.', 'M.', 'minor'), {'words': {'aryans': 'Arians', 'm': 'M.', 'minor': 'miner'}})
    assert [w for *_, w in out] == ['Arians.', 'M.', 'miner']


def test_phrase_fix_replaces_misheard_name_and_keeps_trailing_comma():
    fixes = {'phrases': [[["you're", 'asked', 'to', 'snow'], ['Erastus', 'Snow']], [['st', 'george'], ['St.', 'George']]]}
    out = apply_fixes(_w('and', "you're", 'asked', 'to', 'snow', 'in', 'st.', 'George,', 'Utah'), fixes)
    assert [w for *_, w in out] == ['and', 'Erastus', 'Snow', 'in', 'St.', 'George,', 'Utah']


def test_insert_dropped_word():
    out = apply_fixes(_w('themselves', 'May', '25th'), {'insert': [['themselves', 'May', 'On']]})
    assert [w for *_, w in out] == ['themselves', 'On', 'May', '25th']


def test_ass_time():
    assert ass_t(83.456) == '0:01:23.46'
