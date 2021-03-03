import os
from pathlib import Path
import urllib.parse
import requests
import pandas as pd
import lex as lx
from lex import token
import asyncio

class logger:
    def __init__(self):
        self.derivation = []
        self.restricted = ['id', 'intnum', 'floatnum', 'stringlit']
        self.line_num = 1

    def add(self, item: token):
        text = item.lexeme if len(item.lexeme) == 1 and item.type not in self.restricted else item.type
        self.derivation.append(text)

    def store(self):
        text = ' '.join(self.derivation)

        with open('../_config/out', 'w') as fstream:
            fstream.write(text)


class analyzer:
    def __init__(self):
        self.ll1 = None
        self.terminals = None
        self.non_terminals = None
        self.first = None
        self.follow = None
        self.lexer = None
        self.recovery_mode = None

        self.tokens = None
        self.lookahead = None
        self.stack = []
        self.errors = False

    def parse(self, target: str):
        self.lexer.open(target)
        self.tokens = iter(self.lexer)
        self.lookahead = next(self.tokens)
        self.stack.clear()
        self.stack.append('START')
        self.errors = False
        log = logger()

        while self.stack and self.lookahead:
            top = self.stack[-1]
            if top in self.terminals:
                if top == self.lookahead.type:
                    self.stack.pop()
                    log.add(self.lookahead)
                    self.lookahead = next(self.tokens, None)

                else:
                    self.recovery_mode(self)

            else:
                non_terminal = self.ll1.at[top, self.lookahead.type]

                if non_terminal:
                    non_terminal = non_terminal[::-1]
                    self.stack.pop()

                    if ['ε'] != non_terminal:
                        self.stack.extend(non_terminal)

                else:
                    self.recovery_mode(self)

        log.store()
        if self.lookahead or self.stack or self.errors:
            return False
        return True


def _query(path, grammar, **kwargs):
    uri = 'https://smlweb.cpsc.ucalgary.ca/'
    opts = [key + '=' + value for key, value in kwargs.items()]
    opts = '&' + '&'.join(opts)
    response = requests.get(uri + path + '?grammar=' + grammar + opts)

    if not response.ok:
        raise ConnectionError("Connection to UCalgary's grammar tool is currently unavailable")

    return response.text


def _get_ll1(grammar, backup: str, online: bool = False):
    if not online:
        return pd.read_pickle(backup)

    response_html = _query('ll1-table.php', grammar, substs='')
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

    ll1.to_pickle(backup, compression='xz')
    return ll1


def _get_vitals(grammar, backup: str, online: bool = False):
    if not online:
        return pd.read_pickle(backup)

    response_html = _query('vital-stats.php', grammar, substs='')
    vitals = pd.read_html(response_html)[2]

    vitals.rename(index=dict(zip(vitals.index.to_list(), vitals.xs('nonterminal', 1).to_list())), inplace=True)

    vitals.drop(['nonterminal'], 1, inplace=True)

    for dst, src, value in [(vitals['first set'], vitals['nullable'], ' ε'),
                            (vitals['follow set'], vitals['endable'], ' $')]:
        src.replace(['yes', 'no'], [value, ''], inplace=True)
        dst.mask(dst == '∅', None, inplace=True)
        dst += src
        dst.where(pd.isnull(dst), dst.str.split(), inplace=True)

    vitals.to_pickle(backup, compression='xz')
    return vitals


def load(**kwargs):
    is_online = False
    grammar = None
    loop = asyncio.get_event_loop()
    opts = {'recovery_mode': panic,
            'dir': '../_config/',
            'll1': 'll1.bak.xz',
            'vitals': 'vitals.bak.xz',
            'syntax_config': 'syntax',
            'lexer': None}
    opts.update(kwargs)

    if not opts['lexer']:
        opts['lexer'] = lx.load(lex_suppress_comments=1, **opts)

    for file in ['ll1', 'vitals', 'syntax_config']:
        opts[file] = Path(opts['dir'] + opts[file])

    if not opts['syntax_config'].exists() or opts['syntax_config'].is_dir():
        raise FileNotFoundError('Configuration file "%s" does not exist or is a directory' % opts['syntax_config'])

    for backup in ['ll1', 'vitals']:
        f = opts[backup]
        if f.is_dir() or f.exists() and f.stat().st_mtime < f.stat().st_mtime:
            os.remove(backup)

        if not f.exists():
            is_online = True

    if is_online:
        with open(opts['syntax_config'], 'r') as fstream:
            grammar = urllib.parse.quote_plus(fstream.read())

    ll1 = _get_ll1(grammar, opts['ll1'], is_online)
    vitals = _get_vitals(grammar, opts['vitals'], is_online)

    obj = analyzer()
    obj.ll1 = ll1
    obj.terminals = ll1.columns
    obj.non_terminals = ll1.index
    obj.first = vitals['first set']
    obj.follow = vitals['follow set']
    obj.lexer = opts['lexer']
    obj.recovery_mode = opts['recovery_mode']

    return obj


def panic(parser: analyzer):
    top = parser.stack[-1]
    lookahead = parser.lookahead

    if top in parser.terminals:
        print("[{}] SyntaxError: invalid syntax expectation '{}'".format(lookahead.location, top))
        parser.stack.pop()
        return

    follow = parser.follow.loc[top] or []
    series = parser.ll1.loc[top].dropna().index

    print("[%s] SyntaxError: invalid syntax '%s' ∉ %s" % (lookahead.location, lookahead.type, set(series)))

    if lookahead and lookahead in follow:
        parser.stack.pop()
    else:
        # lookahead and not (lookahead.type in first or 'ε' in first and lookahead.type in follow)
        while lookahead and lookahead.type not in series:
            lookahead = parser.lookahead = next(parser.tokens, None)

    parser.errors = True


if __name__ == '__main__':
    analysis = load()

    analysis.parse('../../examples/bubblesort.src')
    analysis.parse('../../examples/polynomial.src')
