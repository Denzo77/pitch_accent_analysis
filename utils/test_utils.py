import pytest
import pandas as pd

import utils

class TestKanaPhonemeExtraction():
    katakana = 'ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンァィゥェォャュョッ'
    # unigraphs = 'ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンッ'
    # digraph_endings = 'ァィゥェォャュョ'


    def test_pass_if_mora_split_works_on_unigraphs(self):
        # word, accent, expected
        test_words = [
            ("アイゾー", "0111", [('ア', 0), ('イ', 1), ('ゾ', 1), ('ー', 1)]),
        ]
        for word, accent, expected in test_words:
            result = [x.get_pair() for x in utils.mora_split(word, accent)]

            assert result == expected


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
        for word, accent, expected in test_words:
            result = [x.get_pair() for x in utils.mora_split(word, accent)]

            assert result == expected


    def test_pass_if_mora_split_works_on_compound_words(self):
        # word, accent, expected
        test_words = [
            ("アイ・イレナイ", "2000111", [('ア', 2), ('イ', 0), ('・',0), ('イ', 0), ('レ', 1), ('ナ', 1), ('イ', 1)]),
            ("ソクサイ・エンメイ", "011100111", [('ソ',0),('ク',1),('サ',1),('イ',1),('・',0),('エ',0),('ン',1),('メ',1),('イ',1)])
        ]
        for word, accent, expected in test_words:
            result = [x.get_pair() for x in utils.mora_split(word, accent)]

            assert result == expected


    def test_pass_if_transpose_works(self):
        test_input = {'a':list('123'), 'b':list('456'),}
        expected = {'1':'a', '2':'a', '3':'a', '4':'b', '5':'b', '6':'b',}

        result = utils.transpose_dict_of_lists(test_input)

        assert result == expected



    def test_pass_if_get_last_kana_info_works_with_all_kana(self):

        df = pd.DataFrame({
            'midashigo_alt': list(self.katakana),
        })
        utils.get_last_kana_info(df)

