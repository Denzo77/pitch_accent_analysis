import pandas as pd
from . import mora

def read_accent_file(in_file, columns):
    """ Read accent file, retain relevant columns and pad accent column with
    leading 0s.

    # Notes on 'ac' column:
    - 0 = low pitch
    - 1 = high pitch
    - 2 = dropping pitch
    - Entries that end in a 0 or a 1 mean that the trailing particle attaches high.
    - Entries that end in a 2 mean that the trailing particle attaches low
    i.e. there is a pitch drop between the last mora of the word and the
    following one.
    
    If 'ac' begins with a 1, a leading 0 has been ommitted.
    
    # Notes on 'nopronouncepos' and 'nasalpos'
    no idea what's going on here.

    """

    # Some columns contain integers, but must be interpreted as strings.
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


def dedup_and_split_all_mora(df):
    # FIXME: Some Not sure we should be dropping by midashigo_alt.
    # accent.groupby('word_id').apply(lambda x: x[x.midashigo_alt.unique()])
    no_dups = df.drop_duplicates(['word_id','midashigo_alt']).reset_index().drop(columns='index')

    # %timeit [utils.mora_split(word, accent) for word, accent in zip(no_dups.midashigo_alt, no_dups.accent)]
    # 815 ms ± 104 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
    # %timeit no_dups.apply(lambda x: utils.mora_split(x.midashigo_alt, x.accent), axis=1)
    # 3.72 s ± 339 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)

    no_dups['mora'] = [
        mora.mora_split(word, accent) 
        for word, accent 
        in zip(no_dups.midashigo_alt, no_dups.accent)
    ]

    return no_dups


USEFUL_COLUMNS = [
#     'NID', # Unique ID. Ignore as we can just use the row index for this.
    'ID', # ID unique to word & accent (same word with different accents have new `ID`)
    'ACT', # ??? ID unique to each word? This seems to be unique across semantic words, but doesn't distinguish accents.
    'midashigo', # Literally "title word/keyword/entry word"
    'nhk', # Kanji?
    'kanjiexpr', # Kanji 2?
#     'NHKexpr', # This seems to combine nhk and kanjiexpr
    'numberchars', # This is the length of one of the other columns... (midashigo?)
#     'nopronouncepos', # len(midashigo1)
#     'majiri', # Literally means "mixed". Probably an example phrase.
#     'kaisi', # Literally "start". Probably the starting location of the word within `majiri`.
    'midashigo1', # as `midashigo`, but also adds characters for things like word boundaries.
    'akusentosuu', # I think this is "accent+number". Maybe the number of different accents a word can be pronounced with?
#     'bunshou', # Literally "sentence". I think this is 1 when `majiri` contains an example sentence.
    'ac', # This seems to be a list of mora accents. Note that this corresponds to `midashigo1`, not `midashigo`
]

def read_and_process_accent_file(accent_file, columns=USEFUL_COLUMNS):
    """ Read accent file, deduplicate and generate mora-pitch pairs.

    This is equivalent to all but the final cell of ACC_DB_parsing.ipynb.

    TODO: Write test cases.

    :param: accent_file: Path to the accent file to parse.
    :param: columns: List of columns to retain.
    """
    df = read_accent_file(accent_file, columns).rename(columns={
        'ACT':'sem_word_id',
        'ID':'word_id',
        'nhk':'word',
        'kanjiexpr':'kanji',
        'numberchars':'midashigo_alt_len',
        'midashigo1':'midashigo_alt',
        'akusentosuu':'n_accents',
        'ac':'accent',
    })

    df = dedup_and_split_all_mora(df)

    return df


def generate_single_mora_words_file(accent_file, out_path="data/single_mora_words.pickle"):
    df = read_and_process_accent_file(accent_file)

    # Isolate single mora words
    df.loc[df.mora.str.len() == 1, [
        'word_id',
        'sem_word_id',
        'word',
        'kanji',
        'n_accents',
        'mora'
    ]].reset_index().drop(columns='index').to_pickle(out_path)
