import uuid
from collections import deque
from operator import itemgetter

import pandas as pd
import pydot
from tabulate import tabulate

from lex import Scanner, Token
from symantec.label import labels, nlabels
from symantec.postprocessor import PHASE2
from symantec.preprocessor import SYS
from syntax import Parser, AST, Node

EXAMPLE = '../examples/syntax/polynomial_correct.src'

new_label = ('kind', 'type', 'visibility', 'link')


def render(node: Node, src: str):
    queue = deque([node])
    graph = pydot.Dot('AST', graph_type='digraph')
    nodes = {}

    while queue:
        node = queue.pop()
        label = str(node.label)
        if isinstance(node.label, pd.DataFrame):
            label = str(tabulate(node.label, headers='keys', tablefmt='psql'))
        nodes[node.uid] = pydot.Node(node.uid, label=str(label), labeljust='l', shape='box')
        graph.add_node(nodes[node.uid])

        if node.children:
            for c in node.children:
                d = nodes.setdefault(c.uid, pydot.Node(c.uid, label=str(c)))
                queue.append(c)
                graph.add_edge(pydot.Edge(nodes[node.uid], d))
        if isinstance(node.label, pd.DataFrame):
            children = node.label['link'].to_list()
            for c in children:
                if c is not None:
                    for child in c:
                        if isinstance(child, Node):
                            c = nodes.setdefault(child.uid, pydot.Node(child.uid, label=child.label.to_string()))
                            queue.append(child)
                            graph.add_edge(pydot.Edge(nodes[node.uid], c))

    graph.write_png(src, encoding='utf-8')


if __name__ == '__main__':
    scanner = Scanner.load(EXAMPLE, suppress_comments=1)
    syntax_analyzer = Parser.load()
    response = syntax_analyzer.parse(scanner)
    ast = syntax_analyzer.ast
    nodes = list(filter(lambda x: len(x.children) > 0, ast.bfs()))
    nodes.reverse()

    for node in nodes:
        if node.label in SYS:
            SYS[node.label](node)
        if isinstance(node.label, Token) and node.label.lexeme == node.label.type and node.label.lexeme in SYS:
            SYS[node.label.lexeme](node)

    # root = ast.root
    # roots = ast.root
    # function_parse(root)
    # inheritance(root)
    PHASE2['ROOT'] = ast.root
    #reference_fixer(root.label.loc['main']['link'][0])
    # reference_fixer(root.label.loc['POLYNOMIAL']['link'][0].label.loc['evaluate']['link'][0])
    render(ast.root, 'test.png')
