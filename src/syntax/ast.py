from collections import deque
import pydot


from .node import Node


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
            label = node.to_string()

            nodes[node.uid] = pydot.Node(node.uid, label=label.replace('\r\n', '\l'))
            graph.add_node(nodes[node.uid])

            if node.parent:
                pid = node.parent
                graph.add_edge(pydot.Edge(nodes[pid.uid], nodes[node.uid]))
        graph.write_png(src, encoding='utf-8')
