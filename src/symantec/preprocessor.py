import pandas as pd

from syntax import Node

nlabels = ['kind', 'type', 'visibility', 'link']


def dimensions(node: Node):
    node.label = '[' + ']['.join(x.label for x in node.children) + ']'
    node.children = []


def inherits(node: Node):
    node.label = [x.label.lexeme for x in node.children]
    node.children = []


def List(node: Node):
    node.parent.children.remove(node)
    for child in node.children:
        child.parent = node.parent
        node.parent.children.append(child)

    node.children = []


def Class(node: Node):
    name = node.children[0].label.lexeme
    link = [node.children[2]]

    if not isinstance(node.children[2].label, pd.DataFrame):
        node.children[2].label = pd.DataFrame()

    if node.children[1].label != 'ε':
        link.extend(node.children[1].label)

    node.label = pd.Series(['class', None, None, link], index=nlabels, name=name)
    node.children = []


def declaration(node: Node):
    visibility = node.children[0].label.lexeme
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
    name = node.children[1].label.lexeme
    if node.children[0].label != 'ε':
        name = node.children[0].label.lexeme + '::' + name

    if not isinstance(node.children[2].label, pd.DataFrame):
        node.children[2].label = pd.DataFrame(columns=nlabels)
        params = ''
    else:
        params = ', '.join(node.children[2].label['type'])
    params += ' : ' + node.children[3].label.lexeme

    if not isinstance(node.children[4].label, pd.DataFrame):
        node.children[4].label = pd.DataFrame(columns=nlabels)

    node.children[4].label = node.children[2].label.append(node.children[4].label)

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
    name = node.children[1].label.lexeme
    typedef = node.children[0].label.lexeme

    if node.children[2].label != 'ε':
        typedef += '[' + ']['.join(filter(lambda x: x.label.lexeme != 'ε', node.children[2].children)) + ']'

    node.label = pd.Series(data=['variable', typedef, None, None],
                           index=['kind', 'type', 'visibility', 'link'],
                           name=name)

    node.children = []


def body(node: Node):
    node.label = pd.DataFrame(columns=nlabels)
    if node.children:
        if isinstance(node.children[0].label, pd.DataFrame):
            node.label = node.label.append(node.children[0].label)
            node.children.pop(0)


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
