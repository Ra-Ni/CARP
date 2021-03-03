import os
from pathlib import Path
import urllib.parse

import lex as lx
from syntax.recovery import panic
from syntax.ucalgary import get_ll1, get_vitals


class logger:
    def __init__(self):
        self.derivation = []
        self.restricted = ['id', 'intnum', 'floatnum', 'stringlit']
        self.line_num = 1

    def add(self, item: lx.token) -> None:
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

    def parse(self, target: str) -> bool:
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


def load(**kwargs):
    is_online = False
    grammar = None
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

    ll1 = get_ll1(grammar, opts['ll1'], is_online)
    vitals = get_vitals(grammar, opts['vitals'], is_online)

    obj = analyzer()
    obj.ll1 = ll1
    obj.terminals = ll1.columns
    obj.non_terminals = ll1.index
    obj.first = vitals['first set']
    obj.follow = vitals['follow set']
    obj.lexer = opts['lexer']
    obj.recovery_mode = opts['recovery_mode']

    return obj



if __name__ == '__main__':
    analysis = load()

    analysis.parse('../../examples/bubblesort.src')
    analysis.parse('../../examples/polynomial.src')
