import uuid

from syntax import Node, AST
from lex import scanner
import tools.ucalgary as ucal
import logging


def _new(test):
    test.nodes.append(Node(test.top[4:]))


def _push(test):
    test.nodes.append(Node(test.productions[-1].lexeme))


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


class Test:
    def __init__(self, table, follow, terminals, non_terminals, ops, logger):
        self._table = table
        self._follow = follow
        self._terminals = terminals
        self._non_terminals = non_terminals
        self._log = logger
        self._ops = ops

        self._error = False
        self.top = 'Start'
        self._stack = [self.top]
        self.nodes = []
        self._lookahead = None
        self._iterator = None

        self.productions = []
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

        self._log.error('[{}]{}::Invalid Syntax {} not in {}'.format(location, 'ERROR', label, msg))

    def parse(self, reader: scanner):
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
                    self.productions.append(self._lookahead)
                    self._stack.pop()

                    self._lookahead = next(self._iterator, None)
                else:
                    self._recover()

            elif self.top in self._non_terminals:

                non_terminal = self._table.at[self.top, self._lookahead.type]

                if non_terminal:
                    self._log.debug('[{}]{}::{} → {}'.format(self._lookahead.location, 'INFO',
                                                             self.top, ' '.join(non_terminal)))
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
        self.top = 'Start'
        self._stack = [self.top]
        self.nodes = []
        self._lookahead = None
        self._iterator = None

        self.productions = []
        self.ast = None

    @classmethod
    def load(cls, file_handler: logging.FileHandler = None, config_dir: str = './_config/'):
        ll1, vitals = ucal.load(config_dir=config_dir, online=False)
        follow = vitals['follow set']
        terminals = ll1.columns
        non_terminals = ll1.index

        ops = _OPS.copy()
        ops.update([(x, _OPS['NEW']) for x in filter(lambda x: 'NEW' in x, non_terminals.to_list())])
        ops.pop('NEW')

        logger = logging.getLogger(str(uuid.uuid4()))
        logger.setLevel(logging.CRITICAL)

        if file_handler:
            logger.addHandler(file_handler)
            logger.setLevel(file_handler.level)

        return cls(ll1, follow, terminals, non_terminals, ops, logger)
