import uuid
import logging

from _config import CONFIG
from syntax import Node, AST
from lex import Scanner
import tools.ucalgary as ucal


def _new(test):
    test.nodes.append(Node(test.top[4:]))


def _push(test):
    test.nodes.append(Node(test.production.lexeme))


def _pop(test):
    test.nodes.pop()


def _unary(test):
    second = test.nodes.pop()
    first = test.nodes.pop()

    first.adopt(second)
    test.nodes.append(first)


def _chk(test):
    if not test.nodes[-1].children:
        test.nodes[-1].label = 'ε'


def _nop(test):
    test.nodes.append(Node('ε'))


def _bin(test):
    second = test.nodes.pop()
    op = test.nodes.pop()
    first = test.nodes.pop()

    op.adopt(first, second)
    test.nodes.append(op)


_OPS = {
    'NEW': _new,
    'PUSH': _push,
    'POP': _pop,
    'UNARY': _unary,
    'CHK': _chk,
    'NOP': _nop,
    'BIN': _bin
}


class Parser:
    def __init__(self):
        self._table = None
        self._follow = None
        self._terminals = None
        self._non_terminals = None
        self._error_logger = None
        self._derivations_logger = None
        self._ops = None

        self._error = False
        self._lookahead = None
        self._iterator = None
        self._stack = [CONFIG['LL1_START']]

        self.top = self._stack[0]
        self.nodes = []
        self.production = None
        self.ast = None

    def _recover(self):
        self._error = True

        if self.top not in self._terminals:
            follow = self._follow.loc[self.top] or []
            series = self._table.loc[self.top].dropna().index

            msg = str(set(series))
            location = self._lookahead.location
            label = self._lookahead.type

            if self._lookahead and self._lookahead.type in follow:
                self._stack.pop()
            else:
                while self._lookahead and self._lookahead.type not in series:
                    self._lookahead = next(self._iterator, None)

                location = str(location) + (('-' + str(self._lookahead.location)) if self._lookahead else '')

        else:
            msg = self.top
            location = self._lookahead.location
            label = self._lookahead.type

            self._stack.pop()

        self._error_logger.error('[{}]{}::Invalid Syntax {} not in {}'.format(location, 'ERROR', label, msg))

    def parse(self, reader: Scanner):
        self.reset()
        self._iterator = iter(reader)
        self._lookahead = next(self._iterator, None)

        while self._stack and self._lookahead:

            self.top = self._stack[-1]

            if self.top in self._ops:
                self._ops[self.top](self)
                self._stack.pop()

            elif self.top == 'ε':
                self._stack.pop()

            elif self.top in self._terminals:
                if self.top == self._lookahead.type:
                    self.production = self._lookahead
                    self._derivations_logger.info(self._lookahead.type)
                    self._stack.pop()

                    self._lookahead = next(self._iterator, None)
                else:
                    self._recover()

            elif self.top in self._non_terminals:

                non_terminal = self._table.at[self.top, self._lookahead.type]

                if non_terminal:
                    self._error_logger.debug('[{}]{}::{} → {}'.format(self._lookahead.location,
                                                                      'INFO',
                                                                      self.top,
                                                                      ' '.join(non_terminal)))
                    self._stack.pop()
                    if ['ε'] != non_terminal:
                        self._stack.extend(non_terminal[::-1])

                else:
                    self._recover()
            else:
                raise ValueError(f'Value {self.top} not defined in table or operations')

        while self._stack:
            self.top = self._stack[-1]
            if self.top in self._ops:
                self._ops[self.top](self)
                self._stack.pop()
            else:
                break

        if self.nodes:
            self.ast = AST(self.nodes.pop())

        return not (self._lookahead or self._stack or self._error)

    def reset(self):
        self._error = False
        self._lookahead = None
        self._iterator = None
        self._stack = [CONFIG['LL1_START']]

        self.top = self._stack[0]
        self.nodes = []
        self.production = None
        self.ast = None

    @classmethod
    def load(cls, error_handler: logging.FileHandler = None, derivations_handler: logging.FileHandler = None):
        ll1, vitals = ucal.load()
        follow = vitals['follow set']
        terminals = ll1.columns
        non_terminals = ll1.index

        ops = _OPS.copy()
        ops.update([(x, _OPS['NEW']) for x in filter(lambda x: 'NEW' in x, non_terminals.to_list())])
        ops.pop('NEW')

        error_logger = logging.getLogger(str(uuid.uuid4()))
        derivations_logger = logging.getLogger(str(uuid.uuid4()))

        for logger, handler in [(error_logger, error_handler), (derivations_logger, derivations_handler)]:
            if handler:
                logger.addHandler(handler)
                logger.setLevel(handler.level)
            else:
                logger.setLevel(logging.CRITICAL)

        obj = cls()
        obj._table = ll1
        obj._follow = follow
        obj._terminals = terminals
        obj._non_terminals = non_terminals
        obj._ops = ops
        obj._error_logger = error_logger
        obj._derivations_logger = derivations_logger

        return obj
