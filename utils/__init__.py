import pandas as pd

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
                                .apply(lambda x: x.ac.ljust(len(x.midashigo1), '0'),
                                       axis=1))

    # This query shouldn't return any rows.
    assert len(accent[accent.ac.str.len()!=accent.midashigo1.str.len()]) == 0
    
    return accent