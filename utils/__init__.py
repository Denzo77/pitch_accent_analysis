import pandas as pd
import re
# hiragana = 'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽあいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんぁぃぅぇぉゃゅょっ'
# katakana = 'ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンァィゥェォャュョッ'

vowel_part_raw = {
    'a': list('カサタナハアマヤラワガザダバパァャ'),
    'i': list('ギジヂビピイキシチニヒミモリィ'),
    'u': list('グズヅブプウクスツヌフムユルゥュ'),
    'e': list('ゲゼデベペエケセテネヘメレェ'),
    'o': list('ゴゾドボポオコソトノホモヨロヲォョ'),
    False: list('ンッ')
}

onset_raw = {
    'a': list('ア'),
    'i': list('イ'),
    'u': list('ウ'),
    'e': list('エ'),
    'o': list('オ'),
    'g': list('ガギグゲゴ'),
    'z': list('ザジズゼゾ'),
    'd': list('ダヂヅデド'),
    'b': list('バビブベボ'),
    'p': list('パピプペポ'),
    'k': list('カキクケコ'),
    's': list('サシスセソ'),
    't': list('タチツテト'),
    'n': list('ナニヌネノ'),
    'h': list('ハヒフヘホ'),
    'm': list('マミムメモ'),
    'y': list('ヤユヨ'),
    'r': list('ラリルレロ'),
    'w': list('ワヲ'),
    False: list('ンァィゥェォャュョッ'), # These should not exist as an onset.
}

def transpose_dict_of_lists(raw):
    """ 'Transpose' a dictionary of lists.

    Takes a dictionary in form
        `{'a':list('123'), 'b':list('456'),}`
    and outputs it in form
        `{'1':'a', '2':'a', '3':'a', '4':'b', '5':'b', '6':'b',}`

    All individual elements within the lists of original dictionary must be
    unique to prevent collisions.
    """
    transpose = {}
    for k, v in raw.items():
        transpose.update({x: k for x in v})
    
    return transpose


VOWEL_PART = transpose_dict_of_lists(vowel_part_raw)
ONSET = transpose_dict_of_lists(onset_raw)


def process_accent_data(in_file, columns):
    """ Read accent file, retain relevant columns and pad accent column with
    leading 0s.
    """
    accent = pd.read_csv(in_file, dtype={
        'nopronouncepos':str,
        'nasalsoundpos':str,
        'ac':str
    })[columns]
    
    # Get rows where the length of the accent description doesn't match the
    # length of the phonetic spelling.
    index = accent.ac.str.len() != accent.midashigo1.str.len()
    
    # Pad any missing leading 0s in accent.ac
    #
    # Padding function comparison:
    # - lambda x: "{}{}".format("0"*(len(x.midashigo1)-len(x.ac)), x.ac)
    #     3.23 s ± 104 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
    # - lambda x: x.ac.ljust(len(x.midashigo1), '0')
    #     2.32 s ± 73.2 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
    # - lambda x: x.ac.zfill(len(x.midashigo1))
    #     2.35 s ± 83.6 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
    # - lambda x: "{:<0{width}}".format(x.ac, width=len(x.midashigo1))
    #     2.32 s ± 58.4 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
    accent.loc[index,'ac'] = (accent[index]
                                .apply(lambda x: x.ac.rjust(len(x.midashigo1), '0'),
                                       axis=1))

    # This query shouldn't return any rows.
    assert len(accent[accent.ac.str.len() != accent.midashigo1.str.len()]) == 0
    # assert len(accent[accent.ac.str.startswith('1')]) == 0

    return accent


class Mora:
    """ Class representing a single mora

    Currently handles:
    - All unigraphs.
        - NOTE: Unigraphs are not checked to make sure they are in of the
          correct character set.
    - Word delimiter `・`
    - Digraphs e.g. 'シャ'
        - NOTE: Digraphs are not validated in any way.
    
    TODO: If necessary...
    - Silent characters
    - Soft 'G's
    """
    DELIMITER = '・'
    phoneme = None
    accent = None

    def __init__(self, phoneme, accent):
        assert len(phoneme) > 0, "Mora must be at least one character in length.\n\tphoneme = {}".format(phoneme)
        assert len(phoneme) <= 2, "Mora must not be more than 2 characters in length.\n\tphoneme = {}".format(phoneme)
        self.phoneme = phoneme
        self.accent = int(accent)
    
    def get_pair(self):
        return (self.phoneme, self.accent)

    def is_digraph(self):
        return len(self.phoneme) == 2
    
    def is_delimiter(self):
        return self.phoneme == self.DELIMITER


def mora_split(word, accent):
    """ Split a word into a list of phoneme-accent pairs, represented by a Mora
    object.

    word and accent should be of equal length, but this is unchecked.
    """
    # FIXME: Maybe better to split into two lists before running the regex?

    # Split the string into mora the capture groups.
    # First part matches all possible digraphs, the second matches any remaining chars
    result = re.finditer(r"(.[ァィゥェォャュョ]|.)", word)
    # Combine the mora and accents into tuples.
    result = [Mora(x.group(0), accent[x.start(0)]) for x in result if x.group(0)]

    return result


def get_last_kana_info(df):
    """ Get the onset and vowel of each row in the dataframe. """
    df['onset'] = df.midashigo_alt.apply(lambda x: ONSET[x[-1]])
    df['is_vowel'] = df.onset.isin(set('aiueo'))
    df['end_vowel'] = df.midashigo_alt.apply(lambda x: VOWEL_PART[x[-1]])

    return df
