import logging

import pydot


from lex import *
from symantec import *
from syntax import *

EXAMPLE = '../examples/symantec/polyerror.src'


new_label = ('kind', 'type', 'visibility', 'link')


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
        errors.setLevel(logging.DEBUG)
        scanner = Scanner.load(EXAMPLE, suppress_comments=1)
        syntax_analyzer = Parser.load()
        response = syntax_analyzer.parse(scanner)
        ast = syntax_analyzer.ast
        sym_table = SymantecTable.from_ast(ast, errors)


        sym_table.render('test.png')
    except Exception as err:
        help(err)
