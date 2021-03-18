import logging
import sys
from pathlib import Path

from syntax import *
from lex import *


def help(exception: Exception = None):
    print(
        """syntaxdriver.py <file> [config_directory]

    <file>:
        Source code file ending with the extension .src
    [config]:
        Segment of program containing the tokens and regular expressions

        Must contain grammar.conf file within the config folder\n""")

    if exception:
        print(exception)

    exit(0)


if __name__ == '__main__':
    args = len(sys.argv)
    path = Path(sys.argv[1] if args >= 2 else '../examples/bubblesort.src')
    config = sys.argv[2] if args >= 3 else './_config/'

    try:
        out = str(path.parent) + '\\' + str(path.stem)
        out_ast = Path(out + '.outast.png')
        out_errors = Path(out + '.outerrors.log')
        out_derivations = Path(out + '.outderivations.log')

        fh = logging.FileHandler(out_errors, mode='w', encoding='utf-8')
        fh.setLevel(logging.DEBUG)

        s = scanner(suppress_comments=1)
        s.open(path)

        f = Parser.load(fh)
        resp = f.parse(s)
        out_derivations.write_text(' '.join([x.type for x in f.productions]))
        f.ast.render(out_ast)
        print('The src "{}" is {}valid.'.format(str(path), '' if resp else 'not '))
    except Exception as err:
        help(err)
