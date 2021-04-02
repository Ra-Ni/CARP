from collections import deque
from operator import itemgetter

import pandas as pd
import heapq as hq

from _config import CONFIG
from syntax import Node

nlabels = ['kind', 'type', 'visibility', 'link']


def delete(node: Node):
    while node.children:
        del node.children[-1]


def dim(node: Node):
    if node.label == CONFIG['EPSILON']:
        node.label = ''
    elif node.label == 'dim':
        node.label = '[]' * len(node.children)
        node.label = node.label.replace(CONFIG['EPSILON'], '')
        delete(node)


def vardecl(node: Node):
    dim(node.children[2])

    typedef = node.children[0].label + node.children[2].label
    name = node.children[1].label
    node.label = pd.Series(data=['variable', typedef, None, None], index=nlabels, name=name)

    delete(node)


def params(node: Node):
    node.label = pd.DataFrame([x.label for x in node.children], columns=nlabels)
    node.label['kind'] = ['parameter'] * len(node.label['type'])
    delete(node)

    if any(node.label.index.duplicated()):
        raise TypeError('Duplicate parameter found')


def func(node: Node):
    scope = node.children[0].label
    name = node.children[1].label
    parameters = node.children[2]
    return_type = node.children[3].label
    statements = node.children[4]

    if scope == CONFIG['EPSILON']:
        scope = ''
    else:
        scope += '::'
    name = scope + name

    if isinstance(parameters.label, str):
        parameters.label = pd.DataFrame(columns=nlabels)

    if isinstance(statements.label, str):
        statements.label = parameters.label
    else:
        statements.label = parameters.label.append(statements.label)

    param_entries = ', '.join(parameters.label['type']) + ' : ' + return_type

    node.label = pd.Series(['function', param_entries, None, statements], index=nlabels, name=name)
    node.children.remove(statements)
    delete(node)

    if name in statements.label:
        raise ReferenceError('Duplicate name in parameter and function name')


def decl(node: Node):
    node.label = node.children[1].label
    node.label['visibility'] = node.children[0].label
    delete(node)


def group(node: Node):
    frame = pd.DataFrame(columns=nlabels)
    for child in node.children:
        series = child.label
        if series.name in frame.index:
            if series['kind'] == 'function' and series['type'] == frame.loc[series.name]['type']:
                raise TypeError('Duplicate function in group')
            else:
                raise TypeError('Duplicate something in group')

        if series['link']:
            series['link'].parent = node
        frame = frame.append(series)

    node.label = frame.where(frame.notnull(), None)

    delete(node)


def body(node: Node):
    if isinstance(node.children[0].label, pd.DataFrame):
        node.label = node.children[0].label
        del node.children[0]
    else:
        node.label = pd.DataFrame(columns=nlabels)

    body_node = Node('body')
    body_node.adopt(*node.children)
    node.children = []
    body_node.parent = node
    node.label = node.label.append(pd.Series(['function', None, None, body_node], index=nlabels, name='body'))


def inherits(node: Node):
    if node.label == CONFIG['EPSILON']:
        node.label = None
    elif not isinstance(node.label, list):
        node.label = [x.label for x in node.children]
        delete(node)


def Class(node: Node):
    inherits(node.children[1])

    name = node.children[0].label
    inheritance = node.children[1].label
    link = node.children[2]

    node.label = pd.Series(['class', None, None, link, inheritance], index=nlabels + ['inherits'], name=name)
    node.children.pop()
    delete(node)


def main(node: Node):
    child = node.children.pop()
    child.parent = node.parent
    node.label = pd.Series(['function', None, None, child], index=nlabels, name='main')


def inheritance_check(node: Node):
    heap = []

    for index, series in node.label.iterrows():
        if series['inherits'] is None:
            continue
        queue = deque(series['inherits'])

        visited = {index}

        while queue:
            name = queue.pop()
            if name in visited:
                raise RecursionError('cyclic inheritance detected')
            elif name not in node.label.index:
                raise TypeError('inheritance not defined')

            visited.add(name)
            if node.label.loc[name]['inherits']:
                queue.extend(node.label.loc[name]['inherits'])

        if len(visited) != 1:
            hq.heappush(heap, (len(visited) - 1, index))

    while heap:
        _, index = hq.heappop(heap)
        pointer = node.label.loc[index]
        entry = pointer['link'].label
        links = pointer['inherits']
        frame = pd.DataFrame(columns=nlabels)

        for name in links:
            frame = frame.append(node.label.loc[name]['link'].label)
            if any(frame.index.duplicated()):
                raise NameError('Duplicate found')

        node.label.loc[index]['inherits'] = None

        for index, series in frame.iterrows():
            if index in entry.index:
                if series['type'] == entry.loc[index]['type'] and \
                        series['kind'] == entry.loc[index]['kind'] and \
                        series['visibility'] == entry.loc[index]['visibility']:
                    print('warning override')
                else:
                    raise TypeError('multiple definitions')
            else:

                pointer['link'].label = entry.append(series)
    node.label.drop(columns='inherits', inplace=True)


def function_binding(node: Node):
    for index, series in node.label.iterrows():
        if '::' in index:
            class_name, func_name = series.name.split('::')
            func_type = series['type']

            if class_name not in node.label.index:
                raise TypeError('class binding not found')

            function = node.label.loc[class_name]['link']

            if func_name not in function.label.index:
                raise TypeError(f'function name {func_name} does not exist in class {class_name}')
            # elif func_type not in node.label.loc[class_name]['link'].loc[func_name]:
            #     raise TypeError('function signature doesnt exist')

            series['link'].parent = function
            function.label.loc[func_name]['link'] = series['link']

            node.label.drop(index=series.name, inplace=True)


def call(node: Node):
    first = node.children[0]

    if node.parent.label == '.':
        node.parent.children.pop()
        node.parent.children.append(first)
        first.parent = node.parent

        previous = node
        current = node.parent
        while current.label == '.':
            previous = current
            current = current.parent

        i = current.children.index(previous)
        current.children[i] = node
        previous.parent = node
        node.parent = current
        node.children[0] = previous


SYS = {
    'dim': dim,
    'vardecl': vardecl,
    'params': params,
    'func': func,
    'decl': decl,
    'class': Class,
    'group': group,
    'body': body,
    'inherits': inherits,
    'main': main,
    'call': call,
}
