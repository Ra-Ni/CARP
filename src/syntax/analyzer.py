import os
from pathlib import Path
import urllib.parse

import lex as lx
from syntax.recovery import panic
import syntax.ucalgary as ucal


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
        self.stack = None
        self.errors = None
        self.derivations = None

    def parse(self, src: str) -> bool:
        self.lexer.open(src)
        self.tokens = iter(self.lexer)
        self.lookahead = next(self.tokens)
        self.stack = ['START']
        self.errors = []
        self.derivations = []

        current_line = 1
        while self.stack and self.lookahead:
            top = self.stack[-1]

            if top in self.terminals:
                if top == self.lookahead.type:
                    if current_line == self.lookahead.location:
                        prefix = ' '
                    else:
                        prefix = '\n' * (self.lookahead.location - current_line)
                        current_line = self.lookahead.location
                    self.derivations.append(prefix + self.lookahead.type)

                    self.stack.pop()
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

        self.derivations = ''.join(self.derivations)
        self.errors = '\n'.join(self.errors)

        if self.lookahead or self.stack or self.errors:
            return False
        return True


def load(**kwargs):
    is_online = False
    grammar = None
    opts = {'recovery_mode': panic,
            'dir': '_config/',
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

    ll1, vitals = ucal.get(grammar, opts['ll1'], opts['vitals'], is_online)

    obj = analyzer()
    obj.ll1 = ll1
    obj.terminals = ll1.columns
    obj.non_terminals = ll1.index
    obj.first = vitals['first set']
    obj.follow = vitals['follow set']
    obj.lexer = opts['lexer']
    obj.recovery_mode = opts['recovery_mode']

    return obj
