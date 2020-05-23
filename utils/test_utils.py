import pytest
import pandas as pd

import utils

def check_mora_pitch_pairs(test_words):
    for word, accent, expected in test_words:
        result = [x.get_pair() for x in utils.mora.mora_split(word, accent)]

        assert result == expected

class TestKanaPhonemeExtraction():
    katakana = 'ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンァィゥェォャュョッ'
    unigraphs = 'ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンッ'

    # Use linear combinations to generate all possible digraphs.
    # Not all combinations are strictly valid, but this should form a superset
    # of digraphs we're interested in.
    digraphs = [
        "".join((x, y)) 
        for x in 'ギジヂビピキシチニヒミリ'  # diagraph_beginings
        for y in 'ァィゥェォャュョ']  # digraph_endings


    def test_pass_if_mora_split_works_on_unigraphs(self):
        # word, accent, expected
        test_words = [
            ("アイゾー", "0111", [('ア', 0), ('イ', 1), ('ゾ', 1), ('ー', 1)]),
        ]

        check_mora_pitch_pairs(test_words)


    def test_pass_if_mora_split_works_on_digraphs(self):
        # word, accent, expected
        test_words = [
            ("キョ", "12", [('キョ', 2)]),
            ('シャ', "00", [('シャ', 0)]),
            ("アイコーシャ", "012000", [('ア',0), ('イ',1), ('コ',2), ('ー', 0), ('シャ',0)]),
            ("ゾーヒビョー", "011111", [('ゾ',0), ('ー',1), ('ヒ',1), ('ビョ',1), ('ー',1)]),
            # Synthetic example.
            ("ゾーヒビョー", "011112", [('ゾ',0), ('ー',1), ('ヒ',1), ('ビョ',1), ('ー',2)]),
        ]

        check_mora_pitch_pairs(test_words)


    def test_pass_if_mora_split_works_on_compound_words(self):
        # word, accent, expected
        test_words = [
            ("アイ・イレナイ", "2000111", [('ア', 2), ('イ', 0), ('・',0), ('イ', 0), ('レ', 1), ('ナ', 1), ('イ', 1)]),
            ("ソクサイ・エンメイ", "011100111", [('ソ',0),('ク',1),('サ',1),('イ',1),('・',0),('エ',0),('ン',1),('メ',1),('イ',1)])
        ]

        check_mora_pitch_pairs(test_words)


    def test_pass_if_transpose_works(self):
        test_input = {'a':list('123'), 'b':list('456'),}
        expected = {'1':'a', '2':'a', '3':'a', '4':'b', '5':'b', '6':'b',}

        result = utils.mora.transpose_dict_of_lists(test_input)

        assert result == expected


    def test_pass_if_get_last_mora_info_works_with_all_unigraphs(self):
        df = pd.DataFrame({
            'mora': [[utils.mora.Mora(x, 0)] for x in self.unigraphs],
        })

        expected = pd.DataFrame({
            'onset': [
                'g', 'g', 'g', 'g', 'g',
                'z', 'z', 'z', 'z', 'z',
                'd', 'd', 'd', 'd', 'd',
                'b', 'b', 'b', 'b', 'b',
                'p', 'p', 'p', 'p', 'p',
                'a', 'i', 'u', 'e', 'o',
                'k', 'k', 'k', 'k', 'k',
                's', 's', 's', 's', 's',
                't', 't', 't', 't', 't',
                'n', 'n', 'n', 'n', 'n',
                'h', 'h', 'h', 'h', 'h',
                'm', 'm', 'm', 'm', 'm',
                'y', 'y', 'y', 'r', 'r',
                'r', 'r', 'r', 'w', 'w',
                False, False
            ],
            'is_vowel': [
                False, False, False, False, False,
                False, False, False, False, False,
                False, False, False, False, False,
                False, False, False, False, False,
                False, False, False, False, False,
                True, True, True, True, True,
                False, False, False, False, False,
                False, False, False, False, False,
                False, False, False, False, False,
                False, False, False, False, False,
                False, False, False, False, False,
                False, False, False, False, False,
                False, False, False, False, False,
                False, False, False, False, False,
                False, False
            ],
            'end_vowel': [
                'a', 'i', 'u', 'e', 'o',
                'a', 'i', 'u', 'e', 'o',
                'a', 'i', 'u', 'e', 'o',
                'a', 'i', 'u', 'e', 'o',
                'a', 'i', 'u', 'e', 'o',
                'a', 'i', 'u', 'e', 'o',
                'a', 'i', 'u', 'e', 'o',
                'a', 'i', 'u', 'e', 'o',
                'a', 'i', 'u', 'e', 'o',
                'a', 'i', 'u', 'e', 'o',
                'a', 'i', 'u', 'e', 'o',
                'a', 'i', 'u', 'e', 'o',
                'a', 'u', 'o', 'a', 'i',
                'u', 'e', 'o', 'a', 'o',
                False, False
            ],
        })

        result = utils.mora.get_last_mora_info(df).drop('mora', axis=1)
        
        pd.testing.assert_frame_equal(result, expected)


    def test_pass_if_get_last_mora_info_works_with_all_digraphs(self):
        df = pd.DataFrame({
            'mora': [[utils.mora.Mora(x, 0)] for x in self.digraphs],
        })

        expected = pd.DataFrame({
            'onset': [
                'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 
                'z', 'z', 'z', 'z', 'z', 'z', 'z', 'z', 
                'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 
                'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 
                'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 
                'k', 'k', 'k', 'k', 'k', 'k', 'k', 'k', 
                's', 's', 's', 's', 's', 's', 's', 's', 
                't', 't', 't', 't', 't', 't', 't', 't', 
                'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 
                'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 
                'm', 'm', 'm', 'm', 'm', 'm', 'm', 'm', 
                'r', 'r', 'r', 'r', 'r', 'r', 'r', 'r'
            ],
            'is_vowel': [
                False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False
            ],
            'end_vowel': [
                'a', 'i', 'u', 'e', 'o', 'a', 'u', 'o',
                'a', 'i', 'u', 'e', 'o', 'a', 'u', 'o',
                'a', 'i', 'u', 'e', 'o', 'a', 'u', 'o',
                'a', 'i', 'u', 'e', 'o', 'a', 'u', 'o',
                'a', 'i', 'u', 'e', 'o', 'a', 'u', 'o',
                'a', 'i', 'u', 'e', 'o', 'a', 'u', 'o',
                'a', 'i', 'u', 'e', 'o', 'a', 'u', 'o',
                'a', 'i', 'u', 'e', 'o', 'a', 'u', 'o',
                'a', 'i', 'u', 'e', 'o', 'a', 'u', 'o',
                'a', 'i', 'u', 'e', 'o', 'a', 'u', 'o',
                'a', 'i', 'u', 'e', 'o', 'a', 'u', 'o',
                'a', 'i', 'u', 'e', 'o', 'a', 'u', 'o'
            ],
        })

        result = utils.mora.get_last_mora_info(df).drop('mora', axis=1)

        pd.testing.assert_frame_equal(result, expected)
