from collections import deque
from operator import itemgetter
import pandas as pd

from symantec.preprocessor import nlabels
from syntax import Node
from lex import Token

def inheritance(node: Node):
    weights = []

    for index, series in node.label.iterrows():
        queue = deque(series['link'][1:])

        visited = {index}

        while queue:
            name = queue.pop()
            if name in visited:
                raise RecursionError()
            elif name not in node.label.index:
                raise TypeError()

            visited.add(name)
            queue.extend(node.label.loc[name]['link'][1:])

        if len(visited) != 1:
            weights.append((index, len(visited)))

    weights.sort(key=itemgetter(1), reverse=True)

    while weights:
        index, _ = weights.pop()
        pointer = node.label.loc[index]
        entry = pointer['link'][0].label
        links = pointer['link'][1:]

        frame = pd.DataFrame(columns=nlabels)
        for name in links:
            reference = node.label.loc[name]['link'][0]
            frame = frame.append(reference.label)
            if any(frame.index.duplicated()):
                raise NameError()

        node.label.loc[index]['link'] = [node.label.loc[index]['link'][0]]
        for index, series in frame.iterrows():
            if index in entry.index:

                if series['type'] == entry.loc[index]['type'] and \
                        series['kind'] == entry.loc[index]['kind'] and \
                        series['visibility'] == entry.loc[index]['visibility']:
                    print('warning override')
                else:
                    raise TypeError
            else:
                pointer['link'][0].label = entry.append(series)



def bfs(root):
    queue = deque([root])
    while queue:
        node = queue.popleft()
        queue.extend(node.children)
        yield node

def indexlist(node: Node):
    pass



def convert(node: Node, type):
    node.label.type = type

def binary_op(node: Node):
    second = node.children[-1]
    first = node.children[0]

    if first == second:
        node.label.lexeme = node.label.lexeme + second.label.lexeme
        node.label.type = second.label.type
        node.children.pop()
    else:

        if first.label.type != second.label.type:
            raise TypeError('the type {} != {}'.format(first.label.type, second.label.type))

        node.label.type = second.label.type

def args(node: Node):
    types = []
    values = []
    for child in node.children:
        types.append(child.label.type)
        values.append(child.label.lexeme)

    types = ', '.join(types)


    node.label = Token(types, 'args', -1)


def call(node: Node):
    first = node.children[0]
    second = node.children[1]

    if first.label.type != 'id':
        raise TypeError
    else:
        first.label.type = 'function'

    node.label = Token(first.label.lexeme + ' : ' + second.label.type, 'Call', -1)



def dot(node: Node, global_table):
    first = node.children[0]
    second = node.children[1]

    if first.label.type not in global_table.label.index:
        raise TypeError
    ref = global_table.label.loc[first.label.type]
    ref = ref['link'][0]# todo remove the [0]

    if ' : ' in second.label.type:
        func_name, typedef = second.label.type.split(' : ')

        if func_name not in ref.label.index:
            raise TypeError
        ref = ref.label.loc[func_name]

        params, return_type = ref['type'].split(' : ')
        if params != typedef:
            raise TypeError(func_name)

        node.label.type = return_type

    else:
        if first.label.type != second.label.type:
            raise TypeError
        node.label.type = first.label.type


def make_function(node: Node):
    node.label.type = 'function'

def new_token(node: Node):
    node.label = Token(node.label, '{...};', -1)
def variable(node: Node, cache={}):

    name = node.children[0].label.lexeme
    index = node.children[1].label

    if name not in cache:
        parent = node.parent
        while parent and \
                (not isinstance(parent.label, pd.DataFrame) or name not in parent.label.index):
            parent = parent.parent
        if parent and name in parent.label.index:
            cache[name] = parent.label.loc[name]

    name_type = cache[name]['type']
    if index != 'ε':
        pass
    else:
        name_type += ''
    node.label = Token(name_type, name, -1)
    node.children = []

def remove(node: Node):
    i = node.parent.children.index(node)
    node.parent.children[i] = node.children[0]
    node.children[0].parent = node.parent

def return_type(node: Node):
    pass


PHASE2 = {
    'ROOT': None,
    'variable': variable,
    'floatnum': lambda x: convert(x, 'float'),
    'intnum': lambda x: convert(x, 'integer'),
    'stringlit': lambda x: convert(x, 'string'),
    'minus': binary_op,
    'args': args,
    'Call': call,
    'dot': lambda x: dot(x, PHASE2['ROOT']),
    'write': make_function,
    'while': make_function,
    'leq': binary_op,
    'assign': binary_op,
    'Block': new_token,
    'mult': binary_op,
    'plus': binary_op,
}
# 'write': remove,
#     'leq': binary_op,



def reference_fixer(node: Node):

    children = list(bfs(node))
    children.reverse()
    cache = {}
    for child in children:

        if isinstance(child.label, str) and child.label in PHASE2:
            PHASE2[child.label](child)
        elif isinstance(child.label, Token) and child.label.type in PHASE2:
            PHASE2[child.label.type](child)

def function_parse(node: Node):
    functions = list(filter(lambda x: '::' in x, node.label.index.to_list()))
    for function in functions:
        class_name, func_name = function.split('::')

        if class_name in node.label.index:
            class_ref = node.label.loc[class_name]['link']
            for link in class_ref:
                if isinstance(link, Node) and func_name in link.label.index and node.label.loc[function]['type'] == \
                        link.label.loc[func_name]['type']:
                    link.label.loc[func_name] = node.label.loc[function]
        node.label.drop(index=function, inplace=True)
    # todo complete this because we want to bind functions.

