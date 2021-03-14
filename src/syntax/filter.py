import pydot

from lex import scanner
from syntax.node import Node, NodeBuilder


class Filter:
    def __init__(self, table, follow, terminals, logger):
        self.table = table
        self.follow = follow
        self.terminals = terminals

        self.lookahead = None
        self.iterator = None
        self.log = logger

        self.error = False
        self.productions = []

        self.root = Node('Start')
        self.top = self.root

        self.stack = [self.top]

    def _recover(self):
        self.error = True

        if self.top.label not in self.terminals:
            follow = self.follow.loc[self.top.label] or []
            series = self.table.loc[self.top.label].dropna().index

            msg = str(set(series))
            location = self.lookahead.location
            label = self.lookahead.type

            if self.lookahead and self.lookahead.type in follow:
                self.stack.pop()
            else:
                while self.lookahead and self.lookahead.type not in series:
                    self.lookahead = next(self.iterator, None)

                location = str(location) + '-' + str(self.lookahead.location)

        else:
            msg = self.top.label
            location = self.lookahead.location
            label = self.lookahead.type

            self.stack.pop()

        self.log.error('[{}]{}::Invalid Syntax {} not in {}'.format(location, 'ERROR', label, msg))

    def parse(self, reader: scanner):
        builder = NodeBuilder()

        self.reset()
        self.iterator = iter(reader)
        self.lookahead = next(self.iterator, None)

        while self.stack:

            self.top = self.stack[-1]
            if self.top.label == 'ε':
                self.stack.pop()


            elif self.top.label in self.terminals:
                if self.top.label == self.lookahead.type:
                    self.top.label = self.lookahead.lexeme
                    self.productions.append(self.lookahead)
                    self.stack.pop()
                    builder.postbuild(self.top)
                    self.lookahead = next(self.iterator, None)
                else:
                    self._recover()

            else:

                non_terminal = self.table.at[self.top.label, self.lookahead.type]

                if non_terminal:
                    self.log.debug('[{}]{}::{} → {}'.format(self.lookahead.location, 'INFO',
                                                            self.top.label, ' '.join(non_terminal)))

                    self.top.adopt(*non_terminal)

                    self.stack.pop()
                    self.stack.extend(self.top.children[::-1])

                else:
                    self._recover()

        return not (self.lookahead or self.stack or self.error), self.productions

    def reset(self):
        self.productions = []
        self.lookahead = None
        self.iterator = None
        self.root = Node('Start')
        self.top = self.root
        self.stack = [self.top]
        self.error = False
