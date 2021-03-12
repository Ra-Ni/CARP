import logging
import uuid

from collections import deque

import pydot

class State:
    def __init__(self, state):
        self.state = state
        self.left_most = None
        self.right = None
        self.left = None
        self.parent = None
        self._uid = uuid.uuid4()

    @staticmethod
    def make_siblings(first, *other):
        if not first.left_most:
            first.left_most = first
        current = first

        for second in other:
            current.right = second
            second.left = current
            second.parent = current.parent
            second.left_most = current.left_most

    @staticmethod
    def make_family(first, ):
    def __iter__(self):

        while :
            yield child




class Node:
    def __init__(self, label: str, parent=None):
        self.label = label
        self.children = []
        self.parent = parent
        self._uid = uuid.uuid4()

        if isinstance(parent, Node):
            self.parent.children.append(self)

    @property
    def uid(self):
        return str(self._uid)

    def __hash__(self):
        return hash(self._uid)

    def __eq__(self, other):
        return isinstance(other, Node) and self._uid == other._uid

    def __lt__(self, other):
        return isinstance(other, Node) and self._uid < other._uid

    def __str__(self):
        return self.label

    def apply(self, *args: str):
        for arg in args:
            _SYS[arg](self)

    def adopt(self, *children) -> None:

        for child in children:
            node = child
            if isinstance(child, str):
                node = Node(child)
            self.children.append(node)
            node.parent = self

    def remove(self):
        index = self.parent.children.index(self)
        left = self.parent.children[:index]
        right = self.parent.children[index + 1:]
        middle = self.children
        self.parent.children = left + middle + right
        for child in self.children:
            child.parent = self.parent


def difference(first: str, second: str):
    return sum(0 if i[0] == i[1] else 1 for i in zip(first, second)) + abs(len(first) - len(second))

def bfs(root):
    queue = deque([root])
    while queue:
        node = queue.popleft()
        queue.extend(node.children)
        yield node


def _adopt(root, *children) -> None:
    for child in children:
        child.parent = root
        root.children.append(child)


def _new(root, label: str) -> None:
    if label == 'Var':
        print('hi ')
    second = root.children.pop()
    first = root.children.pop()

    other = Node(label, root)
    _adopt(other, first, second)


def _deny(root) -> None:
    child = root.children.pop()
    child.parent = None


def _unary(root) -> None:
    first = root.children.pop()
    op = root.children.pop()

    _adopt(op, first)
    root.children.append(op)


def _binary(root) -> None:
    second = root.children.pop()
    op = root.children.pop()
    first = root.children.pop()

    _adopt(op, first, second)

    root.children.append(op)


def _scope(root):
    spec = root.children.pop()
    first = root.children.pop()

    root.children.append(spec)
    root.children.append(first)


def _root(root):
    first = root.children[0]
    children = root.children[1:]
    root.children = []

    _adopt(first, *children)
    _adopt(root, first)


def remove_duds(root):
    duds = {
        'lcurbr', 'rcurbr',
        'lpar', 'rpar',
        'lsqbr', 'rsqbr',
        'sr',
        'colon',
        'dot',
        'semi',
        'qm',
        'inherits',
        'comma',
        'class',
        'main',
        'then',
        'else'
    }

    nodes = filter(lambda x: x.label in duds, bfs(root))

    for node in nodes:
        node.remove()


def remove_dups(root):
    reverse_bfs = list(bfs(root))[1:]
    reverse_bfs.reverse()

    for node in reverse_bfs:
        if difference(node.parent.label, node.label) <= 1:
            node.remove()


def _flatten_recursion(root):
    if root.parent and difference(root.label, root.parent.label) <= 1:
        root.__dict__.update(root.parent)

        root.parent.__dict__()
        root.parent.children.pop()

        root.children = root.parent.children
        root.parent = root.parent.parent
        # root.remove()

        # root.parent.children.pop()
        # root.children = root.parent.children
        # root.parent = root.parent.parent
        # root.parent.parent.children



def draw(src: str, root):
    graph = pydot.Dot('AST', graph_type='digraph')
    nodes = {}
    for node in bfs(root):
        label = node.label
        if label != 'ε' and len(label) == 1:
            label += ' '
        nodes[node.uid] = pydot.Node(node.uid, label=str(label))
        graph.add_node(nodes[node.uid])

        if node.parent:
            pid = node.parent
            graph.add_edge(pydot.Edge(nodes[pid.uid], nodes[node.uid]))
    graph.write_png(src, encoding='utf-8')


_SYS = {
    'Sys(deny)': _deny,
    'Sys(binary)': _binary,
    'Sys(unary)': _unary,
    'Sys(Var)': lambda _x: _new(_x, 'Var'),
    'Sys(FCall)': lambda _x: _new(_x, 'FCall'),
    'Sys(root)': _root,
    'Sys(scope)': _scope
}

class NodeBuilder:
    def __init__(self):
        self.routines = [_flatten_recursion]

    def build(self, root: Node, *children: str):
        nodes = []
        for child in children:
            node = Node(child, root)
            for routine in self.routines:
                routine(node)
            nodes.append(node)
        return nodes