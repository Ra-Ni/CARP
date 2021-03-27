import uuid
import logging

from _config import CONFIG
from syntax import Node, AST
from lex import Scanner
import tools.ucalgary as ucal


def _new(parser):
    parser.nodes.append(Node(parser.top[4:]))


def _push(parser):
    parser.nodes.append(Node(parser.last_production.lexeme))


def _iunary(parser):
    second = parser.nodes.pop()
    first = parser.nodes.pop()

    second.adopt(first)
    parser.nodes.append(second)


def _epop(parser):
    parent = parser.nodes[-1]
    child = parent.children[-1]
    if child.label == 'ε':
        parent.children.pop()


def _unary(parser):
    second = parser.nodes.pop()
    first = parser.nodes.pop()

    first.adopt(second)
    parser.nodes.append(first)


def _chk(parser):
    if not parser.nodes[-1].children:
        parser.nodes[-1].label = 'ε'


def _chk_merge(parser):
    parent = parser.nodes[-1]
    children = parent.children
    if len(children) == 1:
        child = children[0]
        parser.nodes.pop()
        child.parent = None
        parser.nodes.append(child)


def _nop(parser):
    parser.nodes.append(Node('ε'))


def _cond_unary(parser):
    if parser.nodes[-1].label == 'ε':
        parser.nodes.pop()
    else:
        _unary(parser)


def _swap(parser):
    parent = parser.nodes[-1]
    parent.children[-1], parent.children[-2] = parent.children[-2], parent.children[-1]


def _bin(parser):
    second = parser.nodes.pop()
    op = parser.nodes.pop()
    first = parser.nodes.pop()

    op.adopt(first, second)
    parser.nodes.append(op)


def _shift(parser):
    node = parser.nodes[-1]
    node.children = [node.children[-1]] + node.children[:-1]


def _epsilon(parser):
    pass


_OPS = {
    'NEW': _new,
    'PUSH': _push,
    'EPOP': _epop,
    'UNARY': _unary,
    'CHK': _chk,
    'NOP': _nop,
    'BIN': _bin,
    'COND_UNARY': _cond_unary,
    'IUNARY': _iunary,
    'CHK_MERGE': _chk_merge,
    'SHIFT': _shift,
    'ε': _epsilon,
    'SWAP': _swap
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
        self.last_production = None
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

        self._error_logger.error(f'[{location}]ERROR::Invalid Syntax {label} not in {msg}')

    def parse(self, reader: Scanner):
        self.reset()
        self._iterator = iter(reader)
        self._lookahead = next(self._iterator, None)

        while self._stack and self._lookahead:

            self.top = self._stack[-1]

            if self.top in self._ops:
                self._ops[self.top](self)
                self._stack.pop()

            elif self.top in self._terminals:
                if self.top == self._lookahead.type:
                    self.last_production = self._lookahead
                    self._derivations_logger.info(self._lookahead.type)
                    self._stack.pop()
                    self._lookahead = next(self._iterator, None)
                else:
                    self._recover()

            elif self.top in self._non_terminals:
                non_terminal = self._table.at[self.top, self._lookahead.type]
                if non_terminal:
                    self._error_logger.debug(f'[{self._lookahead.location}]INFO::{self.top} → {" ".join(non_terminal)}')
                    self._stack.pop()
                    if ['ε'] != non_terminal:
                        self._stack.extend(non_terminal[::-1])

                else:
                    self._recover()
            else:
                raise ValueError(f'Value {self.top} not defined in table or operations')

        while self._stack and self._stack[-1] in self._ops:
            self._ops[self._stack.pop()](self)

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
        self.last_production = None
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
