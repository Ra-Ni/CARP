import uuid

import pandas as pd

from _config import CONFIG
from lex import Scanner
from syntax import Parser, AST, Node

EXAMPLE = '../examples/syntax/polynomial.src'

labels = ['name', 'kind', 'type', 'visibility', 'link']
new_label = ('kind', 'type', 'visibility', 'link')


class Table:
    def __init__(self):
        self.name = ''
        self.uuid = uuid.uuid4()
        self.annotations = {}
        self.table = pd.DataFrame(columns=labels)
        self.type = ''

    def as_entry(self):
        pass


class Label:
    def __init__(self):
        self.annotations = {}
        self.frame = pd.DataFrame()

    def __str__(self):
        txt = ''
        for key, value in self.annotations.items():
            txt += key + ': ' + value + '\n'

        return self.frame.to_string() + '\n\n' + txt


def Class(node: Node):
    name = node.children[0].label
    inherits = node.children[1].label
    declarations = node.children[2:]

    label = Label()
    label.annotations['name'] = name
    label.annotations['inherits'] = inherits
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
        decl = func_decl(node.children[1])
        decl['visibility'] = visibility
        node.parent.label.frame = node.parent.label.frame.append(decl, ignore_index=True)
        node.parent.children.remove(node)


def func_decl(node: Node):
    binding = node.children[0].label if node.children[0].label != 'ε' else ''
    name = node.children[1].label
    params = node.children[2]
    return_type = node.children[3].label
    body = None # todo fix

    label = Label()
    label.annotations['binding'] = binding
    label.annotations['name'] = name
    label.frame = parameters(node.children[2])
    s = label.frame['type'].to_list()
    s = ', '.join(s)
    return pd.Series(data=[name, 'function', s, None, label], index=labels)


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

if __name__ == '__main__':
    scanner = Scanner.load(EXAMPLE, suppress_comments=1)
    syntax_analyzer = Parser.load()
    response = syntax_analyzer.parse(scanner)
    ast = syntax_analyzer.ast
    for node in ast.bfs():
        if node.label == 'class':
            Class(node)
        elif node.label == 'declaration':
            declaration(node)

    ast.render('test.png')
