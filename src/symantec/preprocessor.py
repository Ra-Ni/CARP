import logging
import re

from collections import deque

import pandas as pd
from tabulate import tabulate

from syntax import Node


def delete(*nodes: Node):
    for node in nodes:
        if node.parent:
            node.parent.children.remove(node)
        del node


def _duplicated_variables(table: pd.DataFrame):
    v = table.index[table['kind'] == 'variable']
    v = v.append(table.index[table['kind'] == 'parameter'])
    v = v.to_list()

    return len(v) != len(set(v))


def _duplicated_functions(table: pd.DataFrame):
    f = table[table['kind'] == 'function']['type']
    f = f.index + ' ' * len(f.index) + f.values

    return len(f) != len(set(f))


def _tabulate(table: pd.DataFrame):
    return str(tabulate(table, headers='keys', tablefmt='github', numalign='left', floatfmt=',1.5f'))


def _group(node: Node):
    data = pd.DataFrame([x.to_series() for x in node.children])
    data = [data]

    if 'table' in node.parent:
        data.append(node.parent['table'])

    data = pd.concat(data)
    data.where(data.notnull(), None, inplace=True)
    node.parent['table'] = data

    # node.parent.children.remove(node)



def variable(node: Node):
    if 'type' in node:
        dimensions = re.findall(r'\[([0-9]*)]', node['type'])
        if dimensions:
            node['dimensions'] = dimensions
            node['type'] = node['type'][:node['type'].index('[')] + '[]' * len(node['dimensions'])
            node.blacklist('dimensions')

    node.override('__eq__',
                  lambda x:
                  x['type'] == node['type'] and \
                  x['kind'] == node['kind'])


def index(node: Node):
    if any([x['type'] != 'integer' for x in node.children]):
        raise TypeError(f'Array indices "{",".join(x["name"] for x in node.children)}" is not of type integer')

    node.parent['index'] = [int(x['name']) for x in node.children]
    node.parent.blacklist('index')
    delete(*node.children, node)


def function(node: Node):
    if 'return' not in node:
        return

    node['type'] = ' : ' + node['return']

    if '::' in node['name']:
        node['link'] = node

    if 'table' in node:
        table = node['table']
        parameters = ', '.join(table[table['kind'] == 'parameter']['type'])
    else:
        node['table'] = pd.DataFrame()
        parameters = ''

    node['link'] = node
    node['type'] = parameters + ' : ' + node['return']
    node.drop('return')
    node.blacklist('table')
    node.override('__eq__',
                  lambda x:
                  isinstance(x, Node) and \
                  x['name'] == node['name'] and \
                  x['type'] == node['type'] and \
                  x['kind'] == node['kind'])


def Class(node: Node):
    if 'inherits' in node:
        node['inherits'] = set(node['inherits'].split(', '))

    node['link'] = node
    if 'table' not in node:
        node['table'] = pd.DataFrame(columns=['kind', 'type', 'visibility', 'link'])
    table = node['table']

    table['link'] = [None] * len(table.index)

    node.blacklist('table', 'inherits')
    node.override('__eq__',
                  lambda x:
                  isinstance(x, Node) and \
                  x['name'] == node['name'] and \
                  x['kind'] == node['kind'])


def body(node: Node):
    data = []
    if 'table' in node.parent:
        data.append(node.parent['table'])

    if 'table' in node:
        data.append(node['table'])

    data.append(pd.DataFrame([['body', node]], index=['body'], columns=['kind', 'link']))

    data = pd.concat(data)
    data.where(data.notnull(), None, inplace=True)

    node.parent['table'] = data

    node.drop('table')
    node.parent.children.remove(node)



def _has_duplicates(table: pd.DataFrame):
    return _duplicated_functions(table) or _duplicated_variables(table)


def _inheritance_handler(node: Node):
    table = node['table']
    buffer = deque(table['link'][table['kind'] == 'class'].to_list())
    defined = set()
    while buffer:
        length = len(buffer)

        for _ in range(length):

            first = buffer.popleft()

            if 'inherits' in first and not first['inherits'].difference(defined):
                frame = pd.concat([table.loc[x]['link']['table'] for x in first['inherits']])
                if _has_duplicates(frame):
                    raise TypeError(f'Duplicates found while processing:\r\n{_tabulate(frame)}')

                for name, series in frame.iterrows():
                    if name in first['table'].index and series['type'] == first['table'].loc[name]['type']:
                        print('Overriding or overloading')
                    else:
                        first['table'] = first['table'].append(series)

                first.drop('inherits')

            if 'inherits' not in first:
                defined.add(first['name'])

                _func_handler(first, table)
            else:
                buffer.append(first)

        if length == len(buffer):
            raise TypeError(f'Cyclic dependency detected while processing: {", ".join(b["name"] for b in buffer)}')


def _func_handler(node: Node, table: pd.DataFrame):
    funcs = table[table['kind'] == 'function']['link'].to_list()
    funcs = list(filter(lambda x: x is not None, funcs))
    if not funcs:
        return


    func_overrides = list(filter(lambda x: '::' in x['name'] and x['name'].split('::')[0] == node['name'], funcs))

    for func_def in func_overrides:
        class_name, func_name = func_def['name'].split('::')
        if func_name not in node['table'].index:
            raise TypeError(f'No function "{func_name}" exists for class "{class_name}"')

        func_reference = node['table'].loc[func_name]

        if isinstance(func_reference, pd.DataFrame):
            func_reference = func_reference.loc[func_reference['type'] == node['type']]
            if func_reference.empty:
                raise TypeError(f'No function "{func_name}" exists for class "{class_name}"')


        table.drop(index=func_def['name'], inplace=True)
        func_reference['link'] = func_def
        func_def['name'] = func_name
        node.adopt(func_def)


def _bfs(root: Node):
    queue = deque([root])

    while queue:
        parent = queue.popleft()
        if 'table' in parent and 'link' in parent['table'].columns:

            children = list(filter(lambda x: x is not None, parent['table']['link'].to_list()))
            queue.extend(children)
        yield parent


def prog(node: Node):
    for link in node['table']['link']:
        if link:
            node.adopt(link)

    if _has_duplicates(node['table']):
        raise TypeError(f'Duplicates detected in table:\r\n{_tabulate(node["table"])}')

    node['name'] = 'prog'
    _inheritance_handler(node)

    defaults = node['table'].index.to_list() + ['void', 'float', 'integer', 'string']
    defaults.remove('main')

    for node in _bfs(node):
        if 'table' in node:
            for name, series in node['table'].iterrows():
                if series['kind'] == 'function':
                    types = series['type'].split(' : ')
                    t = types.pop(0).split(', ')
                    if isinstance(t, str):
                        types.append(t)
                    else:
                        types.extend(t)

                    for t in types:
                        t = t.replace('[]', '')
                        if t not in defaults:
                            raise TypeError(f'type "{t}" in "{name}" undefined in "{node["name"]}"')
                    if series['link'] is None:
                        raise ReferenceError(f'function "{name}" undefined in class "{node["name"]}"')
                elif series['type'] and series['type'].replace('[]', '') not in defaults:
                    raise TypeError(f'type "{series["type"]}" in "{name}" undefined in "{node["name"]}"')


def main(node: Node):
    node['name'] = 'main'

    node['link'] = node

    node.blacklist('table')

    del node


SYS = {
    'log': logging.getLogger('test'),
    # 'prog': prog,
    'group': _group,
    # 'function': function,
    # 'body': body,
    # 'parameter': variable,
    # 'variable': variable,
    # 'index': index,
    # 'class': Class,
    # 'main': main,
}
