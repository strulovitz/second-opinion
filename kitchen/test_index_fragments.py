"""Fragment continuation, failure recovery and strict-shape regressions; no model."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from index_fragments import fragments, parse_fragments
from index_schema import check_shape


def entry(headword, pages=None, subs=None):
    return {"headword": headword, "display": headword, "see": None,
            "pages": pages or [], "subentries": subs or []}


class FragmentTests(unittest.TestCase):
    def test_stray_top_level_entry_is_not_silently_discarded(self):
        with self.assertRaisesRegex(ValueError, 'stray top-level'):
            check_shape({"entries": [entry('Alpha')], **entry('Beta', ['2'])})

    def test_plan_is_lossless_and_keeps_wrapped_refs_and_labels_together(self):
        text = 'Alpha, 1,\n 2, 3\n detail with wrapped\n words, 4\nBeta, 5\n'
        parts = fragments(text, target=2)
        self.assertEqual([p['text'] for p in parts],
                         ['Alpha, 1,\n 2, 3\n detail with wrapped\n words, 4\n', 'Beta, 5\n'])
        self.assertEqual(''.join(p['text'] for p in parts), text)

    def test_see_target_and_wrapped_numeric_range_stay_together(self):
        text = 'Alpha, 1. See also Other with\n  multiple words\nBeta, 3479–\n 3480, 9\nGamma, 10\n'
        parts = fragments(text, target=1)
        self.assertEqual([p['text'] for p in parts], [
            'Alpha, 1. See also Other with\n  multiple words\n',
            'Beta, 3479–\n 3480, 9\n', 'Gamma, 10\n'])

    def test_continued_entry_ends_before_the_next_main_entry(self):
        text = 'Alpha, 1\n' + ''.join(f' detail {i}, {i}\n' for i in range(2, 7)) + 'Beta, 7\n'
        parts = fragments(text, target=4)
        self.assertEqual([(p['start_line'], p['end_line']) for p in parts], [(0, 4), (4, 6), (6, 7)])

    def test_misread_continuation_is_reported_before_reference_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            ctx = Mock()
            ctx.path.side_effect = lambda suffix: Path(directory) / suffix
            text = 'Alpha, 1\nComplete response, to chemotherapy, 555\n'
            ask = Mock(side_effect=[{"entries": [entry('Alpha', ['1'])]},
                                    {"entries": [entry('CONTINUED', ['555'])]},
                                    {"entries": [entry('CONTINUED', ['555'])]}])
            with self.assertRaisesRegex(ValueError, "it starts 'Complete response, to chemotherapy'"):
                parse_fragments(ctx, ask, text, 3, '3.png', 'parent-key')

    def test_planner_cuts_before_an_entry_named_like_a_reference(self):
        text = ('C1 inhibitor deficiency, 2790t, 2807\n 2808\n'
                'C1q, 2786f, 2790t, 3395\nC1R/S, 2786f, 3329t\n')
        parts = fragments(text, target=4)
        self.assertEqual([p['text'] for p in parts], [
            'C1 inhibitor deficiency, 2790t, 2807\n 2808\n',
            'C1q, 2786f, 2790t, 3395\n', 'C1R/S, 2786f, 3329t\n'])

    def test_partial_fragments_resume_without_reasking_and_merge_full_page_quotes(self):
        with tempfile.TemporaryDirectory() as directory:
            ctx = Mock()
            ctx.path.side_effect = lambda suffix: Path(directory) / suffix
            # A long entry must cross the 24-line boundary; the second fragment
            # contains its continuation and then a separate main entry.
            text = 'Alpha, 1\n' + ''.join(f' detail {i}, {i}\n' for i in range(2, 29)) + 'Beta, 29\n'
            parts = fragments(text)
            self.assertEqual(len(parts), 3)
            cut = parts[0]['end_line']
            first = entry('Alpha', ['1'], [{'text': f'detail {i}', 'pages': [str(i)]}
                                          for i in range(2, cut + 1)])
            second = entry('CONTINUED', [], [{'text': f'detail {i}', 'pages': [str(i)]}
                                             for i in range(cut + 1, 29)])
            ask = Mock(side_effect=[{'entries': [first]}, {'entries': []}, {'entries': []}])
            with self.assertRaisesRegex(ValueError, 'failed validation twice'):
                parse_fragments(ctx, ask, text, 3, '3.png', 'parent-key')
            ask = Mock(side_effect=[{'entries': [second]}, {'entries': [entry('Beta', ['29'])]}])
            result = parse_fragments(ctx, ask, text, 3, '3.png', 'parent-key')
            self.assertEqual(ask.call_count, 2)
            self.assertEqual([r['headword'] for r in result], ['Alpha', 'Beta'])
            self.assertEqual(len(result[0]['subentries']), 27)
            self.assertEqual(result[0]['quote'], text.split('Beta')[0].strip())
            self.assertEqual(result[1]['quote'], 'Beta, 29')
            ask.reset_mock()
            parse_fragments(ctx, ask, text, 3, '3.png', 'parent-key')
            ask.assert_not_called()
            with self.assertRaisesRegex(ValueError, 'stale fragment plan'):
                parse_fragments(ctx, ask, text, 3, '3.png', 'changed-parent')
