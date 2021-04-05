import uuid
import logging

from _config import CONFIG
from syntax import Node, AST
from lex import Scanner
import tools.ucalgary as ucal

IFS = ','


def _new(parser):
    parser.nodes.append(Node(kind=parser.top[4:]))


def _push(parser):
    parser.nodes.append(Node(**parser.last_production.to_dict()))


def _append(parser):
    value = parser.nodes.pop()['name']
    key = parser.top[4:]
    parser.nodes[-1][key] += value


def _conditional_unary(parser):
    if parser.nodes[-1].children:
        _unary(parser)
    else:
        parser.nodes.pop()


def _unary(parser):
    second = parser.nodes.pop()
    first = parser.nodes.pop()

    first.adopt(second)
    parser.nodes.append(first)


def _nop(parser):
    parser.nodes.append(Node(name='ε'))


def _swap(parser):
    parser.nodes[-1], parser.nodes[-2] = parser.nodes[-2], parser.nodes[-1]


def _bin(parser):
    second = parser.nodes.pop()
    op = parser.nodes.pop()
    first = parser.nodes.pop()

    op.adopt(first, second)
    parser.nodes.append(op)


def _update(parser):
    _, key, value = parser.top.split('_', 2)
    parser.nodes[-1][key] = value


def _map(parser):
    node = parser.nodes.pop()
    _, first, second = parser.top.split('_', 2)

    parser.nodes[-1][first] = node[second]


def _begin(parser):
    parser.nodes.append('BEGIN')


def _end(parser):
    current = parser.nodes.pop()
    nodes = []
    while current != 'BEGIN':
        nodes.append(current)
        current = parser.nodes.pop()
    if parser.nodes[-1] == 'BEGIN':
        parser.nodes.pop()

    nodes.reverse()

    parser.nodes.append(Node(name=IFS.join(x['name'] for x in nodes)))


def _ifs(parser):
    delimiter = parser.top[4:]
    if not delimiter:
        delimiter = ''
    elif delimiter == 'sr':
        delimiter = '::'
    else:
        delimiter = ','

    global IFS
    IFS = delimiter


def _insert(parser):
    key, value = parser.top.split('_', 1)
    parser.nodes[-1][key.lower()] = value.replace('_', ' ')


def _as(parser):
    value = parser.nodes.pop()['name']
    key = parser.top[3:]
    parser.nodes[-1][key] = value


def _epsilon(parser):
    pass


_OPS = {
    'NEW': _new,
    'PUSH': _push,
    'UNARY': _unary,
    'NOP': _nop,
    'BIN': _bin,
    'ε': _epsilon,
    'SWAP': _swap,
    'BEGIN': _begin,
    'END': _end,
    'IFS': _ifs,
    'INSERT': _insert,
    'AS': _as,
    'APP': _append,
    'MAP': _map,
    'UPD': _update,
    'CUNARY': _conditional_unary
}

_SPEC = {
    'UPD',
    'MAP',
    'APP',
    'AS',
    'INSERT'
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
                    if [CONFIG['EPSILON']] != non_terminal:
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

        for reference in filter(lambda x: '_' in x, non_terminals.to_list()):
            key, _ = reference.split('_', 1)
            ops[reference] = _OPS['INSERT'] if key not in _OPS else _OPS[key]

        for spec in _SPEC:
            ops.pop(spec)

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
