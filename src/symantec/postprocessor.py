import pandas as pd

from _config import CONFIG
from syntax import Node


def _search(node: Node, item: str = None):
    parent = node
    query = node['name']
    if item:
        query = item
    while True:
        if not parent:
            raise TypeError(f'"{query}" not found')

        if 'table' not in parent or query not in parent['table'].index:
            parent = parent.parent
            continue
        break

    return parent['table'].loc[query]['link']


def vv(node: Node):
    if 'type' in node:
        return

    parent = node
    while True:
        if not parent:
            raise TypeError(f'variable "{node["name"]}" not found')

        if 'table' not in parent or node['name'] not in parent['table'].index:
            parent = parent.parent
            continue

        node['type'] = parent['table'].loc[node['name']]['type']
        if 'index' in node:
            node['type'] = node['type'].replace('[]', '', len(node['index']))
        break


def multop(node: Node):
    first, second = node.children
    if first != second:
        raise TypeError(f'Multop values "{first["name"]}" and "{second["name"]}" are not of the same types')

    node['type'] = first['type']
    node.override('__eq__',
                  lambda x: first == second)


def addop(node: Node):
    multop(node)


def sign(node: Node):
    node['type'] = node.children[-1]['type']
    node['kind'] = node.children[-1]['kind']


def args(node: Node):
    node['signature'] = [x['type'] for x in node.children]


def function(node: Node):
    if 'type' not in node and node.children:
        node['signature'] = node.children[0]['signature']


def dot(node: Node):
    first, second = node.children


    reference = _search(first, first['type'])['table']

    if second['name'] not in reference.index:
        raise TypeError(f'Call for "{first["name"]}.{second["name"]}" inconsistent')

    series = reference.loc[second['name']]
    if second['kind'] != series['kind']:
        raise TypeError(f'signature not matched')
    if series['visibility'] == 'private':
        raise TypeError(f'"{series.name}" is private')

    if second['kind'] == 'variable':
        node['type'] = second['type']
    else:
        signature, returns = series['type'].split(' : ')
        node['type'] = returns
    node['kind'] = 'variable'


def assign(node: Node):
    first, second = node.children
    if first['type'] != second['type']:
        raise TypeError(f'not the same on assign')
    node['type'] = first['type']


def relop(node: Node):
    assign(node)

def returns(node: Node):
    node['type'] = node.children[0]['type']

    current = node
    while 'table' not in current:
        current = current.parent

    if current['return'] != node['type']:
        raise TypeError(f'return type in function "{current["name"]}" not consistent')

PHASE2 = {
    'variable': vv,
    'multop': multop,
    'sign': sign,
    'args': args,
    'function': function,
    'dot': dot,
    'addop': addop,
    'assign': assign,
    'relop': relop,
    'return': returns,

}
