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
    - Add pronunciation info here (replacing get_last_kana_info?)
    - Silent characters
    - Soft 'G's
    """
    DELIMITER = '・'
    kana = None
    accent = None

    def __init__(self, kana, accent):
        assert len(kana) > 0, "Mora must be at least one character in length.\n\tkana = {}".format(kana)
        assert len(kana) <= 2, "Mora must not be more than 2 characters in length.\n\tkana = {}".format(kana)
        self.kana = kana
        self.accent = int(accent)
    
    def __repr__(self):
        return "M('{}', {})".format(self.kana, self.accent)
    
    def get_pair(self):
        return (self.kana, self.accent)

    def is_digraph(self):
        return len(self.kana) == 2
    
    def is_delimiter(self):
        return self.kana == self.DELIMITER


def mora_split(word, accent):
    """ Split a word into a list of phoneme-accent pairs, represented by a Mora
    object.

    word and accent should be of equal length, but this is unchecked.

    TODO: Replace 'ー' with correct vowel.
    """
    # FIXME: Maybe better to split into two lists before running the regex?

    # Split the string into mora the capture groups.
    # First part matches all possible digraphs, the second matches any remaining chars
    result = re.finditer(r"(.[ァィゥェォャュョ]|.)", word)

    def make_mora_from_regex(x):
        """ Extract the mora and the correct accent pattern. """
        char = x.group(0)
        # The accent pattern we want corresponds to the *last* kana in the group.
        # This means for digraphs we need to add one to the capture index.
        index = x.start(0) if len(char) is 1 else x.start(0) + 1
        acc = accent[index]
        return Mora(char, acc)

    # Combine the mora and accents into tuples.
    result = [make_mora_from_regex(x) for x in result if x.group(0)]

    return result


def get_last_mora_info(df):
    """ Get the onset and vowel of the last mora for each row in the dataframe. """
    df['onset'] = df.mora.apply(lambda x: ONSET[x[-1].kana[0]])
    df['is_vowel'] = df.onset.isin(set('aiueo'))
    df['end_vowel'] = df.mora.apply(lambda x: VOWEL_PART[x[-1].kana[-1]])

    return df
