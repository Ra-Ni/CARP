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


def _has_duplicates(frame: pd.DataFrame) -> bool:
    frame['name'] = frame.index
    v = frame[frame['kind'] != 'function'].filter(['name'])
    v = v.index[v.index.duplicated()]

    f = frame[frame['kind'] == 'function'].filter(['type', 'name'])
    f = f.index[f.duplicated()]

    is_duplicate = False
    for i in [v, f]:
        if not i.empty:
            SYS['log'].error(f'ERROR::DUPLICATION::{",".join(i.to_list())}')
            frame.drop(index=i, inplace=True)
            is_duplicate = True

    frame.drop('name', 1, inplace=True)
    return is_duplicate


def _tabulate(table: pd.DataFrame):
    return str(tabulate(table, headers='keys', tablefmt='github', numalign='left', floatfmt=',1.5f'))


def _group(node: Node):
    data = pd.DataFrame([x.to_series() for x in node.children])
    data.where(data.notnull(), None, inplace=True)
    _has_duplicates(data)
    node['table'] = data


def _variable(node: Node):
    if 'type' in node:
        dimensions = re.findall(r'\[([0-9]*)]', node['type'])
        if dimensions:
            node['dimensions'] = dimensions
            node['type'] = node['type'][:node['type'].index('[')] + '[]' * len(node['dimensions'])
            node.blacklist('dimensions')


def _index(node: Node):
    if any([x['type'] != 'integer' for x in node.children]):
        SYS['log'].error(f'Array indices "{",".join(x["name"] for x in node.children)}" is not of type integer')
    else:
        node.parent['index'] = [int(x['name']) for x in node.children]
        node.parent.blacklist('index')
    delete(*node.children, node)


def _function(node: Node):
    if 'return' not in node:
        return

    if 'table' not in node:
        node['table'] = pd.DataFrame(columns=['kind', 'type', 'visibility', 'link'])

    if node.children and node.children[0]['kind'] == 'group':
        child = node.children.pop(0)
        table = pd.concat([node['table'], child['table']])
        table.where(table.notnull(), None, inplace=True)
        node['table'] = table
        _has_duplicates(node['table'])
        del child

    table = node['table']
    table = table[table['kind'] == 'parameter']['type']
    parameters = ', '.join(table)

    node['link'] = node
    node['type'] = parameters + ' : ' + node['return']
    node.drop('return')
    node.blacklist('table')


def _class(node: Node):
    if 'inherits' in node:
        node['inherits'] = set(node['inherits'].split(', '))

    node['table'] = pd.DataFrame(columns=['kind', 'type', 'visibility', 'link'])

    if node.children:
        child = node.children.pop()
        node['table'] = pd.concat([node['table'], child['table']])

    node['link'] = node
    node['table']['link'] = [None] * len(node['table'].index)

    node.blacklist('table', 'inherits')


def _body(node: Node):
    data = []
    if 'table' in node.parent:
        data.append(node.parent['table'])

    if 'table' in node.children[0]:
        data.append(node.children[0]['table'])
        del node.children[0]

    # data.append(pd.DataFrame([['body', node]], index=['body'], columns=['kind', 'link']))
    if data:
        data = pd.concat(data)
        data.where(data.notnull(), None, inplace=True)

        _has_duplicates(data)
        node.parent['table'] = data
    # node.parent.children.remove(node)


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
                _has_duplicates(frame)

                frame = pd.concat([frame, first['table']])
                frame['name'] = frame.index
                frame['name'].mask(frame['kind'] == 'function', frame['name'] + '-' + frame['type'], inplace=True)

                s = frame['name'].duplicated().to_dict()
                for k, v in s.items():
                    if v:
                        SYS['log'].warning(f'WARNING::OVERRIDE::{k} shadowed in {first["name"]}')
                        if first['table'].loc[k]['kind'] == 'variable':
                            SYS['log'].error(f'ERROR::VARIABLE OVERRIDE::{k} illegally shadowed in {first["name"]}')

                frame.mask(frame.isnull(), '-', inplace=True)
                frame.mask(frame['name'].duplicated(), None, inplace=True)
                frame.dropna(axis=0, inplace=True)
                frame.mask(frame == '-', None, inplace=True)
                frame.drop(columns=['name'], inplace=True)

                first['table'] = frame
                first.drop('inherits')

            if 'inherits' not in first:
                defined.add(first['name'])

                _func_handler(first, node)
            else:
                buffer.append(first)

        if length == len(buffer):
            error = [b['name'] for b in buffer]
            SYS['log'].error(f'Cyclic dependency detected while processing {", ".join(error)}')
            node['table'].drop(index=error, inplace=True)
            break


def _func_handler(node: Node, root: Node):
    global_func = root['table']
    global_func = global_func[global_func['kind'] == 'function']
    global_func = global_func[global_func.index.str.contains(node['name'] + '::')]
    global_func.index = global_func.index.str.replace(r'.*::(.*)', r'\g<1>', regex=True)

    local_func = node['table']
    for row, series in global_func.iterrows():
        if row in local_func.index:
            local_series = local_func.loc[row]
            if local_series['type'] == series['type'] and local_series['kind'] == series['kind']:
                node['table'].loc[row]['link'] = series['link']
                node.adopt(series['link'])
                series['link']['name'] = row
        else:
            SYS['log'].error(f'ERROR::BINDING::Function {row} in class {node["name"]} has no binding')

        root.children.remove(series['link'])
        series['link'].drop('link')
        root['table'].drop(index=node['name'] + '::' + row, inplace=True)


def _type_check(root: Node):
    queue = deque(root['table']['link'].dropna().to_list())

    allowed_types = ['float', 'void', 'integer', 'string'] + root['table'].index.to_list()
    visited = set()

    while queue:
        node = queue.popleft()
        if node.uid in visited:
            continue

        visited.add(node.uid)
        if 'link' in node['table'].columns:
            _link_check(node)
            queue.extend(node['table']['link'].dropna().to_list())

        for row, series in node['table'].iterrows():
            typedef = series['type'].replace('[]', '')

            if series['kind'] == 'function':
                typedef = typedef[typedef.index(':') + 2:]

            if typedef not in allowed_types:
                node['table'].drop(index=row, inplace=True)
                SYS['log'].error(f'ERROR::TYPE::{series["type"]} of {row} not allowed in {node["name"]}')


def _link_check(node: Node):
    table = node['table'][node['table']['kind'] == 'function']
    table = table.index[table['link'].isnull()]

    if not table.empty:
        table = table.to_list()
        node['table'].drop(index=table, inplace=True)
        SYS['log'].error(f'ERROR::FUNCTION::Function {table} in class {node["name"]} has not been defined')


def _prog(node: Node):
    child = node.children.pop()
    node.update(child)
    node['name'] = 'prog'
    for n in node['table']['link'].dropna().to_list():
        node.adopt(n)
        n.drop('link')

    _has_duplicates(node['table'])
    _inheritance_handler(node)
    _type_check(node)


def _main(node: Node):
    node['name'] = 'main'
    node['link'] = node
    node.blacklist('table')


SYS = {
    'log': logging.getLogger('test'),
    'prog': _prog,
    'group': _group,
    'function': _function,
    'body': _body,
    'parameter': _variable,
    'variable': _variable,
    'index': _index,
    'class': _class,
    'main': _main,
}
