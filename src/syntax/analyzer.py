import os
import uuid
from pathlib import Path
import urllib.parse
import pydot
import lex as lx
from syntax.recovery import panic
import syntax.ucalgary as ucal


class ast:

    def __init__(self, parent: str = 'START'):

        self.root = 1
        self._sequence = 2
        self.stack = [self.root]
        self.labels = {self.root: parent}
        self.children = {self.root: []}
        self.parent = {self.root: 0}
        self.blacklist = {'rpar', 'lpar', 'lcurbr', 'rcurbr', 'lsqbr', 'rsqbr', 'semi', 'if', 'then', 'else', 'while'}

    def render(self, src):
        graph = pydot.Dot('AST', graph_type='digraph')
        nodes = {}

        for uid, parent in self.parent.items():
            if parent:
                first = nodes.setdefault(uid, pydot.Node(uid, label=self.labels[uid]))
                second = nodes.setdefault(parent, pydot.Node(parent, label=self.labels[parent]))
                graph.add_node(first)
                graph.add_node(second)
                graph.add_edge(pydot.Edge(parent, uid))

        graph.write_png(src)

    def add(self, node_label, parent):
        uid = self._sequence
        self._sequence += 1
        self.labels[uid] = node_label
        self.parent[uid] = parent
        self.children[uid] = []
        self.children[parent].append(uid)
        return uid

    def add_all(self, children: list):
        ls = list(filter(lambda x: x not in self.blacklist, children))
        children_uids = []
        parent = self.stack.pop()

        for child in ls[::-1]:
            uid = self.add(child, parent)
            if child.isupper():
                children_uids.append(uid)

        self.stack.extend(children_uids[::-1])

    def remove(self, uid):

        for child in self.children[uid]:
            self.remove(child)

        if self.parent[uid]:
            self.children[self.parent[uid]].remove(uid)

        del self.children[uid]
        del self.labels[uid]
        del self.parent[uid]

    def _epsilon_remove(self, uid):
        if not self.children[uid]:
            uid_parent = self.parent[uid]
            if uid in self.children[uid_parent]:
                self.children[uid_parent].remove(uid)
            del self.children[uid]
            del self.labels[uid]
            del self.parent[uid]
            self._epsilon_remove(uid_parent)

    def epsilon_remove(self):
        self._epsilon_remove(self.stack.pop())






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
        self.ast = None
        self.logs = None

    def parse(self, src: str) -> bool:
        self.lexer.open(src)
        self.tokens = iter(self.lexer)
        self.lookahead = next(self.tokens)
        self.stack = ['START']
        self.logs = []
        self.ast = ast()
        self.errors = []
        self.derivations = []

        while self.stack and self.lookahead:
            top = self.stack[-1]

            self.logs.append(top)
            if top in self.terminals:
                if top == self.lookahead.type:
                    self.derivations.append(self.lookahead)
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
                        self.ast.add_all(non_terminal)

                    # else:
                    #     self.ast.epsilon_remove(self.ast.stack[-1])
                    # else:
                    #     self.ast.add_all(parent, ['epsilon'])
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

    obj = analyzer()
    obj.ll1 = ll1
    obj.terminals = ll1.columns
    obj.non_terminals = ll1.index
    obj.first = vitals['first set']
    obj.follow = vitals['follow set']
    obj.lexer = opts['lexer']
    obj.recovery_mode = opts['recovery_mode']

    return obj
