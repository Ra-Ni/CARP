import pandas as pd

from _config import CONFIG
from syntax import Node


def search(node: Node, term):
    parent = node.parent

    while True:
        if not parent:
            raise ReferenceError(f'reference {term} not found')
        elif isinstance(parent.label, pd.DataFrame) and term in parent.label.index:
            break
        else:
            parent = parent.parent

    return parent, parent.label.loc[term]


def _to_types(*nodes: Node):
    return list(map(lambda x: x.label if isinstance(x.label, str) else x.label['type'], nodes))


def delete(node: Node):
    while node.children:
        del node.children[-1]
    node.children = []


def purge(node: Node):
    delete(node)
    if node.parent:
        node.parent.children.remove(node)

    del node


def wipe(node: Node):
    node.parent.label.drop(index=node.label, inplace=True)
    node.parent = None
    purge(node)


def var(node: Node):
    first, second = node.children
    _, first = search(node, first.label)
    second = len(second.children)
    dimension = first['type']
    dimension_size = dimension.count('[]')

    if second > dimension_size:
        msg = f'Variable of the form {first} called with index list of {second}'

    dimension = dimension.replace('[]', '') + '[]' * (dimension_size - second)
    node.label = first.copy()
    node.label['type'] = dimension
    delete(node)


def bin(node: Node):
    children = _to_types(*node.children)

    if any(children[0] != x for x in children):
        msg = f'Operation "{node.label}" on sequence ' \
              f'[{", ".join(children)}] is forbidden'
        raise TypeError(msg)

    node.label = children[0]
    delete(node)


def args(node: Node):
    children = _to_types(*node.children)
    node.label = ', '.join(children)

    delete(node)


def const(node: Node):
    first, second = node.children
    node.label = first.label
    delete(node)


def index(node: Node):
    if node.label == CONFIG['EPSILON']:
        node.label = ''
    else:
        node.label = '[]' * len(node.children)
        delete(node)


def call(node: Node):
    first, second = node.children
    first, second = first.label, second.label

    if isinstance(first, str):
        _, first = search(node, first)
        first = first.label

    if first['kind'] != 'function':
        msg = f'Function call on a variable "{first.name}" is illegal'
        raise TypeError(msg)

    parameters, returns = first['type'].split(' : ')

    if parameters != second:
        msg = f'Function call on "{first.name}" ' \
              f'with arguments signature of "{second}" ' \
              f'does not match function signature of "{parameters}"'
        raise TypeError(msg)

    node.label = returns
    delete(node)


def dot(node: Node):
    first, second = node.children
    name = first.label['type']

    _, first = search(node, name)
    first = first['link'].label
    second = second.label

    if not isinstance(second, str):
        second = second.name

    if second not in first.index:
        msg = f'variable or function "{second}" ' \
              f'not visible or existent in class "{name}"'
        raise TypeError(msg)

    node.label = first.loc[second]
    delete(node)


def return_type(node: Node):
    child = _to_types(*node.children)[0]
    parent = node.parent

    while not isinstance(parent.label, pd.DataFrame):
        parent = parent.parent

    link = parent
    parent = parent.parent.label
    parent = parent.loc[parent['link'] == link]
    parent = parent.squeeze()

    _, returns = parent['type'].split(' : ')

    if returns != child:
        msg = f'defined return of type "{child}" ' \
              f'does not match function "{parent.name}" ' \
              f'return type of "{returns}"'
        raise TypeError(msg)

    purge(node)


PHASE2 = {
    'var': var,
    'const': const,
    'return': return_type,
    'args': args,
    '-': bin,
    '*': bin,
    '+': bin,
    '/': bin,
    '<=': bin,
    '>=': bin,
    '=': bin,
    '<': bin,
    '>': bin,
    '.': dot,
    'call': call,
    'write': purge,
    'read': purge,
    'block': purge,
    'while': purge,
    'if': purge,
    'body': wipe,

}

