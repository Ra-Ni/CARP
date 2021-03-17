from syntax import Node
from lex import scanner


class Expr:
    def __init__(self, pattern: str):
        self.pattern = pattern

    def match(self, test):
        return self.pattern == test.top

    def apply(self, test):
        raise NotImplementedError


class New(Expr):
    def __init__(self):
        super().__init__('NEW_')
        self.index = len(self.pattern)

    def match(self, test):
        return self.pattern in test.top

    def apply(self, test):
        test.node_stack.append(Node(test.top[self.index:]))


class Push(Expr):
    def __init__(self):
        super().__init__('PUSH')

    def apply(self, test):
        test.node_stack.append(Node(test.productions[-1].type))


class Pop(Expr):
    def __init__(self):
        super().__init__('POP')

    def apply(self, test):
        test.node_stack.pop()


class Unary(Expr):
    def __init__(self):
        super().__init__('UNARY')

    def apply(self, test):
        second = test.node_stack.pop()
        first = test.node_stack.pop()

        first.adopt(second)
        test.node_stack.append(first)


class IUnary(Expr):
    def __init__(self):
        super().__init__('UNARY')

    def apply(self, test):
        second = test.node_stack.pop()
        first = test.node_stack.pop()

        second.adopt(first)
        test.node_stack.append(second)


class Chk(Expr):
    def __init__(self):
        super().__init__('CHK')

    def apply(self, test):
        if not test.node_stack[-1].children:
            test.node_stack[-1].label = 'ε'


class Nop(Expr):
    def __init__(self):
        super().__init__('NOP')

    def apply(self, test):
        test.node_stack.append(Node('ε'))


class Bin(Expr):
    def __init__(self):
        super().__init__('BIN')

    def apply(self, test):
        second = test.node_stack.pop()
        op = test.node_stack.pop()
        first = test.node_stack.pop()

        op.adopt(first, second)
        test.node_stack.append(op)


class Test:
    def __init__(self, table, follow, terminals, logger):
        self.table = table
        self.follow = follow
        self.terminals = terminals

        self.lookahead = None
        self.iterator = None
        self.log = logger

        self.error = False
        self.productions = []

        self.top = 'Start'

        self.stack = [self.top]
        self.node_stack = []
        self.ops = [New(), Push(), Pop(), Unary(), IUnary(), Chk(), Nop(), Bin()]

    def _recover(self):
        self.error = True

        if self.top not in self.terminals:
            follow = self.follow.loc[self.top] or []
            series = self.table.loc[self.top].dropna().index

            msg = str(set(series))
            location = self.lookahead.location
            label = self.lookahead.type

            if self.lookahead and self.lookahead.type in follow:
                self.stack.pop()
            else:
                while self.lookahead and self.lookahead.type not in series:
                    self.lookahead = next(self.iterator, None)

                location = str(location) + (('-' + str(self.lookahead.location)) if self.lookahead else '')

        else:
            msg = self.top
            location = self.lookahead.location
            label = self.lookahead.type

            self.stack.pop()

        self.log.error('[{}]{}::Invalid Syntax {} not in {}'.format(location, 'ERROR', label, msg))

    def parse(self, reader: scanner):

        self.reset()
        self.iterator = iter(reader)
        self.lookahead = next(self.iterator, None)

        while self.stack and self.lookahead:

            self.top = self.stack[-1]
            f = None
            for i in self.ops:
                if i.match(self):
                    f = i
                    break
            if f:
                f.apply(self)
                self.stack.pop()
                continue

            if self.top == 'ε':
                self.stack.pop()

            elif self.top in self.terminals:
                if self.top == self.lookahead.type:
                    self.productions.append(self.lookahead)
                    self.stack.pop()

                    self.lookahead = next(self.iterator, None)
                else:
                    self._recover()

            else:

                non_terminal = self.table.at[self.top, self.lookahead.type]

                if non_terminal:
                    self.log.debug('[{}]{}::{} → {}'.format(self.lookahead.location, 'INFO',
                                                            self.top, ' '.join(non_terminal)))
                    self.stack.pop()
                    if ['ε'] != non_terminal:
                        self.stack.extend(non_terminal[::-1])

                else:
                    self._recover()


        return not (self.lookahead or self.stack or self.error), self.productions

    def reset(self):
        self.productions = []
        self.lookahead = None
        self.iterator = None
        self.top = 'Start'
        self.stack = [self.top]
        self.node_stack = []
        self.error = False
