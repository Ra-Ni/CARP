import logging

import pydot


from lex import *
from symantec import *
from syntax import *

EXAMPLE = '../examples/syntax/polynomial_correct.src'


new_label = ('kind', 'type', 'visibility', 'link')


def bfs(root: Node):
    queue = deque([(None, root)])
    while queue:
        parent, n = queue.popleft()
        if 'table' in n and 'link' in n['table'].columns:
            children = n['table']['link'].to_list()

            children = list(filter(lambda x: x is not None, children))
            children = list(map(lambda x: (n, x), children))

        else:
            children = list(map(lambda x: (n, x), n.children))

        queue.extend(children)
        yield parent, n


def render(ast: AST, src: str):
    graph = pydot.Dot('AST', graph_type='digraph')
    nodes = {}
    for parent, node in bfs(ast.root):
        label = node.to_string()

        nodes[node.uid] = pydot.Node(node.uid, label=label.replace('\r\n', '\l'))
        graph.add_node(nodes[node.uid])

        if parent:
            graph.add_edge(pydot.Edge(nodes[parent.uid], nodes[node.uid]))
    graph.write_png(src, encoding='utf-8')


def help(exception: Exception = None):
    print(
        """symantecdriver.py <file>

    <file>:
        Source code file ending with the extension .src\n""")

    if exception:
        print(exception)

    exit(0)


if __name__ == '__main__':

    try:
        errors = logging.FileHandler('errors.log', mode='w', encoding='utf-8', delay=True)
        errors.setLevel(logging.ERROR)


        scanner = Scanner.load(EXAMPLE, suppress_comments=1)
        syntax_analyzer = Parser.load()
        response = syntax_analyzer.parse(scanner)
        ast = syntax_analyzer.ast
        symantec_table = SymantecTable(errors)
        symantec_table.parse(ast)

        ast.render('test.png')
    except Exception as err:
        help(err)
