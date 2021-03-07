import os
from pathlib import Path
import urllib.parse
import lex as lx
from syntax.ast import AST
from syntax.recovery import panic
import syntax.ucalgary as ucal


class Analyzer:
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
        self.ast = None
        self.logs = None

    def parse(self, src: str) -> bool:
        self.lexer.open(src)
        self.tokens = iter(self.lexer)
        self.lookahead = next(self.tokens)
        self.logs = []
        self.ast = AST()
        self.errors = []
        self.derivations = []

        while not self.ast.empty() and self.lookahead:
            top = self.ast.peek()

            self.logs.append(top)
            if top.label in self.terminals:
                if top.label == self.lookahead.type:
                    self.derivations.append(self.lookahead)
                    self.ast.pop()
                    top.token = self.lookahead
                    self.lookahead = next(self.tokens, None)
                else:
                    self.recovery_mode(self)

            else:
                non_terminal = self.ll1.at[top.label, self.lookahead.type]

                if non_terminal:
                    non_terminal = non_terminal[::-1]

                    if ['ε'] != non_terminal:
                        self.ast.add_all(non_terminal)

                    else:
                        self.ast.epsilon_remove()
                        
                else:
                    self.recovery_mode(self)

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

    obj = Analyzer()
    obj.ll1 = ll1
    obj.terminals = ll1.columns
    obj.non_terminals = ll1.index
    obj.first = vitals['first set']
    obj.follow = vitals['follow set']
    obj.lexer = opts['lexer']
    obj.recovery_mode = opts['recovery_mode']

    return obj
