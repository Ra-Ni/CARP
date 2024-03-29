from pathlib import Path
import urllib.parse
import pandas as pd
import requests

from _config import CONFIG


def query(path, **kwargs):
    if 'grammar' not in kwargs:
        raise ValueError("Grammar not defined")

    uri = 'https://smlweb.cpsc.ucalgary.ca/'
    opts = [key + '=' + value for key, value in kwargs.items()]
    opts = '&'.join(opts)

    response = requests.get(uri + path + '?' + opts)

    if not response.ok:
        raise ConnectionError("Connection to UCalgary's grammar tool is currently unavailable")

    return response.text


def get_ll1(grammar):
    response_html = query('ll1-table.php', grammar=grammar, substs='')
    ll1 = pd.read_html(response_html)[1]

    ll1.rename(columns=dict(zip(ll1.columns[1:].to_list(), ll1.xs(0, 0)[1:].to_list())),
               index=dict(zip(ll1.index[1:].to_list(), ll1.xs(0, 1)[1:].to_list())),
               inplace=True)

    ll1.drop([0], 0, inplace=True)
    ll1.drop([0], 1, inplace=True)

    for index, series in ll1.iterrows():
        new_series = series.where(pd.notnull(series), None)
        new_series = new_series.replace([r'.*\s*→\s*', '&epsilon'], ['', 'ε'], regex=True)
        ll1.loc[index] = new_series.str.split()

    ll1.to_pickle(CONFIG['LL1_FILE'], compression='xz')
    return ll1


def get_vitals(grammar):
    response_html = query('vital-stats.php', grammar=grammar)
    vitals = pd.read_html(response_html)[2]

    vitals.rename(index=dict(zip(vitals.index.to_list(), vitals.xs('nonterminal', 1).to_list())), inplace=True)

    vitals.drop(['nonterminal'], 1, inplace=True)

    for dst, src, value in [(vitals['first set'], vitals['nullable'], ' ε'),
                            (vitals['follow set'], vitals['endable'], ' $')]:
        src.replace(['yes', 'no'], [value, ''], inplace=True)

        dst.mask(dst == '∅', '', inplace=True)
        dst += src
        dst.mask(dst == '', None, inplace=True)
        dst.where(pd.isnull(dst), dst.str.split(), inplace=True)

    vitals.to_pickle(CONFIG['VITALS_FILE'], compression='xz')
    return vitals


def load():
    if not (CONFIG['LL1_FILE'].exists() and
            CONFIG['VITALS_FILE'].exists() and
            CONFIG['LL1_FILE'].stat().st_mtime >= CONFIG['GRAMMAR_FILE'].stat().st_mtime):
        with open(CONFIG['GRAMMAR_FILE'], 'r') as fstream:
            grammar = urllib.parse.quote_plus(fstream.read())

        return get_ll1(grammar), get_vitals(grammar)

    else:
        return pd.read_pickle(CONFIG['LL1_FILE']), pd.read_pickle(CONFIG['VITALS_FILE'])
