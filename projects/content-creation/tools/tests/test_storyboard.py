"""Regression checks for clip transcript boundaries in the review script."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from capy_storyboard import _transcript_span_text


class ClipTranscriptTests(unittest.TestCase):
    def test_partial_segment_does_not_quote_unplayed_introduction(self):
        segments = [{'start': 6.64, 'end': 11.78,
                     'text': 'it can often be emotionally abusive. Hi, I am Ashley.',
                     'words': [
                         {'word': ' it', 'start': 6.64, 'end': 6.78},
                         {'word': ' can', 'start': 6.78, 'end': 6.92},
                         {'word': ' often', 'start': 6.92, 'end': 7.36},
                         {'word': ' be', 'start': 7.36, 'end': 7.62},
                         {'word': ' emotionally', 'start': 7.62, 'end': 8.20},
                         {'word': ' abusive.', 'start': 8.20, 'end': 8.74},
                         {'word': ' Hi,', 'start': 9.14, 'end': 9.36}]}]
        self.assertEqual(_transcript_span_text(segments, 6.64, 8.95),
                         'it can often be emotionally abusive.')

    def test_zero_duration_word_and_segment_only_fallback(self):
        segments = [{'start': 35.36, 'end': 40.98, 'text': 'concretely. So when',
                     'words': [{'word': ' concretely.', 'start': 35.36, 'end': 36.12},
                               {'word': ' So', 'start': 36.32, 'end': 36.32},
                               {'word': ' when', 'start': 36.32, 'end': 36.52}]}]
        self.assertEqual(_transcript_span_text(segments, 36.2, 36.7), 'So when')
        self.assertEqual(_transcript_span_text([{'start': 1, 'end': 2, 'text': ' fallback '}], 1, 2), 'fallback')


if __name__ == '__main__':
    unittest.main()
