import re

from collections import deque


import pandas as pd

from syntax import Node

nlabels = ['kind', 'type', 'visibility', 'link']


def delete(*nodes: Node):
    for node in nodes:
        if node.parent:
            node.parent.children.remove(node)
        del node


def group(node: Node):
    frame = pd.DataFrame([x.to_series() for x in node.children])
    if any(frame.index.duplicated()):
        raise TypeError(f'Duplicate found in table:\n{str(frame)}')

    deletions = list(filter(lambda x: 'link' not in x, node.children))
    delete(*deletions)

    frame = frame.where(frame.notnull(), None)
    node['table'] = frame


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
        raise TypeError(f'Array indices "{",".join(x["name"] for x in node.children)}" is not of type integer.')

    node.parent['index'] = [int(x['name']) for x in node.children]
    node.parent.blacklist('index')
    delete(*node.children, node)


def function(node: Node):
    if 'return' not in node:
        return

    node['type'] = ' : ' + node['return']

    if node.children:
        ref = node['table'] = pd.concat([x['table'] for x in node.children])

        if any(ref.index.duplicated()):
            raise TypeError(f'Duplication of parameters and variables found in function "{node["name"]}"')

        parameters = ref.loc[ref['kind'] == 'parameter']['type'].to_list()
        node['signature'] = parameters
        node['type'] = ', '.join(parameters) + node['type']

        while True and node.children:
            if node.children[0]['kind'] == 'body':
                # node['link'] = node.children[0]
                node.children[0].drop('table')
                break
            del node.children[0]

        node['link'] = node
        node.blacklist('table', 'signature')

        node.override('__eq__',
                       lambda x:
                       isinstance(x, Node) and \
                       x['name'] == node['name'] and \
                       x['type'] == node['type'] and \
                       x['kind'] == node['kind'])

        if '::' in node['name']:
            node['binding'], _ = node['name'].split('::')
            node.blacklist('type')
    node.blacklist('binding', 'return')


def Class(node: Node):
    if 'inherits' in node:
        node['inherits'] = set(node['inherits'].split(', '))

    if node.children:
        child = node.children.pop()
        node['link'] = child
        child.update(node)
        index = node.parent.children.index(node)
        node.parent.children[index] = child
        child.parent = node.parent

        child.override('__eq__',
                       lambda x:
                       isinstance(x, Node) and \
                       x['name'] == child['name'] and \
                       x['kind'] == child['kind'])

        child.blacklist('table', 'inherits')

    else:
        node.blacklist('table', 'inherits')


def body(node: Node):
    if node.children and 'table' in node.children[0]:
        node['table'] = node.children[0]['table']
        del node.children[0]
    else:
        node['table'] = pd.DataFrame()


def prog(node: Node):
    child = node.children.pop()
    node['table'] = child['table']
    node.adopt(*child.children)
    del child
    table = node['table']


    #CLASSES
    buffer = deque(table['link'][table['kind'] == 'class'].to_list())
    defined = set()
    while buffer:
        length = len(buffer)

        for i in range(length):

            first = buffer.popleft()
            if 'inherits' not in first:
                defined.add(first['name'])

            elif not first['inherits'].difference(defined):
                frame = pd.concat([table.loc[x]['link']['table'] for x in first['inherits']])
                if any(frame.index.duplicated()):
                    raise TypeError(f'duplicates found for inheritance:\r\n{str(frame)}')

                for name, series in frame.iterrows():
                    if name in first['table'].index:
                        print('something')
                    else:
                        first['table'] = first['table'].append(series)


                defined.add(first['name'])
                first.drop('inherits')

            else:
                buffer.append(first)

        if length == len(buffer):
            raise TypeError('no change')

    #FUNCTIONS
    buffer = deque(table['link'][table['kind'] == 'function'].to_list())
    while buffer:
        func = buffer.popleft()
        if 'binding' not in func:
            continue
        name = func['name']

        if func['binding'] not in table.index:
            raise TypeError(f'function "{name}" overrides non-existent class "{func["binding"]}"')

        binding, name = func['name'].split('::')

        reference = table.loc[binding]['link']

        if reference['kind'] != 'class':
            raise TypeError(f'function "{name}" attempting to override a global function "{func["name"]}"')

        if name not in reference['table'].index:
            raise TypeError(f'function "{name}" overriding non-existent class function')


        node.children.remove(func)
        table.drop(index=func['name'], inplace=True)

        c = reference['table'].loc[name]['link']
        i = reference.children.index(c)
        reference.children[i] = func
        reference['table'].loc[name]['link'] = func
        func.parent = reference
        func['name'] = name


def main(node: Node):
    if node.children:


        child = node.children.pop()
        node['link'] = child

        child.parent = node.parent
        index = node.parent.children.index(node)
        node.parent.children[index] = child
        child.update(node)
        child.blacklist('table')

    del node


SYS = {
    'prog': prog,
    'group': group,
    'function': function,
    'body': body,
    'variable': variable,
    'index': index,
    'class': Class,
    'main': main,
}
