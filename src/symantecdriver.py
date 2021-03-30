import uuid
from collections import deque

import pandas as pd
import pydot

from lex import Scanner
from symantec.label import Label, labels, nlabels
from syntax import Parser, AST, Node

EXAMPLE = '../examples/syntax/polynomial_correct.src'

new_label = ('kind', 'type', 'visibility', 'link')


def dimensions(node: Node):
    node.label = '[' + ']['.join(x.label for x in node.children) + ']'
    node.children = []


def inherits(node: Node):
    node.label = [x.label for x in node.children]
    node.children = []


def List(node: Node):
    node.parent.children.remove(node)
    for child in node.children:
        child.parent = node.parent
        node.parent.children.append(child)

    node.children = []


def Class(node: Node):
    name = node.children[0].label
    link = [node.children[2]]

    if not isinstance(node.children[2].label, pd.DataFrame):
        node.children[2].label = pd.DataFrame()

    if node.children[1].label != 'ε':
        link.extend(node.children[1].label)

    node.label = pd.Series(['class', None, None, link], index=nlabels, name=name)
    node.children = []


def declaration(node: Node):
    visibility = node.children[0].label
    label = node.children[1].label

    label['visibility'] = visibility
    index = node.parent.children.index(node)
    node.parent.children[index] = node.children[1]
    node.children[1].parent = node.parent
    node.children = []


def declarations(node: Node):
    node.label = pd.DataFrame([x.label for x in node.children])
    node.children = []


def var(node: Node):
    node.label = pd.DataFrame([x.label for x in node.children], columns=nlabels)

    node.children = []


def func_decl(node: Node):
    name = node.children[1].label
    if node.children[0].label != 'ε':
        name = node.children[0].label + '::' + name

    if not isinstance(node.children[2].label, pd.DataFrame):
        node.children[2].label = pd.DataFrame(columns=nlabels)
        params = ''
    else:
        params = ', '.join(node.children[2].label['type'])
    params += ' : ' + node.children[3].label

    if not isinstance(node.children[4].label, pd.DataFrame):
        node.children[4].label = pd.DataFrame(columns=nlabels)

    node.children[4].label = node.children[4].label.append(node.children[2].label)

    node.label = pd.Series(['function', params, None, [node.children[4]]], index=nlabels, name=name)
    node.children = []


def Main(node: Node):
    node.label = pd.Series(['function', None, None, node.children], index=nlabels, name='main')

    node.children = []


def parameters(node: Node):
    node.label = pd.DataFrame([x.label for x in node.children], columns=nlabels)
    node.label['kind'] = ['parameter'] * len(node.label['type'])

    node.children = []


def var_decl(node: Node):
    name = node.children[1].label
    typedef = node.children[0].label

    if node.children[2].label != 'ε':
        typedef += '[' + ']['.join(filter(lambda x: x.label != 'ε', node.children[2].children)) + ']'

    node.label = pd.Series(data=['variable', typedef, None, None],
                           index=['kind', 'type', 'visibility', 'link'],
                           name=name)

    node.children = []


def body(node: Node):
    node.label = pd.DataFrame(columns=nlabels)
    if node.children and isinstance(node.children[0].label, pd.DataFrame):
        node.label = node.label.append(node.children[0].label)
        node.children.pop(0)


def empty(node: Node, name):
    node.label = Label()

    node.label.frame = pd.DataFrame(columns=['kind', 'type', 'visibility', 'link'])
    node.label.series = pd.Series(index=node.label.frame.columns, name=name, dtype='object')


def prog(node: Node):
    node.label = pd.DataFrame(columns=nlabels)
    node.label = node.label.append([x.label for x in node.children])
    node.children = []


SYS = {

    'var_decl': var_decl,
    'parameters': parameters,
    'func': func_decl,
    'declaration': declaration,
    'declarations': declarations,
    'inherits': inherits,
    'class': Class,
    'ClassList': List,
    'FuncDefList': List,
    'body': body,
    'var': var,
    'main': Main,
    'Prog': prog,
    'DimList': dimensions
}

def function_parse(node: Node):
    functions = node.label.filter(regex='.*::.*', axis=0)
    #todo complete this because we want to bind functions.


def render(node: Node, src: str):
    queue = deque([node])
    graph = pydot.Dot('AST', graph_type='digraph')
    nodes = {}

    while queue:
        node = queue.pop()
        nodes[node.uid] = pydot.Node(node.uid, label=str(node.label))
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

    render(ast.root, 'test.png')
