import uuid

import pandas as pd

from _config import CONFIG
from lex import Scanner
from syntax import Parser, AST, Node

EXAMPLE = '../examples/syntax/polynomial.src'

INJECTIONS = {
    'aParams',
    'ClassList',
    'DataMember',
    'DimList',
    'Factor',
    'FCall',
    'fParam',
    'FParamList',
    'IndiceList',
    'MembList',
    'Prog',
    'StatBlock',
    'StatementList',
    'variable',
    'VarDecl',
    'FuncDefList',
    'VarDeclList',
    'FuncBody'
}

labels = ('name', 'kind', 'type', 'visibility', 'link')
new_label = ('kind', 'type', 'visibility', 'link')


class Table:
    def __init__(self):
        self.name = ''
        self.uuid = uuid.uuid4()
        self.inheritance = []
        self.table = pd.DataFrame(columns=['kind', 'type', 'visibility', 'link'])


def Class(node: Node):
    name = node.children[0].label


def func_decl(node: Node):
    name = node.children[0].label
    return_type = node.children[-1].label

    frame = pd.DataFrame(columns=['kind', 'signature'])
    if len(node.children) == 3:

        for argument in node.children[1].children:
            if argument.label == 'variable_decl':
                frame.append(variable_decl(argument))


def variable_decl(node: Node):
    signature = node.children[0].label
    name = node.children[1].label
    if len(node.children) == 3:
        signature += index(node.children[2])

    return pd.Series(data=['parameter', signature], index=['kind', 'signature'], name=name)


def index(node: Node):
    return '[' + ']['.join(x.label for x in node.children) + ']'


_OPS = {
    'declaration': declaration,
    'func': func,
    'variable_decl': variable_decl,
    'dimensions': dimensions
}

if __name__ == '__main__':
    scanner = Scanner.load(EXAMPLE, suppress_comments=1)
    syntax_analyzer = Parser.load()
    response = syntax_analyzer.parse(scanner)
    ast = syntax_analyzer.ast

    cols = ('name', 'kind', 'type', 'link')
    table = pd.DataFrame(columns=cols)
    table = table.append({'name': 1, 'type': 0, 'kind': 3, 'link': 0}, ignore_index=True)
    print(table)
