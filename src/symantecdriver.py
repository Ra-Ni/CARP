import uuid
from collections import deque
from operator import itemgetter

import pandas as pd
import pydot
from tabulate import tabulate

from lex import Scanner, Token
from symantec.label import Label, labels, nlabels
from syntax import Parser, AST, Node

EXAMPLE = '../examples/syntax/polynomial_correct.src'

new_label = ('kind', 'type', 'visibility', 'link')


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
    if node.children and isinstance(node.children[0].label, pd.DataFrame):
        node.label = node.label.append(node.children[0].label)
        node.children.pop(0)


def empty(node: Node, name):
    node.label = Label()

    node.label.frame = pd.DataFrame(columns=['kind', 'type', 'visibility', 'link'])
    node.label.series = pd.Series(index=node.label.frame.columns, name=name, dtype='object')


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


def inheritance(node: Node):
    watch_list = []

    for index, series in node.label.iterrows():
        series_length = len(series['link'])

        if series_length > 1:

            series['link'].reverse()
            references = []

            while series['link']:
                top = series['link'].pop()
                if isinstance(top, Node):
                    references.append(top)
                elif top in node.label.index:
                    references.extend(node.label.loc[top]['link'])
                else:
                    pass
            series['link'] = references
            watch_list.append((series['link'], series_length))
    watch_list.sort(key=itemgetter(1))

    # todo merge the links


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

roots = None
PHASE2 = {
    'variable': variable,
    'floatnum': lambda x: convert(x, 'float'),
    'intnum': lambda x: convert(x, 'integer'),
    'stringlit': lambda x: convert(x, 'string'),
    'minus': binary_op,
    'args': args,
    'Call': call,
    'dot': lambda x: dot(x, roots),
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


def render(node: Node, src: str):
    queue = deque([node])
    graph = pydot.Dot('AST', graph_type='digraph')
    nodes = {}

    while queue:
        node = queue.pop()
        label = str(node.label)
        if isinstance(node.label, pd.DataFrame):
            label = str(tabulate(node.label, headers='keys', tablefmt='psql'))
        nodes[node.uid] = pydot.Node(node.uid, label=str(label), labeljust='l', shape='box')
        graph.add_node(nodes[node.uid])

        if node.children:
            for c in node.children:
                d = nodes.setdefault(c.uid, pydot.Node(c.uid, label=str(c)))
                queue.append(c)
                graph.add_edge(pydot.Edge(nodes[node.uid], d))
        if isinstance(node.label, pd.DataFrame):
            children = node.label['link'].to_list()
            for c in children:
                if c is not None:
                    for child in c:
                        if isinstance(child, Node):
                            c = nodes.setdefault(child.uid, pydot.Node(child.uid, label=child.label.to_string()))
                            queue.append(child)
                            graph.add_edge(pydot.Edge(nodes[node.uid], c))

    graph.write_png(src, encoding='utf-8')


if __name__ == '__main__':
    scanner = Scanner.load(EXAMPLE, suppress_comments=1)
    syntax_analyzer = Parser.load()
    response = syntax_analyzer.parse(scanner)
    ast = syntax_analyzer.ast
    nodes = list(filter(lambda x: len(x.children) > 0, ast.bfs()))
    nodes.reverse()

    for node in nodes:
        if node.label in SYS:
            SYS[node.label](node)
        if isinstance(node.label, Token) and node.label.lexeme == node.label.type and node.label.lexeme in SYS:
            SYS[node.label.lexeme](node)

    root = ast.root
    roots = ast.root
    #inheritance(root)
    function_parse(root)
    #reference_fixer(root.label.loc['main']['link'][0])
    # reference_fixer(root.label.loc['POLYNOMIAL']['link'][0].label.loc['evaluate']['link'][0])
    render(ast.root, 'test.png')
