"""Synthetic column geometry; no book, model or database access."""

import unittest

from index_order import column_text


def xml(blocks):
    return '<html xmlns="http://www.w3.org/1999/xhtml"><page width="600" height="800">' + ''.join(
        f'<flow><block xMin="{left}" xMax="{right}" yMin="{y}" yMax="{y+10}">'
        f'<line xMin="{left}" yMin="{y}">' + ''.join(f'<word>{word}</word>' for word in text.split())
        + '</line></block></flow>' for left, right, y, text in blocks) + '</page></html>'


class ColumnOrderTests(unittest.TestCase):
    def test_three_scrambled_columns_are_read_left_to_right(self):
        raw = 'Middle, 2\nRight, 3\nI-3\nINDEX\nLeft, 1\n'
        page = xml([(210, 360, 20, 'Middle, 2'), (400, 550, 20, 'Right, 3'),
                    (570, 590, 20, 'I-3'), (570, 590, 60, 'INDEX'), (20, 170, 20, 'Left, 1')])
        text, columns = column_text(page, raw)
        self.assertEqual(text, 'Left, 1\n\nMiddle, 2\n\nRight, 3\n')
        self.assertEqual(len(columns), 3)

    def test_indented_blocks_stay_with_column_and_keep_y_order(self):
        page = xml([(30, 160, 40, 'detail, 2'), (20, 170, 20, 'Alpha'),
                    (20, 170, 60, 'Beta, 3'), (210, 360, 20, 'Gamma, 4')])
        text, columns = column_text(page, 'Alpha\ndetail, 2\nBeta, 3\nGamma, 4')
        self.assertEqual(text, 'Alpha\n   detail, 2\nBeta, 3\n\nGamma, 4\n')
        self.assertEqual(len(columns), 2)

    def test_different_text_inventory_and_ambiguous_spanning_block_fail_closed(self):
        with self.assertRaisesRegex(ValueError, 'text inventory differs'):
            column_text(xml([(20, 170, 20, 'Alpha, 1')]), 'Alpha, 2')
        with self.assertRaisesRegex(ValueError, 'ambiguous spanning'):
            column_text(xml([(20, 170, 20, 'Alpha, 1'), (20, 570, 25, 'Heading'),
                             (210, 360, 60, 'Beta, 2')]), 'Alpha, 1\nHeading\nBeta, 2')

    def test_discretionary_line_hyphen_is_preserved_in_ordered_evidence(self):
        text, _ = column_text(xml([(20, 170, 20, 'Non-ST-'), (20, 170, 40, 'segment, 1')]),
                              'Non-STsegment, 1')
        self.assertEqual(text, 'Non-ST-\nsegment, 1\n')

    def test_bbox_subscript_spacing_is_not_a_content_change(self):
        text, _ = column_text(xml([(20, 170, 20, 'Aflatoxin B 1 , 660'),
                                   (20, 170, 40, 'Airway resistance (R aw ), 270')]),
                              'Aflatoxin B1, 660\nAirway resistance (Raw), 270')
        self.assertEqual(text, 'Aflatoxin B 1 , 660\nAirway resistance (R aw ), 270\n')
