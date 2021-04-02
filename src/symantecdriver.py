import uuid
from collections import deque
from operator import itemgetter

import pandas as pd
import pydot
from tabulate import tabulate

from lex import Scanner, Token
from symantec.label import labels, nlabels
from symantec.postprocessor import PHASE2
from symantec.preprocessor import SYS, inheritance_check, function_binding
from syntax import Parser, AST, Node

EXAMPLE = '../examples/syntax/polynomial_correct.src'

new_label = ('kind', 'type', 'visibility', 'link')


def render(root: Node, src: str):

    graph = pydot.Dot('AST', graph_type='digraph')
    nodes = {}
    visited = set()
    for n in uniquebfs(root):
        if n.uid in visited:
            continue
        else:
            visited.add(n.uid)
        if isinstance(n.label, pd.DataFrame):
            label = str(tabulate(n.label, headers='keys', tablefmt='psql'))
        else:
            label = str(n.label)

        # label += f'\n\nid: {n.uid}\n\nparent: {"None" if not n.parent else n.parent.uid}'
        nodes[n.uid] = pydot.Node(n.uid, label=label)
        graph.add_node(nodes[n.uid])

        if n.parent:
            graph.add_edge(pydot.Edge(nodes[n.parent.uid], nodes[n.uid]))


    # while queue:
    #     child = queue.pop()
    #     cid = child.uid
    #
    #     if isinstance(child.label, pd.DataFrame):
    #         label = str(tabulate(child.label, headers='keys', tablefmt='psql'))
    #     else:
    #         label = str(child.label)
    #     nodes[cid] = pydot.Node(cid, label=str(label))
    #
    #     if child.parent:
    #         pid = child.parent.uid
    #         graph.add_edge(pydot.Edge(nodes[pid], nodes[cid]))
    #
    #     if isinstance(child.label, pd.DataFrame):
    #         children = child.label['link'].to_list()
    #         children = filter(lambda x: x is not None, children)
    #         queue.extend(children)
    #     else:
    #         queue.extend(reversed(child.children))

    #
    # while queue:
    #     parent, child = queue.pop()
    #
    #     if isinstance(child.label, pd.DataFrame):
    #         label = str(tabulate(child.label, headers='keys', tablefmt='psql'))
    #     else:
    #         label = str(child.label)
    #
    #     label += f'\n\nid: {child.uid}\n\nparent: {"None" if not child.parent else child.parent.uid}'
    #     pydot_child = nodes.setdefault(child.uid, pydot.Node(child.uid, label=label))
    #     graph.add_node(pydot_child)
    #
    #     if parent:
    #         graph.add_edge(pydot.Edge(parent, pydot_child))
    #
    #     if isinstance(child.label, pd.DataFrame):
    #
    #         for index, series in child.label.iterrows():
    #             if series['link'] is not None:
    #                 queue.append((pydot_child, series['link']))
    #
    #     else:
    #         entries = []
    #         for descendant in child.children:
    #             entries.append((nodes[child.uid], descendant))
    #         entries.reverse()
    #         queue.extend(entries)
    graph.write_png(src, encoding='utf-8')

def uniquebfs(node: Node):
    queue = deque([node])
    visited = set()
    while queue:
        parent = queue.pop()
        if parent.uid in visited:
            continue

        visited.add(parent.uid)
        if isinstance(parent.label, pd.DataFrame):
            children = parent.label['link'].to_list()
            children = list(filter(lambda x: x is not None, children))
            queue.extend(reversed(children))
        else:
            queue.extend(reversed(parent.children))
        yield parent


def bfs(node: Node):
    queue = deque([node])

    while queue:
        parent = queue.pop()

        if isinstance(parent.label, pd.DataFrame):
            children = parent.label['link'].to_list()
            children = list(filter(lambda x: x is not None, children))
            queue.extend(reversed(children))
        else:
            queue.extend(reversed(parent.children))
        yield parent





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
    function_binding(ast.root)
    inheritance_check(ast.root)

    nodes = list(filter(lambda x: isinstance(x.label, str), bfs(ast.root)))
    nodes.reverse()
    visited = set()
    for node in nodes:
        if node.uid in visited:
            continue
        visited.add(node.uid)


        if node.label in PHASE2:
            PHASE2[node.label](node)
        if isinstance(node.label, Token) and node.label.lexeme == node.label.type and node.label.lexeme in SYS:
            PHASE2[node.label.lexeme](node)
    #reference_fixer(root.label.loc['main']['link'][0])
    # reference_fixer(root.label.loc['POLYNOMIAL']['link'][0].label.loc['evaluate']['link'][0])
    render(ast.root, 'test.png')
