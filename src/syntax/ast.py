from collections import OrderedDict

import pydot

from syntax.node import Node


class AST:

    def __init__(self, parent: str = 'START'):

        self.root = Node(label=parent)
        self.stack = [self.root]
        self.nodes = OrderedDict({self.root.uid: self.root})

        self.blacklist = {'rpar', 'lpar', 'lcurbr', 'rcurbr', 'lsqbr', 'rsqbr', 'semi', 'then', 'else'}

    def render(self, src):
        graph = pydot.Dot('AST', graph_type='digraph')
        nodes = {}

        for uid, node in self.nodes.items():
            if node.parent:
                first = nodes.setdefault(uid, pydot.Node(uid, label=str(node)))
                second = nodes.setdefault(node.parent.uid, pydot.Node(node.parent.uid, label=str(node.parent)))
                graph.add_node(first)
                graph.add_node(second)
                graph.add_edge(pydot.Edge(node.parent.uid, uid))

        graph.write(src, format=src[src.rfind('.') + 1:])

    def add(self, node_label, parent, indexed=True):
        node = Node(label=node_label, parent=parent)
        if indexed:
            self.nodes[node.uid] = node
        return node

    def add_all(self, children: list):
        top = self.stack.pop()

        nodes = [self.add(child, top if child not in self.blacklist else None, child not in self.blacklist) for child in
                 children[::-1]]

        self.stack.extend(nodes[::-1])

    def pop(self):
        return self.stack.pop()

    def label_of(self, uid):
        return self.nodes[uid].label

    def peek(self):
        return self.stack[-1]

    def empty(self):
        return not self.stack

    def remove(self, uid):
        node = self.nodes[uid]
        for child in node.children:
            self.remove(child)

        if node.parent:
            node.parent.children.remove(self)

        del self.nodes[uid]

    def _epsilon_remove(self, node):

        if not node.children:
            parent = node.parent
            if node in parent.children:
                parent.children.remove(node)

            del self.nodes[node.uid]

            self._epsilon_remove(parent)

    def epsilon_remove(self):
        self._epsilon_remove(self.stack.pop())

    def minimize(self):
        filtered_dict = dict(filter(lambda x: not x[1].children, self.nodes.items()))
        for uid, node in filtered_dict.items():
            current = node
            parent = current.parent
            while parent and len(parent.children) == 1:
                del self.nodes[current.uid]
                parent.children.pop()
                parent.token = current.token
                parent.label = current.label
                current = parent
                parent = current.parent

        self._minimize_non_terminals()

    def _minimize_non_terminals(self):
        filtered_dict = dict(filter(lambda x: len(x[1].children) == 1 and x[1].parent, self.nodes.items()))
        for uid, node in filtered_dict.items():
            child = node.children.pop()
            parent = node.parent
            index = parent.children.index(node)
            parent.children[index] = child
            child.parent = parent
            del self.nodes[uid]
