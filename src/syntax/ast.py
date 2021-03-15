from collections import deque, OrderedDict
import pydot

from syntax.node import Node


def _difference(first, second):
    return sum(0 if i[0] == i[1] else 1 for i in zip(first, second)) + abs(len(first) - len(second))


def _remove_recursions(tree):
    reverse_bfs = list(tree.bfs())
    reverse_bfs.reverse()
    for node in reverse_bfs:
        if node.parent and _difference(node.parent.label, node.label) <= 1:
            node.remove()


def _remove_epsilons(tree):
    reverse_bfs = list(tree.bfs())
    reverse_bfs.reverse()
    for node in reverse_bfs:
        if node.label == 'ε':
            if len(node.parent.children) == 1:
                node.parent.label = node.label
            node.remove()


def _terminals_to_root(tree):
    reverse_bfs = list(tree.bfs())
    reverse_bfs.reverse()
    for node in reverse_bfs:
        if not node.children and len(node.parent.children) == 1:
            node.parent.label = node.label
            node.remove()


def _remove_nonterminals(tree):
    for node in list(tree.bfs()):
        if node.parent and len(node.children) == 1:
            node.remove()


def _remove_duds(tree):
    duds = {'{', '}', '(', ')', ';', ',', '.', '::', ':', '[', ']'}

    for node in tree.bfs():
        if node.label in duds:
            node.remove()


_COMMANDS = OrderedDict({
    'remove_recursions': _remove_recursions,
    'remove_epsilons': _remove_epsilons,
    'terminals': _terminals_to_root,
    'remove_nonterminals': _remove_nonterminals,
    'remove_duds': _remove_duds
})

_COMMANDS['all'] = list(_COMMANDS.keys())


class AST:

    def __init__(self, root: Node):
        self.root = root

    def bfs(self):
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            queue.extend(node.children)
            yield node

    def render(self, src: str):
        graph = pydot.Dot('AST', graph_type='digraph')
        nodes = {}
        for node in self.bfs():
            label = node.label
            if label != 'ε':
                label += ' '
            nodes[node.uid] = pydot.Node(node.uid, label=str(label))
            graph.add_node(nodes[node.uid])

            if node.parent:
                pid = node.parent
                graph.add_edge(pydot.Edge(nodes[pid.uid], nodes[node.uid]))
        graph.write_png(src, encoding='utf-8')

    def apply(self, *commands: str):
        comms = _COMMANDS['all'] if 'all' in commands else commands

        for command in comms:
            _COMMANDS[command](self)
