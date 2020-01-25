import pytest

import utils

class TestKanaPhonemeExtraction():
    def test_pass_if_transpose_works(self):
        test_input = {'a':list('123'), 'b':list('456'),}
        expected = {'1':'a', '2':'a', '3':'a', '4':'b', '5':'b', '6':'b',}

        result = utils.transpose_dict_of_lists(test_input)

        assert result == expected
