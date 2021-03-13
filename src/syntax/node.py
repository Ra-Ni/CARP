import logging
import uuid

from collections import deque

import pydot

from lex import token



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


class Routine:
    def apply(self, root):
        raise NotImplementedError

class RecursionHandler(Routine):
    def apply(self, root):
        if root.parent and difference(root.label, root.parent.label) <= 1:
            root.parent.children.pop()

            root.children = root.parent.children
            root._uid = root.parent._uid
            root.parent = root.parent.parent

            # root.remove()

            # root.parent.children.pop()
            # root.children = root.parent.children
            # root.parent = root.parent.parent
            # root.parent.parent.children
class BinaryOpHandler(Routine):
    def __init__(self):
        self.ops = {
            '+',
            '-',
            'and',
            '*',
            '='
        }
    def apply(self, root):
        if root.label in self.ops:
            root.parent.label = root.label
            root.remove()
            return True
        return False

class EpsilonHandler(Routine):
    def apply(self, root):
        if root.label == 'ε':
            root.parent.children.pop()
            if all(x.label == 'ε' for x in root.parent.children):
                root.parent.label = 'ε'
                self.apply(root.parent)
            return True
        return False


class DudHandler(Routine):
    def __init__(self):
        self._duds = {
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
            'else',
            'var'
        }

    def apply(self, root):
        if root.label in self._duds:
            root.parent.children.pop()
            root.parent = None


class ADOPTHandler(Routine):

    def apply(self, root):
        if root.label == 'ADOPT':

            root.parent.children.pop()
            first = root.parent.children.pop()
            second = root.parent.children.pop()

            first.adopt(second)
            root.parent.adopt(first)
            root.label = 'ε'
            root.parent = None

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
        self.prebuilds = []
        self.postbuilds = []
    def postbuild(self, root: Node):
        for routine in self.postbuilds:
            if routine.apply(root):
                break



    def build(self, root: Node, *children: str):
        nodes = []
        for child in children:
            if child in {'MultOp'}:
                print('yhes')
            node = Node(child, root)
            for routine in self.prebuilds:
                routine.apply(node)
            nodes.append(node)
        return nodes


