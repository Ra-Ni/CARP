import uuid


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