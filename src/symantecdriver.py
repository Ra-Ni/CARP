import uuid

import pandas as pd

from _config import CONFIG
from lex import Scanner
from symantec.label import Label, labels
from syntax import Parser, AST, Node

EXAMPLE = '../examples/syntax/polynomial_correct.src'


new_label = ('kind', 'type', 'visibility', 'link')


def inherits(node: Node):
    if node.label == 'ε':
        return ''
    else:
        return repr([x.label for x in node.children])

def Class(node: Node):
    name = node.children[0].label
    inh = inherits(node.children[1])
    declarations = node.children[2:]

    label = Label()
    label.annotations['name'] = name
    label.annotations['inherits'] = inh
    label.annotations['kind'] = 'class'
    label.frame = pd.DataFrame(columns=labels)
    node.label = label

    node.children = node.children[2:]

def declaration(node: Node):
    visibility = node.children[0].label
    if node.children[1].label == 'var_decl':
        variable = var_decl(node.children[1])
        variable['visibility'] = visibility

        node.parent.label.frame = node.parent.label.frame.append(variable, ignore_index=True)
        node.parent.children.remove(node)
    else:
        func_decl(node.children[1])
        node.children[1].label.annotations['visibility'] = visibility
        node.label = node.children[1].label
        node.children = []


def func_decl(node: Node):
    binding = node.children[0].label if node.children[0].label != 'ε' else ''
    name = node.children[1].label
    params = node.children[2]
    return_type = node.children[3].label
    body = node.children[4]

    label = Label()
    label.annotations['binding'] = binding
    label.annotations['name'] = name
    label.annotations['return_type'] = return_type
    label.frame = parameters(node.children[2])
    node.label = label


    node.children = [node.children[4]]


def var(node: Node):
    frame = pd.DataFrame(columns=labels)
    for child in node.children:
        frame = frame.append(var_decl(child, 'variable'), ignore_index=True)

    node.children = []

    parent = node.parent
    while not isinstance(parent.label, Label):
        parent = parent.parent
    parent.label.frame = parent.label.frame.append(frame)
    node.parent.children.remove(node)


def funcDefList(node: Node):


    for child in node.children:
        func_decl(child)

def parameters(node: Node):
    frame = pd.DataFrame(columns=labels)

    for child in node.children:
        frame = frame.append(var_decl(child, 'parameter'), ignore_index=True)

    return frame

def var_decl(node: Node, kind='variable'):
    typedef = node.children[0].label
    var_name = node.children[1].label
    dims = dimensions(node.children[2])

    return pd.Series(data=[var_name, kind, typedef + dims, None, None], index=labels)

def dimensions(node: Node):
    if node.label == 'ε':
        return ''
    else:
        return '[' + ']['.join(filter(lambda x: x.label != 'ε', node.children)) + ']'

def Main(node: Node):
    node.label = Label()
    node.label.annotations['name'] = 'main'

if __name__ == '__main__':
    scanner = Scanner.load(EXAMPLE, suppress_comments=1)
    syntax_analyzer = Parser.load()
    response = syntax_analyzer.parse(scanner)
    ast = syntax_analyzer.ast
    nodes = list(filter(lambda x: len(x.children) > 0, ast.bfs()))
    nodes.reverse()


    for node in ast.bfs():
        if node.label == 'class':
            Class(node)
        elif node.label == 'main':
            Main(node)
        elif node.label == 'declaration':
            declaration(node)
        elif node.label == 'FuncDefList':
            funcDefList(node)
        elif node.label == 'var':
            var(node)
    ast.render('test.png')
