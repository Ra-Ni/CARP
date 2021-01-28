import uuid

class State_Table:
    def __init__(self):
        self.start = str(uuid.uuid4())
        self.final = str(uuid.uuid4())
        self.transition_function = {}

    def print(self):
        for k, v in self.transition_function.items():
            print('{}: {}'.format(k, v))

    @classmethod
    def from_token(cls, token):
        table = cls()
        table.transition_function[table.start] = {token: [table.final]}
        return table

    @classmethod
    def concat(cls, x, y):
        table = cls()
        table.transition_function.update(x.transition_function)
        table.transition_function.update(y.transition_function)
        x_final = table.transition_function.setdefault(x.final, {})
        y_final = table.transition_function.setdefault(y.final, {})
        table_start = table.transition_function.setdefault(table.start, {})

        x_final[None] = [y.start]
        table_start[None] = [x.start]
        y_final[None] = [table.final]
        return table

    @classmethod
    def union(cls, x, y):
        table = cls()
        table.transition_function.update(x.transition_function)
        table.transition_function.update(y.transition_function)
        x_final = table.transition_function.setdefault(x.final, {})
        y_final = table.transition_function.setdefault(y.final, {})
        table_start = table.transition_function.setdefault(table.start, {})

        x_final[None] = [table.final]
        table_start[None] = [x.start, y.start]
        y_final[None] = [table.final]
        return table

    @classmethod
    def
class Node:
    def __init__(self):
        self.transitions = {}

    def add(self, next_node, input=None):
        dict_next = self.transitions.setdefault(input, [])
        dict_next.append(next_node)


def node_init(x: chr) -> list:
    start, end = Node(), Node()
    start.add(end, x)
    return [start, end]


def node_concatenate(x: list, y: list) -> list:
    start, end = Node(), Node()
    start.add(x[0])
    x[1].add(y[0])
    y[1].add(end)
    return [start, end]


def node_or(x: list, y: list) -> list:
    start, end = Node(), Node()
    start.add(x[0])
    start.add(y[0])
    x[1].add(end)
    y[1].add(end)
    return [start, end]


def node_kleene(x: list) -> list:
    start, end = Node(), Node()
    start.add(x[0])
    start.add(end)
    x[1].add(x[0])
    x[1].add(end)
    return [start, end]

def to_table(x: Node):
    print(uuid.uuid4(), type(uuid.uuid4()))