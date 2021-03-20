import logging
import sys
from pathlib import Path


from syntax import *
from lex import *

OUT_AST = '.outast.png'
OUT_ERRORS = '.outerrors.log'
OUT_DERIVATIONS = '.outderivations.log'
EXAMPLE = '../examples/syntax/polynomial.src'


def help(exception: Exception = None):
    print(
        """syntaxdriver.py <file>

    <file>:
        Source code file ending with the extension .src\n""")

    if exception:
        print(exception)

    exit(0)


if __name__ == '__main__':
    path = Path(sys.argv[1] if len(sys.argv) >= 2 else EXAMPLE)

    try:
        out = str(path.parent) + '\\' + str(path.stem)
        out_ast = Path(out + OUT_AST)
        out_errors = Path(out + OUT_ERRORS)
        out_derivations = Path(out + OUT_DERIVATIONS)

        errors = logging.FileHandler(out_errors, mode='w', encoding='utf-8', delay=True)
        errors.setLevel(logging.ERROR)

        derivations = logging.FileHandler(out_derivations, mode='w', encoding='utf-8', delay=True)
        derivations.setLevel(logging.INFO)
        derivations.terminator = ' '

        s = Scanner.load(src_file=path, suppress_comments=1)
        f = Parser.load(errors, derivations)
        resp = f.parse(s)
        f.ast.render(out_ast)
        print('The src "{}" is {}valid.'.format(str(path), '' if resp else 'not '))
    except Exception as err:
        help(err)
